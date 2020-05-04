import sys
import uuid
import psutil
import time
from datetime import datetime
# remove for production
from pprint import pprint 

class Invocation:

    def __init__(self,data:dict):
        self.data=data
        self.uuid = str(uuid.uuid())
        parse_data(dict)

    def get_data:
        return self.name
    
    def dev_print(self):
        pprint(vars(self))
    
    def parse_data(self,data:dict):
        pass

    def conver_unix_time(self,time:str):
        datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

    
