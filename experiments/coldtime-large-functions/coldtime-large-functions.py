
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
{experiment_name}: This experiment investigates whether startup time for a cold function
is affected by the size of the function, in terms of number of lines of code and dependencies.
This is done by first invoking a standard function and then invoking a larger function with
8 times the number of code lines and 3 fairly large dependencies more (Arrow,pandas,numpy)
to check if the latency time varies between the two 
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
# database interface for logging results if needed
db = database(dev_mode)
# name of table to insert data into - HAVE TO BE SET!!
table = None
# =====================================================================================
# set meta data for experiment
# UUID from experiment
experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3), or 'monolith' 
function_endpoint = experiment_name
function = 'function1'

# =====================================================================================
# meassured time for a function to be cold in a sequantial environment
# default value set to 15 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
coldtime = 15 * 60 if coldtime == None else coldtime
# concurrent coldtime
coldtime_concurrent = db.get_delay_between_experiment(provider,threaded=True) 
coldtime_concurrent = 15 * 60 if coldtime_concurrent == None else coldtime_concurrent
# =====================================================================================

# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime)  


# sift away errors at runtime and report them later
errors = []
# ======================================================================================

# ***************************************************
# * comment below function out and other invoke     *
# * function in if experiment is concurrent invoked *
# ***************************************************
def invoke(args:dict= None):
    response = lib.get_dict(
        benchmarker.invoke_function(function_endpoint=function_endpoint, function=function, args=args))
    return response if 'error' not in response else errors.append(response)


# function to be given to validate function if not successful
# if other action is desired give other function as body
def err_func(): benchmarker.end_experiment()

# convinience for not having to repeat values
# x = function to apply, y:str = context, z = arguments for x, if any
def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)


# =====================================================================================

try:
    def run_experiment():
        for i in range(10):
            for x in range(5):
                validate(invoke, f'invoking {function}')
            time.sleep(coldtime)
    
    run_experiment()

    function = 'monolith'

    run_experiment()


   # =====================================================================================
    # end of the experiment, results are logged to database
    benchmarker.end_experiment()
    # =====================================================================================
    # log experiments specific results, hence results not obtainable from the generic Invocation object
    lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                True)

except Exception as e:
    # this will print to logfile
    print(f'Ending experiment {experiment_name} due to fatal runtime error')
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()