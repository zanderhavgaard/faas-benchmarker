
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


class ssh_query:

    def __init__(self, env_file_path: str):

        self.load_env_vars(env_file_path)

        self.ssh_address = (os.getenv('ssh_address'),
                            int(os.getenv('ssh_port')))
        self.ssh_username = os.getenv('ssh_username')
        self.ssh_pkey = paramiko.RSAKey.from_private_key_file(
            os.getenv('ssh_pkey_path'))
        self.remote_bind_address = (
            os.getenv('remote_bind_ip'), int(os.getenv('remote_bind_port')))
        self.db_user = os.getenv('db_user')
        self.db_password = os.getenv('db_password')
        self.database = os.getenv('database')

     # load .env file and parse values
    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)

    def insert_query(self, query):
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

                        cur.execute(query)

                        conn.close()
                        tunnel.stop()

                        return 0

                    except Exception as ex:
                        if(conn != None):
                            conn.close()
                        print(datetime.datetime.now(), type(ex), str(ex))
                        print(datetime.datetime.now(), 'SQL error!', query)

            except Exception as e:
                if(x == 9):
                    print(datetime.datetime.now(), type(e), str(e))
                    print(datetime.datetime.now(), 'SQL error!', query)
                    return -1
                pass

    def retrive_query(self, query):
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

                        data = pd.read_sql_query(query, conn)

                        arr = np.array(data)

                        conn.close()
                        tunnel.stop()

                        return arr

                    except Exception as ex:
                        if(conn != None):
                            conn.close()
                        print(datetime.datetime.now(), type(ex), str(ex))
                        print(datetime.datetime.now(), 'SQL error!', query)

            except Exception as e:
                if(x == 9):
                    print(datetime.datetime.now(), type(e), str(e))
                    print(datetime.datetime.now(), 'SQL error!', query)
                    return -1
                pass
