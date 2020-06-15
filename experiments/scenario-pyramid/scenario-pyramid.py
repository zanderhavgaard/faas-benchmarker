
import sys
import json
import time
from datetime import datetime
import traceback
from benchmarker import Benchmarker
from mysql_interface import SQL_Interface as database
import function_lib as lib
import threading as th
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from functools import reduce

from pprint import pprint

# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = sys.argv[1]

# unique identifier string tying this experiment together with the
# experiments conducted for the other cloud providers in this round
experiment_meta_identifier = sys.argv[2]

# name of cloud function provider for this experiment
provider = sys.argv[3]

# name of the client provider
client_provider = sys.argv[4]

# relative path to experiment.env file
env_file_path = sys.argv[5]

# dev_mode
dev_mode = eval(sys.argv[6]) if len(sys.argv) > 6 else False


# verbose for more prints
verbose = eval(sys.argv[7]) if len(sys.argv) > 7 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment is a simple test of how the platform deals with 
steady increasing load over time. 
"""

# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          experiment_meta_identifier=experiment_meta_identifier,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode,
                          verbose=verbose)
# =====================================================================================
# database interface for logging results if needed
db = database(dev_mode)
# name of table to insert data into - HAVE TO BE SET!!
table = None
# =====================================================================================
# set meta data for experiment
# UUID from experiment
experiment_uuid = benchmarker.experiment.uuid

# =====================================================================================
# meassured time for a function to be cold in a sequantial environment
# default value set to 15 minutes if the experiment has not been run
coldtime = db.get_delay_between_experiment(provider,threaded=True) 
# =====================================================================================

# sleep for 15 minutes to ensure coldstart
if not dev_mode:
    time.sleep(coldtime)  

# results specific gathered and logged from logic of this experiment
results = []

# sift away errors at runtime and report them later
errors = []
# ======================================================================================

# ***************************************************
# * comment below function out and other invoke     *
# * function in if experiment is concurrent invoked *
# ***************************************************
def invoke(fx:str, args:dict= None):
    response = lib.get_dict(
        benchmarker.invoke_function(function_name=fx, function_args=args))
    return response if 'error' not in response else errors.append(response)

def invoke_function_conccurrently(fx:str, thread_numb:int, args:dict= None):

    err_count = len(errors)
    # sift away potential error responses and transform responseformat to list of dicts from list of dict of dicts
    invocations = list(filter(None, [x if 'error' not in x else errors.append(x) for x in map(lambda x: lib.get_dict(x), 
    benchmarker.invoke_function_conccurrently(function_name=fx, numb_threads=thread_numb,function_args=args))]))
   
    return None if invocations == [] else invocations

# parse data that needs to be logged to database.
# can take whatever needed arguments but has to return/append a dict
def append_result(*values_to_log) -> None:
    # key HAS to have same name as column in database
    results.append({
        'exp_id' : experiment_uuid,
        'total_runtime': values_to_log[0],
        'total_invocations': values_to_log[1],
        'total_errors': len(errors),
        'increment': values_to_log[2],
        'peak_invocations': values_to_log[3],
        'functions': values_to_log[4],
        'increment_runtime': values_to_log[5],
        'sleep_time': values_to_log[6],
        'threads_per_invocation': values_to_log[7],
        'invocations_for_increment': values_to_log[8]
        })



# =====================================================================================

try:
    # list to append futures to when executing 
    futures = []

    # this is needed to ensure that all threads have finished when moving to next execution or the experiment is finished
    def get_futures():
        global futures
        print('precheck',len(futures))
        for fu in futures:
            for i in range(10):
                if not fu.done():
                    time.sleep(0.1)
                else:
                    fu.result()
                    break
        futures = reduce(lambda x,y: x+y,map(lambda x: x if isinstance(x,list) else [x],futures))    
        print('check',len(futures))

    # builds and executes pyramid  
    def invoke_pyramid(function_names:list, args:list, increment:int, peak:int, run_time:int):
        # from microbenchmarking it found that the overhead of executing a thread is below time
        avg_tread_time = 0.0016
        # threadpool for executing each invocation as a thread
        pool = ThreadPoolExecutor(peak)

        # aux function to produce new tuple with concurrent execution and new sleeptime
        def set_concurrent(vals:tuple):
            invo_count = vals[0]
            # mod_invo = 0
            thread_numb = 1
            sleep = vals[1]
            while(sleep < 0.05):
                thread_numb += 1
                invo_count = int(vals[0] / thread_numb)
                sleep = vals[2] / invo_count - avg_tread_time
            fxs = [lambda args,fx=f, n=thread_numb: futures.apend(pool.submit(invoke_function_conccurrently,fx,n,args)) for f in function_names] 
            return (vals[2],sleep,fxs,args,thread_numb,vals[0])

        # lambdas for sequantial execution (base case)
        sequantial_functions = [lambda x,fx=f: futures.append(pool.submit(invoke, fx, x)) for f in function_names]

        # set parameters for pyramid
        invo_ascending = [(x+1)*increment for x in range(int(peak / increment))]
        sleep_times = [ (run_time / len(invo_ascending) / x) - avg_tread_time for x in invo_ascending ]
        times = [run_time/len(invo_ascending)]*len(invo_ascending)
        # zip parameters for further use
        zipped = list(zip(invo_ascending,sleep_times,times))
        # map each zipped value to a sequantial or concurrent execution
        mapped = list(map(lambda x: (x[2],x[1],sequantial_functions,args,1,x[0]) if x[1] > 0.05 else \
            set_concurrent(x), zipped))
        # append reversed version of mapped values to the mapped values to finish the pyramid structure
        pyramid_vals = mapped + mapped[:-1][::-1]

        # execute the baseline for 60 seconds
        lib.baseline(run_time=60, sleep_time=0.333-avg_tread_time, functions=sequantial_functions, args=args)
        
        # execute the pyramid
        for (rt,st,fxs,argv,tn,ic) in pyramid_vals:
            lib.baseline(run_time=rt,sleep_time=st,functions=fxs,args=argv)
            if verbose:
                print('meta for pyramid:',run_time,invocation_count,increment,peak)
                print('iteration',rt,st,tn,ic)

        # execute baselien as tail
        lib.baseline(run_time=60, sleep_time=0.333-avg_tread_time, functions=sequantial_functions, args=args)

        get_futures()

        # log metadata for pyramid
        # number of invocations that should ideally have been invoked
        invocation_count = reduce(lambda x,y: x+y, invo_ascending) * 2 - peak
        for (rt,st,fxs,argv,tn,ic) in pyramid_vals:
            append_result(runtime,
                        invocation_count,
                        increment,
                        peak,
                        str(function_names),
                        rt,
                        st,
                        tn,
                        ic)
            
        
        errors = []


    # execute the logic of this experiment
        
    invoke_pyramid(['function1','function2'],[{"throughput_time":0.1}],5,50,60)

    if dev_mode:
        benchmarker.end_experiment()
        lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x, table) for x in results]))

        raise Exception('Ending experiment due to devmode')

    time.sleep(coldtime)
    
    invoke_pyramid(invoke_pyramid(['function1'],[{"throughput_time":0.05}],5,200,300))

    time.sleep(coldtime)

    invoke_pyramid(invoke_pyramid(['function2'],[{"throughput_time":0.05}],5,200,180))

    time.sleep(coldtime)
    
    invoke_pyramid(invoke_pyramid(['function3'],[{"throughput_time":0.05}],5,200,60))

    time.sleep(coldtime)

    invoke_pyramid(invoke_pyramid(['function1'],[{"throughput_time":0.05}],10,1000,300))



  
    

   # =====================================================================================
    # end of the experiment, results are logged to database
    benchmarker.end_experiment()
    # =====================================================================================
    # log experiments specific results, hence results not obtainable from the generic Invocation object
    lib.log_experiment_specifics(experiment_name,
                                experiment_uuid, 
                                len(errors), 
                                db.log_exp_result([lib.dict_to_query(x, table) for x in results]))

except Exception as e:
    # this will print to logfile
    print(f'Ending experiment {experiment_name} due to fatal runtime error')
    print(str(datetime.now()))
    print('Error message: ', str(e))
    print('Trace: {0}'.format(traceback.format_exc()))
    print('-----------------------------------------')
    benchmarker.end_experiment()