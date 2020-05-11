# from benchmark.provider_openfaas import OpenFaasProvider as of
from benchmarker import Benchmarker as bench
import time
from pprint import pprint
from invocation import Invocation
from ssh_query import SSH_query
from mysql_interface import SQL_Interface
# import benchmark.provider_abstract as abstract



# of = of('/home/thomas/Msc/faas-benchmarker/.test_env')
# of.test()
nested = [
       {
        "function_name": 'function1',
        "invoke_payload": {
            "StatusCode": 500,
            "sleep": "test"
        }
    }
]


path = '/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.ssh_query_test_env'

ssh = SSH_query()

db_interface = SQL_Interface()

# db_interface.delete_data_table_Experiment()
# db_interface.delete_data_table_Invocation()
# db_interface.delete_data_table_Error()

# print('experiment',db_interface.get_most_recent_experiment(flag=False))
# print()
# print('invocations',db_interface.get_all_from_Invocation(flag=False))
# print()
# print('errors',db_interface.get_all_from_Error(flag=False))
print('all experiments',db_interface.get_all_experiments('id',flag=False))
print()
print()

bench = bench('exp2','openfaas','foobar', 'testter','/home/thomas/Msc/faas-benchmarker/.test_env')
bench.invoke_function('function1',0.0,nested,0.3)
bench.invoke_function('function1',0.0,nested,1.0)
# bench.invoke_function_conccurrently('function2',throughput_time=0.8,numb_threads=8)

print()
print('UUID: ',bench.experiment.uuid)

invocations = bench.experiment.get_invocations()
print('invocations',len(invocations))

bench.log_experiment_running_time()

print('experiment',db_interface.get_most_recent_experiment(flag=False))
print()
invos = db_interface.get_most_recent_invocations(args='function_cores',flag=False)
print('length',len(invos[0]))
print('invocations\n',invos)

print()
print('errors',db_interface.get_most_recent_errors(flag=False))
# print('numbered',db_interface.get_explicit_number_experiments('uuid,cores',4, False,False))
# print('invocation',db_interface.get_explicit_number_invocations('uuid,exp_id',4,False,True))
print()
print('errors asc order',db_interface.get_explicit_number_errors('uuid,exp_id',4,False,False))
print()
print('errors desc order',db_interface.get_explicit_number_errors('uuid,exp_id',4,False,True))

# print('invocations',db_interface.get_all_from_Invocation(flag=False))
# print()
# print('errors',db_interface.get_all_from_Error(flag=False))
# print('newest invocations',db_interface.get_most_recent_invocations(flag=False))
# print()
# all_experiment_vals = db_interface.get_all_from_Experiment(flag=False) 
# print('All Experiments',all_experiment_vals)
# print()
# all_invocations = db_interface.get_all_from_Invocation(flag=False)
# print('All Invocations',all_invocations)
# print()
# all_errors = db_interface.get_all_from_error(flag=False)
# print('All errors',all_errors)
# print()
# experiment_vals = db_interface.get_most_recent_experiment(flag=False)
# print('MOST RECENT EXPERIMENT',experiment_vals)
# print()
# experiment_uuid = db_interface.get_most_recent_experiment('uuid',flag=False)
# print('experiment uuid',experiment_uuid)




