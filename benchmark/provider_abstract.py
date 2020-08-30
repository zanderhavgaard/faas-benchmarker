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
          
            return future if not parse else [self.parse_data(a,b,c,d,e) for (a,b,c,d,e) in future.result()]
        
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

