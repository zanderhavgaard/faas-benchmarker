from ssh_query import SSH_query


path = '/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.ssh_query_test_env'

ssh = SSH_query(path)

print(ssh.insert_queries(['TRUNCATE TABLE Experiment']))

queries = [
    """insert into Experiment (e_uuid, e_name, e_desc, e_cl_providor, e_client, e_py_version, e_cores, e_memory, e_start_time, e_end_time, e_total_time) 
    values ('test1', 'test', 'test', 'test', 'test', 'test',27, 10, 10.0, 11.0, 12.0);""",
        """insert into Experiment (e_uuid, e_name, e_desc, e_cl_providor, e_client, e_py_version, e_cores, e_memory, e_start_time, e_end_time, e_total_time) 
        values ('test1', 'test', 'test', 'test', 'test', 'test',27, 10, 10.0, 11.0, "test");""",

    # """insert into Experiment (uuid,name,desc,cl_provider,client,py_version,cores,memory,start_time,end_time,total_time,root_invocation) 
    # values ('test2', 'test', 'test', 'test', 'test', 'test',27, 10, 10.0,11.0,12.0,'test');""",
    # """insert into Experiment (uuid,name,desc,cl_provider,client,py_version,cores,memory,start_time,end_time,total_time,root_invocation) 
    # values ('test3', 'test', 'test', 'test', 'test', 'test',''test, 10, 10.0,11.0,12.0,'test');"""
    # """insert into Experiment (uuid,timing) values (null,20)""",
    # """insert into Experiment (uuid,timing) valu ('test11',0)""",
    # """insert into Experiment (uuid,timing) values ('test3',30)""",
]

val = ssh.insert_queries(queries)
print(val)
vals = ssh.retrive_query('select * from Experiment')
print(vals)