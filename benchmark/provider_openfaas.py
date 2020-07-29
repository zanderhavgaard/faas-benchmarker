import time
import json
import requests
import dotenv
import os
from provider_abstract import AbstractProvider
import traceback
import http
from pprint import pprint
import aiohttp
import asyncio


class OpenFaasProvider(AbstractProvider):

    def __init__(self, experiment_name: str, env_file_path: str) -> None:
        # Create executor service
        AbstractProvider.__init__(self)
        #log some metadata
        self.experiment_name = experiment_name
        self.env_file_path = env_file_path

        # timeout for invoking function
        self.request_timeout = 600

        # load openfaas envrionment variables
        self.load_env_vars(env_file_path)

        # http headers, contains authentication and data type
        self.headers = {
            'Content-Type': 'application/json'
        }

    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)
    
    async def invoke_wrapper(self,
                        url:str,
                        data:dict,
                        aiohttp_session:aiohttp.ClientSession,
                        thread_number:int,
                        number_of_threads:int
                        ) -> dict:

        # TODO remove when we feel sure that all of the stuff works...
        print('url', url)

        # log start time of invocation
        start_time = time.time()

        try:
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
                        elif (i == 4):
                            res = await response.text()
                            print(f'E001 : A non 200 response code recieved at iteration {i}. \
                                    Response_code: {response.status}, message: {res}')
             
            return (res, start_time, time.time(), thread_number, number_of_threads) if response_code == 200 \
                    else ({'statusCode': response_code, 'message': res.strip()}, start_time, time.time(), thread_number, number_of_threads)

        except Exception as e:
            return ({'statusCode': 9999999, 'message': str(e)}, time.time(), time.time(), thread_number, number_of_threads)
    
    def invoke_function(self,
                        function_name:str,
                        function_args:dict = None,
                        ) -> dict:
        
        try:
            
            # for openfaas we do not need the endpoint, as it is always the same
            # create url of function to invoke
            invoke_url = self.get_url(function_name)

            # fix for experimetns that use threads, since each thread need to have an event loop
            # overhead of creating new loops should be negligable
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # was 
            # loop = asyncio.get_event_loop()
            
            tasks = [asyncio.ensure_future(self.invoke_wrapper(
                                                url=invoke_url,
                                                data=function_args if function_args != None else {}, 
                                                aiohttp_session=aiohttp.ClientSession(),
                                                thread_number=1,
                                                number_of_threads=1))]

            loop.run_until_complete(asyncio.wait(tasks))

            # close created loop
            loop.close()

            (response,start_time,end_time, thread_number, number_of_threads) = tasks[0].result()

            return self.parse_data(response,start_time,end_time, thread_number, number_of_threads)
        
        except Exception as e:
            return self.error_response(start_time=time.time(),exception=e)


    
    def parse_data(self, response:dict, start_time:float, end_time:float, thread_number:int, number_of_threads:int) -> dict:
        try:
        
            if (response != None) and (response['statusCode'] == 200):
                    
                # get the identifier
                # identifier = response_json['identifier']
                identifier = response['identifier']

                # parse response body
                response_data = json.loads(response['body'])

                # insert thread_id and total number of threads for the sake of format for database
                for val in response_data:
                    response_data[val]['numb_threads'] = thread_number
                    response_data[val]['thread_id'] = number_of_threads

                # add invocation metadata to response
                response_data[identifier]['invocation_start'] = start_time
                response_data[identifier]['invocation_end'] = end_time
                response_data['root_identifier'] = identifier

                return response_data

            else:
                statuscode = response['statusCode']
                message = response['message']
                error_dict = {
                    f'StatusCode-error-provider_openfaas-{self.experiment_name}-{str(end_time)}': {
                        'identifier': f'StatusCode-error-provider_openfaas-{self.experiment_name}-{str(end_time)}',
                        'uuid': None,
                        'function_name': self.experiment_name,
                        'error': {'trace': f'None 200 code in provider_openfaas: {str(statuscode)}', 'type': 'StatusCodeException', 'message': message},
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
                        'invocation_end': end_time,
                    },
                    'root_identifier': f'StatusCode-error-provider_openfaas-{self.experiment_name}-{str(end_time)}'
                }
                return error_dict

        except Exception as e:
            return self.error_response(start_time=start_time, exception=e)


    def error_response(self, start_time, exception):
        end_time = time.time()
        error_dict = {
            f'exception-provider_openfaas-{self.experiment_name}-{end_time}': {
                'identifier': f'exception-provider_openfaas-{self.experiment_name}-{end_time}',
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
            'root_identifier': f'exception-provider_openfaas-{self.experiment_name}-{end_time}'
        }
        return error_dict
    

    def get_url(self,function_name:str):
        openfaas_hostname = os.getenv('openfaas_hostname')
        openfaas_port = os.getenv('openfaas_port')
        # TODO remove experiment name from invoke url when back to running on EKS
        # return f'http://{openfaas_hostname}:{openfaas_port}/function/{function_name}'
        url = f'http://{openfaas_hostname}:{openfaas_port}/function/{self.experiment_name}-{function_name}'
        #  print('url',url)
        return url
        
