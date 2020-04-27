import mysql.connector as mysql

class SQL_Interface:

    def __init__(self):
        self.host = 'localhost:5000/'
        self.user = 'faas'
        self.password = 'faas'
        self.database = 'Benchmarks'

    def insert_query(self, query:str, values:tuple=None):
        connection = mysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                database=self.database
        )
        try:
            cur = connection.cursor()
            if values is None:
                cur.execute(query)
            else:
                cur.execute(query, values)
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print('Caught an exception while executing query ...', str(e))
            return False
    
    def insert(self,query):
        try:
            cur = connect()
            cur.execute(query)
        else:
            cur 