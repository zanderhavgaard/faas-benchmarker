
from ssh_query import SSH_query
from experiment import Experiment
from pprint import pprint


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

    def get_most_recent_experiment(self, args: str = '*',flag:bool=True) -> list:
        query = 'select {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        return self.tunnel.retrive_query(query,flag)

  
    def get_most_recent_experiment(self,args:str='*',flag:bool=True): 
        query = 'select {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        return self.tunnel.retrive_query(query,flag)
    
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
