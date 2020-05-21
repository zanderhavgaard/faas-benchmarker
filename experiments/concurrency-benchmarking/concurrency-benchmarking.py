import sys
import json
import time
from pprint import pprint
from benchmarker import Benchmarker
from datetime import datetime
from mysql_interface import SQL_Interface as database
import function_lib as lib
import traceback 



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
{experiment_name}: This 
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
db = database()
# =====================================================================================
# set meta data for experiment
# UUID from experiment

experiment_uuid = benchmarker.experiment.uuid

# number of thread to run
thread_numb = 8

# meassured time for a function to be cold in a sequantial environment
# default value set to 11 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
coldtime = 11 * 60 if coldtime == None else coldtime
# meassured time for a function to be cold in a concurrent environment
# default value set to 13 minutes if the experiment has not been run
coldtime_threaded = db.get_delay_between_experiment(provider,threaded=True) 
coldtime_threaded = 13 * 60 if coldtime_threaded == None else coldtime_threaded

# what function to test on (1-3)
fx_num = 2
fx = f'{experiment_name}{fx_num}'
# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime)  # more??

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
def invoke():
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

def insert_into_db(dict:dict,errors) -> None:
    throughput_time = dict['throughput_time']
    throughput = 0 if throughput_time == 0.0 else dict['throughput']
    p_time = dict['process_time']
    cores = dict['cores']
    success_rate = 1-errors/thread_numb
    acc_exe_st = dict['execution_start']
    acc_exe_end = dict['execution_end']
    acc_invo_st = dict['invocation_start']
    acc_invo_end = dict['invocation_end']
    acc_exe_total = dict['execution_total']
    acc_invo_total = dict['invocation_total']
    acc_latency = acc_exe_st - acc_invo_st

    db.log_concurrent_result(experiment_uuid,
                            fx,
                            thread_numb,
                            coldtime,
                            errors,
                            throughput_time,
                            throughput,
                            p_time,
                            cores,
                            success_rate,
                            acc_exe_st,
                            acc_exe_end,
                            acc_invo_st,
                            acc_invo_end,
                            acc_exe_total,
                            acc_invo_total,
                            acc_latency)

# =====================================================================================
# The actual logic if the experiment

try:

    while(thread_numb < 260):
        for i in range(5):
            (errors,response) = validate(invoke,f'Invoking with {thread_numb} threads')
            insert_into_db(response,errors)
            time.sleep(coldtime)
        if not dev_mode:
            thread_numb *= 2
        else: 
            thread_numb += 2
            if(thread_numb > 14):
                benchmarker.end_experiment()
    
    # reset threadnumb to run again with coldtime_threaded
    thread_numb = 8
    coldtime = coldtime_threaded
    
    while(thread_numb <= 256):
        for i in range(5):
            (errors,response) = validate(invoke,f'Invoking with {thread_numb} threads')
            insert_into_db(response,errors)
            time.sleep(coldtime)
        if not dev_mode:
            thread_numb *= 2
        else: 
            thread_numb += 2
            if(thread_numb > 14):
                benchmarker.end_experiment()
    
    # print to logfile
    print(f'{experiment_name} with UUID: {experiment_uuid} using function{fx_num} ended wtih {len(errors)} errors')
        
    
         
    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================

except Exception as e:
    # this will print to logfile
    print('Ending experiment {0} due to fatal runtime error'.format(
        experiment_name))
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()