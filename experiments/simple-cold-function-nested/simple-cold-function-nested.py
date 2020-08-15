

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
Every invocation is made with a nested invocation to avoid any outside noise and
network overhead, measuring only the latency from one invocation to the next.
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
nested_fx = 'function2'

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

invoke_1_nested = [
        {
            "function_name": f"{experiment_name}-{nested_fx}",
            "invoke_payload": {
                "StatusCode": 200,
            }
        }
    ]
# invoke function and return the result dict
def invoke():
    response = benchmarker.invoke_function(function_name=fx,
                                        function_args= {'invoke_nested': invoke_1_nested})
    if 'error' in response:
        return errors.append(response)
    nested_dict = response[list(response.keys())[1]]
    return nested_dict if 'error' not in nested_dict else errors.append(nested_dict)



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

def find_benchmark():
    from functools import reduce

    iterations = 100
    response_times = []

    # should be a cold invocation
    first_res = benchmarker.invoke_function(function_name='function3')
    cold_latency = first_res['execution_start']-first_res['invocation_start']

    if verbose:
        print('first cold invocation:')
        pprint(first_res)
        print()

    if verbose:
        print(f'invoking function {iterations} times to find an average latency')

    for i in range(iterations):
        t1 = time.time()
        res = lib.get_dict( benchmarker.invoke_function(function_name='function3') )
        t2 = time.time()
        time.sleep(1)
        response_times.append(
            (i, res['execution_start']-res['invocation_start'], t2-t1, res['instance_identifier'])
        )

    response_times.sort(key=lambda x: x[1])

    sliced = response_times[20:80]

    sliced_avg = reduce(lambda x,y: x+y[1],[0.0] + sliced)/len(sliced)

    average_warmtime = sliced_avg * 2

    if verbose:
        print(f'found average {sliced_avg}, adjusted: {average_warmtime}')

    return (cold_latency, sliced_avg, average_warmtime)

def check_coldtime(sleep: int, coldtime: float):
    global benchmark

    if verbose:
        print('check_coldtime', sleep, coldtime)

    if(coldtime > benchmark):
        print(f'benchmark found: {benchmark}, with {coldtime} as coldtime')
        return
    elif(sleep > 7200):
        raise Exception(
            'Benchmark could not be established after 2 hours sleep_time')
    else:
        time.sleep(sleep)
        local_coldtime, avg_warmtime, benchmark = find_benchmark()
        if(coldtime < benchmark):
            check_coldtime(sleep+1200, coldtime)
    
    # Find the values for when coldtimes occure
def set_cold_values():
    global sleep_time, increment, granularity, latest_latency_time, large_increment, minute_increment
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
                ('experiment_uuid,result_dict[\'instance_identifier\']',experiment_uuid, result_dict['instance_identifier']),
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
                ('Final result', False),
                ('latency', latency_time)
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

    #  initial_cold_start_response = validate(invoke, 'initial coldtime')
    #  coldtime = initial_cold_start_response['execution_start'] - initial_cold_start_response['invocation_start']
    #  if verbose:
        #  print('init coldtime', coldtime)

    # calculates avg. time for warm function, default is 5 invocations as input and keys execution_start - invocation_start
    #  invo_list = create_invocation_list()
    #  avg_warmtime = validate(lib.reduce_dict_by_keys, 
                            #  'avg_warmtime',
                            #  (invo_list, ('execution_start', 'invocation_start')) )
    
    # coldtime is adjusted by 10% to avoid coldtime being an outlier
    # openfaas sometimes has large variation in cold time
    #  if coldtime > (10 * avg_warmtime):
        #  benchmark = avg_warmtime * 10
    #  else:
        #  benchmark = coldtime * 0.8
        #  benchmark = avg_warmtime * 1.75

    coldtime, avg_warmtime, benchmark = find_benchmark()

    if verbose:
        print('init benchmark', benchmark)
    # sleep for 40 minutes if coldtime is not cold
    check_coldtime(40*60, coldtime)

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
