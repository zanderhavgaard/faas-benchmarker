
from ssh_query import SSH_query
from experiment import Experiment
from pprint import pprint
import time


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

    def get_most_recent_experiment(self, args:str = '*',flag:bool = True) -> list:
        query = 'SELECT {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        return self.tunnel.retrive_query(query,flag)
    
    def get_all_experiments(self,args:str = '*', flag:bool=True):
        query = 'SELECT {0} from Experiment;'.format(args)
        return self.tunnel.retrive_query(query,flag)
    
    def get_most_recent_invocations(self,args:str = '*', flag:bool = True):  
        query = 'select {0} from Invocation where exp_id=(SELECT uuid from Experiment where id=(select max(id) from Experiment));'.format(args)
        return self.tunnel.retrive_query(query,flag)
    
    def get_most_recent_errors(self,args:str = '*', flag:bool = True):  
        query = 'select {0} from Error where exp_id=(SELECT uuid from Experiment where id=(select max(id) from Experiment));'.format(args)
        return self.tunnel.retrive_query(query,flag)
    
    def get_explicit_number_experiments(self,args:str= '*', number:int=1, flag:bool= True, order:bool= True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Experiment order by id {1} limit {2};'.format(args,key_word,number)
        return self.tunnel.retrive_query(query,flag)
    
    def get_explicit_number_invocations(self,args:str= '*', number:int=1, flag:bool= True, order:bool= True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Invocation order by execution_start {1} limit {2};'.format(args,key_word,number)
        return self.tunnel.retrive_query(query,flag)
    
    def get_explicit_number_errors(self,args:str= '*', number:int=1, flag:bool= True, order:bool= True):
        key_word = 'desc' if order else 'asc'
        query = 'SELECT {0} from Error order by execution_start {1} limit {2};'.format(args,key_word,number)
        return self.tunnel.retrive_query(query,flag)
    
    def cpu_efficiency_lats_experiment(self,falg:bool = True):
        calc:values = self.get_most_recent_invocations()
    
    
    def get_all_from_Experiment(self,flag:bool=True):
        query ='select * from Experiment;'
        return self.tunnel.retrive_query(query,flag)
    
    def get_all_from_Invocation(self,flag:bool=True):
        query = 'select * from Invocation;'
        return self.tunnel.retrive_query(query,flag)
    
    def get_all_from_Error(self,flag:bool=True):
        query = 'select * from Error;'
        return self.tunnel.retrive_query(query,flag)
    




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


