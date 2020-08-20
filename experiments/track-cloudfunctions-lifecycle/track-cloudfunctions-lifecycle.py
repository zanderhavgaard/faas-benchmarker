
import sys
import json
import time
from datetime import datetime
import traceback
from benchmarker import Benchmarker
from mysql_interface import SQL_Interface as database
import function_lib as lib
from functools import reduce
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

# verbode mose
verbose = eval(sys.argv[7]) if len(sys.argv) > 7 else False


# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment will test whether there is a pattern to which instance 
of a cloud function that will serve request. This is done by invoking a number of functions
simultaneously, checking that they have different ids, and then invoking one less function
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
                          dev_mode=dev_mode,
                          verbose=verbose)
# =====================================================================================
# create database interface for logging results
db = database(dev_mode)
# name of table to insert data into - HAVE TO BE SET!!
table = 'Function_lifecycle' 
# =====================================================================================
# set meta data for experiment
# UUID from experiment
experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3)
fx = 'function2'

# meassured time for a function to be cold in a sequantial environment
# default value set to 15 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 

# meassured time for a function to be cold in a concurrent environment
# default value set to 13 minutes if the experiment has not been run
coldtime_threaded = db.get_delay_between_experiment(provider,threaded=True) 
coldtime_threaded = coldtime if coldtime_threaded == None else coldtime_threaded

# throughput time for invocations
throughput_time = 0.2


# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime)  # more??

# results specific gathered and logged from logic of this experiment
results = []
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
    benchmarker.invoke_function_conccurrently(function_name=fx, 
                                            numb_threads=th_numb,
                                            function_args={'throughput_time':throughput_time}))]))
    # return error count for this particular invocation and accumulated result
    return (len(errors)-err_count, invocation_list)


# the wrapper ends the experiment if any it can not return a valid value
def err_func(): benchmarker.end_experiment()

# convinience for not having to repeat values
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)

# get instance identifiers from invocations
def get_identifiers(dicts:list):
    return list(filter(None, map(lambda x: x['instance_identifier'] if isinstance(x['instance_identifier'],str) else None,dicts)))
  

def set_init_values(th_numb:int):
    global throughput_time  
    (err,init_responses) = validate(invoke,'initial invocations',th_numb)
    id_list = get_identifiers(init_responses)
    if(len(id_list) == set(id_list) or throughput_time >= 1.0):
        return (err,id_list)
    else:
        throughput_time += 0.1 
        return set_init_values(th_numb)

# parse data that needs to be logged to database.
# can take whatever needed arguments but has to return/append a dict
def append_result(errors:int, start_thread_numb:int, th_numb:int, vals:list, orig:list) -> None:
    repeats_from_orig = [x for x in set(vals) if x in orig]
    diff_from_orig = len([x for x in set(vals) if x not in orig])
    unique_instances = len(set(vals))
    distribution = float(th_numb / unique_instances)
    error_dist = float(errors / th_numb)
    identifiers = reduce(lambda x,y: f'{x+y},',['']+sorted(vals))[:-1]
    repeats_from_orig_string = reduce(lambda x,y: f'{x+y},',['']+sorted(repeats_from_orig))[:-1]

    results.append({
        'exp_id': experiment_uuid,
        'function_name': fx,
        'numb_invokations': th_numb,
        'numb_invocations_orig': start_thread_numb,
        'throughput_time': throughput_time,
        'errors': errors,
        'unique_instances': unique_instances,
        'distribution': distribution,
        'error_dist': error_dist,
        'diff_from_orig': diff_from_orig,
        'identifiers': identifiers,
        'repeats_from_orig': repeats_from_orig_string
        })

# =====================================================================================
# The actual logic if the experiment


# runs the logic experiment with a specified number of concurrent requests
def run_experiment(th_threads):
    global throughput_time
    throughput_time = 0.2

    (err_count,invocations) = set_init_values(th_threads)
    orig = invocations
    append_result(err_count,th_threads, th_threads, orig, [])

    if verbose:
        lib.dev_mode_print(context=f'orig identifiers with {th_threads} threads',
        values=[('throughput_time',throughput_time)]+orig)
    
    for i in range(10):
        local_thread_numb = th_threads - (i * int(th_threads / 10))
        
        for i in range(5):
            time.sleep(30)
            (err,ids) = validate(invoke,f'invoking with {local_thread_numb} threads',local_thread_numb)
            append_result(err, th_threads, local_thread_numb, get_identifiers(ids), orig)
            
            if verbose:
                lib.dev_mode_print(context=f'identifiers with {local_thread_numb} threads, iter: {i}',
                values=[('throughput_time',throughput_time),('errors: ',err)]+get_identifiers(ids))
    
try:
    run_experiment(10)

    if dev_mode:
        benchmarker.end_experiment()
        lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
        if benchmarker.print_all_data:
            lib.dev_mode_print(
                f'Experiment {experiment_name} with UUID: {experiment_uuid} ended due to dev_mode. {len(errors)} errors occured.', 
                ['Queries for experiment:']+[lib.dict_to_query(x, table) for x in results])
        sys.exit()


    time.sleep(coldtime_threaded)

    run_experiment(20)

    time.sleep(coldtime_threaded)

    run_experiment(40)

    time.sleep(coldtime_threaded)

    run_experiment(80)

   
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
    print('Ending experiment {0} due to fatal runtime error'.format(
        experiment_name))
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print(f'Trace: {traceback.format_exc()}')
    print('-----------------------------------------')
    benchmarker.end_experiment()
