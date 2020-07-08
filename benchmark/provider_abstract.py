# import Abstract Base Class module
# to add abstract class functionality
from abc import ABC, abstractmethod
import multiprocessing as mp
import threading as th
from functools import reduce
from concurrent import futures
import time
from datetime import datetime
from pprint import pprint
import traceback
import aiohttp
import asyncio


class AbstractProvider(ABC):

    def __init__(self):
        self.executor = futures.ThreadPoolExecutor(max_workers=40)
        

    @abstractmethod
    def invoke_function(
            self,
            function_name: str,
            function_args:dict = None,
            aiohttp_session = None
            ) -> dict:
        pass

    def close(self):
        pass
        # asyncio.get_event_loop().close()


#   ____
#  / ___|___  _ __   ___ _   _ _ __ _ __ ___ _ __   ___ _   _
# | |   / _ \| '_ \ / __| | | | '__| '__/ _ \ '_ \ / __| | | |
# | |__| (_) | | | | (__| |_| | |  | | |  __/ | | | (__| |_| |
#  \____\___/|_| |_|\___|\__,_|_|  |_|  \___|_| |_|\___|\__, |
#                                                       |___/



    def invoke_function_conccrently(self, 
                                    function_name: str,
                                    numb_requests:int=1,
                                    function_args:dict= None,
                                    parse:bool = True) -> list:
        try:

            invoke_url = self.get_url(function_name)


            def asyncio_execution(bench, url, numb_requests, function_args):
                

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                tasks = []

                for i in range(numb_requests):
                    tasks.append(asyncio.ensure_future(bench.invoke_wrapper(
                                                url=url,
                                                data=function_args if function_args != None else {}, 
                                                aiohttp_session=aiohttp.ClientSession(),
                                                thread_number=i,
                                                number_of_threads=numb_requests)))
                
                loop.run_until_complete(asyncio.wait(tasks))
                loop.close()

                return [x.result() for x in tasks]
            
            future = self.executor.submit(asyncio_execution, self, invoke_url, numb_requests, function_args)

            return future if not parse else [self.parse_data(a,b,c,d,e) for (a,b,c,d,e) in  future.result()]
        
        except Exception as e:
            self.print_error(function_args,e)

            
    def print_error(self, *args, exception: Exception) -> None:
        if args != None:
            for arg in args:
                print(args)
        print('type:', str(type(exception)))
        print('message: ', str(exception))
        print('-----------------------------------------------------------------')
        print('trace:')
        print(traceback.format_exc())
        print('-----------------------------------------------------------------')

