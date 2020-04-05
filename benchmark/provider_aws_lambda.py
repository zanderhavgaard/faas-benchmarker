#!/bin/python

import requests
import json
import time
import os
import dotenv
from provider_abstract import AbstractProvider


class AWSLambdaProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> None:

        # load aws lambda specific invocation url and credentials
        self.load_env_vars(env_file_path)

        # http headers, contains authentication and data type
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    # load .env file and parse values
    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)
        self.api_key = os.getenv('api_key')
        self.gateway_url = os.getenv('invoke_url')

    # in the case of AWS Lambda the name actually references
    # the api endpoint where the funcion is attached:
    #   --> eg: https://..../prod/<name>
    def invoke_function(self,
                        function_endpoint: str,
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

        # create url of function to invoke
        invoke_url = f'{self.gateway_url}/{function_endpoint}'

        # invoke the function
        response = requests.post(
            url=invoke_url,
            headers=self.headers,
            data=json.dumps(params)
        )

        # log the end time of the invocation
        end_time = time.time()

        # parse response json
        response_data = response.json()

        # parse reponse body json
        #  response_data['body'] = json.loads(response_data['body'])
        # TODO make more concise
        response_data = json.loads(response_data['body'])

        # get the identifer
        identifier = response_data['identifier']

        response_data[identifier]['invocation_start'] = start_time
        response_data[identifier]['invocation_end'] = end_time

        # add start / end times to body
        #  response_data['body'][identifier]['invocation_start'] = start_time
        #  response_data['body'][identifier]['invocation_end'] = end_time

        response_data['root_identifier'] = identifier

        return response_data
