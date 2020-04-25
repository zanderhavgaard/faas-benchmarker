# import Abstract Base Class module
# to add abstract class functionality
from abc import ABC, abstractmethod
import multiprocessing as mp
import threading as th
from functools import reduce 
from concurrent import futures
import time


class AbstractProvider(ABC):

    @abstractmethod
    def invoke_function(self, name: str, sleep=0.0, invoke_nested=None):
        pass

    
#   ____                                                      
#  / ___|___  _ __   ___ _   _ _ __ _ __ ___ _ __   ___ _   _ 
# | |   / _ \| '_ \ / __| | | | '__| '__/ _ \ '_ \ / __| | | |
# | |__| (_) | | | | (__| |_| | |  | | |  __/ | | | (__| |_| |
#  \____\___/|_| |_|\___|\__,_|_|  |_|  \___|_| |_|\___|\__, |
#                                                       |___/ 


# auxiliary method for running X number of threads on a core/cpu
    def aux_concurrent(self,invo_args,
                            th_count:int,
                            numb_threads:int, 
                            process_barrier:mp.Barrier,
                            pipe:mp.Pipe):
        
        try:
            # results to be returned
            responses = []
            # threads to be build in advance to ensure all are executed at the same time
            threads = []
            # lock for protection against race  conditions
            lock = th.Lock()
            # threading.barrier for ensuring execution is done simultaneously
            barrier = th.Barrier(numb_threads)
             # ThreadPoolExecutor for executing threads and getting futures in each process
            executor = futures.ThreadPoolExecutor(max_workers=numb_threads)

            # wrapper with barrier is needed to ensure all threads are executed simultaneously
            def thread_wrapper(executor, th_id, thread_args):
                # wait for all threads to have been started
                barrier.wait()
                # call cloud function 
                future = executor.submit(self.invoke_function,thread_args[0])
                result = future.result()

                with lock:
                    # append tuble of thread id and result to responses
                    responses.append((th_id,result))
            
                barrier.wait()

            # build threads and append to threads list
            for i in range(numb_threads):
                thread_args = (executor, (th_count+i), invo_args)
                threads.append(th.Thread(target=thread_wrapper,args=thread_args))
              
            # wait for all proccesses to have build threads
            process_barrier.wait()
            
            # execute threads
            for t in threads:
                t.start()
            # join threads, hence all results will have been appended to responses
            for x in threads:
                t.join()

            
            # return agregated responses
            pipe.send(responses)
            pipe.close()

        except Exception as e:
            print('caught exception in aux of type',type(e),str(e))

    # method for orchastrating threads to processes/cpu's and returning results 
    # TODO refactor to include throughput 
    def invoke_function_conccrently(self,name:str, 
                                        sleep=0.0, 
                                        invoke_nested=None, 
                                        numb_threads=1) -> list:

        print('invoke concurrent called')

        thread_args = (name,sleep,invoke_nested)

        system_cores = mp.cpu_count() 
        threads_per_core = int(numb_threads / system_cores)
        remaining_threads = numb_threads % system_cores

        try:
           
            # barrier to inforce excution is done simultaneously at process level
            mp_barrier = mp.Barrier(system_cores)
            # list of processes to run
            processes = []
            # pipes to recieve return data from (futures)
            recieve_pipes = []
            
            # distribute threads to proccesses 
            id_count = 1
            for i in range(system_cores):
                # number of threads given to the process
                t_numb = threads_per_core
                id_start = id_count
                # pipes to send computed data back
                recieve_pipe, send_pipe = mp.Pipe(False)
                # if threads can be distributed evenly add remaining to first process
                if(remaining_threads != 0 and i == 0):
                    t_numb += remaining_threads
                    id_count += remaining_threads
                # args for concurrent wrapper method
                process_args = (thread_args, id_start, t_numb, mp_barrier, send_pipe)
                # create and add process to list
                processes.append( mp.Process(target=self.aux_concurrent, args=process_args))
                recieve_pipes.append(recieve_pipe)
                id_count += threads_per_core
            
            # run processes concurrently
            for p in processes:
                p.start()

            # join processes
            for p in processes:
                p.join()
        
        # computation is parallelized but recieveing computed results is sequential
            data_list = []
            for x in recieve_pipes:
                data_list.append(x.recv())
                x.close()

            # flatten list of lists
            flatten_list = reduce(lambda x,y: x+y,data_list)

            return flatten_list

        except Exception as e:
            print('caught exception of in concurrent type',type(e),str(e)) 

        

