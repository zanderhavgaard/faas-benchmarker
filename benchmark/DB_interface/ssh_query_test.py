from ssh_query import ssh_query


path = '/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.ssh_query_test_env'

ssh = ssh_query(path)

print(ssh.insert_queries(['TRUNCATE TABLE Experiment']))

queries = [
    """insert into Experiment (uuid,timing) values ('test1',27)""",
    """insert into Experiment (uuid,timing) values (null,20)""",
    """insert into Experiment (uuid,timing) values ('test11',0)""",
    """insert into Experiment (uuid,timing) values ('test3',30)""",
]

val = ssh.insert_queries(queries)
print(val)
vals = ssh.retrive_query('select * from Experiment')
print(vals)