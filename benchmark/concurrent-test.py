# from benchmark.provider_openfaas import OpenFaasProvider as of
from benchmarker import Benchmarker as bench
import time
from pprint import pprint
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
        "function_name": 'function2',
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2
        }
    }
]
bench = bench('exp','openfaas','concurrent','/home/thomas/Msc/faas-benchmarker/.test_env')
data_list = bench.invoke_function_conccurrently('function1',0.2,nested,numb_threads=8) 

# for i in data_list:
#     print(i[0])

# data = of.invoke_function('function1')
# print(data)

# data_list = of.invoke_function_conccurrently('function1',numb_threads=16)
# print()
pprint(data_list)
print(len(data_list))
# print()
# single = bench.invoke_function('function1',0.2,nested)
# pprint(single)



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


