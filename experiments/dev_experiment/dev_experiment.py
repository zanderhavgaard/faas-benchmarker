#!/bin/python

# this is a example of how to use the benchmarker
# to create different experiments

# imports
from benchmarker import Benchmarker


# describe experiment, should be verbose enough to
# to
description = 'dev-experiment: this experiment tests \
    the implmentation of the benchmarking platform'
# name of cloud function provider for this experiment
provider = 'aws_lambda'

benchmarker = Benchmarker(provider=provider,
                          experiment_desription=description)

# name of function to be invoked
fx_name = 'dev1-python'

# invoke function and recieve a response body as a dict
response = benchmarker.invoke_function(function_name=fx_name)

print(response)


# log the total running time of this experiment
benchmarker.log_experiment_running_time()


#  url = subprocess.getoutput('terraform output invoke_url') + '/dev1'
#  api_key = subprocess.getoutput('terraform output api_key')

#  headers = {
#  'x-api-key': api_key,
#  'Content-Type': 'application/json',
#  }
#  params = {
#  "StatusCode": 200,
#  "sleep": 0.1,
#  "invoke_nested": [
#  {
#  "lambda_name": "dev2-python",
#  "invoke_payload": {
#  "StatusCode": 200,
#  "sleep": 0.2
#  },
#  "invocation_type": "RequestResponse"
#  },
#  {
#  "lambda_name": "dev3-python",
#  "invoke_payload": {
#  "StatusCode": 200,
#  "sleep": 0.3
#  },
#  "invocation_type": "RequestResponse"
#  }
#  ]
#  }

#  #  response = requests.post(url=url, headers=headers)
#  response = requests.post(url=url, data=json.dumps(params), headers=headers)

#  print(response.json())
