import sys
import uuid
import psutil
import time
from invocation import Invocation
# remove for production
from pprint import pprint



class Experiment:

    def __init__(self,name:str,desc:str,cl_provider:str,clinet:str,invocations:list = None):
        self.name = name
        self.desc = desc
        self.cl_provider = cl_provider
        self.client = client
        self.py_version = psutil.py_version()
        self.cores = psutil.cpu_count()
        self.memory:tuble = psutil.virtual_memory()
        if(invocations != None):
            self.invocations=invocations
        else:
            self.invocations= []

    def dev_print(self):
        pprint(vars(self))
    
    def get_invocations(self):list:
        pass