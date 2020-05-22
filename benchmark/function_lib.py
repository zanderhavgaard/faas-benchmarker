from functools import reduce
from datetime import datetime
import traceback
import os


def accumulate_dicts(list_dicts: list):
    return dict(map(lambda n: n if (isinstance(n[1], str) or n[1] is None) else (n[0], float(n[1] / len(list_dicts))),
                    reduce(lambda x, y: dict(map(lambda z: z[0] if (isinstance(z[0][1], str) or z[0][1] is None) else (z[0][0], z[0][1]+z[1][1]), zip(x.items(), y.items()))), list_dicts).items()))

# calculated the average of specified keys (str1,str2) from a list of dicts
# args: tuble (list,(key1,key2)) -> value of key2 to be subtracked from value of key1
def reduce_dict_by_keys(args):
    return reduce(lambda x, y: x+y, map(lambda x: x[0][x[1][0]]-x[0][x[1][1]], [(x, args[1]) for x in args[0]])) / float(len(args[0]))

# wrapped version of reduce_dict_by_keys with default values
# def wrappped_reduce_dict_by_keys(x:str,y:str, z:tuble, err=None):
#     return iterator_wrapper(reduce_dict_by_keys, x, y, z, err)


def get_dict(data: dict) -> dict:
    root = data['root_identifier']
    return data[root]


def iterator_wrapper(func, error_point: str, experiment_name: str, args=None, err_func=None):

    try:
        for i in range(5):
            val = func(args) if args != None else func()
            if(val != None):
                return val
        raise Exception(
            'No result for: {0} , might not be any connection to provider'.format(error_point))
    except Exception as e:
        print('Ending experiment {0} due to fatal runtime error from iterator_wrapper'.format(
            experiment_name))
        print(str(datetime.now()))
        print('function type: '+str(type(func)))
        print('function args:', str(args))
        print('Error message: ', str(e))
        print('Trace: {0}'.format(traceback.format_exc()))
        print('----------------------------------------------------------------------')
        if err_func != None:
            err_func()

# function for writing error messages to ErrorLogFile.txt"
def write_errorlog(self, ex:Exception, description:str, dev_mode, query: str = None):

    path = '/home/docker/shared/ErrorLogFile.log' if not dev_mode else os.environ['fbrd']+'/secrets/ssh_keys/db_server'
    with open(path, "a+") as f:
        f.write(description+'\n')
        if(query != None):
            f.write(query + '\n')
        f.write(str(datetime.datetime.now()) + '\n')
        f.write('type: ' + str(type(ex)) + ' exception: ' + str(ex) + '\n')
        f.write("--------------------------\n")
        f.close()
    


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