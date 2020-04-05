#!/bin/python

import requests
import json
import time
import os
import dotenv
from provider_abstract import AbstractProvider


class AzureFunctionsProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> None:

        # load azurw functions specific invocation url and credentials
        self.load_env_vars(env_file_path)

        # http headers, contains data type
        self.headers = {
            'Content-Type': 'application/json'
        }


    # load .env file and parse values
    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)
        #  self.function_app_url = os.getenv('function_app_url)')
        #  self.function_key = os.getenv('function_key')

    # for azure functions the function_endpoint refers to the function name
    # the functions are available under
    # https://<funtion_app_name>/api/<function_name>?code=<function_key>
    def invoke_function(self,
                        function_endpoint: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:

        function_app_url = os.getenv(f'{function_endpoint}_function_app_url')
        function_key = os.getenv(f'{function_endpoint}_function_key')

        print('url', function_app_url)
        print('key', function_key)

        if function_app_url is None or function_key is None:
            raise RuntimeError('Could not parse function app url or key.')

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
        invoke_url = f'https://{function_app_url}/api/{function_endpoint}?code={function_key}'

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

        # get the identifer
        identifier = response_data['identifier']

        # add start / end times to body
        response_data[identifier]['invocation_start'] = start_time
        response_data[identifier]['invocation_end'] = end_time
        response_data['root_identifier'] = identifier

        return response_data
