import sys
import json
import time
from pprint import pprint
from benchmarker import Benchmarker
import function_lib as lib
from mysql_interface import SQL_Interface as database
from datetime import datetime
import traceback
from functools import reduce

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
{experiment_name}: This experiment will test whether there is a pattern to which instance 
of a cloud function that will serve request. This is done by invoking a number of functions
simultaneously, checking that they have different id's, and then invoking one less function
for every iteration down to 1. 
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
# =====================================================================================
# set meta data for experiment
# UUID from experiment

experiment_uuid = benchmarker.experiment.uuid


# meassured time for a function to be cold in a sequantial environment
# default value set to 11 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
coldtime = 11 * 60 if coldtime == None else coldtime
# meassured time for a function to be cold in a concurrent environment
# default value set to 13 minutes if the experiment has not been run
coldtime_threaded = db.get_delay_between_experiment(provider,threaded=True) 
coldtime_threaded = 13 * 60 if coldtime_threaded == None else coldtime_threaded

# throughput time for invocations
throughput_time = 0.2

# what function to test on (1-3)
fx_num = 2
fx = f'{experiment_name}{fx_num}'
# sleep for 15 minutes to ensure coldstart
# if not dev_mode:
#     time.sleep(coldtime)  # more??

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
def invoke(th_numb:int):
    global errors
    err_count = len(errors)
    # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
    invocation_list = list(filter(None, [x if 'error' not in x else errors.append(x) for x in map(lambda x: lib.get_dict(x), 
    benchmarker.invoke_function_conccurrently(function_endpoint=fx, numb_threads=th_numb,throughput_time=throughput_time))]))
    # return error count for this particular invocation and accumulated result
    return (len(errors)-err_count, invocation_list)

def set_init_values(th_numb:int):
    global throughput_time  
    (err,init_responses) = validate(invoke,'initial invocations',th_numb)
    id_list = get_identifiers(init_responses)
    if(len(id_list) == set(id_list) or throughput_time >= 1.0):
        return (err,id_list)
    else:
        throughput_time += 0.1 
        return set_init_values(th_numb)

# get instance identifiers from invocations
def get_identifiers(dicts:list):
    return list(filter(None,map(lambda x: x['instance_identifier'] if isinstance(x['instance_identifier'],str) else None,dicts)))

# the wrapper ends the experiment if any it can not return a valid value
def err_func(): return benchmarker.end_experiment()

# convinience for not having to repeat values
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)

# results being stored in database
def insert_into_db(errors:int, th_numb, vals:list, orig:list) -> None:

    diff_from_orig = [x for x in set(vals) if x not in orig]

    unique_instances = len(set(vals))
    distribution = float(th_numb / unique_instances)
    error_dist = float(th_numb / errors)
    identifiers = reduce(lambda x,y: f'{x+y},',['']+vals)[:-1]

    db.log_clfunction_lifecycle(experiment_uuid,
                                fx,
                                th_numb,
                                throughput_time,
                                errors,
                                unique_instances,
                                distribution,
                                error_dist,
                                len(diff_from_orig),
                                identifiers)   

# =====================================================================================
# The actual logic if the experiment

try:

# runs the logic experiment with a specified number of concurrent requests
    def run_experiment(th_threads):
        global throughput_time
        throughput_time = 0.2

        (err_count,invocations) = set_init_values(th_threads)
        orig = invocations
        if not dev_mode:
            insert_into_db(err_count,orig,[])
        else:
            lib.dev_mode_print(context=f'orig identifiers with {th_threads} threads',
            values=[('throughput_time',throughput_time)]+orig)
        
        for i in range(th_threads):
            local_thread_numb = th_threads - (i + int(th_threads / 10))
            print('local_thread_numb',local_thread_numb)
            for i in range(5):
                time.sleep(10)
                (err,ids) = validate(invoke,f'invoking with {local_thread_numb} threads',local_thread_numb)
                if not dev_mode:
                    insert_into_db(err,local_thread_numb,get_identifiers(ids),orig)
                else:
                    lib.dev_mode_print(context=f'identifiers with {local_thread_numb} threads, iter: {i}',
                    values=[('throughput_time',throughput_time),('errors: ',err)]+get_identifiers(ids))
    

    run_experiment(10)

    if dev_mode:
        benchmarker.end_experiment()
        sys.exit()

    time.sleep(coldtime_threaded)

    run_experiment(20)

    time.sleep(coldtime_threaded)

    run_experiment(40)

        
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
    print(f'Trace: {traceback.format_exc()}')
    print('-----------------------------------------')
    benchmarker.end_experiment()
