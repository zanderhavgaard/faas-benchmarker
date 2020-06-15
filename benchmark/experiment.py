import sys
import uuid
import psutil
import time
import platform
from functools import reduce
from invocation import Invocation
# remove for production
from pprint import pprint


class Experiment:

    def __init__(self,
                 experiment_meta_identifier: str,
                 name: str,
                 cl_provider: str,
                 cl_client: str,
                 desc: str,
                 dev_mode: bool):

        self.uuid = str(uuid.uuid4())
        self.start_time = time.time()
        self.experiment_meta_identifier = experiment_meta_identifier
        self.name = name
        self.cl_provider = cl_provider
        self.cl_client = cl_client
        self.description = desc
        self.dev_mode = dev_mode
        self.python_version = platform.python_version()
        self.cores = psutil.cpu_count()
        self.memory = psutil.virtual_memory()[0]

        self.invocations = []


    def dev_print(self) -> None:
        pprint(vars(self))

    def get_invocations(self) -> list:
        return reduce(lambda x, y: x+y, self.invocations) if len(self.invocations) != 0 \
            else [] and print('Error! no invocations') 

    def get_invocations_original_form(self) -> list:
        return self.invocations

    # make Invocation object out of function invocation dict and append to experiment list
    def add_invocation(self, invocations: dict) -> None:
        invocation_list = []
        root = invocations.pop('root_identifier')

        for x in invocations.keys():
            invocation_list.append(Invocation(self.uuid, root, invocations[x]))

        self.invocations.append(invocation_list)
        invocations['root_identifier'] = root

    # for concurrent invoked function runs that returns a list of invocation dicts
    def add_invocations_list(self, invocations: list) -> None:
        for i in invocations:
            self.add_invocation(i)

    # end experiment, log time and return some data to benchmarker
    def end_experiment(self, invocation_count:int):
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time
        if invocation_count != 0:
            self.invocation_count = invocation_count
        return (self.end_time, self.total_time)

    def get_experiment_query_string(self) -> str:
        self_dict = self.__dict__.copy()
        self_dict.pop('invocations')
   
        (keys,vals) = reduce(lambda x,y: ( f'{x[0]}{y[0]},', f'{x[1]}{y[1]},') if not isinstance(y[1],str) 
                            else ( f'{x[0]}{y[0]},', f"""{x[1]}'{y[1]}',""") ,[('','')] + list(self_dict.items()))
        return 'INSERT INTO Experiment ({0}) VALUES ({1});'.format(keys[:-1], vals[:-1])

    def log_experiment(self):
        return ([self.get_experiment_query_string()], list(reduce(lambda x,y: x+y, [i.get_query_string() for i in self.get_invocations()])) )
