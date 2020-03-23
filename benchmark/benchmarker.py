#!/bin/python

import time
import json
import requests
import multiprocessing as mp
from abstract_provider import AbstractProvider
from provider_aws_lambda import AWSLambdaProivder
from provider_azure_functions import AzureFunctionsProvider
from provider_openfaas import OpenFaasProvider


class Benchmarker:

    def __init__(self, provider: str, experiment_description: str):
        # log the time of experiment start
        self.start_time = time.time()

        # desribe experiment, to be logged along with results
        self.experiment_description = experiment_description

    def get_provider(self, provider: str) -> AbstractProvider:
        # implemented providers
        self.providers = ['aws_lambda', 'azure_functions', 'openfaas']

        if provider in self.providers:
            # choose provider to invoke cloud function
            if provider == "aws_lambda":
                self.provider = self.get_aws_provider()

            elif provider == "azure_functions":
                raise NotImplementedError()

            elif provider == "openfaas":
                raise NotImplementedError()
        else:
            raise RuntimeError(
                "Error: Please use an implemented provider, \
                    options are: {}".formate(str(self.providers)))

    # get aws provider singleton
    def get_aws_provider(self) -> AWSLambdaProivder:
        if self.aws_provider is None:
            self.aws_provider = AWSLambdaProivder()
        return self.aws_provider

    def get_azure_provider(self) -> ProviderAzureFunctions:
        raise NotImplementedError()

    def get_openfaas_provider(self) -> ProviderOpenFaas:
        raise NotImplementedError()

    # log the total time of running an experiment
    # call this method as the last thing in experiment clients
    def log_experiment_running_time(self):
        end_time = time.time()
        experiment_running_time = end_time - self.start_time
        print('Experiment running time:', experiment_running_time)

    # main method to be used by experiment clients
    def invoke_function(self,
                        function_name: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:

        response = self.provider.invoke_function(name=function_name,
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
