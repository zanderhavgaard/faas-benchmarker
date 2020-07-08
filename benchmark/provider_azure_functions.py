#!/bin/python

import requests
import json
import time
import os
import dotenv
import traceback
from provider_abstract import AbstractProvider
import aiohttp
import asyncio


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
    
    async def invoke_wrapper(self,
                        url:str,
                        data,
                        aiohttp_session,
                        ) -> dict:
        
        try:
            # add optional dict describing nested invocations, if presente
            if 'invoke_nested' in data:
                inv_nest = data['invoke_nested']
                if(check_for_nested_deadlock(inv_nest, {url.split('/').pop()})):
                    function_args['invoke_nested'] = add_function_code_for_nested_invocations(
                        nested_invocations=inv_nest
                    )
                else:
                    raise Exception('azure deadlock')
            
            # log start time of invocation
            start_time = time.time()

        
            # async with aiohttp.ClientSession() as session:
            response_code = 0
            res = None
            async with aiohttp_session as session:
                for i in range(5):
                    async with session.post(
                        url=url,
                        headers=self.headers,
                        data=json.dumps(data),
                        timeout=self.request_timeout
                    ) as response:
                        response_code = response.status
                        if response_code == 200:
                            res = await response.json()
                            break
                        elif i == 4:
                            res = await response.text()
                            print(f'E001 : A non 200 response code recieved at iteration {i}. \
                                    Response_code: {response.status}, message: {res}')
                            
            return (json.loads(res.content.decode()), start_time,time.time()) if response_code == 200 \
                                else ({'statusCode': response_code, 'message': res.strip()}, start_time, time.time())
        except Exception as e:
            return self.error_response(start_time=start_time, exception=e) 


    # the functions are available under
    # https://<funtion_app_name>/api/<function_name>?code=<function_key>
    def invoke_function(self,
                        function_name: str,
                        function_args: dict = None
                        ) -> dict:


        # paramters, the only required paramter is the statuscode
        if function_args is None:
            function_args = {"StatusCode": 200}
        else:
            function_args["StatusCode"] = 200
        
        # set default value for sleep if not present in function_args
        if 'sleep' not in function_args:
            function_args["sleep"] = 0.0
     
        try:

            # create url of function to invoke
            invoke_url = self.get_url(function_name) 

            loop = asyncio.get_event_loop()

            tasks = [asyncio.ensure_future(self.invoke_wrapper(invoke_url,
                                        function_args, 
                                        aiohttp.ClientSession()))]

            (response,start_time,end_time) = tasks[0].result()

            return self.parse_data(response,start_time,end_time)
        
        except Exception as e:
            return self.error_response(start_time=time.time(),exception=e)

    def parse_data(self, response:dict, start_time:float, end_time:float) -> dict:
        try:
        
            if (response != None) and (response['statusCode'] == 200):
                    
                # get the identifier
                # identifier = response_json['identifier']
                identifier = response['identifier']

                # parse response body
                response_data = json.loads(response['body'])

                # insert thread_id and total number of threads for the sake of format for database
                for val in response_data:
                    response_data[val]['numb_threads'] = 1
                    response_data[val]['thread_id'] = 1

                # add invocation metadata to response
                response_data[identifier]['invocation_start'] = start_time
                response_data[identifier]['invocation_end'] = end_time
                response_data['root_identifier'] = identifier

                return response_data

            else:
                statuscode = response['statusCode']
                message = response['message']
                error_dict = {
                    f'StatusCode-error-provider_azure-{self.experiment_name}-{str(end_time)}': {
                        'identifier': f'StatusCode-error-provider_azure-{self.experiment_name}-{str(end_time)}',
                        'uuid': None,
                        'function_name': self.experiment_name,
                        'error': {'trace': f'None 200 code in provider_azure: {str(statuscode)}', 'type': 'StatusCodeException', 'message': message},
                        'parent': None,
                        'sleep': response['sleep'],
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
                    'root_identifier': f'StatusCode-error-provider_azure-{self.experiment_name}-{str(end_time)}'
                }
                return error_dict

        except Exception as e:
            return self.error_response(start_time=start_time, exception=e)

        except Exception as e:
            end_time = time.time()
            error_dict = {
                f'exception-provider_azure_functions-{self.experiment_name}-{str(end_time)}': {
                    'identifier': f'exception-provider_azure_functions-{self.experiment_name}-{str(end_time)}',
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
                'root_identifier': f'exception-provider_azure_functions-{self.experiment_name}-{str(end_time)}'
            }
            return error_dict

def error_response(self, start_time, exception):
        end_time = time.time()
        error_dict = {
            f'exception-provider_azure-{self.experiment_name}-{end_time}': {
                'identifier': f'exception-provider_azure-{self.experiment_name}-{str(end_time)}',
                'uuid': None,
                'function_name': self.experiment_name,
                'error': {"trace": traceback.format_exc(), "type": str(type(exception).__name__), 'message': str(exception)},
                'parent': None,
                'sleep': 0.0,
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
            'root_identifier': f'exception-provider_azure-{self.experiment_name}-{str(end_time)}'
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

def get_url(self,function_name):
    function_app_url = os.getenv(f'{self.experiment_name}-{function_name}_function_app_url')
    function_key = os.getenv(f'{self.experiment_name}-{function_name}_function_key')
     # create url of function to invoke

    if function_app_url is None or function_key is None:
        raise RuntimeError('Could not parse function app url or key.')

    invoke_url = f'https://{function_app_url}/api/{self.experiment_name}-{function_name}?code={function_key}'

    return invoke_url
