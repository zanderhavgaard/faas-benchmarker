#!/bin/python

import time
import json
import requests
import multiprocessing as mp
from provider_abstract import AbstractProvider
from provider_aws_lambda import AWSLambdaProvider
from provider_azure_functions import AzureFunctionsProvider
from provider_openfaas import OpenFaasProvider


class Benchmarker:

    def __init__(self, experiment_name:str, provider: str, experiment_description: str, env_file_path: str):

        # log the experiment name
        self.experiment_name = experiment_name

        # log the time of experiment start
        self.start_time = time.time()

        # desribe experiment, to be logged along with results
        self.experiment_description = experiment_description

        # get function execution provider
        self.provider = self.get_provider(
            provider=provider, env_file_path=env_file_path)

        print('\n=================================================')
        print('FaaS benchmarker ~ Stating experiment ...')
        print('=================================================')
        print(f'experiment name:         {experiment_name}')
        print(f'using provider:          {provider}')
        print(f'using environment file:  {env_file_path}')
        print(f'experiment start time:   {time.ctime(int(self.start_time))}')
        print('=================================================')
        print(f'experiment description: {self.experiment_description}')
        print('=================================================\n')

    # create cloud function execution provider

    def get_provider(self, provider: str, env_file_path: str) -> AbstractProvider:
        # implemented providers
        providers = ['aws_lambda', 'azure_functions', 'openfaas']

        # choose provider to invoke cloud function
        if provider in providers:
            if provider == 'aws_lambda':
                return AWSLambdaProvider(env_file_path=env_file_path)
            elif provider == 'azure_functions':
                raise NotImplementedError()
                #  return AzureFunctionsProvider(env_file_path=env_file_path)
            elif provider == 'openfaas':
                raise NotImplementedError()
                #  return OpenFaasProvider(env_file_path=env_file_path)
        else:
            raise RuntimeError(
                f'Error: Please use an implemented provider, options are: ' +
                '{str(self.providers)}')

    # log the total time of running an experiment
    # call this method as the last thing in experiment clients
    def log_experiment_running_time(self):
        end_time = time.time()
        experiment_running_time = end_time - self.start_time
        print('=================================================')
        print(f'Experiment end time: {time.ctime(int(end_time))}')
        print('Experiment running time: ' +
              f'{time.strftime("%H:%M:%S", time.gmtime(experiment_running_time))}')
        print('=================================================')

    # main method to be used by experiment clients
    def invoke_function(self,
                        function_endpoint: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:

        response = self.provider.invoke_function(function_endpoint=function_endpoint,
                                                 sleep=sleep,
                                                 invoke_nested=invoke_nested)

        if response is None:
            raise EmptyResponseError(
                'Error: Empty response from lambda invocation.')

        # log repsonse to db
        # TODO

        return response


class EmptyResponseError(RuntimeError):
    def __ini__(self, error_msg: str):
        super(error_msg)
