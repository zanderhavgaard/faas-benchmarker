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
import threading as th
from concurrent import futures
import traceback


from datetime import datetime
from pprint import pprint


class Benchmarker:

    def __init__(self,
                 experiment_name: str,
                 experiment_meta_identifier: str,
                 provider: str,
                 client_provider: str,
                 experiment_description: str,
                 env_file_path: str,
                 dev_mode: bool = False,
                 verbose: bool = False) -> None:

        # do not log anything if running in dev mode
        self.dev_mode = dev_mode
        self.verbose = verbose
        self.invocation_count = 0
        self.futures = []
        self.idx = 0
        self.append_lock = th.Lock()
        self.future_lock = th.Lock()
        self.sync_flag = True
        self.futures_parsed = True

        # get function execution provider
        self.provider = self.get_provider(
            provider=provider, experiment_name=experiment_name, env_file_path=env_file_path)

        # experiment object holds all data for experiment
        self.experiment = Experiment(experiment_meta_identifier,
                                     experiment_name,
                                     provider,
                                     client_provider,
                                     experiment_description,
                                     dev_mode)
        
        self.background_sync()

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
            f'Experiment start time:      {time.ctime(int(self.experiment.start_time))}')
        print('=================================================')
        print(
            f'Experiment description: {self.experiment.description}')
        print('=================================================\n')

    # create cloud function execution provider

    def get_provider(self, provider: str, experiment_name: str, env_file_path: str) -> AbstractProvider:
        # implemented providers
        providers = ['aws_lambda', 'azure_functions', 'openfaas']

        # choose provider to invoke cloud function
        if provider in providers:
            if provider == 'aws_lambda':
                return AWSLambdaProvider(experiment_name=experiment_name, env_file_path=env_file_path)
            elif provider == 'azure_functions':
                return AzureFunctionsProvider(experiment_name=experiment_name, env_file_path=env_file_path)
            elif provider == 'openfaas':
                return OpenFaasProvider(experiment_name=experiment_name, env_file_path=env_file_path)
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
        print(f'{len(self.experiment.get_invocations())} invocations were made')
        print('=================================================\n')


    def dump_data(self):
        # store all data from experiment in database
        db = db_interface(self.dev_mode)
        db.log_experiment(self.experiment.uuid, self.experiment.log_experiment())


        if self.dev_mode:
            print('\n\n')
            print('dev mode --------------------------------------')
            invocations_orig = self.experiment.get_invocations_original_form()
            print('Experiment:', self.experiment.name, 'invoked', len(
                invocations_orig), 'times from its provider:', self.experiment.cl_provider)
            invocations = self.experiment.get_invocations(self.provider)
            print('EXPERIMENT META DATA')
            # print(self.experiment.dev_print())
            print()
            print('SQL query for experiment:')
            print(self.experiment.get_experiment_query_string())
            print()
            print('Number of functions invoked in total:', len(invocations))
            if self.verbose:
                print('--- DATA OF EACH INVOCATION ---')
                for invo in invocations:
                    print()
                    print('INVOCATION META DATA FOR identifier:', invo.identifier)
                    print(invo.dev_print())
                    print()
                    print('SQL query for invocation')
                    print(invo.get_query_string())
                    print('-------------------------------------------')
            print('----------------------------------------------')

    def end_experiment(self, invocation_count:int= None) -> None:
        if invocation_count != None:
            self.invocation_count = invocation_count
        self.kill_background_sync()
        # log the experiment running time, and print to log
        self.log_experiment_running_time()
        self.dump_data()
        self.provider.close()
        
        

    # main method to be used by experiment clients

    def invoke_function(self,
                        function_name: str,
                        function_args:dict = None) -> None:
        
        response = self.provider.invoke_function(function_name=function_name,
                                                 function_args=function_args)

        if response is None:
            raise EmptyResponseError(
                'Error: Empty response from cloud function invocation.')


        identifier = response['root_identifier']
        if ('StatusCode-error' not in identifier) and ('exception-provider' not in identifier):
            response[identifier]['invocation_total'] = response[identifier]['invocation_end'] - response[identifier]['invocation_start']
            response[identifier]['execution_total'] = response[identifier]['execution_end'] - response[identifier]['execution_start']
        with self.append_lock:
                self.experiment.add_invocations((self.idx, [response]))
                self.idx += 1

        return response

    def invoke_function_conccurrently(self,
                                      function_name: str,
                                      numb_threads: int = 1,
                                      function_args:dict= None,
                                      parse: bool = True,
                                      ) -> None:
       
        response = self.provider.invoke_function_conccrently(function_name=function_name,
                                                                  numb_requests=numb_threads,
                                                                  function_args=function_args,
                                                                  parse=parse,
                                                                  )
        if response is None:
            raise EmptyResponseError(
                'Error: Empty response from cloud function invocation.')
       
        if parse:
            with self.append_lock:
                self.experiment.add_invocations((self.idx, response))
        else:
            with self.future_lock:
                self.futures.append((self.idx,response))
                self.futures_parsed = False
        self.idx += 1
        return response if parse else None


    def background_sync(self):

        def sync_wrapper(bench):
            try:
                while(bench.sync_flag):
                    while(not bench.futures_parsed):
                       
                        idx = None
                        future = None
                        with bench.future_lock:
                            if len(bench.futures) > 0:
                                val = self.futures.pop(0)
                                idx = val[0]
                                future = val[1]
                            else:
                                bench.futures_parsed = True
                                break       

                        result_list = list(map(lambda x: bench.provider.parse_data(x[0],x[1],x[2]),
                                                            future.result() ))
                        
                        with bench.append_lock:
                            bench.experiment.add_invocations((idx, result_list))
    
            except Exception as e:
                print('Exception caught in background sync')
                print(str(type(e)))
                print(str(e))
                print(traceback.format_exc())
                print('---------------------------------')
        
        background_thread = th.Thread(target=sync_wrapper, args=[self])
        background_thread.start()

    def kill_background_sync(self):
        self.sync_flag = False
        self.ensure_futures()
        
    
    def ensure_futures(self):
        while(not self.futures_parsed):
            time.sleep(1)


# create exception class for empty responses
# do something smarter here
class EmptyResponseError(RuntimeError):
    def __init__(self, error_msg: str):
        super(error_msg)

