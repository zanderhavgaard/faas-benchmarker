import sys
import json
from pprint import pprint
from benchmarker import Benchmarker
import time
from functools import reduce
from datetime import datetime
import traceback
from benchmark.mysql_interface import SQL_Interface as db

# =====================================================================================
# Read cli arguments from calling scriptimport sys
import json
from pprint import pprint
from benchmarker import Benchmarker
import time
from functools import reduce


# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = sys.argv[1]

# name of cloud function provider for this experiment
provider = sys.argv[2]

# name of the client provider
client_provider = sys.argv[3]

# relative path to experiment.env file
env_file_path = sys.argv[4]

# # number of thread to run 
thread_numb = 1
# dev_mode
dev_mode = False
# set optional arguments dev_mode and thread_numb
if(len(sys.argv) > 5):
    try:
        int_val = int(sys.argv[5])
        thread_numb = int_val
        dev_mode = eval(sys.argv[6]) if len(sys.argv) > 6 else False
    except Exception as e:
        dev_mode = eval(sys.argv[5])


# thread_numb = int(sys.argv[5]) if len(sys.argv) > 5 else 1
# print(thread_numb)
# # dev_mode
# dev_mode = eval(sys.argv[6]) if len(sys.argv) > 6 else False
# print(dev_mode)

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment tests the time it takes for
a single function instance to no longer be available due to inactivity.
The experiment is conducted by first invoking a single function 11 times,
the first time to make sure that the function instane is created, the the following
10 times to create a baseline for a 'hot' invocation.
Then the function is invoked continually with increasing delay between invocations,
until the function is a cold start for each invocation with that delay.
This process is then repeated and averaged.
"""
# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode)
# =====================================================================================
# set meta data for experiment
# UUID from experiment

experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3)
fx_num = 1
fx = f'{experiment_name}{fx_num}'
# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(15*60) # more??

# sift away errors at runtime and report them later
errors = []
#======================================================================================
# Convienience methods needed for this experiment 
def get_dict(dict:dict) -> dict:
    root = dict['root_identifier']
    return dict[root]

def invoke():
    if(thread_numb == 1):
        response = get_dict(benchmarker.invoke_function(function_endpoint=fx))
        return response if 'error' not in response else errors.append(response)
    else:
        # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
        invocation_list = [x if 'error' not in x else errors.append(x) for x in map(lambda x: get_dict(x),benchmarker.invoke_function_conccurrently(function_endpoint=fx,numb_threads=thread_numb))]
        # add list of transformed dicts together (only numerical values) and divide with number of responses to get average
        accumulated = dict(map(lambda n: n if (isinstance(n[1],str) or n[1] is None) else (n[0],float(n[1] / len(invocation_list) ) ), 
        reduce(lambda x,y: dict(map(lambda z: z[0] if (isinstance(z[0][1],str) or z[0][1] is None) else (z[0][0],z[0][1]+z[1][1]), zip(x.items(),y.items()))),invocation_list).items()))
    
        return accumulated if accumulated != {} else None

def iterator_wrapper(func,error_point:str,args=None):
    
    
    try:
        for i in range(5):
            val = func(args) if args != None else func()
            if(val != None):
                return val
        raise Exception('No result for: {0} , might not be any connection to providor'.format(error_point))
    except Exception as e:
        print('Ending experiment {0} due to fatal runtime error from iterator_wrapper'.format(experiment_name))
        print(str(datetime.now()))
        print('function type: '+str(type(func)))
        print('function args:',str(args))
        print('Error message: ',str(e))
        print('Trace: {0}'.format(traceback.format_exc()))
        print('----------------------------------------------------------------------')
        benchmarker.end_experiment()

# creates list of invocation dicts.
# args: tuble(x,y) -> x=length_of_list, y=error_point_string
create_invocation_list = lambda x=(5,'create invocation_list'): [iterator_wrapper(invoke,x[1]) for i in range(x[0])]
# calculated the average of specified keys (str1,str2) from a list of dicts
# args: tuble (list,(key1,key2)) -> value of key2 to be subtracked from value of key1
# default behavior, calculate avg startuptime of 5 invocations  
calc_avg_by_keys = lambda args=(create_invocation_list(),('execution_start','invocation_start')): reduce(lambda x,y: x+y, map(lambda x: x[0][x[1][0]]-x[0][x[1][1]],[(x,args[1]) for x in args[0]] ) ) / float(len(args[0]))
# wrapped version of calc_avg_by_key with default values
wrapped_calc_avg_by_keys = lambda x='calc_avg_by_keys', y=('execution_start','invocation_start'), n=5,: iterator_wrapper(calc_avg_by_keys, x, (create_invocation_list((n,x)),y) )        


# =====================================================================================
# The actual logic if the experiment

try:
   
    initial_cold_start_response = iterator_wrapper(invoke,'initial coldtime')
    coldtime = initial_cold_start_response['execution_start']-initial_cold_start_response['invocation_start']
    
    # coldtime is adjusted by 5% to avoid coldtime being an outlier
    benchmark = coldtime * 0.90


    # calculates avg. time for warm function, default is 5 invocations as input
    avg_warmtime = wrapped_calc_avg_by_keys()

    if(dev_mode):
        coldtime += 1.0
        benchmark = coldtime * 0.90
        print('coldtime',coldtime)
        print('benchmark',benchmark)
        print('avg_warmtime',avg_warmtime)

    # sleep for 60 minutes if coldtime is not cold

    if(avg_warmtime > benchmark):
        time.sleep(60 * 60)

    # time to sleep in between invocations, start at 5 minutes
    sleep_time = 300
    # increment for each iteration
    increment = sleep_time
    # granularity of result
    granularity = 10
    # value for last response latency 
    latest_latency_time = avg_warmtime   

    def set_cold_values():
        
        while( increment > granularity ):

            time.sleep(sleep_time)
            result_dict = iterator_wrapper(invoke,'invoking function: {0} from cold start experiment'.format(fx))
            latest_latency_time = result_dict['execution_start'] - result_dict['invocation_start']

            if(latest_latency_time > benchmark):
                db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, True, False) 
                increment /= 2
                sleep_time -= increment
            else:
                db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, False, False)
                sleep_time += increment

    
    set_cold_values()
    # variefy that result is valid by using same sleeptime between invocations 5 times
    for i in range(5):
        time.sleep(sleep_time)
        result_dict = iterator_wrapper(invoke,'invoking function: {0} from validation of cold start experiment'.format(fx))
        latency_time = result_dict['execution_start'] - result_dict['invocation_start']
        # if sleeptime did not result in coldstart adjust values and reset iterations
        if(latency_time < benchmark):
            db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, False, False)
            granularity *= 2
            increment *= 4
            sleep_time += increment
            set_cold_values()
            i = 0
        else:
            db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, True, False)
            
    # sleep for 60 minutes and validate result
    time.sleep(60 * 60)

    result_dict = iterator_wrapper(invoke,'invoking function: {0} from final invocation of cold start experiment'.format(fx))
    latency_time = result_dict['execution_start'] - result_dict['invocation_start']
    if(latency_time < benchmark):
        db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, False, True)
    else:
        db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, True, True)




    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================

except Exception as e:
    # this will print to logfile
    print('Ending experiment {0} due to fatal runtime error'.format(experiment_name))
    print(str(datetime.now()))
    print('Error message: ',str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()

