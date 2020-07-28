from functools import reduce
from datetime import datetime
import traceback
import function_lib as lib
import os
from os.path import expanduser
import time
import sys
from pprint import pprint


def accumulate_dicts(list_dicts: list):
    return dict(map(lambda n: n if (isinstance(n[1], str) or n[1] is None) else (n[0], float(n[1] / len(list_dicts))),
                    reduce(lambda x, y: dict(map(lambda z: z[0] if (isinstance(z[0][1], str) or z[0][1] is None) \
                        else (z[0][0], z[0][1]+z[1][1]), zip(x.items(), y.items()))), list_dicts).items())) \
                if list(filter(None,list_dicts)) != [] else {}

# calculated the average of specified keys (str1,str2) from a list of dicts
# args: tuble (list,(key1,key2)) -> value of key2 to be subtracked from value of key1
def reduce_dict_by_keys(args):
    return reduce(lambda x, y: x+y, map(lambda x: x[0][x[1][0]]-x[0][x[1][1]], [(x, args[1]) for x in args[0]])) / float(len(args[0]))

# wrapped version of reduce_dict_by_keys with default values
# def wrappped_reduce_dict_by_keys(x:str,y:str, z:tuble, err=None):
#     return iterator_wrapper(reduce_dict_by_keys, x, y, z, err)

def flatten_list(acc, args:list):
    return reduce(lambda x,y: x+y,[acc]+args)

def get_dict(data: dict) -> dict:
    root = data['root_identifier']
    return data[root]


def iterator_wrapper(func, error_point:str, experiment_name: str, args=None, err_func=None):
  
    try:
        # breakpoint()
        for i in range(5):
            val = func(args) if args != None else func()
            if(list(filter(None, [val])) != []):
                return val
        raise Exception(
            f'No result for: {error_point} , might not be any connection to provider')
    except Exception as e:
        print(f'Ending experiment {experiment_name} due to fatal runtime error from iterator_wrapper')
        print(str(datetime.now()))
        print('function type: '+str(type(func)))
        print('function args:', str(args))
        print('Error message: ', str(e))
        print(f'Trace: {traceback.format_exc()}')
        print('----------------------------------------------------------------------')
        if err_func != None:
            err_func()
        sys.exit()

# function for writing error messages to ErrorLogFile.txt"
def write_errorlog(ex:Exception, description:str, dev_mode:bool, query: str = None):
    path = '/home/docker/shared/ErrorLogFile.log' if not dev_mode else expanduser("~")+'/ErrorLogFile.log'
    with open(path, "a+") as f:
        f.write(description+'\n')
        if(query != None):
            f.write(query + '\n')
        f.write(str(datetime.now()) + '\n')
        f.write('type: ' + str(type(ex)) + ' exception: ' + str(ex) + '\n')
        f.write("--------------------------\n")
    return True
    
# print function for development purpose
def dev_mode_print(context: str, values: list):
    print('--------------------------------------------')
    print('Context: ', context)
    for i in values:
        print(i)
    print('--------------------------------------------')

def convert_unix_time(self, time: str):
        datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')

def str_replace(text:str, pat:list)-> str:
    for (c,p) in pat:
        text = text.replace(c,p)
    return text

def generate_key_value_strings(dict:dict):
    (key_string,value_string) = reduce(lambda x,y: ( f'{x[0]}{y[0]},', f'{x[1]}{y[1]},') if not isinstance(y[1],str) 
                                    else ( f'{x[0]}{y[0]},', f"""{x[1]}'{y[1]}',""") ,[('','')] + list(dict.items()))
    return (key_string[:-1],value_string[:-1])

def dict_to_query(dict:dict,table:str) -> str:
    (keys,values) = lib.generate_key_value_strings(dict)
    return f"""INSERT INTO {table} ({keys}) VALUES ({values});"""

# print metadata about experiment database insertion to logfile 
def log_experiment_specifics(exp_name:str, uuid:str, err:int, db_check:bool=True):
   
    print('=======================================================================')
    print(f'Experiment: {exp_name} with UUID: {uuid} has ended with {err} errors.')
    print(f'Results from experiments has been succesfully added to database: {db_check}')
    print('=======================================================================\n')

# ============================================================================================
# scenario testing

def baseline(run_time:int, 
            sleep_time:float, 
            functions:list, 
            args:list, 
            special_func= None,
            special_args= None,
            dist:float= None,
            ):
    try: 
        starttime = time.time()
        invocation_count = 0

        while(run_time > time.time() - starttime ):
            if(dist != None and invocation_count % dist == dist-1 and special_func != None):
                special_func(special_args)
            else:
                functions[invocation_count % len(functions)](args[invocation_count % len(args)])
            invocation_count += 1
            time.sleep(sleep_time)
    except Exception as e:
        print(f'Error in baseline function')
        print(str(datetime.now()))
        print('function args:', str(args))
        print('Error message: ', str(e))
        print(f'Trace: {traceback.format_exc()}')
        print('----------------------------------------------------------------------')

  

def invocation_pattern(iterations:int, 
                        functions:list, 
                        args:list,  
                        sleep_time:int = None):

    for i in range(iterations):
        for idx,func in enumerate(functions):
            func(args[idx % len(args)])

# aux functions
def exponential_list(start:int, n:int, reverse:bool=False):
    result = [start]
    for i in range(n):
        result.appen(result[i]*2)
    return result if not reverse else result[::-1]

def increment_list(start:int, increment:int, n:int, reverse:bool=False):
    result = [start]
    for i in range(n):
        result.append(result[i]+increment)
    return result if not reverse else result[::-1]

def range_list(low_bound:int, increment:int, upper_bound:int, reverse:bool=False):
    result = [low_bound]
    count = low_bound
    while(True):
        count += increment
        if(count > upper_bound):
            break
        else:
            result.append(count)    
    return result if not reverse else result[::-1]
