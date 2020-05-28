import sys
import uuid
import psutil
import time
from datetime import datetime
# remove for production
from pprint import pprint
from functools import reduce
import function_lib as lib


class Invocation:

    def __init__(self, exp_uuid: str, root: str, data: dict):
        self.exp_id = exp_uuid
        self.root_identifier = root
        # parse data to self
        self.parse_data(data)

    def get_data(self):
        return self.__dict__

    # def is_error(self) -> bool:
    #     return self.is_error

    def dev_print(self):
        pprint(vars(self))  # use get_data

    def parse_data(self, data: dict):
        for i in map(lambda x: setattr(self, x, data[x]), list(data)):
            pass

        # invocation can be either a success or an error, this will be marked
        if('error' in data):
            self.is_error = True

            self.type = lib.str_replace(self.error['type'],[('\'',''),('\"','')]) 
            self.trace = lib.str_replace(self.error['trace'],[('\'',''),('\"','')])
            self.message = lib.str_replace( self.error['message'], [('\'',''),('\"','')])
            delattr(self, 'error')
        else:
            self.is_error = False
            self.execution_total = self.execution_end - self.execution_start
            self.invocation_total = self.invocation_end - self.invocation_start

    def get_query_string(self):
        key_values = self.__dict__.copy()
        is_error = key_values.pop('is_error') 
        list(map(lambda x: x if x[1] != None else key_values.pop(x[0]), key_values.copy().items()))
         
        (keys,vals) = lib.generate_key_value_strings(key_values)
        return """INSERT INTO {0} ({1}) VALUES ({2});""".format('Error' if is_error else 'Invocation', keys, vals)

    
