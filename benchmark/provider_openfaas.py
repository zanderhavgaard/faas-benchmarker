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
                # pprint(response_data)

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
            
