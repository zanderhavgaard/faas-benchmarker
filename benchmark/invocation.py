import sys
import uuid
import psutil
import time
from datetime import datetime
# remove for production
from pprint import pprint 

class Invocation:

    def __init__(self,exp_uuid:str, data:dict):
        self.exp_uuid = exp_uuid
        # parse data to self
        self.parse_data(data)

    def get_data(self):
        return self.__dict__
    
    def is_error(self) -> bool:
        return self.is_error
    
    def dev_print(self):
        pprint(vars(self)) # use get_data
    
    def parse_data(self,data:dict):
        for attr in data.keys():
            if(attr == 'root_identifier'):
                self.root_identifier = data[attr]
            else:
                for i in map(lambda x: setattr(self,x,data[attr][x]) , list(data[attr])):
                    pass
            
                # invocation can be either a success or an error, this will be marked
                if('error' in data[attr]):
                    self.is_error = True
                    # self.type = self.error['']
                else:
                    self.is_error = False
    
    
            

    def conver_unix_time(self,time:str):
        datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

    
