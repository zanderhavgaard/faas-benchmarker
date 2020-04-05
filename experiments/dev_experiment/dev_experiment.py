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

# describe experiment, should be verbose enough to figure 
# out what the experiment does and what it attempts to test
description = 'dev-experiment: this experiment tests ' + \
    'the implmentation of the benchmarking platform'

# name of cloud function provider for this experiment
provider = sys.argv[2]

#  provider = 'aws_lambda'
#  provider = 'azure_functions'
# relative path experiment.env file
# TODO make argument
#  env_file_path = 'dev-exp.env'
env_file_path = sys.argv[3]

# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          provider=provider,
                          experiment_description=description,
                          env_file_path=env_file_path)

# name of function to be invoked
fx_name = f'{experiment_name}1'
sleep_amount = 0.5
invoke_nested = [
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2
        },
        "invocation_type": "RequestResponse"
    },
    {
        "function_name": f"{experiment_name}3",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.3
        },
        "invocation_type": "RequestResponse"
    }
]

# invoke function and recieve a response body as a dict

print('invoking with no arguments: ')
# invoke with no arugments
response = benchmarker.invoke_function(function_endpoint=fx_name)
pprint(response)
print()

print('invoking with sleep argument')
# invoke with a sleep argument
response = benchmarker.invoke_function(function_endpoint=fx_name,
                                       sleep=sleep_amount)
pprint(response)
print()

#  print('invoking with nested invocations')
#  # invoke with nested invocations
#  response = benchmarker.invoke_function(function_endpoint=fx_name,
                                       #  sleep=sleep_amount,
                                       #  invoke_nested=invoke_nested)
#  #  response = response.json()
#  #  response['body'] = json.loads(response['body'])
#  pprint(response)
#  print()


# log the total running time of this experiment
benchmarker.log_experiment_running_time()
