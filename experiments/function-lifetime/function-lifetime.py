import sys
import json
from pprint import pprint
from benchmarker import Benchmarker
import time
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

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: Finds whether or not the is a limit for how long a FaaS function
instance is being kept alive. A cut-off of 24 hours is used for when a platform is
determined to let functions run without ever reclaiming the resources, resulting in a
cold start. The experiment is conducted by invoking a function at a interval 2 min.
lower than the cold start cut of found in the single-function-time-to-cold-start 
experiment and its instance identifier is checked to be the same every time.     
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
db = SQL_Interface()
# =====================================================================================
# set meta data for experiment
# UUID from experiment

experiment_uuid = benchmarker.experiment.uuid


# what function to test on (1-3)
fx_num = 2
fx = f'{experiment_name}{fx_num}'
# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(15*60)  # more??

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
# if thread_numb > 1 it will be done concurrently and the result averaged
def invoke():
    response = lib.get_dict(benchmarker.invoke_function(function_endpoint=fx))
    return response if 'error' not in response else errors.append(response)
    


# the wrapper ends the experiment if any it can not return a valid value
def err_func(): return benchmarker.end_experiment()

# convinience for not having to repeat values


def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)

# =====================================================================================
# The actual logic if the experiment

try:

    coldstart_time = db.get_explicit_number_coldstart(args='minutes',provider=provider,flag=False)
    sleep_time = int(coldstart_time[0][0] / 2)
    start_time = int(time.time())
    _24hours = 24 * 60 * 60
    init_response = validate(invoke,'first invokation') 
    function_id = init_response['instance_identifier']

    last_recorded = int(init_response['execution_start'])

    while( last_recorded < start_time + _24hours ):
        response = validate(invoke,'invokation from loop')
        if(response['instance_identifier'] != function_id):
            instance_latest = datetime.fromtimestamp(last_recorded)
            start_time_datetiem = datetime.fromtimestamp(start_time)
            instance_lifetime = instance_latest - start_time_datetiem
            conv_time = (datetime.min + instance_lifetime).time()
             # log result as False for the platform not reclaiming the instance resource within 24 hours
            db.log_liftime(experiment_uuid,
                            function_id,
                            conv_time.hours,
                            conv_time.minute,
                            conv_time.second,
                            sleep_time,
                            False)
            benchmarker.end_experiment()
            sys.exit()

        else:
            last_recorded = int(response['execution_start'])
            time.sleep(sleep_time)
            
    # log result as True for the platform nor reclaiming the instance resource within 24 hours
    db.log_liftime(experiment_uuid,
                    function_id,
                    24,
                    0,
                    0,
                    sleep_time,
                    True)
         
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