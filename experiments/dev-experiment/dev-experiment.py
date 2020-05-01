#!/bin/python

# this is a example of how to use the benchmarker
# to create different experiments

# imports
import sys
import json
from pprint import pprint
from benchmarker import Benchmarker

# name of the terraform experiment
experiment_name = sys.argv[1]

# name of cloud function provider for this experiment
provider = sys.argv[2]

# relative path to experiment.env file
env_file_path = sys.argv[3]

# do not log anything if running in dev mode
#  dev_mode = bool(sys.argv[4]) if len(sys.argv) > 3 else False
#  print('dev_mode', dev_mode)


# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = """
dev-experiment: this experiment tests
the implmentation of the benchmarking platform"""

# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          provider=provider,
                          experiment_description=description,
                          env_file_path=env_file_path)

experiment_name = 'dev-experiment'

# name of function to be invoked
fx_name = f'{experiment_name}1'
sleep_amount = 0.5
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

# invoke function and recieve a response body as a dict

print('invoking with no arguments: ')
# invoke with no arugments
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1')
pprint(response)
print()

print('invoking with no arguments: ')
# invoke with no arugments
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}2')
pprint(response)
print()

print('invoking with sleep argument')
# invoke with a sleep argument
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}3',
                                       sleep=sleep_amount)
pprint(response)
print()

#  print('invoking function2')
#  response = benchmarker.invoke_function(function_endpoint='dev-exp2')
#  print(response)
#  pprint(response)

#  print('invoking function3')
#  response = benchmarker.invoke_function(function_endpoint='dev-exp3')
#  print(response)
#  pprint(response)

print('========================================================================')


print('invoking with nested invocations')
#  invoke with nested invocations
response = benchmarker.invoke_function(function_endpoint=f'{experiment_name}1',
                                       sleep=sleep_amount,
                                       invoke_nested=invoke_nested)
#  print(response)
#  response = response.json()
#  response['body'] = json.loads(response['body'])
pprint(response)
print()


# log the total running time of this experiment
benchmarker.log_experiment_running_time()
