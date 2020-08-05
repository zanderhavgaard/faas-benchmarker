import sys
import json
import time
from pprint import pprint
from benchmarker import Benchmarker
from datetime import datetime
import traceback
from mysql_interface import SQL_Interface
import function_lib as lib

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
function instances to no longer be available due to inactivity in a multithreaded
environment.
The experiment is conducted by first creating a cold time baseline. This is done by i
nvoking a single function with 12 concurrent requests and average over the results. 
Then the same function is is invoked 10 times, again with 12 concurrent requests and 
averaged as a warm-time baseline.
Then the function is invoked with 12 multithreaded requests continually with increasing 
delay between invocations, until the avg of the requests falls within the cold time 
baseline.
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
# create database interface for logging results
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
    time.sleep(45*60) 

# number of threads to be used
threads = 0

# values used for aborting experiment if it runs more than 24 hours
_30_hours = 30 * 60 * 60
start_time = time.time()

# benchmark for cold value for function
benchmark = None
# avg_warmtime defines benchmark for warm start time for function
avg_warmtime = None
# time to sleep in between invocations, start at 5 minutes
sleep_time = None
# increment for each iteration
increment = None
# granularity of result
granularity = None
# flags for controlling granularity of sleep value
large_increment = None
minute_increment = None

# results specific gathered and logged from logic of this experiment
results = []

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
def invoke(thread_numb:int):
    
    # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
    invocations = list(filter(None, [x if 'error' not in x else errors.append(x) for x in map(lambda x: lib.get_dict(x), 
    benchmarker.invoke_function_conccurrently(function_name=fx, 
                                            numb_threads=thread_numb,
                                            function_args= {'throughput_time':0.2}))]))
<<<<<<< Updated upstream

    print('Trace for invocation with thread_numb:',thread_numb)
=======
    print('Trace for invocation with thread_numb',thread_numb)
>>>>>>> Stashed changes
    if len(errors) != 0:
        print('ERRORS',len(errors))
        pprint(errors)
        print()
    if len(invocations) != 0:
        print(f'values from invoke with {len(invocations)} invocations')
        latency_with_identifier = latency = list(map(lambda x: (x['instance_identifier'],x['execution_start']-x['invocation_start']),invocations))
        print('identifier, latency')
        pprint(latency_with_identifier)
        print()

        invo_start = list(map(lambda x: x['invocation_start'],invocations))
        invo_start.sort()
        first_invocation = invo_start[0]
        invo_start_dist = list(map(lambda x: x-first_invocation,invo_start))
        print('invo_start_distribution')
        pprint(invo_start_dist)
        print()
        execution_start = list(map(lambda x: x['execution_start'],invocations))
        execution_start.sort()
        first_execution = execution_start[0]
        execution_start_dist = list(map(lambda x: x-first_execution,execution_start))
        print('execution_start_dist')
        pprint(execution_start_dist)
        print()

    print('=====================================')
    # return result for as an acumulated dict or None for failure
    return None if invocations == {} else lib.accumulate_dicts(invocations)


# the wrapper ends the experiment if any it can not return a valid value
def err_func(): return benchmarker.end_experiment()

# convinience for not having to repeat values

def validate(x, y, z=None): 
    global threads
    return lib.iterator_wrapper(x, y, experiment_name, threads if z == None else z, err_func)

# creates list of invocation dicts.
# args: tuble(x,y) -> x=length_of_list, y=error_point_string
create_invocation_list = lambda x=(5, 'create invocation_list'): [
    validate(invoke, x[1]) for i in range(x[0]) ]

# parse data that needs to be logged to database.
def append_result(
                invo_id,
                minutes,
                seconds,
                granularity,
                cold,
                final,
                ) -> None:
    global threads, benchmark

    results.append({
        'exp_id': experiment_uuid,
        'invo_id': invo_id,
        'minutes': minutes,
        'seconds': seconds,
        'granularity': granularity,
        'threads': threads,
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
        coldtime = res_dict['execution_start'] - res_dict['invocation_start']
        benchmark = coldtime * 0.80 if not dev_mode else coldtime * 0.90
        avg_warmtime = validate(lib.reduce_dict_by_keys, 
                            'avg_warmtime reset', 
                            (create_invocation_list((10, 'create invocation_list')), 
                            ('execution_start', 'invocation_start')))
        if(avg_warmtime > benchmark):
            check_coldtime(sleep+1200,avg_warmtime)




# Find the values for when coldtimes occure
def set_cold_values():
    global sleep_time, increment, granularity,large_increment,minute_increment
    while(True):
        if time.time() - start_time > _30_hours:
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
    global sleep_time
    # variefy that result is valid by using same sleeptime between invocations 5 times
    iter_count = 5 if not dev_mode else 2
    while(iter_count > 0):
        if time.time() - start_time > _30_hours:
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
                ('experiment_uuid,result_dict[identifier]',experiment_uuid, result_dict['identifier']),
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


    # run one last time and log result as final
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


def run_experiment(thread_numb:int,function:str):
    global threads,fx,sleep_time,increment,granularity,coldtime,benchmark,large_increment,minute_increment
    fx = function
    threads = thread_numb

    print(f'starting experiment with {threads} threads, invoking {fx}')

    # time to sleep in between invocations, start at 5 minutes
    sleep_time = 300
    # increment for each iteration
    increment = sleep_time
    # granularity of result
    granularity = 20
    # flags for controlling granularity of sleep value
    large_increment = True
    minute_increment = True

    print(f"""init values: sleep_time = {sleep_time}, increment = {increment}, granularity = {granularity}, 
            flags = {large_increment} and {minute_increment} | (should be True)""")

    initial_cold_start_response = validate(invoke, 'initial coldtime')
    coldtime = initial_cold_start_response['execution_start'] - initial_cold_start_response['invocation_start']
    if verbose:
        print('init coldtime', coldtime)

    # coldtime is adjusted by 10% to avoid coldtime being an outlier
    benchmark = coldtime * 0.80
    if verbose:
        print('init benchmark', benchmark)

    invo_list = create_invocation_list()

    # calculates avg. time for warm function, default is 5 invocations as input and keys execution_start - invocation_start
    avg_warmtime = validate(lib.reduce_dict_by_keys, 
                            'avg_warmtime',
                            (invo_list, ('execution_start', 'invocation_start')) )
    
                        
    check_coldtime(40*60, avg_warmtime)

    if(verbose):
        lib.dev_mode_print('pre set_cold_values() coldtime exp', [
                            ('sleep_time', sleep_time), 
                            ('increment', increment),
                            ('granularity', granularity),
                            ('benchmark',benchmark),
                            ])

    set_cold_values()

    if(verbose):
        lib.dev_mode_print('post set_cold_values() coldtime exp', [
                            ('sleep_time', sleep_time), 
                            ('increment', increment),
                            ('granularity', granularity),
                            ('benchmark',benchmark),
                            ])
    
    verify_result()
    print(f'ending experiment with {threads} threads at {datetime.now()}')

    
    # =======================
    # Run experiments
    # =======================

try:
    # run_experiment(6,'function1')

    # time.sleep(sleep_time)

    run_experiment(12,'function2')

    # time.sleep(sleep_time)

    # run_experiment(18,'function3')


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
