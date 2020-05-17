 
import sys
import json
from pprint import pprint
from benchmarker import Benchmarker
import time
from functools import reduce
from datetime import datetime
import traceback
from mysql_interface import SQL_Interface
import function_lib as lib



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
# create database interface for logging results
db = SQL_Interface()
# =====================================================================================
# set meta data for experiment
# UUID from experiment

experiment_uuid = benchmarker.experiment.uuid

# what function to test on (1-3)
fx_num = 2
fx = f'{experiment_name}{fx_num}'
# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(15*60) # more??

# sift away errors at runtime and report them later
errors = []
#======================================================================================
# Convienience methods needed for this experiment 


def invoke():
    if(thread_numb == 1):
        response = lib.get_dict(benchmarker.invoke_function(function_endpoint=fx))
        return response if 'error' not in response else errors.append(response)
    else:
        # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
        invocation_list = filter(None,[x if 'error' not in x else errors.append(x) for x in map(lambda x: lib.get_dict(x),benchmarker.invoke_function_conccurrently(function_endpoint=fx,numb_threads=thread_numb))])
        # add list of transformed dicts together (only numerical values) and divide with number of responses to get average
        accumulated = lib.accumulate_dicts(invocation_list)
    
        return accumulated if accumulated != {} else None

# the wrapper ends the experiment if any it can not return a valid value
err_func = lambda: benchmarker.end_experiment()
# convinience for not having to repeat values
validate = lambda x,y,z=None: lib.iterator_wrapper(x, y, experiment_name, z, err_func)  

        

# creates list of invocation dicts.
# args: tuble(x,y) -> x=length_of_list, y=error_point_string
create_invocation_list = lambda x=(5,'create invocation_list'): [validate(invoke,x[1]) for i in range(x[0])]
# calculated the average of specified keys (str1,str2) from a list of dicts
# args: tuble (list,(key1,key2)) -> value of key2 to be subtracked from value of key1
# default behavior, calculate avg startuptime of 5 invocations  
# calc_avg_by_keys = lambda args=(create_invocation_list(),('execution_start','invocation_start')): reduce(lambda x,y: x+y, map(lambda x: x[0][x[1][0]]-x[0][x[1][1]],[(x,args[1]) for x in args[0]] ) ) / float(len(args[0]))
# wrapped version of calc_avg_by_key with default values
# wrapped_calc_avg_by_keys = lambda x='calc_avg_by_keys', y=('execution_start','invocation_start'), n=5,: iterator_wrapper(calc_avg_by_keys, x, (create_invocation_list((n,x)),y) )        
# 

# =====================================================================================
# The actual logic if the experiment

