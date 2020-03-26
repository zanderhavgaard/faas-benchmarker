#!/bin/python

# this is a example of how to use the benchmarker
# to create different experiments

# imports
import json
from pprint import pprint
from benchmarker import Benchmarker


# describe experiment, should be verbose enough
# to figure out what the experiment does and what it
# attempts to test
description = 'dev-experiment: this experiment tests ' + \
    'the implmentation of the benchmarking platform'
# name of cloud function provider for this experiment
provider = 'aws_lambda'
# relative path experiment.env file
env_file_path = 'experiment.env'

# create the benchmarker
benchmarker = Benchmarker(provider=provider,
                          experiment_description=description,
                          env_file_path=env_file_path)

# name of function to be invoked
fx_name = 'exp1'
sleep_amount = 0.5
invoke_nested = [
    {
        "lambda_name": "exp2-python",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2
        },
        "invocation_type": "RequestResponse"
    },
    {
        "lambda_name": "exp3-python",
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
response = benchmarker.invoke_function(function_name=fx_name)
pprint(response)
print()

print('invoking with sleep argument')
# invoke with a sleep argument
response = benchmarker.invoke_function(function_name=fx_name,
                                       sleep=sleep_amount)
pprint(response)
print()

print('invoking with nested invocations')
# invoke with nested invocations
response = benchmarker.invoke_function(function_name=fx_name,
                                       sleep=sleep_amount,
                                       invoke_nested=invoke_nested)
#  response = response.json()
#  response['body'] = json.loads(response['body'])
pprint(response)
print()


# log the total running time of this experiment
benchmarker.log_experiment_running_time()
