import time
import json
import requests
import dotenv
import os
from provider_abstract import AbstractProvider


class OpenFaasProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> None:

        # load aws lambda specific invocation url and credentials
        self.load_env_vars(env_file_path)

        # http headers, contains authentication and data type
        self.headers = {
            'Content-Type': 'application/json'
        }

    # load .env file and parse values
    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)

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

        # TODO change to read from env
        self.gateway_url = 'http://localhost:8080/function'

        # create url of function to invoke
        invoke_url = f'{self.gateway_url}/{function_endpoint}'

        # log start time of invocation
        start_time = time.time()

        # invoke the function
        response = requests.post(
            url=invoke_url,
            headers=self.headers,
            data=json.dumps(params)
        )

        # log the end time of the invocation
        end_time = time.time()

        # TODO remove
        #  print('provider')
        #  print(response)
        #  print(response.content.decode())

        #  import sys
        #  sys.exit()

        # parse response
        response_json = json.loads(response.content.decode())

        #  print('type', type(response_json))

        #  import sys
        #  sys.exit()

        # get the identifier
        identifier = response_json['identifier']

        # parse response body
        response_data = json.loads(response_json['body'])

        # add invocation metadata to response
        response_data[identifier]['invocation_start'] = start_time
        response_data[identifier]['invocation_end'] = end_time
        response_data['root_identifier'] = identifier

        return response_data
