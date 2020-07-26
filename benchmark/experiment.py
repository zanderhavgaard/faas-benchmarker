import sys
import uuid
import psutil
import time
import platform
from functools import reduce
from invocation import Invocation
import function_lib as lib
# remove for production
from pprint import pprint
import aiohttp
import asyncio



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

  
    def get_invocations_original_form(self) -> list:
        return self.invocations

    # make Invocation object out of function invocation dict and append to experiment list
    def add_invocations(self, args) -> None:
        self.invocations.append(args)
    

    def get_invocations(self):
    
        self.invocations.sort(key=lambda tup: tup[0])
       
        invocations_flattened = lib.flatten_list([],list(map(lambda x: x[1],self.invocations)))
        
        invocation_list = []
        
        for val in invocations_flattened:
            root = val.pop('root_identifier')

            for x in val.keys():
                invocation_list.append(Invocation(self.uuid, root, val[x]))
            val['root_identifier'] = root
        
        return invocation_list
        

    # end experiment, log time and return some data to benchmarker
    def end_experiment(self):
        self.end_time = time.time()
        self.total_time = self.end_time - self.start_time
        return (self.end_time, self.total_time)

    def get_experiment_query_string(self) -> str:
        self_dict = self.__dict__.copy()
        self_dict.pop('invocations')
   
        (keys,vals) = reduce(lambda x,y: ( f'{x[0]}{y[0]},', f'{x[1]}{y[1]},') if not isinstance(y[1],str) 
                            else ( f'{x[0]}{y[0]},', f"""{x[1]}'{y[1]}',""") ,[('','')] + list(self_dict.items()))
        return 'INSERT INTO Experiment ({0}) VALUES ({1});'.format(keys[:-1], vals[:-1])

    def log_experiment(self):
        # invocations = [x if type(x)__name__ == 'dict' else providor.parse_data( x.result()) for x in self.get_invocations()]
        # [self.parse_data(a,b,c) for (a,b,c) in map(lambda x: x.result(), tasks)]
        return ([self.get_experiment_query_string()], list(reduce(lambda x,y: x+y, [i.get_query_string() for i in self.get_invocations()])) )
