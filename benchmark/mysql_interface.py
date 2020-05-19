
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

    def log_experiment(self, experiment) -> None:
        # a tuble of lists, first the query of the experiment, second arbitrary many invocations
        query_strings = experiment.log_experiment()
        if(self.tunnel.insert_queries(query_strings[0])):
            was_successful = self.tunnel.insert_queries(query_strings[1])
            print(
                '|------------------------- INSERTING EXPERIMENT DATA IN DB -------------------------|')
            print('Experiment with UUID:', experiment.get_uuid(),
                  'successfully inserted data in DB:', was_successful)
            print()

    
    def get_delay_between_experiment(self,provider:str) -> int:
        query = """SELECT minutes,seconds FROM Coldstart WHERE exp_id in 
        (SELECT uuid FROM Experiment WHERE cl_provider='{0}') AND cold=True AND final=True 
        ORDER BY id DESC LIMIT 1;""".format(provider)
        res = np.array(self.tunnel.retrive_query(query)).tolist()
        return None if res == [] else res[0][0]*60+res[0][1]


    def get_most_recent_experiment(self, args: str = '*', flag: bool = True) -> list:
        query = 'SELECT {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_from_table(self, table:str, args: str = '*', flag: bool = False):
        query = 'SELECT {0} from {1};'.format(args,table)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_most_recent_invocations(self, args: str = '*', flag: bool = False):
        query = 'select {0} from Invocation where exp_id=(SELECT uuid from Experiment where id=(select max(id) from Experiment));'.format(
            args)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_most_recent_from_table(self, table:str, args: str = '*', flag: bool = True):
        query = """select {0} from {1} where exp_id=(SELECT uuid from Experiment 
        where id=(select max(id) from Experiment));""".format(args,table)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_explicit_number_experiments(self, args: str = '*', number: int = 1, flag: bool = False, order: bool = True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Experiment order by id {1} limit {2};'.format(args, key_word, number)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_explicit_number_invocations(self, args: str = '*', number: int = 1, flag: bool = False, order: bool = True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Invocation order by execution_start {1} limit {2};'.format(
            args, key_word, number)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_explicit_number_errors(self, args: str = '*', number: int = 1, flag: bool = False, order: bool = True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Error order by execution_start {1} limit {2};'.format(
            args, key_word, number)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    # note that this is not very usefull if invocations are nested

    def cpu_efficiency_last_experiment(self) -> float:
        cpu_efficiencies = self.cpu_efficiency_per_invocation()
        return reduce(lambda x, y: x+y, cpu_efficiencies) / float(len(cpu_efficiencies))

    # note that this is not very usefull if invocations are nested
    def cpu_efficiency_per_invocation(self) -> list:
        # below link for formula
        # https://www.ibm.com/support/knowledgecenter/en/SSVMSD_9.1.4/RTM_faq/rtm_calculating_cpu_efficiency.html
        calc_values = np.array(self.get_most_recent_invocations(
            'process_time,execution_total,function_cores'))
        return [float(x[0])/float(x[1]*x[2]) for x in calc_values]

    def cpu_efficiency_for_throughput_per_invocation(self, exp_uuid:str = None):
        exp_id = f"""'{exp_uuid}'""" if exp_uuid != None else '(SELECT uuid from Experiment where id=(select max(id) from Experiment))'
        query = """SELECT throughput_process_time,throughput_running_time,function_cores,throughput_time FROM Invocation 
                   WHERE throughput != 0 AND exp_id={0};""".format(exp_id)
        data = self.tunnel.retrive_query(query)
        return [(float(x[0])/float(x[1]*x[2]), x[3]) for x in data]

    def cpu_efficiency_for_throughput_experiment(self, exp_uuid: str = None):
        data = self.cpu_efficiency_for_throughput_per_invocation(exp_uuid)
        return tuple(i for i in map(lambda x: x / float(len(data)), reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]), data)))

    def get_all_from_Experiment(self, flag: bool = True):
        query = 'select * from Experiment;'
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_all_from_Invocation(self, flag: bool = True):
        query = 'select * from Invocation;'
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_all_from_Error(self, flag: bool = True):
        query = 'select * from Error;'
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    # coldstart experiment specific

    def log_coldtime(self, 
                    exp_id: str,
                    invo_id: str,
                    minutes: int,
                    seconds: int,
                    granularity: int,
                    cold: bool = True,
                    final: bool = False):

        query = """INSERT INTO Coldstart (exp_id,invo_id,minutes,seconds,granularity,cold,final) 
                VALUES ('{}','{}',{},{},{},{},{});""".format(exp_id, invo_id, minutes, seconds, granularity, cold, final)
        return self.tunnel.insert_queries([query])

    def get_from_coldtimes(self, args: str = '*', provider:str='', flag: bool = True):
        providor_q = """WHERE exp_id IN (SELECT uuid FROM Experiment WHERE cl_provider='{0}')""".format(provider)
        query = """SELECT {0} FROM Coldstart {1};""".format(args,provider if provider == '' else providor_q)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_all_final_coldtimes(self, args: str = '*', provider:str = '', flag: bool = True):
        providor_q = """AND exp_id IN (SELECT uuid FROM Experiment WHERE cl_provider='{0}')""".format(provider)
        query = """SELECT {0} FROM Coldstart WHERE final=True {1};""".format(args,provider if provider == '' else providor_q)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_explicit_number_coldstart(self, args:str = '*', provider:str = '', number:int = 1, flag:bool = False, order:bool = True):
        key_word = 'desc' if order else 'asc'
        providor_q = """WHERE exp_id IN (SELECT uuid FROM Experiment WHERE cl_provider='{0}') AND final=True""".format(provider)
        query = """SELECT {0} from Coldstart {1} order by id {2} limit {3};""".format(args, provider if provider == '' else providor_q, key_word, number)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()
    
    # Function lifetime experiment specific

    def log_lifetime(self,exp_id:str, instance_identifier:str, hours:int, minutes:int, sec:int, sleep_time:int, reclaimed:bool) -> bool:
        query = """INSERT INTO Function_lifetime (exp_id,instance_identifier,hours,minutes,seconds,sleep_time,reclaimed) 
        VALUES ('{0}','{1}',{2},{3},{4},{5},{6});""".format(exp_id,instance_identifier,hours,minutes,sec,sleep_time,reclaimed)
        return self.tunnel.insert_queries([query])
    

    

    # ----- DEV FUNCTIONS BELOW

    def delete_data_table(self, table_name: str):
        query = """truncate {table_name};""".format(0)
        return self.tunnel.insert_queries([query])

   
