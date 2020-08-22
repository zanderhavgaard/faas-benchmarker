
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
10 times to create a baseline for a hot invocation so that it can be determined that the
first was a coldstart.
Then the function is invoked continually with increasing delay between invocations,
until the function_identifier changes and the time elapsed between last function call is logged 
This process is then repeated to verify the result.
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


# time to sleep in between invocations, start at 5 minutes
sleep_time = 300
# increment for each iteration
increment = sleep_time
# granularity of result
granularity = 10
# value for last response latency
cold_identifier = None
# flags for controlling granularity of sleep value
large_increment = True
minute_increment = True
benchmark = 0.0

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
        'benchmark': 0.0,
        'cold': cold,
        'final': final
        })

# =====================================================================================
# The actual logic if the experiment

# function to be given to validate function if not successful
# if other action is desired give other function as body
def err_func(): benchmarker.end_experiment()

# convinience for not having to repeat values
# x = function to apply, y:str = context, z = arguments for x, if any
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)



# =====================================================================================

try:

    def find_cold_instance(sleep):
        from functools import reduce

        print(f'finding_cold_instance with {sleep} sleeptime')

        iterations = 50
        response_times = []

        time.sleep(sleep)

        # should be a cold invocation
        first_res = validate(invoke,'first invocation from find_cold_instance')
        cold_latency = first_res['execution_start'] - first_res['invocation_start']

        if verbose:
            print('first cold invocation:')
            pprint(first_res)
            print()

        if verbose:
            print(f'invoking function {iterations} times to find an average latency')

        for i in range(iterations):
            t1 = time.time()
            res =  validate(invoke,'invocation from warmtime baseline')
            t2 = time.time()
            response_times.append(
                (i, res['execution_start']-res['invocation_start'], t2-t1)
            )

        response_times.sort(key=lambda x: x[1])

        sliced = response_times[10:40]

        sliced_avg = reduce(lambda x,y: x+y[1],[0.0] + sliced)/len(sliced)

        if cold_latency > sliced_avg * 2:
            return (first_res['instance_identifier'])

        elif sleep >= 7200:
            print('Aborting after trying to find cold instance for 2 hours')

            benchmarker.end_experiment()
            # log experiments specific results, hence results not obtainable from the generic Invocation object
            lib.log_experiment_specifics(experiment_name,
                                    experiment_uuid, 
                                    len(errors), 
                                    db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
            sys.exit()

        else:
            return find_cold_instance(sleep+1200)


    def set_cold_values():
        global sleep_time, increment, granularity, cold_identifier, large_increment, minute_increment
        # global sleep_time, increment, granularity, latest_latency_time, large_increment, minute_increment
        while(True):
            if time.time() - start_time > _timeout:
                print('ABORTING due to 24 hour time constraint from set_cold_values function\n')
                benchmarker.end_experiment()
                # log experiments specific results, hence results not obtainable from the generic Invocation object
                lib.log_experiment_specifics(experiment_name,
                                        experiment_uuid, 
                                        len(errors), 
                                        db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
                sys.exit()

            time.sleep(sleep_time)
            result_dict = validate(invoke,f'invoking function: {fx} from cold start experiment')
            local_identifier = result_dict['instance_identifier'] 

            if(verbose):
                lib.dev_mode_print('logging time from set_cold_values', [
                    ('experiment_uuid,result_dict[\'instance_identifier\']',experiment_uuid, result_dict['instance_identifier']),
                    ('sleep_time / 60', int(sleep_time / 60)),
                    ('sleep_time % 60', int( sleep_time % 60)),
                    ('increment', increment),
                    ('cold_identifier', cold_identifier),
                    ('Final result', False),
                    ('cold instance found',local_identifier != cold_identifier)
                    ])
            if(local_identifier == cold_identifier):
                sleep_time += increment 
            elif large_increment:   
                sleep_time -= increment
                large_increment = False
                increment = 60
                sleep_time += increment 
                cold_identifier = local_identifier
            elif minute_increment:
                sleep_time -= increment
                minute_increment = False
                increment = granularity
                sleep_time += increment 
                cold_identifier = local_identifier
            else:
                append_result(
                            result_dict['identifier'],
                            int(sleep_time / 60),
                            int(sleep_time % 60),
                            increment,
                            local_identifier != cold_identifier,
                            False)
        
                return

    def verify_result():
        global sleep_time, granularity, cold_identifier
        # variefy that result is valid by using same sleeptime between invocations 5 times
        iter_count = 5 if not dev_mode else 2
        while(iter_count > 0):
            if time.time() - start_time > _timeout:
                print('ABORTING due to 24 hour time constraint from varification loop\n')
                benchmarker.end_experiment()
                # log experiments specific results, hence results not obtainable from the generic Invocation object
                lib.log_experiment_specifics(experiment_name,
                                        experiment_uuid, 
                                        len(errors), 
                                        db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
                sys.exit()
                
            time.sleep(sleep_time)
            result_dict = validate(invoke, f'invoking function: {fx} from validation of cold start experiment')
            local_identifier = result_dict['instance_identifier']

            if(verbose):
                lib.dev_mode_print(f'logging cold time: {local_identifier != cold_identifier} -> coldtime exp', [
                    ('experiment_uuid,result_dict[instance_identifier]',experiment_uuid, result_dict['instance_identifier']),
                    ('sleep_time / 60', int(sleep_time / 60)),
                    ('sleep_time % 60', int(sleep_time % 60)),
                    ('increment', increment),
                    ('cold identifier', cold_identifier),
                    ('Final result', False),
                     ('cold instance found',local_identifier != cold_identifier)
                    ])
            
            append_result(
                        result_dict['identifier'],
                        int(sleep_time / 60),
                        int(sleep_time % 60),
                        increment,
                        local_identifier != cold_identifier,
                        False)


            if(local_identifier == cold_identifier):
                sleep_time += granularity
                iter_count = 5 if not dev_mode else 2
            else:
                iter_count -= 1
                cold_identifier = local_identifier
        
        # run one last time and log result as final or 
        time.sleep(sleep_time)

        result_dict = validate(invoke, f'invoking function: {fx} from final invocation of cold start experiment')
        identifier = result_dict['instance_identifier']
        if identifier == cold_identifier:
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
            cold_identifier = identifier
            verify_result()       

    #  RUN THE EXPERIMENT LOGIC

    cold_identifier = find_cold_instance(0.0)

    set_cold_values()

    verify_result()

   # =====================================================================================
    # end of the experiment, results are logged to database
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
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()
