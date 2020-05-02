#!/bin/python

import requests
import json
import time
import os
import dotenv
from provider_abstract import AbstractProvider

from pprint import pprint


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
                        invoke_nested: list = None) -> dict:

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
            check_for_nested_invocation_deadlocks(
                nested_invocations=invoke_nested,
                illegal_fx_names=[function_endpoint]
            )
            params['invoke_nested'] = add_function_code_for_nested_invocations(
                nested_invocations=invoke_nested
            )

        # log start time of invocation
        start_time = time.time()

        # create url of function to invoke
        invoke_url = f'https://{function_app_url}/api/{function_endpoint}?code={function_key}'

        try:

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

            # TODO make same change with if else for AWS and azure
            # if succesfull invocation parse response
            if(response.status_code == 200):

                response_json = json.loads(response.content.decode())

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

            else:
                error_dict = {
                    'StatusCode-error-providor_openfaas'+function_endpoint+'-'+str(response.status_code): {
                        'identifier': 'StatusCode-error-providor_openfaas'+function_endpoint+'-'+str(response.status_code),
                        'uuid': None,
                        'error':{'message':'None 200 code','responsecode':response.status_code},
                        'sleep': sleep,
                        'python_version': None,
                        "level": 0,
                        "memory": None,
                        "instance_identifier": None,
                        "execution_start": None,
                        "execution_end": None,
                        'invocation_start': start_time,
                        'invocation_end': end_time,
                    },
                    'root_identifier':'StatusCode-error-providor_openfaas'+function_endpoint+'-'+str(response.status_code)
                }
                return error_dict               

        except Exception as e:
            error_dict = {
                    'exception-providor_openfaas-'+function_endpoint: {
                        'identifier': 'exception-providor_openfaas'+function_endpoint,
                        'uuid': None,
                        "error": {"message": str(e), "type": str(type(e))},
                        'sleep': sleep,
                        'python_version': None,
                        "level": 0,
                        "memory": None,
                        "instance_identifier": None,
                        "execution_start": None,
                        "execution_end": None,
                        'invocation_start': start_time,
                        'invocation_end': time.time(),
                    },
                    'root_identifier':'exception-providor_openfaas'+function_endpoint
                }
            return error_dict

# recursively add function codes to invoke nested dict


def add_function_code_for_nested_invocations(nested_invocations: list) -> list:
    for ni in nested_invocations:
        fx = ni['function_name']
        ni["code"] = os.getenv(f'{fx}_function_key')
        if 'invoke_nested' in ni['invoke_payload']:
            ni['invoke_payload']["invoke_nested"] = add_function_code_for_nested_invocations(
                nested_invocations=ni['invoke_payload']['invoke_nested'],
            )
    return nested_invocations

# checks that the same fucntions are not invoked recursively
# creating a deadlock


def check_for_nested_invocation_deadlocks(
        nested_invocations: list,
        illegal_fx_names: list) -> list:
    for ni in nested_invocations:
        if ni['function_name'] in illegal_fx_names:
            raise RuntimeError(
                'This nested invocation tree will cause a deadlock.')
        else:
            if 'invoke_nested' in ni['invoke_payload']:
                illegal_fx_names.append(ni['function_name'])
                check_for_nested_invocation_deadlocks(
                    nested_invocations=ni['invoke_payload']['invoke_nested'],
                    illegal_fx_names=illegal_fx_names
                )
