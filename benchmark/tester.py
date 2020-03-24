#!/bin/python

import requests
import json
import time
import subprocess

url = subprocess.getoutput('terraform output invoke_url') + '/dev1'
api_key = subprocess.getoutput('terraform output api_key')

headers = {
    'x-api-key': api_key,
    'Content-Type': 'application/json',
}
params = {
    "StatusCode": 200,
    "sleep": 0.1,
    "invoke_nested": [
        {
            "lambda_name": "dev2-python",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.2
            },
            "invocation_type": "RequestResponse"
        },
        {
            "lambda_name": "dev3-python",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.3
            },
            "invocation_type": "RequestResponse"
        }
    ]
}

print(url)
print(params)

#  response = requests.post(url=url, headers=headers)
response = requests.post(url=url, data=json.dumps(params), headers=headers)

print(response.json())
