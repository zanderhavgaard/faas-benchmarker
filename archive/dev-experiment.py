import sys
import json
from pprint import pprint
from benchmarker import Benchmarker

# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = sys.argv[1]

# name of cloud function provider for this experiment
provider = sys.argv[2]

# relative path to experiment.env file
env_file_path = sys.argv[3]

# dev_mode
dev_mode = eval(sys.argv[4]) if len(sys.argv) > 4 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: this experiment tests the implmentation of the benchmarking platform
"""

# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          provider=provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode)
# =====================================================================================


# name of function to be invoked
fx_name = f'{experiment_name}1'
sleep_amount = 0.5

print('invoking with no arguments: ')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1')
pprint(response)
print()

print('invoking with no arguments: ')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}2')
pprint(response)
print()

print('invoking with sleep argument')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}3',
                                       sleep=sleep_amount)
pprint(response)
print()

invoke_nested = [
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2,
            "invoke_nested": [
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2
                    }
                },
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2
                    }
                }
            ]
        }
    }
]

print('invoking with nested invocations')
#  invoke with nested invocations
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1',
                                       sleep=sleep_amount,
                                       invoke_nested=invoke_nested)
pprint(response)
print()


# =====================================================================================
# end of the experiment
benchmarker.end_experiment()
# =====================================================================================