try:
  
    initial_cold_start_response = validate(invoke,'initial coldtime')
    coldtime = initial_cold_start_response['execution_start']-initial_cold_start_response['invocation_start']
    
    # coldtime is adjusted by 5% to avoid coldtime being an outlier
    benchmark = coldtime * 0.90

    # calculates avg. time for warm function, default is 5 invocations as input and keys execution_start - invocation_start
    # avg_warmtime = lib.wrappped_reduce_dict_by_keys('avg_warmtime', experiment_name, (create_invocation_list,('execution_start','invocation_start')),err_func)
    avg_warmtime = validate(lib.reduce_dict_by_keys,'avg_warmtime',(create_invocation_list,('execution_start','invocation_start')))


    if(dev_mode):
        benchmark = coldtime * 0.98
        # avg_warmtime_list = []
        # for i in range(10):
        #     time.sleep(3)
        #     avg_warmtime_list.append(invoke())
        # acc = 0.0
        # for x in avg_warmtime_list:
        #     print(x['execution_start'])
        #     print(x['invocation_start'])
        #     print(x['execution_start'] - x['invocation_start'])
        #     acc += x['execution_start'] - x['invocation_start']
        #     print()
        # print(acc)
        # avg_warmtime = acc / float(len(avg_warmtime_list))
        # comment below in and above out!!
        # avg_warmtime = calc_avg_by_keys( (avg_warmtime_list ,('execution_start','invocation_start')) )
        avg_warmtime = validate(lib.reduce_dict_by_keys,'avg_warmtime',(create_invocation_list(10,'create invocation_list'),('execution_start','invocation_start')))
        lib.dev_mode_print('Values before any checks -> coldtime xp',[('coldtime',coldtime),('benchmark',benchmark),('avg_warmtime',avg_warmtime)])


    def check_coldtime(sleep:int):
        global benchmark,avg_warmtime,coldtime

        if(avg_warmtime < benchmark):
            return
        elif(sleep > 7200):
            raise Exception('Benchmark could not be established after 2 hours sleep_time')
        else:
            time.sleep(sleep)
            res_dict = validate(invoke,'initial coldtime')
            coldtime = initial_cold_start_response['execution_start']-initial_cold_start_response['invocation_start']
            benchmark = coldtime * 0.90
            avg_warmtime = lib.wrappped_reduce_dict_by_keys('avg_warmtime', experiment_name, (create_invocation_list(),('execution_start','invocation_start')),err_func)
            if(avg_warmtime > benchmark):
                check_coldtime(sleep+1200)

    # sleep for 60 minutes if coldtime is not cold   
    check_coldtime(40*60)
    
    if(dev_mode):
        lib.dev_mode_print('Initial Coldtime ',[('coldtime',coldtime),('benchmark',benchmark),('avg_warmtime',avg_warmtime)])
    
    # time to sleep in between invocations, start at 5 minutes
    sleep_time = 300
    # increment for each iteration
    increment = sleep_time
    # granularity of result
    granularity = 10
    # value for last response latency 
    latest_latency_time = avg_warmtime   

    if(dev_mode):
        lib.dev_mode_print('pre set_cold_values() coldtime exp',[('sleep_time',sleep_time),('increment',increment),('granularity',granularity),('latest_latency_time',latest_latency_time)])

    def set_cold_values():
        global sleep_time,increment,granularity,latest_latency_time
        while( increment > granularity ):
          
            time.sleep(sleep_time)
            result_dict = validate(invoke,'invoking function: {0} from cold start experiment'.format(fx))
            latest_latency_time = result_dict['execution_start'] - result_dict['invocation_start']

            if(latest_latency_time > benchmark):
                increment /= 2
                sleep_time -= increment
            else:
                sleep_time += increment

            if(dev_mode):
                lib.dev_mode_print('logging WARM time coldtime exp',[('experiment_uuid,result_dict[identifier]',experiment_uuid,result_dict['identifier']),
                                                                ('sleep_time / 60',sleep_time / 60), ('sleep_time % 60',sleep_time % 60),
                                                                ('increment*2',increment*2),( 'coldtime',latest_latency_time > benchmark), 
                                                                ('Final result',False),('latest_latency_time',latest_latency_time)])
            else:
                db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, latest_latency_time > benchmark, False)
        # reset increment as last value was never applayed
        increment * 2
    
    set_cold_values()

    if(dev_mode):
        lib.dev_mode_print('pre set_cold_values() coldtime exp',[('sleep_time',sleep_time),('increment',increment),('granularity',granularity),('latest_latency_time',latest_latency_time)])

    # variefy that result is valid by using same sleeptime between invocations 5 times
    for i in range(5):
        time.sleep(sleep_time)
        result_dict = validate(invoke,'invoking function: {0} from validation of cold start experiment'.format(fx))
        latency_time = result_dict['execution_start'] - result_dict['invocation_start']
        # if sleeptime did not result in coldstart adjust values and reset iterations
        if(latency_time < benchmark):
            if(dev_mode):
                validate('logging warm time coldtime exp',[('experiment_uuid,result_dict[identifier]',experiment_uuid,result_dict['identifier']),
                                                                ('sleep_time / 60',sleep_time / 60), ('sleep_time % 60',sleep_time % 60),
                                                                ('increment*2',increment*2),( 'coldtime',False), ('Final result',False)])
            else:    
                db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, False, False)

            granularity *= 2
            increment *= 2
            sleep_time += increment
            set_cold_values()
            i = 0

        else:
            if(dev_mode):
                lib.dev_mode_print('logging warm time coldtime exp',[('experiment_uuid,result_dict[identifier]',experiment_uuid,result_dict['identifier']),
                                                                ('sleep_time / 60',sleep_time / 60), ('sleep_time % 60',sleep_time % 60),
                                                                ('increment*2',increment*2),( 'coldtime',True), ('Final result',False)])
            else:
                db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment*2, True, False)
    
    if(dev_mode):
        lib.dev_mode_print('post set_cold_values() coldtime exp',[('sleep_time',sleep_time),('increment',increment),('granularity',granularity),('latest_latency_time',latest_latency_time)])
        raise Exception('Ending experiment pga dev_mode')


    # sleep for 60 minutes and validate result
    time.sleep(60 * 60)

    result_dict = validate(invoke,'invoking function: {0} from final invocation of cold start experiment'.format(fx))
    latency_time = result_dict['execution_start'] - result_dict['invocation_start']
    # log final result
    db.log_coldtime(experiment_uuid,result_dict['identifier'],sleep_time / 60, sleep_time % 60, increment, latency_time < benchmark, True)
  




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

