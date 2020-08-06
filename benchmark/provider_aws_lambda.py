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


class AWSLambdaProvider(AbstractProvider):

    def __init__(self, experiment_name: str, env_file_path: str, ntp_diff: float) -> None:
        # Create executor service
        AbstractProvider.__init__(self)

        # name of experiment to conduct
        self.experiment_name = experiment_name
        self.ntp_diff = ntp_diff

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
        print('key', self.api_key, 'url', self.gateway_url)

    async def invoke_wrapper(self,
                             url: str,
                             data: dict,
                             aiohttp_session: aiohttp.ClientSession,
                             thread_number: int,
                             number_of_threads: int
                             ) -> dict:

        # log start time of invocation
        start_time = time.time() + self.ntp_diff

        try:
            # async with aiohttp.ClientSession() as session:
            response_code = 0
            res = None
            async with aiohttp_session as session:

                for i in range(5):

                    try:
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
                            else:
                                print(f'trying to invoke {url} for the {i}th time, did not recieve a 200 response, the response recieved was:\n', response)

                    except aiohttp.ClientConnectionError:
                        print(f'Caught a ClientConnectionError at invocation attempt #{i}')

            end_time = time.time() + self.ntp_diff

            return (res, start_time, end_time, thread_number, number_of_threads) if response_code == 200 \
                else ({'statusCode': response_code, 'message': res.strip()}, start_time, end_time, thread_number, number_of_threads)

        except Exception as e:
            return ({'statusCode': 9999999, 'message': str(e)}, time.time(), time.time(), thread_number, number_of_threads)

    # in the case of AWS Lambda the name actually references
    # the api endpoint where the funcion is attached:
    #   --> eg: https://..../prod/<name>
    def invoke_function(self,
                        function_name: str,
                        function_args: dict = None) -> dict:

        try:

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

            (response, start_time, end_time, thread_number, number_of_threads) = tasks[0].result()

            return self.parse_data(response, start_time, end_time, thread_number, number_of_threads)

        except Exception as e:
            return (self.error_response(start_time=start_time, exception=e), start_time, time.time(), thread_number, number_of_threads)

    def parse_data(self,
                   response: dict,
                   start_time: float,
                   end_time: float,
                   thread_number: int,
                   number_of_threads: int) -> dict:
        try:
            # if succesfull invocation parse response
            if (response != None) and (response['statusCode'] == 200):

                # get the identifier
                identifier = response['identifier']

                # parse response body
                response_data = json.loads(response['body'])

                # insert thread_id and total number of threads for the sake of format fot database
                for val in response_data:
                    response_data[val]['thread_id'] = thread_number
                    response_data[val]['numb_threads'] = number_of_threads

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
        end_time = time.time() + self.ntp_diff
        error_dict = {
            f'exception-provider_aws_lambda-{self.experiment_name}-{end_time}': {
                'identifier': f'exception-provider_aws_lambda-{self.experiment_name}-{str(end_time)}',
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
            'root_identifier': f'exception-provider_aws_lambda-{self.experiment_name}-{str(end_time)}'
        }
        return error_dict

    def get_url(self,function_name):
        return f'{self.gateway_url}/{self.experiment_name}-{function_name}'
