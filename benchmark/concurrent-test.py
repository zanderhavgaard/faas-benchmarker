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


# path = '/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.ssh_query_test_env'

# ssh = SSH_query(path)

# db_interface = SQL_Interface()

# db_interface.delete_data_table_Experiment()
# db_interface.delete_data_table_Invocation()
# db_interface.delete_data_table_Error()


bench = bench('exp','openfaas','test', 'concurrent','/home/thomas/Msc/faas-benchmarker/.test_env')

# # bench.log_experiment_running_time()
# # print(bench.get_self())
# bench.invoke_function('function1',0.0,nested)
# print('invocations',len(bench.experiment.get_invocations()))

# bench.log_experiment_running_time()

# # experiment_vals = db_interface.get_most_recent_experiment()
# # print(experiment_vals)
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







# print(bench.experiment.get_experiment_query_string())
# pprint(bench.experiment.log_experiment())


# invocations = bench.experiment.get_invocations()
# # # pprint(invocations)
# # # print()
# # for invo in invocations:
# #     print(invo.get_query_string())
# #     print()


# for x in queries:
#     print('query in loop',x)
#     print()

# val = ssh.insert_queries(queries)
# print(val)
# vals = ssh.retrive_query('select * from Invocation')
# print(vals)
# print()
# # print('length',len(vals))
# vals2 = ssh.retrive_query('select * from Error')
# print(vals2)
# print('---------------------------------------')

# bench.invoke_function_conccurrently('function1',numb_threads=8)
# invocations2 = bench.experiment.get_invocations()

# for invo in invocations2:
#     pprint(invo.get_data())
#     print()

# pprint(single)

# invo = Invocation('test',single)
# pprint(invo.get_data())


# pprint(bench.experiment.get_invocations())
# print()
# pprint(bench.experiment.get_invocations_original_form())
# print()
# print('-------------------------------------------')
# bench.invoke_function_conccurrently('function1',0.2,nested,numb_threads=8) 
# pprint(bench.experiment.get_invocations())
# print()
# pprint(bench.experiment.get_invocations_original_form())
# print()


# for i in data_list:
#     print(i[0])

# data = of.invoke_function('function1')
# print(data)

# data_list = of.invoke_function_conccurrently('function1',numb_threads=16)
# print()
# pprint(data_list)
# print(len(data_list))
# print()
# pprint(single)
# pprint(bench.experiment.get_invocations())



# print()
# for x in data_list:
#     print()
#     val = x[1]
#     # print(val)
#     l = list(val)
#     # print(l)
#     # print()
#     if(l[0] == 'Error' or l[0] == 'Exception'):
#         print_dict(val[l[0]])

# bench.log_experiment_running_time()
# print()
# for y in data_list:
#     print()
#     print(y)
#     print()


# insert into Invocation (exp_id,root_identifier,identifier,function_name,uuid,parent,level,sleep,instance_identifier,python_version,memory,throughput,numb_threads,thread_id,execution_start,execution_end,invocation_start,invocation_end,execution_total,invocation_total) values ('testid','test','test2','func1','uuid','far',0,1.1,'test','3.7',100,12.0,1,1, 2.2, 2.2, 3.3,3.3,4.4,5.5);
