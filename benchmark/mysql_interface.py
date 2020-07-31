
from ssh_query import SSH_query
from experiment import Experiment
from pprint import pprint
import time
from functools import reduce
import pandas as pd
import numpy as np


class SQL_Interface:

    def __init__(self, dev_mode: bool = False):
        self.tunnel = SSH_query(dev_mode)

    def log_experiment(self, uuid, queries) -> None:
        # a tuble of lists, first the query of the experiment, second arbitrary many invocations
        (experiment_query, invocation_queries) = queries
       
        if(self.tunnel.insert_queries(experiment_query)):
            was_successful = self.tunnel.insert_queries(invocation_queries)
            print(
                '|------------------------- INSERTING EXPERIMENT DATA IN DB -------------------------|')
            print('Experiment with UUID:', uuid,
                  'successfully inserted data in DB:', was_successful)
            print()

    
    def get_delay_between_experiment(self,provider:str,threaded:bool) -> int:
        query = f"""SELECT minutes,seconds FROM Coldstart WHERE exp_id in \ 
        (SELECT uuid FROM Experiment WHERE cl_provider='{provider}') AND cold=True AND final=True \ 
        AND threads { '> 1' if threaded else '= 1'} ORDER BY id DESC LIMIT 1;"""
        res = np.array(self.tunnel.retrive_query(query)).tolist()
        return res[0][0]*60+res[0][1] if res != [] and res != None else 20 * 60
    
    def get_most_recent_from_table(self, table:str, args: str = '*', flag: bool = True) -> list:
        query = 'SELECT {0} from {1} where exp_id=(select max(id) from Experiment) ORDER BY id DESC LIMIT 1;'.format(args,table)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()


    def get_most_recent_experiment(self, args: str = '*', flag: bool = True) -> list:
        query = 'SELECT {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()


    def get_from_table(self, table:str, args: str = '*', flag: bool = True):
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
    
    def delete_dev_mode_experiments(self):
        query = " DELETE FROM Experiment WHERE dev_mode=True"
        return self.tunnel.insert_queries([query])

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
            'process_time,execution_total,function_cores')).tolist()
        return [float(x[0])/float(x[1]*x[2]) for x in calc_values]

    def cpu_efficiency_for_throughput_per_invocation(self, exp_uuid:str = None):
        exp_id = f"""'{exp_uuid}'""" if exp_uuid != None else '(SELECT uuid from Experiment where id=(select max(id) from Experiment))'
        query = """SELECT throughput_process_time,throughput_running_time,function_cores,throughput_time FROM Invocation 
                   WHERE throughput != 0 AND exp_id={0};""".format(exp_id)
        data = np.array(self.tunnel.retrive_query(query)).tolist()
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

    # ========================================================================================================
    # coldstart experiment specific

    def log_coldtime(self, 
                    exp_id: str,
                    invo_id: str,
                    minutes: int,
                    seconds: int,
                    granularity: int,
                    threads:int=1,
                    benchmark:float=0.0,
                    cold: bool = True,
                    final: bool = False):

        query = """INSERT INTO Coldstart (exp_id,invo_id,minutes,seconds,granularity,threads,benchmark,cold,final) 
                    VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7});""".format(
                    exp_id, invo_id, minutes, seconds, granularity, threads, benchmark, cold, final)
        return self.tunnel.insert_queries([query])

    def get_from_coldtimes(self, args: str = '*', provider:str='', flag: bool = True):
        provider_q = """WHERE exp_id IN (SELECT uuid FROM Experiment WHERE cl_provider='{0}')""".format(provider)
        query = """SELECT {0} FROM Coldstart {1};""".format(args,provider if provider == '' else provider_q)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_all_final_coldtimes(self, args: str = '*', provider:str = '', flag: bool = True):
        provider_q = """AND exp_id IN (SELECT uuid FROM Experiment WHERE cl_provider='{0}')""".format(provider)
        query = """SELECT {0} FROM Coldstart WHERE final=True {1};""".format(args,provider if provider == '' else provider_q)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()

    def get_explicit_number_coldstart(self, args:str = '*', provider:str = '', number:int = 1, flag:bool = False, order:bool = True):
        key_word = 'desc' if order else 'asc'
        provider_q = """WHERE exp_id IN (SELECT uuid FROM Experiment WHERE cl_provider='{0}') AND final=True""".format(provider)
        query = """SELECT {0} from Coldstart {1} order by id {2} limit {3};""".format(args, provider if provider == '' else provider_q, key_word, number)
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()
    
    def get_coldtime_benchmark(self,provider:str,uuid:str=None,threaded:bool=False):
        latest_cold_q = """(SELECT exp_id FROM Coldstart WHERE exp_id IN (SELECT uuid FROM Experiment 
        WHERE cl_provider='{0}') AND multithreaded={1} ORDER BY id DESC LIMIT 1)""".format(provider,threaded)
        query = """SELECT execution_start-invocation_start AS latency FROM Invocation WHERE exp_id={0} 
        ORDER BY id LIMIT 1;""".format(uuid if uuid != None else latest_cold_q)
        res = np.array(self.tunnel.retrive_query(query)).tolist()
        return None if res == [] else res[0][0]
    
    def get_invocations_experiment_type(self,experiment_name, args:str = None, flag: bool = True):
        fields = f"""name,cl_provider,total_time,experiment_uuid, {args}""" if args != None else "*"
        query = f"""SELECT {fields} from (select name, cl_provider, total_time, uuid as experiment_uuid from Experiment 
                where name = '{experiment_name}') x left join Invocation i on i.exp_id=x.experiment_uuid;"""
     
        res = self.tunnel.retrive_query(query)
        return res if flag else np.array(res).tolist()
        


    
    # Function lifetime experiment specific

    def log_lifetime(self,exp_id:str, 
                    instance_identifier:str, 
                    orig_identifier:str,
                    hours:int, 
                    minutes:int, 
                    sec:int, 
                    sleep_time:int, 
                    reclaimed:bool) -> bool:

        query = f"""INSERT INTO Function_lifetime (exp_id, orig_identifier, instance_identifier, hours, minutes, seconds, sleep_time, reclaimed) 
        VALUES ('{exp_id}','{orig_identifier}','{instance_identifier}',{hours},{minutes},{sec},{sleep_time},{reclaimed})"""
        return self.tunnel.insert_queries([query])
    

    # Concurrent-benchmarking experiment specific

    def log_concurrent_result(self,
                            exp_uuid:str,
                            fx:str,
                            thread_numb:int,
                            errors:int,
                            p_time:float,
                            cores:float,
                            success_rate:float,
                            acc_exe_st:float,
                            acc_exe_end:float,
                            acc_invo_st:float,
                            acc_invo_end:float,
                            acc_exe_total:float,
                            acc_invo_total:float,
                            acc_latency:float,
                            acc_throughput:int=0,
                            acc_throughput_time:float= 0.0,
                            acc_throughput_process_time:float= 0.0,
                            acc_throughput_running_time:float= 0.0,
                            sleep_time:float= 0.0):

        query = f"""INSERT INTO Cc_bench (exp_id,function_name,numb_threads,errors,acc_process_time,cores,success_rate,acc_execution_start,
        acc_execution_end,acc_invocation_start,acc_invocation_end,acc_execution_total,acc_invocation_total,acc_latency,acc_throughput,
        acc_throughput_time,acc_throughput_process_time,acc_throughput_running_time,sleep) VALUES ('{exp_uuid}','{fx}',{thread_numb},
        {errors},{p_time},{cores},{success_rate},{acc_exe_st},{acc_exe_end},{acc_invo_st},{acc_invo_end},{acc_exe_total},{acc_invo_total},
        {acc_latency},{acc_throughput},{acc_throughput_time},{acc_throughput_process_time},{acc_throughput_running_time},{sleep_time});"""



        # query = f"""INSERT INTO Cc_bench (exp_id,function_name,numb_threads,sleep,errors,
        #             acc_process_time,cores,success_rate,acc_execution_start,acc_execution_end,acc_invocation_start,
        #             acc_invocation_end,acc_execution_total,acc_invocation_total,acc_latency) 
        #             VALUES ('{0}','{1}',{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16});"""
                    # .format(
                    # exp_uuid,fx,thread_numb,sleep_time,errors,throughput_time,throughput,p_time,cores,success_rate,acc_exe_st,
                    # acc_exe_end,acc_invo_st,acc_invo_end,acc_exe_total,acc_invo_total,acc_latency)
                    
        return self.tunnel.insert_queries([query])

    # track-cloudfunctions-lifecycle experiment specific
    def log_clfunction_lifecycle(self,
                                exp_uuid:str,
                                func_name:str,
                                numb_invokation:int,
                                numb_invocations_orig:int,
                                throughput_time:float,
                                errors:int,
                                unique_instances:int,
                                distribution:float,
                                error_dist:float,
                                diff_from_first:int,
                                identifiers:str,
                                repeats_from_orig:str):
        query = f"""INSERT INTO Function_lifecycle (exp_id,function_name,numb_invokations,numb_invocations_orig,throughput_time,errors,
        unique_instances,distribution,error_dist,diff_from_orig,identifiers,repeats_from_orig) VALUES ('{exp_uuid}','{func_name}',{numb_invokation},{numb_invocations_orig},
        {throughput_time},{errors},{unique_instances},{distribution},{error_dist},{diff_from_first},'{identifiers}','{repeats_from_orig}');"""
        
        # .format(
        # exp_uuid,func_name,numb_invokation,throughput_time,errors,unique_instances,distribution,error_dist,diif_from_first,identifiers)
        return self.tunnel.insert_queries([query])
    
    def log_exp_result(self,results:list) -> bool:
        return self.tunnel.insert_queries(results)
        

    # ----- DEV FUNCTIONS BELOW

    def delete_data_table(self, table_name: str):
        query = """truncate {table_name};""".format(0)
        return self.tunnel.insert_queries([query])

   
