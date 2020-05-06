# from benchmark.provider_openfaas import OpenFaasProvider as of
from benchmarker import Benchmarker as bench
import time
from pprint import pprint
from invocation import Invocation
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



bench = bench('exp','openfaas','test', 'concurrent','/home/thomas/Msc/faas-benchmarker/.test_env')

# bench.log_experiment_running_time()
# print(bench.get_self())

bench.invoke_function('function1','test')
single = bench.experiment.get_invocations()[0]

invo = Invocation('test',single)
pprint(invo.get_data())


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


