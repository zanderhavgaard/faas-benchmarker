#!/bin/python

import requests
import json
import time
import os
import dotenv
import traceback
from provider_abstract import AbstractProvider


class AzureFunctionsProvider(AbstractProvider):

    def __init__(self, experiment_name: str, env_file_path: str) -> None:

        # name of experiment
        self.experiment_name = experiment_name

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
        print('path',env_file_path)

    # the functions are available under
    # https://<funtion_app_name>/api/<function_name>?code=<function_key>
    def invoke_function(self,
                        function_name:str,
                        function_args:dict = None
                        ) -> dict:

        function_app_url = os.getenv(f'{self.experiment_name}-{function_name}_function_app_url')
        function_key = os.getenv(f'{self.experiment_name}-{function_name}_function_key')

        print('env',function_app_url,function_key)

        if function_app_url is None or function_key is None:
            raise RuntimeError('Could not parse function app url or key.')

        # set default value for sleep if not present in function_args
        if function_args is not None:
            sleep = function_args["sleep"] if "sleep" in function_args.keys() else 0.0
        else:
            sleep = 0.0

        # paramters, the only required paramter is the statuscode
        if function_args is None:
            function_args = {"StatusCode":200}
        else:
            function_args["StatusCode"] = 200


        # add optional dict describing nested invocations, if presente
        if 'invoke_nested' in function_args:
            inv_nest = function_args['invoke_nested']
            if(check_for_nested_deadlock(inv_nest, {function_name})):
                function_args['invoke_nested'] = add_function_code_for_nested_invocations(
                    nested_invocations=inv_nest
                )
            else:
                raise Exception('azure deadlock')

        # log start time of invocation
        start_time = time.time()

        # create url of function to invoke
        invoke_url = f'https://{function_app_url}/api/{self.experiment_name}-{function_name}?code={function_key}'

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
                        data=json.dumps(function_args),
                        timeout=self.request_timeout
                    )
                    if response.status_code == 200:
                        break
                    print(f'Invocation attempt {i} Did not get a 200 statuscode, retrying ...')
                except Exception as e:
                    print(
                        f"Caught an error for attempt {i}, retrying invocation ...")
                    print(e)
                    continue

            # log the end time of the invocation
            end_time = time.time()

            # TODO make same change with if else for AWS and azure
            # if succesfull invocation parse response
            if(response != None and response.status_code == 200):

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
                    'StatusCode-error-provider_azure_functions-' + self.experiment_name + '-' + str(end_time): {
                        'identifier': 'StatusCode-error-provider_azure_functions' + self.experiment_name + '-' + str(end_time),
                        'uuid': None,
                        'function_name': self.experiment_name,
                        'error': {'trace': 'None 200 code in provider_azure_functions: ' + str(response.status_code), 'type': 'StatusCodeException', 'message': 'statuscode: ' + str(response.status_code)},
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
                    'root_identifier': 'StatusCode-error-provider_azure_functions' + self.experiment_name + '-' + str(end_time)
                }
                return error_dict

        except Exception as e:
            end_time = time.time()
            error_dict = {
                'exception-provider_azure_functions-' + self.experiment_name + str(end_time): {
                    'identifier': 'exception-provider_azure_functions' + self.experiment_name + str(end_time),
                    'uuid': None,
                    'function_name': self.experiment_name,
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
                'root_identifier': 'exception-provider_azure_functions' + self.experiment_name + str(end_time)
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
