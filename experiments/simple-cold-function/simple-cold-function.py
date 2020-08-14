

import sys
import json
from benchmarker import Benchmarker
import time
from datetime import datetime
import traceback
from mysql_interface import SQL_Interface
import function_lib as lib
from pprint import pprint

# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = sys.argv[1]

# unique identifier string tying this experiment together with the
# experiments conducted for the other cloud providers in this round
experiment_meta_identifier = sys.argv[2]

# name of cloud function provider for this experiment
provider = sys.argv[3]

# name of the client provider
client_provider = sys.argv[4]

# relative path to experiment.env file
env_file_path = sys.argv[5]

# dev_mode
dev_mode = eval(sys.argv[6]) if len(sys.argv) > 6 else False

# verbose mode
verbose = eval(sys.argv[7]) if len(sys.argv) > 7 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment tests the time it takes for
a single function instance to no longer be available due to inactivity.
The experiment is conducted by first invoking a single function 11 times,
the first time to make sure that the function instane is created, the the following
10 times to create a baseline for a hot invocation.
Then the function is invoked continually with increasing delay between invocations,
until the function is a cold start for each invocation with that delay.
This process is then repeated and averaged.
"""
# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          experiment_meta_identifier=experiment_meta_identifier,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode,
                          verbose=verbose)
# =====================================================================================
# database interface for logging results if needed
db = SQL_Interface(dev_mode)
# name of table to insert data into
table = 'Coldstart'
# =====================================================================================
# set meta data for experiment
# UUID from experiment
experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3)
fx = 'function1'

# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(65*60)

# values used for aborting experiment if it runs more than 24 hours
_timeout = 24 * 60 * 60
start_time = time.time()

# cold benchmark 
benchmark = None

# time to sleep in between invocations, start at 5 minutes
sleep_time = 300
# increment for each iteration
increment = sleep_time
# granularity of result
granularity = 20
# value for last response latency
latest_latency_time = 0
# flags for controlling granularity of sleep value
large_increment = True
minute_increment = True

# results specific gathered and logged from logic of this experiment
results = []

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
# if thread_numb > 1 it will be done concurrently and the result averaged
def invoke():
    response = lib.get_dict(
        benchmarker.invoke_function(function_name=fx))
    return response if 'error' not in response else errors.append(response)



# the wrapper ends the experiment if any it can not return a valid value
def err_func(): return benchmarker.end_experiment()

# convinience for not having to repeat values
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)


# creates list of invocation dicts.
# args: tuble(x,y) -> x=length_of_list, y=error_point_string
create_invocation_list = lambda x=(5, 'create invocation_list'): [
    validate(invoke, x[1]) for i in range(x[0])]

# parse data that needs to be logged to database.
def append_result(
                invo_id,
                minutes,
                seconds,
                granularity,
                cold,
                final,
                multithreaded=False) -> None:
    global benchmark

    results.append({
        'exp_id': experiment_uuid,
        'invo_id': invo_id,
        'minutes': minutes,
        'seconds': seconds,
        'granularity': granularity,
        'threads':1,
        'benchmark': benchmark,
        'cold': cold,
        'final': final
        })

# =====================================================================================
# The actual logic if the experiment

def check_coldtime(sleep: int, warmtime: float):
    global benchmark

    if verbose:
        print('check_coldtime', sleep, warmtime)

    if(warmtime * 1.2 < benchmark):
        print(f'benchmark found: {benchmark}, with {warmtime} as warmtime')
        return
    elif(sleep > 7200):
        raise Exception(
            'Benchmark could not be established after 2 hours sleep_time')
    else:
        time.sleep(sleep)
        res_dict = validate(invoke, 'initial coldtime reset')
        local_coldtime = res_dict['execution_start'] - res_dict['invocation_start']

        avg_warmtime = validate(lib.reduce_dict_by_keys, 
                                'avg_warmtime reset', 
                                (create_invocation_list((10, 'create invocation_list')), 
                                ('execution_start', 'invocation_start')))

        if local_coldtime > (10 * avg_warmtime):
            benchmark = avg_warmtime * 10
        else:
            benchmark = local_coldtime * 0.8

        if(avg_warmtime > benchmark):
            check_coldtime(sleep+1200, avg_warmtime)
    
    # Find the values for when coldtimes occure
def set_cold_values():
    global sleep_time, increment, granularity, latest_latency_time,large_increment,minute_increment
    while(True):
        if time.time() - start_time > _timeout:
            print('ABORTING due to 30 hour time constraint from set_cold_values function\n')
            benchmarker.end_experiment()
            # log experiments specific results, hence results not obtainable from the generic Invocation object
            lib.log_experiment_specifics(experiment_name,
                                    experiment_uuid, 
                                    len(errors), 
                                    db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
            sys.exit()

        time.sleep(sleep_time)
        result_dict = validate(invoke,f'invoking function: {fx} from cold start experiment')
        latest_latency_time = result_dict['execution_start'] - result_dict['invocation_start']

        if(verbose):
            lib.dev_mode_print('logging time from set_cold_values', [
                ('experiment_uuid,result_dict[identifier]',experiment_uuid, result_dict['identifier']),
                ('sleep_time / 60', int(sleep_time / 60)),
                ('sleep_time % 60', int( sleep_time % 60)),
                ('increment', increment),
                ('coldtime', latest_latency_time > benchmark),
                ('Final result', False),
                ('latest_latency_time',latest_latency_time),
                ])
        if(latest_latency_time > benchmark):
            if large_increment:
                sleep_time -= increment
                large_increment = False
                increment = 60
                sleep_time += increment 
            elif minute_increment:
                sleep_time -= 60
                minute_increment = False
                increment = granularity
                sleep_time += increment 
            else:
                append_result(
                            result_dict['identifier'],
                            int(sleep_time / 60),
                            int(sleep_time % 60),
                            increment,
                            latest_latency_time > benchmark,
                            False)
                return
        else:
            sleep_time += increment

def verify_result():
    global sleep_time, granularity
    # variefy that result is valid by using same sleeptime between invocations 5 times
    iter_count = 5 if not dev_mode else 2
    while(iter_count > 0):
        if time.time() - start_time > _timeout:
            print('ABORTING due to 30 hour time constraint from varification loop\n')
            benchmarker.end_experiment()
            # log experiments specific results, hence results not obtainable from the generic Invocation object
            lib.log_experiment_specifics(experiment_name,
                                    experiment_uuid, 
                                    len(errors), 
                                    db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
            sys.exit()
            
        time.sleep(sleep_time)
        result_dict = validate(invoke, f'invoking function: {fx} from validation of cold start experiment')
        latency_time = result_dict['execution_start'] - result_dict['invocation_start']

        if(verbose):
            lib.dev_mode_print(f'logging cold time: {latency_time > benchmark} -> coldtime exp', [
                ('experiment_uuid,result_dict[instance_identifier]',experiment_uuid, result_dict['instance_identifier']),
                ('sleep_time / 60', int(sleep_time / 60)),
                ('sleep_time % 60', int(sleep_time % 60)),
                ('increment', increment),
                ('coldtime', latency_time > benchmark),
                ('Final result', False)
                ])
        
        append_result(
                    result_dict['identifier'],
                    int(sleep_time / 60),
                    int(sleep_time % 60),
                    increment,
                    latency_time > benchmark,
                    False)


        if(latency_time < benchmark):
            sleep_time += granularity
            iter_count = 5 if not dev_mode else 2
        else:
            iter_count -= 1
    
    # run one last time and log result as final or 
    time.sleep(sleep_time)

    result_dict = validate(invoke, f'invoking function: {fx} from final invocation of cold start experiment')
    latency_time = result_dict['execution_start'] - result_dict['invocation_start']
    if latency_time > benchmark:
        # log final result
        append_result(
                    result_dict['identifier'],
                    int(sleep_time / 60),
                    int(sleep_time % 60),
                    granularity,
                    True,
                    True)
    else:
        sleep_time += granularity
        verify_result()


try:

    initial_cold_start_response = validate(invoke, 'initial coldtime')
    coldtime = initial_cold_start_response['execution_start'] - initial_cold_start_response['invocation_start']
    if verbose:
        print('init coldtime', coldtime)

    # calculates avg. time for warm function, default is 5 invocations as input and keys execution_start - invocation_start
    invo_list = create_invocation_list()
    avg_warmtime = validate(lib.reduce_dict_by_keys, 
                            'avg_warmtime',
                            (invo_list, ('execution_start', 'invocation_start')) )
    
    # coldtime is adjusted by 10% to avoid coldtime being an outlier
    # openfaas sometimes has large variation in cold time
    if coldtime > (10 * avg_warmtime):
        benchmark = avg_warmtime * 10
    else:
        benchmark = coldtime * 0.8

    if verbose:
        print('init benchmark', benchmark)
    # sleep for 40 minutes if coldtime is not cold
    check_coldtime(40*60, avg_warmtime)

    if(verbose):
        lib.dev_mode_print('Initial Coldtime ', [
            ('coldtime', coldtime),
            ('benchmark', benchmark),
            ('avg_warmtime', avg_warmtime)
        ])


    if(verbose):
        lib.dev_mode_print('pre set_cold_values() coldtime exp', [
                            ('sleep_time', sleep_time), 
                            ('increment', increment),
                            ('granularity', granularity),
                            ('latest_latency_time',latest_latency_time)
                            ])
    
    set_cold_values()

    if(verbose):
        lib.dev_mode_print('post set_cold_values() coldtime exp', [
                            ('sleep_time', sleep_time), 
                            ('increment', increment),
                            ('granularity', granularity),
                            ('latest_latency_time',latest_latency_time)])
    
    verify_result()


    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================
    # log experiments specific results, hence results not obtainable from the generic Invocation object
    lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x, table) for x in results]))

except Exception as e:
    # this will print to logfile
    print(f'Ending experiment {experiment_name} due to fatal runtime error')
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print(f'Trace: {traceback.format_exc()}')
    print('-----------------------------------------')
    benchmarker.end_experiment()
