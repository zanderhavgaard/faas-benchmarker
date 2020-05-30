import sys
import json
import time
from datetime import datetime
import traceback
from benchmarker import Benchmarker
from mysql_interface import SQL_Interface as database
import function_lib as lib
from pprint import pprint
import os




# unique identifier string tying this experiment together with the
# experiments conducted for the other cloud providers in this round
experiment_meta_identifier = sys.argv[1]

# name of cloud function provider for this experiment
provider = sys.argv[2]

# name of the client provider
client_provider = sys.argv[3]

# relative path to experiment.env file
env_file_path = sys.argv[4]




def create_benchmarker(experiment_name:str,description:str):
    benchmarker = Benchmarker(experiment_name=experiment_name,
                            experiment_meta_identifier=experiment_meta_identifier,
                            provider=provider,
                            client_provider=client_provider,
                            experiment_description=description,
                            env_file_path=env_file_path,
                            dev_mode=True,
                            verbose=False)
    
    print('=============================================')
    print(f'Experiment {experiment_name}\n')

    return benchmarker


db = database(True)

# ======================================================
# coldstart experiment test
# ======================================================
coldstart_results = []

coldstart_benchmarker = create_benchmarker('coldstart','coldstart-test')

response = coldstart_benchmarker.invoke_function('function1')
pprint(response)
response1 = lib.get_dict(response)
response2 = lib.get_dict(coldstart_benchmarker.invoke_function('function1'))

coldstart_results.append({
        'exp_id': coldstart_benchmarker.experiment.uuid,
        'invo_id': response1['identifier'],
        'minutes': 10,
        'seconds': 15,
        'granularity': 20,
        'multithreaded':False,
        'cold': False,
        'final': False
        })

coldstart_results.append({
        'exp_id': coldstart_benchmarker.experiment.uuid,
        'invo_id': response2['identifier'],
        'minutes': 11,
        'seconds': 10,
        'granularity': 30,
        'multithreaded':False,
        'cold': True,
        'final': True
        })

coldstart_benchmarker.end_experiment()

queries = [lib.dict_to_query(x, 'Coldstart') for x in coldstart_results]
pprint(queries)
lib.log_experiment_specifics(
    coldstart_benchmarker.experiment.name,
    coldstart_benchmarker.experiment.uuid,
    0,
    db.log_exp_result(queries))

print('queries:')
print(coldstart_benchmarker.experiment.get_experiment_query_string())
print()
print(lib.dict_to_query(coldstart_results[0],'Coldstart'))
print(lib.dict_to_query(coldstart_results[1],'Coldstart'))
print()
uuids = db.get_most_recent_from_table(table='Coldstart', args='invo_id', flag=False)
pprint(uuids)

# ======================================================
# concurrent coldstart experiment test
# ======================================================

# coldstart_threaded_results = []

# coldstart_threaded_benchmarker = create_benchmarker('coldstart threaded','coldstartthreaded--test')

# multi_response1 = [lib.get_dict(x) for x in coldstart_threaded_benchmarker.invoke_function_conccurrently(function_endpoint='function2', numb_threads=8,throughput_time=0.1)]
# multi_response2 = [lib.get_dict(x) for x in coldstart_threaded_benchmarker.invoke_function_conccurrently(function_endpoint='function2', numb_threads=8,throughput_time=0.1)]
# acc_multi_response1 = lib.accumulate_dicts(multi_response1)
# acc_multi_response2 = lib.accumulate_dicts(multi_response2)

# coldstart_threaded_results.append({
#         'exp_id': coldstart_threaded_benchmarker.experiment.uuid,
#         'invo_id': acc_multi_response1['identifier'],
#         'minutes': 15,
#         'seconds': 15,
#         'granularity': 40,
#         'multithreaded':True,
#         'cold': False,
#         'final': False
#         })

# coldstart_threaded_results.append({
#         'exp_id': coldstart_threaded_benchmarker.experiment.uuid,
#         'invo_id': acc_multi_response2['identifier'],
#         'minutes': 14,
#         'seconds': 10,
#         'granularity': 40,
#         'multithreaded':True,
#         'cold': True,
#         'final': True
#         })

# coldstart_benchmarker.end_experiment()

# lib.log_experiment_specifics(
#     coldstart_benchmarker.experiment.name,
#     coldstart_benchmarker.experiment.uuid,
#     0,
#     db.log_exp_result([lib.dict_to_query(x, 'Coldstart') for x in coldstart_threaded_results]))

# print('queries:')
# print(coldstart_benchmarker.experiment.get_experiment_query_string())
# print()
# print(lib.dict_to_query(coldstart_threaded_results[0],'Coldstart'))
# print(lib.dict_to_query(coldstart_threaded_results[1],'Coldstart'))