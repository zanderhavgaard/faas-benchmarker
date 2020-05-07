import sys
import uuid
import psutil
import time
from datetime import datetime
# remove for production
from pprint import pprint 
from functools import reduce

class Invocation:

    def __init__(self,exp_uuid:str, root:str, data:dict):
        self.exp_id = exp_uuid
        self.root_identifier = root
        # parse data to self
        self.parse_data(data)

    def get_data(self):
        return self.__dict__
    
    def is_error(self) -> bool:
        return self.is_error
    
    def dev_print(self):
        pprint(vars(self)) # use get_data
    
    def parse_data(self,data:dict):
        for i in map(lambda x: setattr(self,x,data[x]) , list(data)):
            pass
    
        # invocation can be either a success or an error, this will be marked
        if('error' in data):
            self.is_error = True
            self.type = self.error['type']
            self.trace = self.error['trace'].replace('\'','*')+'all qoutationmarks have been replaced with *'
            self.message = self.error['message']
            delattr(self,'error')
        else:
            self.is_error = False
            self.execution_total = self.execution_end - self.execution_start
            self.invocation_total = self.invocation_end - self.invocation_start
    
    def get_query_string(self):
        key_values = self.__dict__
        is_error = key_values.pop('is_error')
        # if(is_error):
        #     key_values['trace'] = 'test'
        keys = reduce(lambda x,y: str(x)+','+str(y), key_values.keys()) 
        vals = ''
        for k,v in key_values.items():
            if(isinstance(v,str)):
                vals += """'{0}',""".format(v)
            else:
                vals += str(v)+','
        values = vals[:-1].replace('None', 'NULL') 
       
       
        if(is_error):            
            return 'INSERT INTO Error ({0}) VALUES ({1});'.format(keys,values)
        else:
            return 'INSERT INTO Invocation ({0}) VALUES ({1});'.format(keys,values)

            
    def conver_unix_time(self,time:str):
        datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

    
