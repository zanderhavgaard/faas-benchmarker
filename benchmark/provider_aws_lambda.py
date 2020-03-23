#!/bin/python

import requests
import json
import time
from abstract_provider import AbstractProvider


class AWSLambdaProivder(AbstractProvider):

    def __init__(self):

        # aws lambda specific invocation url and credentials
        self.api_key = ""
        self.url = ""

        # http headers, contains authentication and data type
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def invoke_function(self,
                        name: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:

        # paramters, the only required paramter is the statuscode
        params = {
            "StatusCode": 200
        }

        # add optional sleep parameter if present
        if sleep != 0.0:
            params['sleep'] = sleep

        # add optional dict describing nested invocations, if presente
        if invoke_nested != None:
            params['invoke_nested'] = invoke_nested

        # log start time of invocation
        start_time = time.time()

        # invoke the function
        response = requests.post(
            url=self.url,
            headers=self.headers,
            data=json.dumps(params)
        )

        # log the end time of the invocation
        end_time = time.time()

        response_data = response.json()

        return response
