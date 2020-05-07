import time
import json
import requests
import dotenv
import os
from provider_abstract import AbstractProvider
import traceback
import sys


class OpenFaasProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> None:

        # http headers, contains authentication and data type
        self.headers = {
            'Content-Type': 'application/json'
        }

    def invoke_function(self,
                        function_endpoint: str,
                        sleep: float = 0.0,
                        invoke_nested: list = None
                        ) -> dict:

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

        function_number = function_endpoint[len(function_endpoint)-1:]

        # create url of function to invoke
        invoke_url = f'http://localhost:8080/function/function{function_number}'

        # log start time of invocation
        start_time = time.time()

        try:
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
                    'StatusCode-error-providor_openfaas-'+function_endpoint+'-'+str(end_time): {
                        'identifier': 'StatusCode-error-providor_openfaas'+function_endpoint+'-'+str(end_time),
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
                    'root_identifier': 'StatusCode-error-providor_openfaas'+function_endpoint+'-'+str(end_time)
                }
                return error_dict

        except Exception as e:
            end_time = time.time()
            error_dict = {
                'exception-providor_openfaas-'+function_endpoint+str(end_time): {
                    'identifier': 'exception-providor_openfaas'+function_endpoint+str(end_time),
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
                    'invocation_end': end_time
                },
                'root_identifier': 'exception-providor_openfaas'+function_endpoint+str(end_time)
            }
            return error_dict
