#!/bin/python

import requests
import json
import time
import os
import dotenv
import traceback
from provider_abstract import AbstractProvider


class AWSLambdaProvider(AbstractProvider):

    def __init__(self, experiment_name: str, env_file_path: str) -> None:

        # name of experiment to conduct
        self.experiment_name = experiment_name

        # timeout for invoking function
        self.request_timeout = 600

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
                        function_name:str,
                        function_args:dict = None
                        ) -> dict:

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

        # create url of function to invoke
        invoke_url = f'{self.gateway_url}/{self.experiment_name}-{function_name}'

        print('url',invoke_url)

        # log start time of invocation
        start_time = time.time()

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
            if(response != None and  response.status_code == 200):

                #  response_json = json.loads(response.content.decode())
                response_json = response.json()

                # get the identifier
                identifier = response_json['identifier']

                # parse response body
                response_data = json.loads(response_json['body'])

                # insert thread_id and total number of threads for the sake of format fot database
                for val in response_data:
                    response_data[val]['numb_threads'] = 1
                    response_data[val]['thread_id'] = 1

                # add invocation metadata to response
                response_data[identifier]['invocation_start'] = start_time
                response_data[identifier]['invocation_end'] = end_time
                response_data['root_identifier'] = identifier

                # get rid of key we do not need
                # TODO see if key can be removed from cloud function instead
                #  response_data.pop('identifier')

                return response_data

            else:
                error_dict = {
                    'StatusCode-error-provider_aws_lambda-' + self.experiment_name + '-' + str(end_time): {
                        'identifier': 'StatusCode-error-provider_aws_lambda' + self.experiment_name + '-' + str(end_time),
                        'uuid': None,
                        'function_name': self.experiment_name,
                        'error': {'trace': 'None 200 code in provider_aws_lambda: ' + str(response.status_code), 'type': 'StatusCodeException', 'message': 'statuscode: ' + str(response.status_code)},
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
                    'root_identifier': 'StatusCode-error-provider_aws_lambda' + self.experiment_name + '-' + str(end_time)
                }
                return error_dict

        except Exception as e:
            end_time = time.time()
            error_dict = {
                'exception-provider_aws_lambda-' + self.experiment_name + str(end_time): {
                    'identifier': 'exception-provider_aws_lambda' + self.experiment_name + str(end_time),
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
                'root_identifier': 'exception-provider_aws_lambda' + self.experiment_name + str(end_time)
            }
            return error_dict
