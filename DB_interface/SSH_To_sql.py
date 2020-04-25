
import pymysql 
import sshtunnel
import paramiko
# from paramiko import SSHClient
import numpy as np
import pandas as pd
import os
from os.path import expanduser
import subprocess 
from sshtunnel import SSHTunnelForwarder


class SQL_Interface:


    def __init__(self):
        # TODO set variables from environment in a more clever way
        self.ssh_address=('134.209.237.37',22)
        self.ssh_username='root'
        self.ssh_pkey=paramiko.RSAKey.from_private_key_file(expanduser('~')+
        '/Msc/faas-benchmarker/secrets/ssh_keys/db_server') #if key is password protected add password as second argument
        self.remote_bind_address=('127.0.0.1',3306)
        self.db_user = 'root'
        self.db_password = 'faas'
        self.database = 'Benchmarks'


    def query_via_ssh(self,query:str):  
        try:
            with SSHTunnelForwarder(
                ssh_address=self.ssh_address,
                ssh_username=self.ssh_username,
                ssh_private_key=self.ssh_pkey,
                remote_bind_address=self.remote_bind_address,
                ) as tunnel:
     
                try:     
                        #   docker_ip = self.remote_bind_address[0]
                    docker_ip = subprocess.run(["""docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' DB"""], 
                                                stdout=subprocess.PIPE,shell=True)
                    ip_cleaned = docker_ip.stdout.decode('utf-8').strip()
                
                    conn = pymysql.connect(host=ip_cleaned, 
                                        user='root',
                                        passwd=self.db_password, 
                                        db=self.database,
                                        port=self.remote_bind_address[1]
                                        )
                    data = pd.read_sql_query(query, conn)
                   
                    arr = np.array(data)

                    return arr # or data for <class 'pandas.core.frame.DataFrame'>

                except Exception as e:
                    return None

        except Exception as e:
            return None
        finally:
            conn.close()
            tunnel.close()
                    
                
 