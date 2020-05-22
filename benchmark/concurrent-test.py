# from benchmark.provider_openfaas import OpenFaasProvider as of
from benchmarker import Benchmarker as bench
import time
from pprint import pprint
from invocation import Invocation
from ssh_query import SSH_query
from mysql_interface import SQL_Interface
from functools import reduce
import pandas as pd
import numpy as np
# import benchmark.provider_abstract as abstract


# of = of('/home/thomas/Msc/faas-benchmarker/.test_env')
# of.test()
nested = [
    {
        "function_name": 'function1',
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 1.0
        }
    }
]


path = '/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.ssh_query_test_env'

# ssh = SSH_query()

db_interface = SQL_Interface()

# db_interface.log_lifetime('experiment_uuid',
#                             'function_id',
#                             2,
#                             4,
#                             'NULL',
#                             12,
#                             False)
# print(db_interface.get_from_table('Function_lifetime',flag=True))
# db_interface.log_coldtime('test','test',10,30,20,True,True)
# db_interface.log_coldtime('test','test',10,30,20,True,False)
# # print()
# print(db_interface.get_from_table('Coldstart',flag=False))

# exp_query = """INSERT INTO Experiment (experiment_meta_identifier,uuid,name,description,cl_provider,cl_client,python_version,cores,memory,start_time,end_time,total_time) Values ('meta','uuid','name','desc','openfaas','client','py',2,8,2.0,3.0,1.0);"""
# db_interface.tunnel.insert_queries([exp_query,"""INSERT INTO Error (exp_id,root_identifier,identifier,function_name,type,trace,message,execution_start,invocation_start) VALUES ('uuid','root','fuckname','name2', 'ValueError','someTrace','message',1,NULL);"""])

# errors = db_interface.get_most_recent_from_table('Error')
# print(errors)
# print()
# df = errors['invocation_start']
# filtered = list(filter(lambda x: not pd.isna(x),df))
# print(filtered)
# print()
# arr = np.array(df)
# print(arr)




# t1 = db_interface.log_coldtime('test2', 'identifier2', 10, 30, 20, True, False)
# print(t1)
# t2 = db_interface.log_coldtime(
#     'test3', 'identifier3', 100, 300, 200, True, True)
# print(t2)
# all_cold = db_interface.get_from_coldtimes(flag=False)
# print('all_cold', all_cold)
# finals = db_interface.get_all_final_coldtimes(flag=False)
# print('finals', finals)
# last2 = db_interface.get_explicit_number_coldstart(number=2, flag=False)
# print('lat2', last2)
# first2 = last2 = db_interface.get_explicit_number_coldstart(
#     number=2, flag=False, order=False)
# print('first2', first2)
# print(db_interface.delete_data_table_Coldstart())

# db_interface.delete_data_table_Experiment()
# db_interface.delete_data_table_Invocation()
# db_interface.delete_data_table_Error()

# print('experiment',db_interface.get_most_recent_experiment(flag=False))
# print()
# print('invocations')
# invocations = db_interface.get_most_recent_invocations(flag=False)
# print('number of invocations',len(invocations))
# pprint(invocations)
# print()
# print('errors',db_interface.get_all_from_Error(flag=False))
# print('all experiments',db_interface.get_all_experiments('id',flag=False))
# print()
# print()

bench1 = bench('exp30','meta','openfaas','foobar', 'testter','/home/thomas/Msc/faas-benchmarker/.test_env')
# bench.invoke_function('function1',invoke_nested=nested)
bench1.invoke_function_conccurrently('function1',numb_threads=8)
# bench.invoke_function('function1',0.0,nested,1.0)
# # bench.invoke_function_conccurrently('function2',throughput_time=0.8,numb_threads=8)
# for i in bench.experiment.get_invocations():
#     print()
#     print(i.get_query_string())
#     print()
# db_interface.log_lifetime('experiment_uuid',
#                             'function_id',
#                             2,
#                             4,
#                             'NULL',
#                             12,
#                             False)
# print(db_interface.get_from_table('Function_lifetime',flag=True))
db_interface.log_coldtime(f'{bench1.experiment.uuid}','test',2,2,20,True,True,True)
# print()


bench1.end_experiment()

#########################

bench2 = bench('exp31','meta','openfaas','foobar', 'tester','/home/thomas/Msc/faas-benchmarker/.test_env')
bench2.invoke_function('function3')
db_interface.log_coldtime(f'{bench2.experiment.uuid}','test',5,30,20,False,True,True)

bench2.end_experiment()

delay = db_interface.get_delay_between_experiment(bench1.experiment.get_cl_provider(),True)
print()
# delay2 = db_interface.get_delay_between_experiment(bench.experiment.get_cl_provider(),False)
# print('delay2',delay2)

cold_bench1 = db_interface.get_coldtime_benchmark(bench1.experiment.get_cl_provider(),threaded=True)
print(cold_bench1)
cold_bench2 = db_interface.get_coldtime_benchmark(bench2.experiment.get_cl_provider())
print(cold_bench2)

# delay = db_interface.get_delay_between_experiment('openfaas')
# print(delay)
# out = db_interface.get_most_recent_experiment(args='uuid,cl_provider',flag=False)
# # print(out)
# # out = list(out)
# print(str(type(out)))
# print(out[0][1])



# print()
# print('UUID: ',bench.experiment.uuid)

# invocations = bench.experiment.get_invocations()
# print('invocations',len(invocations))

# bench.log_experiment_running_time()

# print('experiment',db_interface.get_most_recent_experiment(flag=False))
# print()
# invos = db_interface.get_most_recent_invocations(flag=False)
# print('length',len(invos[0]))
# print('invocations\n',invos)

# print()
# print('errors',db_interface.get_most_recent_errors(flag=False))
# # print('numbered',db_interface.get_explicit_number_experiments('uuid,cores',4, False,False))
# # print('invocation',db_interface.get_explicit_number_invocations('uuid,exp_id',4,False,True))
# print()
# print('4 first errors',db_interface.get_explicit_number_errors('uuid,exp_id',4,False,False))
# print()
# print('4 last errors',db_interface.get_explicit_number_errors('uuid,exp_id',4,False,True))
# print()
# print('cpu effeciency')
# cpu_efficiency = db_interface.cpu_efficiency_last_experiment()
# print('acc',cpu_efficiency[0])
# print('res list',cpu_efficiency[1])
# print('input vals',cpu_efficiency[2])

# # test = reduce(lambda x,y: x+y,cpu_efficiency[2])

# for x in cpu_efficiency[2]:
#     print(x[0])
#     print(x[1])
#     print(x[2])
#     print()

# cpu_efficiencies = db_interface.cpu_efficiency_per_invocation()
# print('cpus',cpu_efficiencies)
# print('cpu efficiency for last experiment',db_interface.cpu_efficiency_last_experiment())
# print()
# cpu_efficiencies_throughputfunction = db_interface.cpu_efficiency_for_throughput_per_invocation()
# print('cpu_throughput',cpu_efficiencies_throughputfunction)
# cpu_throughput_uuid = db_interface.cpu_efficiency_for_throughput_per_invocation(bench.experiment.uuid)
# print('with uuid',cpu_throughput_uuid)
# print('acc',db_interface.cpu_efficiency_for_throughput_experiment())
# print('acc with uuid',db_interface.cpu_efficiency_for_throughput_experiment(bench.experiment.uuid))


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
