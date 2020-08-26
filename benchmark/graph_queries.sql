-- all regular throughput
SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, total_time, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 order by process_fraction;

-- throughput per provider
SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and cl_provider='aws_lambda' order by process_fraction;

SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and cl_provider='azure_functions' order by process_fraction;

SELECT throughput,throughput_time, throughput_process_time,(throughput_process_time/throughput_time)*100 as process_fraction, cl_provider from (select name, cl_provider, uuid
as experiment_uuid from Experiment where name = 'throughput-benchmarking') x left join Invocation i on i.exp_id=x.experiment_uuid where throughput != 0 and cl_provider='openfaas' order by process_fraction;
