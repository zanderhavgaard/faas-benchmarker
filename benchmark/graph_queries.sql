-- all regular throughput
SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, total_time, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 ;

-- throughput per provider
SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and cl_provider='aws_lambda' order by process_fraction;

SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and cl_provider='azure_functions' order by process_fraction;

SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and cl_provider='openfaas' order by process_fraction;




-- throughput monolith
select function_argument,process_time_matrix,running_time_matrix,monolith_result,(process_time_matrix/running_time_matrix)*100 as process_fraction, 
            execution_start-invocation_start as latency, thread_id, numb_threadscl_provider 
from (Monolith m left join Experiment e on m.exp_id=e.uuid) join Invocation i on m.invo_id=i.identifier ;

select function_argument,process_time_matrix,running_time_matrix,monolith_result,(process_time_matrix/running_time_matrix)*100 as process_fraction, 
execution_start-invocation_start as latency, thread_id, numb_threads,cl_provider  from (Monolith m left join Experiment e on m.exp_id=e.uuid) join 
Invocation i on m.invo_id=i.identifier;

-- works but wrong - not needed
-- select function_argument, monolith_result as res, thread_id, numb_threads,cl_provider from (Monolith m left join Experiment e on m.exp_id=e.uuid) 
-- join Invocation i on m.invo_id=i.identifier where monolith_result in (select distinct(monolith_result) from Monolith);



-- select seed, function_argument,function_called,process_time_matrix,running_time_matrix,monolith_result,cl_provider,execution_total 
-- from (Monolith m left join Experiment e on m.exp_id=e.uuid) join Invocation i on m.invo_id=i.identifier group by seed,function_argument order by monolith_result,cl_provider;
select uuid from openfaas_uuid from Experiment where name = 'throughput-benchmarking' and  cl_provider = 'openfaas' order by id desc limit 1) x,
(select uuid as azure_uuid from Experiment where name = 'throughput-benchmarking' and  cl_provider = 'azure_functions' order by id desc limit 1) y,
(select uuid as aws_uuid from Experiment where name = 'throughput-benchmarking' and  cl_provider = 'aws_lambda' order by id desc limit 1) z;


SELECT name, execution_start-invocation_start as latency, instance_identifier as id, execution_total as total, thread_id, 3*avg, if(execution_total-invocation_start > avg,1,0) as cold, if(numb_threads > 1,0,1) as multi, cl_provider as provider from Experiment e left join Invocation i on i.exp_id=e.uuid left join (select avg(execution_start-invocation_start) as avg,exp_id as xexp_id from Invocation where exp_id ='fc94a2dd-254d-4623-ab59-bbe965d172f9') x on e.uuid=x.xexp_id where exp_id ='fc94a2dd-254d-4623-ab59-bbe965d172f9' order by identifier,latency;


select latency,instance_id, total, thread_id,  multi, provider, if(latency > coldtime, 'cold','warm') as cold  
from (SELECT instance_identifier as instance_id, execution_total as total, thread_id,  if(numb_threads > 1,0,1) as multi, cl_provider as
provider, coldtime, execution_start-invocation_start as latency from Experiment e 
left join Invocation i on i.exp_id=e.uuid left join (select avg(execution_start-invocation_start)*3 as coldtime,exp_id as xexp_id from Invocation 
where exp_id ='fc94a2dd-254d-4623-ab59-bbe965d172f9') x on e.uuid=x.xexp_id where exp_id ='fc94a2dd-254d-4623-ab59-bbe965d172f9') y;
