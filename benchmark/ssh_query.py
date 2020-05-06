
import pymysql
import sshtunnel
import paramiko
import numpy as np
import pandas as pd
import os
import subprocess
from sshtunnel import SSHTunnelForwarder
import datetime
import dotenv
import traceback


class SSH_query:
    # set variables for connection to MySql on DB server via ssh tunnel
    def __init__(self, env_file_path: str):
        self.load_env_vars(env_file_path)
        self.ssh_address = (os.getenv('DB_HOSTNAME'),22)

        # comment below lines out if you do not want to use default variable names
        self.ssh_username = 'ubuntu'
        # comment below line in and the line below that out for production
        # self.ssh_pkey = paramiko.RSAKey.from_private_key_file('/home/ubuntu/.ssh/id_rsa')
        self.ssh_pkey = paramiko.RSAKey.from_private_key_file('/home/thomas/Msc/faas-benchmarker/secrets/ssh_keys/db_server')
        self.remote_bind_address = ('127.0.0.1',3306)
        self.db_user = 'root'
        self.db_password = 'faas'
        self.database = 'Benchmarks'
        
        # comment below lines in if you want to load it from environment variables instead of default
        # self.ssh_username = os.getenv('ssh_username')
        # self.ssh_pkey = paramiko.RSAKey.from_private_key_file(os.getenv('ssh_pkey_path'))
        # self.remote_bind_address = (os.getenv('remote_bind_ip'), int(os.getenv('remote_bind_port')))
        # self.db_user = os.getenv('db_user')
        # self.db_password = os.getenv('db_password')
        # self.database = os.getenv('database')

     # load .env file and parse values
    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)
    
    # apply arbitrary many insert queries on MySql 
    def insert_queries(self, queries:list) -> bool:
        # try up 10 times to establish an ssh tunnel
        for x in range(10):
            try:
                with SSHTunnelForwarder(
                    ssh_address=self.ssh_address,
                    ssh_username=self.ssh_username,
                    ssh_private_key=self.ssh_pkey,
                    remote_bind_address=self.remote_bind_address,
                ) as tunnel:
                    try:
                        conn = pymysql.connect(host=self.remote_bind_address[0],
                                               user=self.db_user,
                                               passwd=self.db_password,
                                               db=self.database,
                                               port=tunnel.local_bind_port
                                               )

                        cur = conn.cursor()
                        list_length = len(queries)
                        # iterate over list of queries and execute. Try up to 3 times if exception is thrown
                        for i in range(list_length):
                            for x in range(3):
                                try:
                                    cur.execute(queries[0])
                                    # if query is successful then remove it from list
                                    queries.pop(0)
                                    break
                                
                                except Exception as qe:
                                    if(x == 2):
                                        # if not successful remove query from list and log error message
                                        q = queries.pop(0)
                                        self.write_errorlog(qe,'Sql error with query:',q)
                                        
                        conn.close()
                        tunnel.stop()

                        return True

                    except Exception as ex:
                        if('conn' in locals()):
                            conn.close()
                        # log error message if database connection failed
                        self.write_errorlog(ex,'MySql connection error')


            except Exception as e:
                if(x == 9):
                    # if all 10 atempts failed log error and return False
                    self.write_errorlog(e,"Caught tunnel exception while inserting")
                    return False
                

    def retrive_query(self, query):
        # try up 10 times to establish an ssh tunnel
        for x in range(10):
            try:
                with SSHTunnelForwarder(
                    ssh_address=self.ssh_address,
                    ssh_username=self.ssh_username,
                    ssh_private_key=self.ssh_pkey,
                    remote_bind_address=self.remote_bind_address,
                ) as tunnel:
                    # try query up to 3 times
                    for i in range(3):
                        try:
                            # consider executemany if more complicated queries has to be made
                            conn = pymysql.connect(host=self.remote_bind_address[0],
                                                user=self.db_user,
                                                passwd=self.db_password,
                                                db=self.database,
                                                port=tunnel.local_bind_port
                                                )

                            # retrive and read data
                            data = pd.read_sql_query(query, conn)
                            # convert dataframe to list
                            arr = np.array(data)

                            conn.close()
                            tunnel.stop()

                            return arr

                        except Exception as ex:
                            # log error message if its the third atempt
                            if('conn' in locals()):
                                conn.close()
                            if(i == 2):
                                self.write_errorlog(ex,"Exception caught at remote site while retriving data")
                        
            # log error message if tunnel could not be established within 10 atempts
            except Exception as e:
                if(x == 9):
                    self.write_errorlog(e,'Caught tunnel exception while retriving data')
                    return None
               

    # function for writing wroor messages to ErrorLogFile.txt"
    def write_errorlog(self, ex:Exception, description:str, query:str = None):
       
        # with open("/home/ubuntu/ErrorLogFile.log","a+") as f:
        with open("/home/thomas/ErrorLogFile.log","a+") as f:
            f.write(description+'\n')
            if(query != None):
                f.write(query+'\n')
            f.write(str(datetime.datetime.now()) +'\n' )
            f.write('type: '+ str(type(ex)) +' exception: '+ str(ex) + '\n') 
            f.write("--------------------------\n")
            f.close()