#!/bin/python

import sys
import time
import json
import requests
import multiprocessing as mp
from provider_abstract import AbstractProvider
from provider_aws_lambda import AWSLambdaProvider
from provider_azure_functions import AzureFunctionsProvider
from provider_openfaas import OpenFaasProvider
from experiment import Experiment
from mysql_interface import SQL_Interface as db_interface

from pprint import pprint


class Benchmarker:

    def __init__(self,
                 experiment_name: str,
                 experiment_meta_identifier: str,
                 provider: str,
                 client_provider: str,
                 experiment_description: str,
                 env_file_path: str,
                 dev_mode: bool = False) -> None:

        # do not log anything if running in dev mode
        self.dev_mode = dev_mode

        # get function execution provider
        self.provider = self.get_provider(
            provider=provider, env_file_path=env_file_path)

        # experiment object holds all data for experiment
        self.experiment = Experiment(experiment_meta_identifier,
                                     experiment_name,
                                     provider,
                                     client_provider,
                                     experiment_description)

        print('\n=================================================')
        print('FaaS Benchmarker --> Starting Experiment ...')
        print('=================================================')
        print(f'Python version: {sys.version}')
        print('=================================================')
        print(f'dev_mode: {self.dev_mode}')
        print(f'Experiment name:            {experiment_name}')
        print(f'Experiment meta identifier: {experiment_meta_identifier}')
        print(f'Using provider:             {provider}')
        print(f'Using client provider:      {client_provider}')
        print(f'Using environment file:     {env_file_path}')
        print(
            f'Experiment start time:      {time.ctime(int(self.experiment.get_start_time()))}')
        print('=================================================')
        print(
            f'Experiment description: {self.experiment.get_experiment_description()}')
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
                return AzureFunctionsProvider(env_file_path=env_file_path)
            elif provider == 'openfaas':
                return OpenFaasProvider(env_file_path=env_file_path)
        else:
            raise RuntimeError(
                'Error: Please use an implemented provider, options are: ' +
                f'{str(providers)}')

    # log the total time of running an experiment
    # call this method as the last thing in experiment clients
    def log_experiment_running_time(self) -> None:
        (end_time, total_time) = self.experiment.end_experiment()
        # experiment_running_time = end_time - self.start_time
        print('=================================================')
        print(f'Experiment end time: {time.ctime(int(end_time))}')
        print('Experiment running time: ' +
              f'{time.strftime("%H:%M:%S", time.gmtime(total_time))}')
        print('=================================================\n')
       

    def dump_data(self):
        # do not log data if running in development mode locally
        if not self.dev_mode:
            # store all data from experiment in database
            db = db_interface()
            db.log_experiment(self.experiment)
        else:
            print('\n\n')
            invocations_orig = self.experiment.get_invocations_original_form()
            print('Experiment:', self.experiment.name, 'invoked', len(
                invocations_orig), 'times from its provider:', self.experiment.cl_provider)
            invocations = self.experiment.get_invocations()
            print('EXPERIMENT META DATA')
            print(self.experiment.dev_print())
            print()
            print('SQL query for experiment:')
            print(self.experiment.get_experiment_query_string())
            print()
            print('Number of functions invoked in total:', len(invocations))
            print('--- DATA OF EACH INVOCATION ---')
            for invo in invocations:
                print()
                print('INVOCATION META DATA FOR identifier:', invo.identifier)
                print(invo.dev_print())
                print()
                print('SQL query for invocation')
                print(invo.get_query_string())
                print('-------------------------------------------')

    def end_experiment(self) -> None:
        # log the experiment running time, and print to log
        self.log_experiment_running_time()
        self.dump_data()

    # main method to be used by experiment clients

    def invoke_function(self,
                        function_endpoint: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None,
                        throughput_time: float = 0.0) -> None:

        response = self.provider.invoke_function(function_endpoint=function_endpoint,
                                                 sleep=sleep,
                                                 invoke_nested=invoke_nested,
                                                 throughput_time=throughput_time)

        if response is None:
            raise EmptyResponseError(
                'Error: Empty response from cloud function invocation.')
            

        identifier = response['root_identifier']
        if ('StatusCode-error' not in identifier) and ('exception-provider' not in identifier):
            response[identifier]['invocation_total'] = response[identifier]['invocation_end'] - response[identifier]['invocation_start']
            response[identifier]['execution_total'] = response[identifier]['execution_end'] - response[identifier]['execution_start']

        self.experiment.add_invocation(response)

        return response

    def invoke_function_conccurrently(self,
                                      function_endpoint: str,
                                      sleep: float = 0.0,
                                      invoke_nested: dict = None,
                                      throughput_time: float = 0.0,
                                      numb_threads: int = 1
                                      ) -> None:

        response_list = self.provider.invoke_function_conccrently(function_endpoint,
                                                                  sleep,
                                                                  invoke_nested,
                                                                  throughput_time,
                                                                  numb_threads
                                                                  )

        if response_list is None:
            raise EmptyResponseError(
                'Error: Empty response from cloud function invocation.')

        self.experiment.add_invocations_list(response_list)

        return response_list

    # def get_delay_between_experiment_iterations(self):
    #     provider = self.experiment.get_cl_provider()
    #     delay = self.db.get_delay_between_experiment(provider)
    #     return delay if delay != None else 35 * 60


# create exception class for empty responses

# do something smarter here
class EmptyResponseError(RuntimeError):
    def __ini__(self, error_msg: str):
        super(error_msg)
        
