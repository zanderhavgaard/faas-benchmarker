# from ..experiment import Experiment
from ssh_query import SSH_query
from experiment import Experiment
from pprint import pprint


class SQL_Interface:

    def __init__(self, env_path:str):
        self.tunnel = SSH_query(env_path)
        print('hello from db_interface')


    def log_experiment(self,experiment) -> None:
        
        # a tuble of lists, first the query of the experiment, second arbitrary many invocations 
        query_strings = experiment.log_experiment()
        print('logging experiment!!',len(query_strings[1]))
        # print('experiment query: ',query_strings[0])
        # print()
        # pprint(query_strings[1])
        # print()
        # print()
        if(self.tunnel.insert_queries(query_strings[0])):
            was_successful = self.tunnel.insert_queries(query_strings[1])
            print('|----------- INSERTING EXPERIMENT DATA IN DB -----------|')
            print('Experiment with UUID:',experiment.get_uuid(),'successfully inserted data in DB:',was_successful)
            print()
    # consider using other return type then list 
    def get_most_recent_experiment(self,args:str='*') -> list: 
        print('get_most_recent_experiment')
        query = 'select {0} from Experiment where id=(select max(id) from Experiment);'.format(args)
        return self.tunnel.retrive_query(query)
    

    # ----- DEV FUNCTIONS BELOW
    def delete_data_table_Experiment(self):
        print('delete_data_table_Experiment')
        query = 'truncate Experiment;'
        return self.tunnel.retrive_query([query])
    
    def delete_data_table_Invocation(self):
        print('delete_data_table_Invocation')
        query = 'truncate Invocation;'
        return self.tunnel.retrive_query([query])
    
    def delete_data_table_Error(self):
        print('delete_data_table_Error')
        query = 'truncate Error;'
        return self.tunnel.retrive_query([query])
    
    def get_all_from_Experiment(self):
        query ='select * from Experiment;'
        return self.tunnel.retrive_query(query)
    
    def get_all_from_Invocation(self):
        query = 'select * from Invocation;'
        return self.tunnel.retrive_query(query)
    
    
    def get_all_from_error(self):
        query = 'select * from Error;'
        return self.tunnel.retrive_query(query)
   
