
import sys
import json
import time
from datetime import datetime
import traceback
from benchmarker import Benchmarker
from mysql_interface import SQL_Interface as database
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

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment will test how the provider, {provider}, performes in
a concurrent environment were multiple requests has to be handled simultaneously.
The experiment is done by invoking an increasing number of cloudfunctions in between a
sleeping pause defined by the time-to-coldstart experiment.
"""

# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          experiment_meta_identifier=experiment_meta_identifier,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode)
# =====================================================================================
# create database interface for logging results
db = database(dev_mode)
# name of table to insert data into - HAVE TO BE SET!!
table = 'Cc_bench'
# =====================================================================================
# set meta data for experiment
# UUID from experiment
experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3)
fx_num = 1
fx = f'{experiment_name}{fx_num}'

# =====================================================================================
# meassured time for a function to be cold in a sequantial environment
# default value set to 11 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
coldtime = 11 * 60 if coldtime == None else coldtime
# meassured time for a function to be cold in a concurrent environment
# default value set to 13 minutes if the experiment has not been run
coldtime_threaded = db.get_delay_between_experiment(provider,threaded=True) 
coldtime_threaded = 15 * 60 if coldtime_threaded == None else coldtime_threaded
# =====================================================================================

# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime)  

# results specific gathered and logged from logic of this experiment
results = []

# results specific gathered and logged from logic of this experiment
results = []

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
def invoke(thread_numb:int):
    err_count = len(errors)
    # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
    invocation_list = list(filter(None, [x if 'error' not in x else errors.append(x) for x in map(lambda x: lib.get_dict(x), 
    benchmarker.invoke_function_conccurrently(function_endpoint=fx, numb_threads=thread_numb,throughput_time=0.3))]))
    # add list of transformed dicts together (only numerical values) and divide with number of responses to get average
    accumulated = lib.accumulate_dicts(invocation_list)
    # return error count for this particular invocation and accumulated result
    return (len(errors)-err_count, accumulated) if accumulated != {} else None


# the wrapper ends the experiment if any it can not return a valid value
def err_func(): return benchmarker.end_experiment()

# convinience for not having to repeat values
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)

def append_result(dict:dict, err:int, thread_numb:int) -> None:
    
    results.append({
        'exp_id':experiment_uuid,
        'function_name': fx,
        'numb_threads': thread_numb,
        'sleep_time': coldtime,
        'errors': err,
        'throughput_time': dict['throughput_time'],
        'acc_throughput': 0 if dict['throughput_time'] == 0.0 else dict['throughput'],
        'acc_process_time': dict['process_time'], 
        'cores': dict['cores'],
        'success_rate': 1-errors/thread_numb,
        'acc_execution_start': dict['execution_start'],
        'acc_execution_end': dict['execution_end'],
        'acc_invocation_start': dict['invocation_start'],
        'acc_invocation_end': dict['invocation_end'],
        'acc_execution_total': dict['execution_total'],
        'acc_invocation_total': dict['invocation_total'],
        'acc_latency': dict['execution_start'] - dict['invocation_start'] 
        })

# =====================================================================================
# The actual logic if the experiment
def run_experiment(thread_numb:int,upper_bound:int):
    global coldtime
    while(thread_numb <= upper_bound):
        for i in range(5):
            (err,response) = validate(invoke,f'Invoking with {thread_numb} threads',thread_numb)
            if not dev_mode:
                append_result(response,err,thread_numb)
                thread_numb *= 2
            else:
                lib.dev_mode_print(f'Invocation with {thread_numb} threads and {err} errors', response.items())
                thread_numb += 2
                if(thread_numb > 14):
                    raise Exception('Ending experiment due to dev_mode')
            time.sleep(coldtime)
    
try:

    # run experiment with coldstart time meassured for a sequential environment 
    run_experiment(8,256)

    # set coldtime to meassured time for concurrent environment
    coldtime = coldtime_threaded
    # run experiment with new coldtime
    run_experiment(8,256)
    
    # =====================================================================================
    # end of the experiment, results are logged to database
    benchmarker.end_experiment()
    # =====================================================================================
    # log experiments specific results, hence results not obtainable from the generic Invocation object
    lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x,table) for x in results]))

except Exception as e:
    # this will print to logfile
    print('Ending experiment {0} due to fatal runtime error'.format(
        experiment_name))
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()
    
    