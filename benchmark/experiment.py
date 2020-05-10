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

    def __init__(self, name:str, cl_provider:str, cl_client:str, desc:str):
        self.uuid = str(uuid.uuid4())
        self.start_time = time.time()
        self.name = name
        self.cl_providor = cl_provider
        self.cl_client = cl_client
        self.description = desc
        self.python_version = platform.python_version()
        self.cores = psutil.cpu_count()
        self.memory = psutil.virtual_memory()[0]
        
        self.invocations= []

    def get_start_time(self) -> float:
        return self.start_time
    
    def get_end_time(self) -> float:
        return self.end_time
    
    def get_uuid(self):
        return self.uuid
    
    def get_experiment_description(self) -> str:
        return self.description

    def dev_print(self) -> None:
        pprint(vars(self))
    
    def get_invocations(self) -> list:
        return reduce(lambda x,y: x+y,self.invocations)
    
    def get_invocations_original_form(self) -> list:
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
    
    def get_experiment_query_string(self) -> str:
        self_dict = self.__dict__.copy()
        self_dict.pop('invocations')
        key_string = ''
        val_string = ''
        for k,v in self_dict.items():
            key_string += k+','
            if(isinstance(v,str)):
                val_string += """'{0}',""".format(v)
            else:
                val_string += str(v)+','
        return 'INSERT INTO Experiment ({0}) VALUES ({1})'.format(key_string[:-1],val_string[:-1])
    
    def log_experiment(self):
        return ([self.get_experiment_query_string()], [i.get_query_string() for i in self.get_invocations()])

    
