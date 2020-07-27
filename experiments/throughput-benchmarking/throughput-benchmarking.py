
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

# verbose
verbose = eval(sys.argv[7]) if len(sys.argv) > 7 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment benchmarks the computational throughput of each platform.
First functions are invoked with increasing values for the 'throughput' argument,
which will do as many computations as possible in the time alloted. These invocations
are then repeated with concurrency. 
Followed by invocations of the monolith function using it's matrix multiplication function
to check how long the function spends on computing the multiplication of increasingly
larger matrices. These invocations are then repeated concurrently. 
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
db = database(dev_mode)
# name of table to insert data into - HAVE TO BE SET!!
table = None
# =====================================================================================
# set meta data for experiment
# UUID from experiment
experiment_uuid = benchmarker.experiment.uuid

function = 'function1'


# =====================================================================================
# meassured time for a function to be cold in a sequantial environment
# default value set to 15 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
coldtime = 15 * 60 if coldtime == None else coldtime
# threaded coldtime
coldtime = db.get_delay_between_experiment(provider,threaded=True) 
coldtime = 15 * 60 if coldtime == None else coldtime

# =====================================================================================

# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime)  

# results specific gathered and logged from logic of this experiment
results = []

# sift away errors at runtime and report them later
errors = []
# ======================================================================================

# ***************************************************
# * comment below function out and other invoke     *
# * function in if experiment is concurrent invoked *
# ***************************************************
def invoke(args:dict= None):
    response = lib.get_dict(
        benchmarker.invoke_function(function_name=function, function_args=args))
    return response if 'error' not in response else errors.append(response)

def invoke_concurrently( args:tuple ):

    err_count = len(errors)
    # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
    invocations = list(filter(None, [x if 'error' not in x else errors.append(x) for x in map(lambda x: lib.get_dict(x), 
    benchmarker.invoke_function_conccurrently(function_name=function, function_args=args[0], numb_threads=args[1]))]))
    # add list of transformed dicts together (only numerical values) and divide with number of responses to get average
   
    # invocations = lib.accumulate_dicts(invocations)
    # return error count and result for this particular invocation 
    return None if invocations == {} or invocations == [] else (len(errors)-err_count, invocations)

# function to be given to validate function if not successful
# if other action is desired give other function as body
def err_func(): benchmarker.end_experiment()

# convinience for not having to repeat values
# x = function to apply, y:str = context, z = arguments for x, if any
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)



# =====================================================================================

try:

    throughput_times = [0.1,0.2,0.4,0.8,1.2,1.6,2.4,5,10,20]
    for t in throughput_times:
        for i in range(5):
            if verbose:
                print(f'invoking sequantially with {t} throughput_time')
            validate(invoke,f'invoking sequantially with {t} throughput_time', {'throughput_time':t})
    
    for t in throughput_times[:-2]:
        for i in range(5):
            if verbose:
                print(f'invoking concurrently with {t} throughput_time')
            validate(invoke_concurrently, f'invoking concurrently with {t} throughput_time', ({'throughput_time':t}, 12))
    
    # change endpoint to monolith function and invoke throughput in terms of matrix multiplication

    matrix_size = [100,120,140,180,200,220]
    function = 'monolith'
    for n in matrix_size:
        for i in range(5):
            if verbose:
                print(f'invoking monolith with args {n}')
            validate(invoke, 
                    f'invoking monolith with args {n}', 
                    {
                    'seed':i,
                    'run_function': 'matrix_mult',
                    'args': n
                    })
    
    for n in matrix_size[:-3]:
        for i in range(3):
            if verbose:
                print(f'invoking monolith concurrently with args {n}')
            validate(invoke_concurrently, 
                    f'invoking monolith with args {n}', 
                    ({
                    'seed':i,
                    'run_function': 'matrix_mult',
                    'args': n
                    }, 12))


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
