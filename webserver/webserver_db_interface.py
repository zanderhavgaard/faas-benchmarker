import pymysql


class DB_interface():

    def __init__(self):
        self.db_host = '127.0.0.1'
        self.db_port = 3306
        self.db_user = 'root'
        self.db_password = 'faas'
        self.database = 'Benchmarks'

    def get_experiments(self) -> list:

        # default value to return if no data is retrieved
        result = "Could not get any data ..."

        query = """select name, experiment_meta_identifier, uuid, start_time, end_time, total_time, cl_provider, cl_client, python_version, cores, memory, invocation_count, dev_mode from Experiment;"""

        try:
            with pymysql.connect(host=self.db_host,
                                 user=self.db_user,
                                 passwd=self.db_password,
                                 db=self.database,
                                 port=self.db_port,
                                 cursorclass=pymysql.cursors.DictCursor
                                 ) as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
        except Exception() as e:
            print('Caught an exception when trying to get experiment data from database:')
            print(e)

        return result
