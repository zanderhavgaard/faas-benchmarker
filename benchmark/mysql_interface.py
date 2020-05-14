
from ssh_query import SSH_query
from experiment import Experiment
from pprint import pprint
import time
from functools import reduce
import pandas as pd
import numpy as np


class SQL_Interface:

    def __init__(self):
        self.tunnel = SSH_query()


    def log_experiment(self,experiment) -> None:
        # a tuble of lists, first the query of the experiment, second arbitrary many invocations 
        query_strings = experiment.log_experiment()
        if(self.tunnel.insert_queries(query_strings[0])):
            was_successful = self.tunnel.insert_queries(query_strings[1])
            print('|------------------------- INSERTING EXPERIMENT DATA IN DB -------------------------|')
            print('Experiment with UUID:', experiment.get_uuid(),
                  'successfully inserted data in DB:', was_successful)
            print()

    # consider using other return type then list

    def get_most_recent_experiment(self, args:str = '*',flag:bool = False) -> list:
        query = 'SELECT {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res
    
    def get_all_experiments(self,args:str = '*', flag:bool=False):
        query = 'SELECT {0} from Experiment;'.format(args)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res
    
    def get_most_recent_invocations(self,args:str = '*', flag:bool = False):  
        query = 'select {0} from Invocation where exp_id=(SELECT uuid from Experiment where id=(select max(id) from Experiment));'.format(args)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res
    
    def get_most_recent_errors(self,args:str = '*', flag:bool = False):  
        query = 'select {0} from Error where exp_id=(SELECT uuid from Experiment where id=(select max(id) from Experiment));'.format(args)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res
    
    def get_explicit_number_experiments(self,args:str= '*', number:int=1, flag:bool= False, order:bool= True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Experiment order by id {1} limit {2};'.format(args,key_word,number)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res

    def get_explicit_number_invocations(self,args:str= '*', number:int=1, flag:bool= False, order:bool= True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Invocation order by execution_start {1} limit {2};'.format(args,key_word,number)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res

    def get_explicit_number_errors(self,args:str= '*', number:int=1, flag:bool= False, order:bool= True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Error order by execution_start {1} limit {2};'.format(args,key_word,number)
        res = self.tunnel.retrive_query(query)
        if(flag):
            res = np.array(res)
        return res

    
    # note that this is not very usefull if invocations are nested
    def cpu_efficiency_last_experiment(self):
        cpu_efficiencies = self.cpu_efficiency_per_invocation()
        return reduce(lambda x,y: x+y,cpu_efficiencies) / float(len(cpu_efficiencies))
    
    # note that this is not very usefull if invocations are nested
    def cpu_efficiency_per_invocation(self):
        # below link for formula
        # https://www.ibm.com/support/knowledgecenter/en/SSVMSD_9.1.4/RTM_faq/rtm_calculating_cpu_efficiency.html
        calc_values = np.array(self.get_most_recent_invocations('process_time,execution_total,function_cores'))
        return [float(x[0])/float(x[1]*x[2]) for x in calc_values]
    
    def cpu_efficiency_for_throughput_per_invocation(self,exp_uuid:str=None):
        exp_id = f"""'{exp_uuid}'""" if exp_uuid != None else '(SELECT uuid from Experiment where id=(select max(id) from Experiment))'
        query = """SELECT throughput_process_time,throughput_running_time,function_cores,throughput_time FROM Invocation 
                   WHERE throughput != 0 AND exp_id={0};""".format(exp_id)
        data = self.tunnel.retrive_query(query)
        return [(float(x[0])/float(x[1]*x[2]),x[3]) for x in data]

    def cpu_efficiency_for_throughput_experiment(self,exp_uuid:str=None):
        data = self.cpu_efficiency_for_throughput_per_invocation(exp_uuid)
        return tuple(i for i in map(lambda x: x / float(len(data)), reduce(lambda x,y: (x[0]+y[0],x[1]+y[1]),data)))
    
    
    def get_all_from_Experiment(self,flag:bool=True):
        query ='select * from Experiment;'
        return self.tunnel.retrive_query(query,flag)
    
    def get_all_from_Invocation(self,flag:bool=True):
        query = 'select * from Invocation;'
        return self.tunnel.retrive_query(query,flag)
    
    def get_all_from_Error(self,flag:bool=True):
        query = 'select * from Error;'
        return self.tunnel.retrive_query(query,flag)
    

    # coldstart experiment specific

    def log_coldtime(self,exp_id:str,
                    invo_id:str,
                    minutes:int,
                    seconds:int,
                    granularity:int,
                    cold:bool=True,
                    final:bool=False):

        query = """INSERT INTO Coldstart (exp_id,invo_id,minutes,seconds,granularity,cold,final) 
                VALUES ({},{},{},{},{},{},{});""".format(exp_id,invo_id,minutes,seconds,granularity,cold,final) 
        return self.



    # ----- DEV FUNCTIONS BELOW

    def delete_data_table_Experiment(self):
        query = 'truncate Experiment;'
        return self.tunnel.insert_queries([query])

    def delete_data_table_Invocation(self):
        query = 'truncate Invocation;'
        return self.tunnel.insert_queries([query])
    
    def delete_data_table_Error(self):
        query = 'truncate Error;'
        return self.tunnel.insert_queries([query])


