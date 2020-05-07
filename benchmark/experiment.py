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

    def __init__(self, name:str, cl_provider:str, cl_client:str, desc:str, invocations:list = None):
        self.uuid = str(uuid.uuid4())
        self.start_time = time.time()
        self.name = name
        self.cl_provider = cl_provider
        self.cl_client = cl_client
        self.description = desc
        self.py_version = platform.python_version()
        self.cores = psutil.cpu_count()
        self.memory = psutil.virtual_memory()[0]
        self.invocations= []

    def get_start_time(self) -> float:
        return self.start_time
    
    def get_end_time(self) -> float:
        return self.end_time
    
    def get_experiment_description(self) -> str:
        return self.description

    def dev_print(self):
        pprint(vars(self))
    
    def get_invocations(self) -> list:
        return reduce(lambda x,y: x+y,self.invocations)
    
    def get_invocations_original_form(self):
        return self.invocations
    
    # make Invocation object out of function invocation dict and append to experiment list
    def add_invocation(self, invocations:dict) -> None:
        invocation_list = []
        root = invocations['root_identifier']
        del invocations['root_identifier']

        for x in invocations.keys():
            invocation_list.append(Invocation(self.uuid,root,invocations[x]))

        self.invocations.append(invocation_list)

    # for concurrent invoked function runs that returns a list of invocation dicts
    def add_invocations_list(self,invocations:list) -> None:
        for i in invocations:
            self.add_invocation(i)

    # end experiment, log time and return some data to benchmarker
    def end_experiment(self):
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time
        return (self.end_time, self.total_time)
    
    def 
    

