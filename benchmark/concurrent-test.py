# from benchmark.provider_openfaas import OpenFaasProvider as of
from benchmarker import Benchmarker as bench
import time
from pprint import pprint
from invocation import Invocation
from ssh_query import SSH_query
# import benchmark.provider_abstract as abstract

def print_dict(d:dict):
    for key, value in d.items():
        if isinstance(value,dict):
            print(key,'-> dict')
            print_dict(value)
        else:
            print(key, '->', value)

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



bench = bench('exp','openfaas','test', 'concurrent','/home/thomas/Msc/faas-benchmarker/.test_env')

# bench.log_experiment_running_time()
# print(bench.get_self())
bench.invoke_function('function1',0.0,nested)

invocations = bench.experiment.get_invocations()
# # pprint(invocations)
# # print()
# for invo in invocations:
#     print(invo.get_query_string())
#     print()
path = '/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.ssh_query_test_env'

ssh = SSH_query(path)

queries = ['truncate Error','truncate Invocation']+[i.get_query_string() for i in invocations]
print()
for x in queries:
    print('query in loop',x)
    print()

val = ssh.insert_queries(queries)
print(val)
vals = ssh.retrive_query('select * from Invocation')
print(vals)
print()
# print('length',len(vals))
vals2 = ssh.retrive_query('select * from Error')
print(vals2)
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
