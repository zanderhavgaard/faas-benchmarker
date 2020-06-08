
import sys
import json
import time
from datetime import datetime
import traceback
from benchmarker import Benchmarker
from mysql_interface import SQL_Interface as database
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
{experiment_name}: This experiment tests the relationship
between cloud functions that invoke each other.
The experiment is conducted by first invoking function 1 and function 2 such that
they are hot. Then we invoke function 1, with a nested invocation dict, such that
function1 will invoke function2 which will invoke function 3. We then expect that
of the total time of the nested invocation that function3 will account for the majority
of the response time, as should be the only cold start. We then wait for all of the functions
to become cold and repeat the invocations a number of times.
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

# setup convenient function names
fx1 = 'function1'
fx2 = 'function2'
fx3 = 'function3'
fx4 = 'monolith'

# =====================================================================================
# meassured time for a function to be cold in a sequantial environment
# default value set to 15 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=False) 
coldtime = 15 * 60 if coldtime == None else coldtime
# =====================================================================================

def create_nesting(functions:list):
    nested = {
        "function_name": functions[0],
            "invoke_payload": {
            "StatusCode": 200,
            }
        }
    if(len(functions)-1 != 0):
        nested["invoke_nested"] = [create_nesting(functions[1:])]
    return nested

def run_experiment(iterations:int, invoke_order:list, hot_instances:int):
    for i in range(iterations):

        if verbose:
            print(f'Experiment {experiment_name}, iteration {i} ...')

        for n in range(hot_instances):
        # invoke function 1 and 2 such that they are hot
            hot_response = benchmarker.invoke_function(function_name=invoke_order[0])
        
            if verbose:
                print('Response from prewarming function {invoke_order[n]} at level {n}')
                pprint(hot_response)
            

        # setup nested invocations
        nested = [
            {
                "function_name": fx2,
                "invoke_payload": {
                    "StatusCode": 200,
                    "invoke_nested": [
                        {
                            "function_name": fx3,
                            "invoke_payload": {
                                "StatusCode": 200,
                                "invoke_nested": [
                                    {
                                        'function_name':
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]

        # invoke function 1, that will invoke function 2, which will invoke funcion 3
        # we expect that only function3 will be a cold start, and thus the majority of the response time
        nested = benchmarker.invoke_function(function_name=fx1, function_args=nested)

        time.sleep(coldtime)
try:

    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================

except Exception as e:
    # this will print to logfile
    print(f'Ending experiment {experiment_name} due to fatal runtime error')
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()