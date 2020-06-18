import sys
import json
from pprint import pprint
from benchmarker import Benchmarker
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

# verbose
verbose = eval(sys.argv[7]) if len(sys.argv) > 7 else False

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
                          dev_mode=dev_mode,
                          verbose=verbose)
# =====================================================================================
# create database interface for logging results
db = SQL_Interface(dev_mode)
# name of table to insert data into - HAVE TO BE SET!!
table = 'Function_lifetime'
# =====================================================================================
# set meta data for experiment
# UUID from experiment

experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3)

fx = 'function1'
# sleep for 15 minutes to ensure coldstart

# =====================================================================================
# meassured time for a function to be cold in a sequantial environment
# default value set to 15 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
# =====================================================================================

# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime) 

# results specific gathered and logged from logic of this experiment
results = []

# sift away errors at runtime and report them later
errors = []
# ======================================================================================
# Convienience methods needed for this experiment

# invoke function and return the result dict
# if thread_numb > 1 it will be done concurrently and the result averaged
def invoke():
    response = lib.get_dict(benchmarker.invoke_function(function_name=fx))
    return response if 'error' not in response else errors.append(response)
    

# the wrapper ends the experiment if any it can not return a valid value
def err_func(): return benchmarker.end_experiment()

# convinience for not having to repeat values


def validate(x, y, z=None): return lib.iterator_wrapper(
    x, y, experiment_name, z, err_func)

# parse data that needs to be logged to database.
# can take whatever needed arguments but has to return/append a dict
def append_result(exp_id:str,
                identifier:str,
                orig_identifier:str,
                hours:int,
                minutes:int,
                seconds:int,
                sleep_time:float,
                reclaimed:bool
                ) -> None:
    # key HAS to have same name as column in database
    results.append({
                'exp_id': exp_id,
                'instance_identifier': identifier,
                'orig_identifier': orig_identifier,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'sleep_time': sleep_time,
                'reclaimed': reclaimed
            })

    if verbose:
        print('inserted in results:')
        pprint(results[len(results)-1])
        print()

# =====================================================================================
# The actual logic if the experiment

try:

    sleep_time = int(coldtime / 2) if not dev_mode else 60 * 15
    start_time = int(time.time())
    _24hours = 24 * 60 * 60 if not dev_mode else 30 * 60
    init_response = validate(invoke,'first invokation') 
    function_id = init_response['instance_identifier']

    last_recorded = int(init_response['execution_start'])

    while( last_recorded < start_time + _24hours ):
        response = validate(invoke,'invokation from loop')
        last_recorded = int(response['execution_start'])
        
        if(response['instance_identifier'] != function_id):
            instance_latest = datetime.fromtimestamp(last_recorded)
            start_time_datetime = datetime.fromtimestamp(start_time)

            instance_lifetime = relativedelta(instance_latest, start_time_datetime)

             # log result as False for the platform not reclaiming the instance resource within 24 hours
            append_result(experiment_uuid,
                        function_id,
                        response['instance_identifier'],
                        instance_lifetime.hours,
                        instance_lifetime.minutes,
                        instance_lifetime.seconds,
                        sleep_time,
                        True)

            # lifetime found, end experiment 
            benchmarker.end_experiment()
            lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
            pprint(results)
            if verbose:
                print('result found')
                print(results[len(results)-1])
                print()
            sys.exit()

        time.sleep(sleep_time)
            
    # log result as True for the platform nor reclaiming the instance resource within 24 hours
    append_result(experiment_uuid,
                function_id,
                response['instance_identifier'],
                24,
                0,
                0,
                sleep_time,
                False)
         
    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================
    lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x, table) for x in results]))
    if dev_mode:
        print('result found')
        print(lib.dict_to_query( results[len(results)-1],table))
        print()

except Exception as e:
    # this will print to logfile
    print('Ending experiment {0} due to fatal runtime error'.format(
        experiment_name))
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()