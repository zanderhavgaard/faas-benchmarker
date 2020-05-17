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
    
    # def is_error(self) -> bool:
    #     return self.is_error
    
    def dev_print(self):
        pprint(vars(self)) # use get_data
    
    def parse_data(self,data:dict):
        for i in map(lambda x: setattr(self,x,data[x]) , list(data)):
            pass
    
        # invocation can be either a success or an error, this will be marked
        if('error' in data):
            self.is_error = True
            self.type = self.error['type']
            self.trace = self.error['trace'].replace('\'','*')+'all qoutation marks have been replaced with *'
            self.message = self.error['message']
            self.write_errorlog(self.error,self.identifier)
            delattr(self,'error')
        else:
            self.is_error = False
    
    def get_query_string(self):
        key_values = self.__dict__
        is_error = key_values.pop('is_error')
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
    
    def write_errorlog(self, error_dict:dict, id:str):

        with open("/home/ubuntu/ErrorLogFile.log","a+") as f:
        #  with open("/home/thomas/ErrorLogFile.log","a+") as f:

            f.write('An error occurred in a cloud function invocation'+'\n')
            f.write('function UUID: '+id+'\n')
            f.write(str(datetime.now()) + '\n')
            f.write('type: ' + error_dict['type']+'«\n')
            f.write('message: '+error_dict['message']+'\n')
            f.write('trace: '+error_dict['trace']+'\n')
            f.write("--------------------------\n")
            f.close()

    
