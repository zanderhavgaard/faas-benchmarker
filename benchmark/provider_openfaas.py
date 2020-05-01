import time
import json
import requests
import dotenv
import os
from provider_abstract import AbstractProvider
import traceback
from pprint import pprint


class OpenFaasProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> None:

        # load aws lambda specific invocation url and credentials
        self.load_env_vars(env_file_path)
        # added for testing with .test_env
        self.gateway_url = str(os.getenv('invoke_url'))
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
                        invoke_nested: list = None
                        ) -> dict:

        # paramters, the only required paramter is the statuscode
        params = {
            "StatusCode": 200
            # "level": 0
        }

        # add optional sleep parameter if present
        if sleep != 0.0:
            params['sleep'] = sleep

        # add optional dict describing nested invocations, if presente
        if invoke_nested != None:
            params['invoke_nested'] = invoke_nested

        # TODO change to read from env
        # commented out while testing
        # self.gateway_url = 'http://localhost:8080/function'

        # create url of function to invoke
        invoke_url = f'{self.gateway_url}/{function_endpoint}'

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
                # pprint(response_json)
                # print()

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
                    'Error': {
                        'identifier': function_endpoint+'-None-'+str(response.status_code),
                        'uuid': None,
                        'sleep': sleep,
                        'ip_address': None,
                        'python_version': None,
                        'hostname': None,
                        'invocation_start': start_time,
                        'invocation_end': end_time,
                        'invocation_start': None,
                        'invocation_end': None,
                        'status_code': response.status_code
                    },
                    'root_identifier': function_endpoint+'-None-'+str(response.status_code),
                }
                return error_dict

        except Exception as e:
            tb = traceback.format_exc()
            # exception_dict = {
            #                 'Exception':{
            #                             'identifier': function_endpoint+'-None-'+str(type(e)),
            #                             'type':str(type(e)),
            #                             'message':str(e),
            #                             'traceback':tb
            #                             }
            #                 }
            # return exception_dict
            print('caught exception in openfaas of type', type(e), str(e), tb)
