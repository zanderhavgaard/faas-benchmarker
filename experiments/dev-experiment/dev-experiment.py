import sys
import json
import time
from pprint import pprint
from benchmarker import Benchmarker

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
{experiment_name}: this experiment tests the implmentation of the benchmarking platform
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


# name of function to be invoked
fx_name = f'{experiment_name}1'
sleep_amount = 0.5

print('invoking with no arguments: ')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1')
pprint(response)
print()

print('invoking with sleep argument')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}2',
                                       sleep=sleep_amount)
pprint(response)
print()

print('invoking with 1 second throughput argument: ')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}3',
                                       throughput_time=1.0)
pprint(response)
print()

print('invoking with 2 second throughput argument: ')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}3',
                                       throughput_time=2.0)
pprint(response)
print()

invoke_1_nested = [
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.1
        }
    }
]

print('invoking with 1 nested invocation')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1',
                                       invoke_nested=invoke_1_nested)
pprint(response)
print()

invoke_1_nested = [
    {
        "function_name": f"{experiment_name}3",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.1
        }
    }
]

print('invoking with 1 nested invocation')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}2',
                                       invoke_nested=invoke_1_nested)
pprint(response)
print()

invoke_1_nested = [
    {
        "function_name": f"{experiment_name}1",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.1
        }
    }
]

print('invoking with 1 nested invocation')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}3',
                                       invoke_nested=invoke_1_nested)
pprint(response)
print()

invoke_nested = [
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "invoke_nested": [
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                    }
                },
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                    }
                }
            ]
        }
    }
]

print('invoking with nested invocations')
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1',
                                       invoke_nested=invoke_nested)
pprint(response)
print()


# =====================================================================================
# end of the experiment
benchmarker.end_experiment()
# =====================================================================================