# auxiliary method for running X number of threads on a core/cpu


    # def delegate_to_core(self, 
    #                     function_name:str,
    #                     th_count: int,
    #                     numb_threads: int,
    #                     total_numb_threads: int,
    #                     process_barrier: mp.Barrier,
    #                     pipe: mp.Pipe,
    #                     invo_args:dict=None,) -> list:

    #     # results to be returned
    #     responses = []
    #     # threads to be build in advance to ensure all are executed at the same time
    #     threads = []
    #     # list of expetions to be logged sequentialy at the end, if any
    #     exceptions = []
    #     # lock for protection against race  conditions
    #     lock = th.Lock()

    #     try:
    #         # threading.barrier for ensuring execution is done simultaneously
    #         barrier = th.Barrier(numb_threads)
    #         # ThreadPoolExecutor for executing threads and getting futures in each process
    #         executor = futures.ThreadPoolExecutor(max_workers=numb_threads)

    #         # wrapper with barrier is needed to ensure all threads are executed simultaneously
    #         def thread_wrapper(th_id):
    #             # wait for all threads to have been started
    #             barrier.wait()
    #             try:
    #                 # call cloud function
    #                 future = executor.submit(self.invoke_function, function_name, invo_args)
    #                 result = future.result()
    #                 for identifier in result.keys():
    #                     if(identifier != 'root_identifier'):
    #                         result[identifier]['thread_id'] = th_id
    #                         result[identifier]['numb_threads'] = total_numb_threads

    #                 with lock:
    #                     # append tuble of thread id and result to responses
    #                     responses.append(result)
    #                 # wait for all threads to have delivered responses
    #                 barrier.wait()
    #             except Exception as xe:
    #                 # collect exception for later print to log
    #                 with lock:
    #                     print(traceback.format_exc())
    #                     exceptions.append(('caught exception in thread_wrapper', datetime.now(), 
    #                                         xe, f'one of {th_count}-{th_count+numb_threads-1}'))
                        

    #         # build threads and append to threads list
    #         for i in range(numb_threads):
    #             threads.append(
    #                 th.Thread(target=thread_wrapper, args=[(th_count+i)]))

    #         # wait for all proccesses to have build threads
    #         process_barrier.wait()

    #         # execute threads
    #         for t in threads:
    #             t.start()
    #         # join threads, hence all results will have been appended to responses
    #         for x in threads:
    #             x.join()

    #         # return agregated responses
    #         pipe.send((responses, exceptions))
    #         pipe.close()

    #     except Exception as e:
    #         # atempt to send whatever computed results back to main process + exception
    #         exceptions.append(('caught exception in delegate_to_core', datetime.now(
    #         ), e, f'one of {th_count}-{th_count+numb_threads-1}'))
    #         try:
    #             pipe.send((responses, exceptions))
    #             pipe.close()
    #         except Exception as ex:
    #             # super edge-case that pipe.send() or pipe.close() throws and exception! if so, we print to log.
    #             # exception here might cause main process to deadlock as it will wait for process running on same core
    #             self.print_error('caught exception in delegate_to_core', datetime.now(), e, 
    #                             invo_args, f'on of {th_count}-{th_count+numb_threads-1}', total_numb_threads)


    # # method for orchastrating threads to processes/cpu's and returning results
    # def invoke_function_conccrently(self, function_name: str,
    #                                 numb_threads:int=1,
    #                                 function_args:dict= None) -> list:
        
    #     thread_args = function_args
    #     # find number of cpus that work can be delegated to
    #     system_cores = mp.cpu_count() if mp.cpu_count() < numb_threads else numb_threads
    #     # find number of threads to assign to each core
    #     threads_per_core = int(numb_threads / system_cores)
    #     # find remaining threads if perfect distribution cant be done
    #     remaining_threads = numb_threads % system_cores

    #     # data recieved from processes
    #     data_list = []
    #     # if any exceptions from processes they are agregated on main thread to be
    #     # printed to log sequantialy
    #     exception_list = []

    #     try:

    #         # barrier to inforce excution is done simultaneously at process level
    #         mp_barrier = mp.Barrier(system_cores)
    #         # list of processes to run
    #         processes = []
    #         # pipes to recieve return data from (futures)
    #         recieve_pipes = []

    #         # distribute threads to proccesses
    #         id_count = 1
    #         for i in range(system_cores):
    #             # number of threads given to the process
    #             t_numb = threads_per_core
    #             id_start = id_count
    #             # pipes to send computed data back
    #             recieve_pipe, send_pipe = mp.Pipe(False)
    #             # if threads can be distributed evenly add remaining to first process
    #             if(remaining_threads > 0 ):
    #                 t_numb += remaining_threads
    #                 id_count += remaining_threads
    #                 remaining_threads = 0
    #             # args for concurrent wrapper method
    #             process_args = (function_name, id_start, t_numb, numb_threads, mp_barrier, send_pipe, thread_args)
    #             # create and add process to list
    #             processes.append(mp.Process(target=self.delegate_to_core, args=process_args))
    #             # pup pipe in list to later retrive results
    #             recieve_pipes.append(recieve_pipe)
    #             # adjust count to give each core/cpu right load and thread id's
    #             id_count += threads_per_core

    #         # run processes concurrently
    #         for p in processes:
    #             p.start()


    #         # join processes
    #         for p in processes:
    #             p.join()

    #         # computation is parallelized but recieveing computed results is sequential
    #         for x in recieve_pipes:
    #             try:
    #                 data = x.recv()
    #                 data_list.append(data[0])
    #                 exception_list.append(data[1])
    #                 x.close()
    #             except Exception as eof:
    #                 exception_list.append(
    #                     [('caught exception while recieving from pipe', datetime.now(), eof, 'main')])

    #         # flatten list of lists
    #         flatten_data_list = reduce(lambda x, y: x+y, data_list)
    #         flatten_exception_list = reduce(lambda x, y: x+y, exception_list)
    #         # print all exception, if any, to log
    #         for e in flatten_exception_list:
    #             self.print_error(e[0], e[1], e[2],thread_args, e[3], numb_threads)

    #         return flatten_data_list

    #     except Exception as e:
    #         self.print_error('caught exception in invoke_function_conccrently', datetime.now(),
    #                             e, thread_args, 'main', numb_threads)
    #         return reduce(lambda x, y: x+y, data_list) if len(data_list) > 0 else None

    
            
        

    






    # def invoke_function_conccrently(self, 
    #                                 function_name: str,
    #                                 numb_requests:int=1,
    #                                 function_args:dict= None) -> list:
        

    #     # find number of cpus that work can be delegated to
    #     system_cores = mp.cpu_count() if mp.cpu_count() < numb_requests else 1
    #     # find number of threads to assign to each core
    #     threads_per_core = int(numb_requests / system_cores)
    #     # find remaining threads if perfect distribution cant be done
    #     remaining_threads = numb_requests % system_cores

    #     # data recieved from processes
    #     data_list = []
    #     # if any exceptions from processes they are agregated on main thread to be
    #     # printed to log sequantialy
    #     exception_list = []

    #     if function_args is None:
    #         function_args = {"StatusCode": 200}
    #     else:
    #         function_args["StatusCode"] = 200

    #     try:

    #         # barrier to inforce excution is done simultaneously at process level
    #         mp_barrier = mp.Barrier(system_cores)
    #         # list of processes to run
    #         processes = []
    #         # pipes to recieve return data from (futures)
    #         recieve_pipes = []

    #         # distribute threads to proccesses
    #         id_count = 1
    #         for i in range(system_cores):
    #             # number of threads given to the process
    #             t_numb = threads_per_core
    #             id_start = id_count
    #             # pipes to send computed data back
    #             recieve_pipe, send_pipe = mp.Pipe(False)
    #             # if threads can be distributed evenly add remaining to first process
    #             if(remaining_threads > 0 ):
    #                 t_numb += remaining_threads
    #                 id_count += remaining_threads
    #                 remaining_threads = 0
    #             # args for concurrent wrapper method
    #             process_args = (self.get_url(function_name), id_start, t_numb, numb_requests, mp_barrier, send_pipe, function_args)
    #             # create and add process to list
    #             processes.append(mp.Process(target=self.delegate_to_core, args=process_args))
    #             # pup pipe in list to later retrive results
    #             recieve_pipes.append(recieve_pipe)
    #             # adjust count to give each core/cpu right load and thread id's
    #             id_count += threads_per_core

    #         # run processes concurrently
    #         for p in processes:
    #             p.start()


    #         # join processes
    #         for p in processes:
    #             p.join()

    #         # computation is parallelized but recieveing computed results is sequential
    #         for pip in recieve_pipes:
    #             # try:
    #             data_list.append(pip.recv())
    #             pip.close()
    #             # except Exception as eof:
    #             #     exception_list.append(
    #             #         [('caught exception while recieving from pipe', datetime.now(), eof, 'main')])

    #         # flatten list of lists
    #         flatten_data_list = reduce(lambda x, y: x+y, data_list) if data_list != [] else None
    #         # flatten_exception_list = reduce(lambda x, y: x+y, exception_list)
    #         # # print all exception, if any, to log
    #         # for e in flatten_exception_list:
    #         #     self.print_error(e[0], e[1], e[2],thread_args, e[3], numb_requests,e[4])

    #         return flatten_data_list

    #     except Exception as e:
    #         self.print_error(
    #                         ('caught exception in invoke_function_conccrently', 
    #                         ('timestamp:',datetime.now()),
    #                         (' total_numb_requests', numb_requests),
    #                         ('invo_args',function_args)),
    #                         exception=e)

    #         return reduce(lambda x, y: x+y, data_list) if len(data_list) > 0 else None
    

    # def delegate_to_core(self, 
    #                     invoke_url:str,
    #                     th_count: int,
    #                     numb_requests: int,
    #                     total_numb_requests: int,
    #                     process_barrier: mp.Barrier,
    #                     pipe: mp.Pipe,
    #                     invo_args:dict=None,) -> list:

    #     # results to be returned
    #     results = []
     
    #     try:

    #         tasks = []
    #         ids = []

    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)

    #         for i in range(numb_requests):
    #             tasks.append(asyncio.ensure_future(self.invoke_wrapper(invoke_url,
    #                                         invo_args, 
    #                                         aiohttp.ClientSession())))
    #             ids.append(th_count + i)
        
            
    #     # tasks = [asyncio.ensure_future(self.invoke_wrapper(invoke_url,
    #     #                             function_args, 
    #     #                             aiohttp_session if aiohttp_session != None else aiohttp.ClientSession()))]
    #         process_barrier.wait()
    #         loop.run_until_complete(asyncio.wait(tasks))

    #         try:
    #             results = [self.parse_data(a,b,c) for (a,b,c) in map(lambda x: x.result(), tasks)]
                
    #             for idx,res in enumerate(results):
    #                 for key in res.keys():
    #                     if(key != 'root_identifier'):
    #                         res[key]['numb_threads'] = total_numb_requests
    #                         res[key]['thread_id'] = ids[idx]
    #         except Exception as e:
    #             self.print_error( 
    #                             ('caught exception in delegate_to_core', 
    #                             ('timestamp:',datetime.now()),
    #                             f'on of {th_count}-{th_count+numb_requests-1}',
    #                             (' total_numb_requests', total_numb_requests),
    #                             ('invo_args',invo_args), 
    #                             exx))

    #         loop.close()
    #         # return agregated responses
    #         pipe.send(results)
    #         pipe.close()

    #     except Exception as ex:
    #         # atempt to send whatever computed results back to main process + exception
    #         self.print_error( 
    #                         ('caught exception in delegate_to_core', 
    #                         ('timestamp:',datetime.now()),
    #                         f'on of {th_count}-{th_count+numb_requests-1}',
    #                         (' total_numb_requests', total_numb_requests),
    #                         ('invo_args',invo_args), 
    #                         ex))
    #         try:
    #             pipe.send(results)
    #             pipe.close()
    #         except Exception as exx:
    #             # super edge-case that pipe.send() or pipe.close() throws and exception! if so, we print to log.
    #             # exception here might cause main process to deadlock as it will wait for process running on same core
    #             self.print_error( 
    #                             ('caught exception in delegate_to_core', 
    #                             ('timestamp:',datetime.now()),
    #                             f'on of {th_count}-{th_count+numb_requests-1}',
    #                             (' total_numb_requests', total_numb_requests),
    #                             ('invo_args',invo_args), 
    #                             exx))
                                
