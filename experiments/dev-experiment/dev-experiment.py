import sys
import json
import time
from pprint import pprint
from benchmarker import Benchmarker
from mysql_interface import SQL_Interface as database
import function_lib as lib
import uuid
from datetime import datetime


# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = 'test'

# unique identifier string tying this experiment together with the
# experiments conducted for the other cloud providers in this round
experiment_meta_identifier = 'meta'

# name of cloud function provider for this experiment
provider = 'openfaas'

# name of the client provider
client_provider = 'client'

# relative path to experiment.env file
env_file_path = 'somefile'

# dev_mode
dev_mode = True

# verbose mode
verbose = False

if len(sys.argv) > 1:

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

    # verbose mode
    verbose = eval(sys.argv[7]) if len(sys.argv) > 7 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: this experiment tests the implmentation of the benchmarking platform
"""

def create_benchmarker(exp_name:str,desc:str,verbose= False):
    benchmarker = Benchmarker(experiment_name=exp_name,
                          experiment_meta_identifier=experiment_meta_identifier,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=desc,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode,
                          verbose=verbose)
    
    print('=============================================')
    print(f'Experiment {experiment_name}\n')

    return benchmarker


db = database(dev_mode)
# =====================================================================================

def sequential_sanity_check():
    benchmarker = create_benchmarker(experiment_name,'testing linked invocations')
    # name of function to be invoked
    fx_name = 'function'
    sleep_amount = 0.5

    print('invoking with no arguments: ')
    response = benchmarker.invoke_function(f'{fx_name}1')
    pprint(response)
    print()

    print('invoking with sleep argument')
    response = benchmarker.invoke_function(function_name=f'{fx_name}2',
                                        function_args={'sleep':sleep_amount})
    pprint(response)
    print()

    sleep_amount = 0.5

    print('invoking with no arguments: ')
    response = benchmarker.invoke_function(
        function_name="function1"
        )
    pprint(response)
    print()


    print('invoking with sleep argument')
    response = benchmarker.invoke_function(
        function_name="function2"
        )
    pprint(response)
    print()

    print('invoking with 1 second throughput argument: ')
    response = benchmarker.invoke_function(function_name='function3',
                                        function_args= {'throughput_time': 1.0})
    pprint(response)
    print()


    invoke_1_nested = [
        {
            "function_name": f"{experiment_name}-function2",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.1
            }
        }
    ]

    print('invoking function1 with 1 nested invocation')
    response = benchmarker.invoke_function(function_name='function1',
                                        function_args= {'invoke_nested': invoke_1_nested})
    pprint(response)
    print()



    invoke_1_nested = [
        {
            "function_name": f"{experiment_name}-function3",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.1
            }
        }
    ]

    print('invoking function2 with 1 nested invocation')
    response = benchmarker.invoke_function(
        function_name='function2',
        function_args={"invoke_nested":invoke_1_nested}
        )
    pprint(response)
    print()

    invoke_1_nested = [
        {
            "function_name": f"{experiment_name}-function2",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.1
            }
        }
    ]

    print('invoking function3 with 1 nested invocation')
    response = benchmarker.invoke_function(
        function_name='function3',
        function_args={"invoke_nested":invoke_1_nested}
        )
    pprint(response)
    print()

 
    invoke_nested = [
        {
            "function_name": f"{experiment_name}-function2",
            "invoke_payload": {
                "StatusCode": 200,
                "invoke_nested": [
                        {
                        "function_name": f"{experiment_name}-function3",
                        "invoke_payload": {
                            "StatusCode": 200,
                            }
                        },
                        {
                        "function_name": f"{experiment_name}-function3",
                        "invoke_payload": {
                            "StatusCode": 200,
                            }
                        }
                    ]
                }
            }
        ]

    print('invoking with double nested invocation')
    response = benchmarker.invoke_function(
        function_name='function1',
        function_args={"invoke_nested":invoke_nested}
        )
    pprint(response)
    print()

   

    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================

def concurrent_sanity_check():
    
    benchmarker = create_benchmarker(experiment_name, 'run with different thread counts')
    
    response = benchmarker.invoke_function_conccurrently(function_name='function1',numb_threads=1)
    pprint(response)
    print()
   
    response = benchmarker.invoke_function_conccurrently(function_name='function1',numb_threads=2)
    pprint(response)
    print()
   
    response = benchmarker.invoke_function_conccurrently(function_name='function1',numb_threads=3)
    pprint(response)
    print()
    args = {
        'throughput_time': 0.2
    }
    response = benchmarker.invoke_function_conccurrently(function_name='function1',numb_threads=7,function_args=args)
    pprint(response)
    print()
    args['sleep'] = 0.1
    response = benchmarker.invoke_function_conccurrently(function_name='function1',numb_threads=7,function_args=args)
    pprint(response)
    print()

    invoke_1_nested = [
        {
            "function_name": f"{experiment_name}-function2",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.1
            }
        }
    ]

    response = benchmarker.invoke_function_conccurrently(function_name='function1',
                                                        numb_threads=7,
                                                        function_args={'invoke_nested':invoke_1_nested})
    pprint(response)
    print()
    
    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================


def test_monolith():
    benchmarker = create_benchmarker(experiment_name, 'monolith feature test')
    
    args = {
        'args': 8,
        'run_function': 'random',
        'seed': 2,
        }
    response = benchmarker.invoke_function(function_name='monolith',function_args=args)
    pprint(response)
    print()


    args['run_function'] = 'matrix_mult'
    response = benchmarker.invoke_function(function_name='monolith',function_args=args)
    pprint(response)
    print()

    benchmarker.invoke_function_conccurrently(function_name='monolith',numb_threads=6,function_args=args)
    pprint(response)
    print()

   
    f_list = [
            'fib', 
            'isSymmetric', 
            'levelOrder',
            'maxDepth', 
            'levelOrderBottom', 
            'sortedArrayToBST', 
            'zigzagLevelOrder', 
            'sortedListToBST', 
            'isBalanced', 
            'minDepth',
            'flatten', 
            'maxPathSum', 
            'preorderTraversal', 
            'rightSideView', 
            'dummie_webpage', 
            'docker_documentation', 
            'use_arrow', 
            'pandas_numpy', 
            'matrix_mult',
    ]
    for f in f_list:
        args['run_function'] = f
        response = benchmarker.invoke_function(function_name='monolith',function_args=args)
        d = lib.get_dict(response)
        print(f)
        if 'error' in d:
            pprint(d)
    
    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================

# ============================================================

def db_interface_sanity_check():

    print('\nRunning database test')

    db = database(dev_mode)
    benchmarker = create_benchmarker(experiment_name, 'monolith feature test')
    print('invoking with sleep: ')
    response = benchmarker.invoke_function(function_name='function1',function_args={'sleep':0.2})
    pprint(response)
    print()
    print('invoking with sleep=str (error): ')
    response_error = benchmarker.invoke_function(function_name='function1',function_args={'sleep':'0.2'})
    pprint(response_error)
    print()
    print('invoking Monolith ')
    response_error = benchmarker.invoke_function(function_name='monolith',function_args={'seed':8,
                                                                                        'args':12,
                                                                                        'run_function':'random'})
    pprint(response_error)
    print()

    # =====================================================================================
    # end of the experiment
    benchmarker.end_experiment()
    # =====================================================================================
    # for q in benchmarker.experiment.log_experiment()[1]:
    #     print(q)
    print('coldtime check')
    db.log_coldtime(benchmarker.experiment.uuid,
                    lib.get_dict(response)['identifier'],
                    10,
                    10,
                    30,
                    2,
                    1.2,
                    True,
                    False)
    
    db.log_coldtime(benchmarker.experiment.uuid,
                    lib.get_dict(response)['identifier'],
                    10,
                    10,
                    30,
                    1,
                    3.4,
                    True,
                    True)
    
    cold_res = db.get_from_table(table='Coldstart')
    print('Coldtime table results')
    print(cold_res)
    print()

    print('lifetime check')
    db.log_lifetime(benchmarker.experiment.uuid, 
                    lib.get_dict(response)['identifier'], 
                    lib.get_dict(response)['identifier'],
                    10, 
                    25, 
                    12, 
                    12, 
                    True)
    
    lifetime_res = db.get_from_table(table='Function_lifetime')
    print('Function_lifetime table results')
    print(lifetime_res)
    print()

    print('concurrent check')
    db.log_concurrent_result(
                            benchmarker.experiment.uuid,
                            'function1',
                            8,
                            2,
                            1.1,
                            4.0,
                            1.2,
                            0.5,
                            4.0,
                            0.9,
                            1.2,
                            2.2,
                            3.3,
                            3.4,
                            22,
                            4.4,
                            5.5,
                            6.6,
                            7.7) 
    
    concurrent_res = db.get_from_table(table='Cc_bench', args='exp_id,acc_latency')
    print('concurrent table results')
    print(concurrent_res)
    print()

    print('lifecycle check')
    db.log_clfunction_lifecycle(
                                benchmarker.experiment.uuid,
                                'function1',
                                8,
                                10,
                                1.2,
                                3,
                                2,
                                1.2,
                                2.2,
                                2,
                                'some ids',
                                'some more ids')
    
    Function_lifecycle_res = db.get_from_table(table='Function_lifecycle')
    print('Function_lifecycle table results')
    print(Function_lifecycle_res)
    print()


    print('Invocation check')
    print(db.get_from_table(table='Invocation',args='identifier'))
    print()
    print('Error check')
    print(db.get_from_table(table='Error',args='identifier'))
    print()
    print('Monolith check')
    print(db.get_from_table(table='Monolith',args='invo_id'))
    print()


# ============================================================
# run the tests - comment out to leave out
def low_level_conccurent():
    import function_lib as lib
    from functools import reduce
    num_invo = 30
    benchmarker1 = create_benchmarker(experiment_name+str(1), 'run with different thread counts')
    benchmarker2 = create_benchmarker(experiment_name+str(2), 'run with different thread counts')
    benchmarker3 = create_benchmarker(experiment_name+str(3), 'run with different thread counts')
    benchmarker4 = create_benchmarker(experiment_name+str(4), 'run with different thread counts')
    benchmarker5 = create_benchmarker(experiment_name+str(5), 'run with different thread counts')
    start_times = []

    def bench(fx,b):
        ts = time.time()
        response = fx()
        te = time.time()
        start_times.append((ts,te,b))
        print('bench time',te-ts)
    
    def print_dev(args,end=True,pr=False):
       
        (ts,te,benchmarker) = args
        print('futures parsed pre',benchmarker.futures_parsed)
        benchmarker.ensure_futures()
        print('futures parsed post',benchmarker.futures_parsed)
        responses = benchmarker.experiment.get_invocations(dev=True)

        # pprint(res)
        print()
        # responses = list(map(lambda x: lib.get_dict(x),res))
        if pr:
            print('printing responses')
            pprint(responses)
            print()
        # pprint(responses)
        print('running time',datetime.fromtimestamp(te-ts))
        print('length of responselist',len(responses))
        filtered = list(filter(lambda x: 'error' not in x, responses))
        errors = len(responses) - len(filtered)
        filtered = errors if len(filtered) == 0 else filtered
        print('number of errors',errors)
        # latency = lib.reduce_dict_by_keys((list(map(lambda x: lib.get_dict(x),responses)),('execution_start','invocation_start')))
        print()
        latency = list(map(lambda x: x['execution_start']-x['invocation_start'],filtered) ) 
        print('latency',latency)
        avg_latency = reduce(lambda x,y: x+y,latency)/len(latency)
        print('avg latency',datetime.fromtimestamp(avg_latency))
        print()
        invocation_start = list(map(lambda x: x['invocation_start'],filtered))
        print('invocation_start',invocation_start)
        print()
        avg_invo_start = reduce(lambda x,y: x+y, invocation_start) / len(invocation_start)
        print('avg_invocation_start',datetime.fromtimestamp( avg_invo_start))
        print()
        invocation_time_offset = list(map(lambda x: x-ts,invocation_start))
        print('invocation_time_offset',invocation_time_offset)
        print()
        print('avg invocation_time_offset',datetime.fromtimestamp( avg_invo_start - ts))
        print()
        time_from_start = list(map(lambda x: x['invocation_start']-ts,filtered))
        print('time_from_start',time_from_start)
        print()
        avg_time_from_start = reduce(lambda x,y: x+y, time_from_start) / len(time_from_start)
        print('avg_time_from_start',datetime.fromtimestamp(avg_time_from_start))
        print()
        time_to_exc_end = list(map(lambda x: x['execution_end']-ts,filtered))
        print('time_to_exc_end',time_to_exc_end)
        avg_time_to_exc_end = reduce(lambda x,y: x+y, time_to_exc_end) / len(time_to_exc_end)
        print('avg_time_to_exc_end',datetime.fromtimestamp(avg_time_to_exc_end))
        print()
        if end:
            print('ending experiment')
            benchmarker.end_experiment()
        print('----------------------------------------------------')
    
    bench(lambda : benchmarker1.invoke_function_conccurrently(function_name='function1',numb_threads=num_invo,parse=True),benchmarker1)
    bench(lambda : benchmarker2.invoke_function_conccurrently(function_name='function1',numb_threads=num_invo,parse=False),benchmarker2)
    time.sleep(30)
    num_invo = 20
    bench(lambda : benchmarker3.invoke_function_conccurrently(function_name='function1',numb_threads=num_invo,parse=False),benchmarker3)
    time.sleep(30)
    num_invo = 30
    print()
    print('divider')
    print()
    bench(lambda: [benchmarker4.invoke_function('function1') for i in range(num_invo)],benchmarker4)
    time.sleep(60)
    print('start_times')
    for idx,(t,te,b) in enumerate(start_times):
        if idx == 0:
            print('first', t)
        else:
            print('time_between', t-start_times[idx-1][0])

    print()
    
    for idx,x in enumerate(start_times):
        print(f'--------- benchmarker {idx+1} ---------------------')
        print_dev(x,end=True)
    
    print()
    num_invo = 10
    # time.sleep(5)
    # print()
    print('last round')
    start_times = []
    for i in range(5):
        bench(lambda : benchmarker5.invoke_function_conccurrently(function_name='function1',numb_threads=num_invo,parse=False),benchmarker5)
        # if i == 1:
        #     time.sleep(20)
    for idx,(t,te,b) in enumerate(start_times):
        if idx == 0:
            print('first', t)
        else:
            print('time_between', t-start_times[idx-1][0])

    print()
    for idx,x in enumerate(start_times):
        print(f'--------- multi! benchmarker {idx+1} ---------------------')
        print_dev(x,end=False)
        # if i == 0:
        #     benchmarker5.experiment.invocations = []



    # print()
    # print('length of starttime',len(start_times))
    # print('starttimes')
    # for idx,(t,te,b) in enumerate(start_times):
    #     if idx == 0:
    #         print('first', t)
    #     else:
    #         print('time_between', t-start_times[idx-1][0])
    
    # print()
    # time.sleep(20)
    # for idx,x in enumerate(start_times):
    #     print('print_dev for',idx,'!!!!!!!!!!!!!!!!!!!!!!!!!')
    #     print_dev(x,False)
    
    # =====================================================================================
    # end of the experiment
    (a,b,c) = start_times[0]
    c.end_experiment()
    # =====================================================================================

def number_test():
    from functools import reduce

    db = database(dev_mode)
    benchmarker = create_benchmarker('dev-experiment', 'test distrubution of latencies')

    iterations = 100
    response_times = []

    first_res = benchmarker.invoke_function(function_name='function3')
    pprint(first_res)
    print()

    for i in range(iterations):
        t1 = time.time()
        res = lib.get_dict( benchmarker.invoke_function(function_name='function3') )
        t2 = time.time()
        time.sleep(1)
        response_times.append(
            (i, res['execution_start']-res['invocation_start'], t2-t1, res['instance_identifier'])
        )

    response_times.sort(key=lambda x: x[1])

    sliced = response_times[20:80]

    sliced_avg = reduce(lambda x,y: x+y[1],[0.0] + sliced)/len(sliced)

    #  pprint(response_times)

    print('\n','sliced avg',sliced_avg,'\n')

    print('sorted after latency from responses')
    print('index 0 latency:',response_times[0][1],'tuple:',response_times[0])
    print('index 99 latency:',response_times[len(response_times)-1][1],'tuple:',response_times[len(response_times)-1])
    print('avg latency',reduce(lambda x,y: x+y[1],[0.0] + response_times)/iterations)

    benchmarker.end_experiment()
    
sequential_sanity_check()
concurrent_sanity_check()
test_monolith()
db_interface_sanity_check()
number_test()

# only relevant if changes to concurrent implementation is made
# low_level_conccurent()

# db.delete_dev_mode_experiments()

