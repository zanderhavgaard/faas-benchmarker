#!/bin/python

import requests
import json
import time
import os
import dotenv
import traceback
from provider_abstract import AbstractProvider


class AzureFunctionsProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> None:

        # timeout for invoking function
        self.request_timeout = 600

        # load azurw functions specific invocation url and credentials
        self.load_env_vars(env_file_path)

        # http headers, contains data type
        self.headers = {
            'Content-Type': 'application/json'
        }

    # load .env file and parse values

    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)

    # for azure functions the function_endpoint refers to the function name
    # the functions are available under
    # https://<funtion_app_name>/api/<function_name>?code=<function_key>
    def invoke_function(self,
                        function_endpoint: str,
                        sleep: float = 0.0,
                        invoke_nested: list = None,
                        throughput_time: float = 0.0) -> dict:

        function_app_url = os.getenv(f'{function_endpoint}_function_app_url')
        function_key = os.getenv(f'{function_endpoint}_function_key')

        if function_app_url is None or function_key is None:
            raise RuntimeError('Could not parse function app url or key.')

        # paramters, the only required paramter is the statuscode
        params = {
            "StatusCode": 200
        }

        # add optional sleep parameter if present
        if sleep != 0.0:
            params['sleep'] = sleep

        if(throughput_time != 0.0):
            params['throughput_time'] = throughput_time

        # add optional dict describing nested invocations, if presente
        if invoke_nested != None:
            if(check_for_nested_deadlock(invoke_nested, {function_endpoint})):
                params['invoke_nested'] = add_function_code_for_nested_invocations(
                    nested_invocations=invoke_nested
                )
            else:
                raise Exception('azure deadlock')

        # log start time of invocation
        start_time = time.time()

        # create url of function to invoke
        invoke_url = f'https://{function_app_url}/api/{function_endpoint}?code={function_key}'

        try:

            # log start time of invocation
            start_time = time.time()

            # the invocation might fail if it is a cold start,
            # seems to be some timeout issue, so in that case we try again
            for i in range(5):
                try:
                    # invoke the function
                    response = requests.post(
                        url=invoke_url,
                        headers=self.headers,
                        data=json.dumps(params),
                        timeout=self.request_timeout
                    )
                    if response.status_code == 200:
                        break
                except Exception as e:
                    print(
                        f"Caught an error for attempt {i}, retrying invocation ...")
                    print(e)
                    continue

            # log the end time of the invocation
            end_time = time.time()

            # TODO make same change with if else for AWS and azure
            # if succesfull invocation parse response
            if(response.status_code == 200):

                # parse the response json
                response_data = json.loads(response.content.decode())

                # get the identifier
                identifier = response_data['identifier']

                if 'identifier' in response_data:
                    response_data.pop('identifier')

                # insert thread_id and total number of threads for the sake of format fot database
                for val in response_data:
                    response_data[val]['numb_threads'] = 1
                    response_data[val]['thread_id'] = 1

                # add invocation metadata to response
                response_data[identifier]['invocation_start'] = start_time
                response_data[identifier]['invocation_end'] = end_time
                response_data['root_identifier'] = identifier

                return response_data

            else:
                error_dict = {
                    'StatusCode-error-providor_openfaas-' + function_endpoint + '-' + str(end_time): {
                        'identifier': 'StatusCode-error-providor_openfaas' + function_endpoint + '-' + str(end_time),
                        'uuid': None,
                        'function_name': function_endpoint,
                        'error': {'trace': 'None 200 code in providor_openfaas: ' + str(response.status_code), 'type': 'StatusCodeException', 'message': 'statuscode: ' + str(response.status_code)},
                        'parent': None,
                        'sleep': sleep,
                        'numb_threads': 1,
                        'thread_id': 1,
                        'python_version': None,
                        'level': None,
                        'memory': None,
                        'instance_identifier': None,
                        'execution_start': None,
                        'execution_end': None,
                        'invocation_start': start_time,
                        'invocation_end': end_time,
                    },
                    'root_identifier': 'StatusCode-error-providor_openfaas' + function_endpoint + '-' + str(end_time)
                }
                return error_dict

        except Exception as e:
            end_time = time.time()
            error_dict = {
                'exception-providor_openfaas-' + function_endpoint + str(end_time): {
                    'identifier': 'exception-providor_openfaas' + function_endpoint + str(end_time),
                    'uuid': None,
                    'function_name': function_endpoint,
                    'error': {"trace": traceback.format_exc(), "type": str(type(e).__name__), 'message': str(e)},
                    'parent': None,
                    'sleep': sleep,
                    'numb_threads': 1,
                    'thread_id': 1,
                    'python_version': None,
                    'level': None,
                    'memory': None,
                    'instance_identifier': None,
                    'execution_start': None,
                    'execution_end': None,
                    'invocation_start': start_time,
                    'invocation_end': end_time,
                },
                'root_identifier': 'exception-providor_openfaas' + function_endpoint + str(end_time)
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


def check_for_nested_deadlock(nested_invocations: list, illegal_fx_names: set):
    for invo in nested_invocations:
        if(invo['function_name'] in illegal_fx_names):
            return False
    illegal_fx_names.update(i['function_name'] for i in nested_invocations)

    for x in nested_invocations:
        if('invoke_nested' in x['invoke_payload']):
            if not(check_for_nested_deadlock(x['invoke_payload']['invoke_nested'], illegal_fx_names)):
                return False
    return True
