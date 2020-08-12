def lambda_handler(event: dict, context: dict) -> dict:
    # event contains json parameters
    # context contains metadata of the lambda instance
    #   --> provided by AWS

    # get start time
    start_time, start_overhead = get_time()

    import time
    import json
    import uuid
    import platform
    import random
    import psutil

    # we create an UUID to ensure that the function has
    # to do some arbitrary computation such that responses cannot
    # be cached, as well for identifying unique invocations
    invocation_uuid = str(uuid.uuid4())

    # unique name of this function
    function_name = 'function3'

    # whoami?
    identifier = f'{function_name}-{invocation_uuid}'

    try:
        # create a dict that will be parsed to json
        body = {
            identifier: {
                "identifier": identifier,
                "uuid": invocation_uuid,
                "function_name": function_name,
                "function_cores": psutil.cpu_count()
            },
        }

        # set parent (previous invocation) of this invocation
        if 'parent' not in event:
            # if first in chain mark as root
            body[identifier]['parent'] = 'root'
        else:
            body[identifier]['parent'] = event['parent']

        # set level if root in invocation tree
        if 'level' not in event:
            body[identifier]['level'] = 0
        else:
            body[identifier]['level'] = event['level'] + 1

        # if request contains a sleep argument, then sleep for that amount
        # and log the amount of time slept
        if 'sleep' in event:
            time.sleep(event['sleep'])
            body[identifier]['sleep'] = event['sleep']
        

        if 'throughput_time' in event:
            random.seed(event['throughput_time'] * 100)
            process_time_start = time.process_time()
            throughput_start = time.time()
            throughput = []

            while(time.time()-throughput_start < event['throughput_time']):
                throughput.append(random.random())
            throughput_process_time = time.process_time() - process_time_start

            body[identifier]['throughput_running_time'] = time.time() - \
                throughput_start
            body[identifier]['throughput'] = len(throughput)
            body[identifier]['throughput_time'] = event['throughput_time']
            body[identifier]['throughput_process_time'] = throughput_process_time
            body[identifier]['random_seed'] = event['throughput_time'] * 100
        

        # add invocation metadata to response
        if context is None:
            # add dummy data
            body[identifier]['memory'] = 128
            body[identifier]['instance_identifier'] = "foobar"
        else:
            # add memory allocation / size of lambda instance
            body[identifier]['memory'] = context.memory_limit_in_mb
            # add unique lambda instance identifier
            body[identifier]['instance_identifier'] = context.log_stream_name

        # add python version metadata
        body[identifier]['python_version'] = platform.python_version()

        # invoke nested lambdas from arguments
        if 'invoke_nested' in event:
            # invoke nested will contain a list of dicts specifying how invoke nested functions
            # execute each nested lambda invocation command
            for invoke in event['invoke_nested']:
                invoke['invoke_payload']['parent'] = identifier
                invoke['invoke_payload']['level'] = body[identifier]['level']
                nested_response = invoke_lambda(
                    lambda_name=invoke['function_name'],
                    invoke_payload=invoke['invoke_payload']
                )
                # add each nested invocation to response body
                for id in nested_response.keys():
                    body[id] = nested_response[id]

        body[identifier]['cpu'] = platform.processor()
        body[identifier]['process_time'] = time.process_time()

        # get the end time and tne overhead
        end_time, end_overhead = get_time()
        # add timings and return
        body[identifier]['execution_start'] = start_time
        body[identifier]['execution_end'] = end_time - start_overhead
        body[identifier]['invocation_ntp_diff'] = start_overhead + end_overhead

        # create return dict and parse json body
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(body),
            "identifier": identifier
        }

    except Exception as e:
        import traceback
        end_time, end_overhead = get_time()
        return json.dumps({
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps({
                identifier: {
                    "identifier": identifier,
                    "uuid": invocation_uuid,
                    "function_name": function_name,
                    "error": {"trace": traceback.format_exc(), 'message': str(e), "type": str(type(e).__name__)},
                    "parent": None,
                    "sleep": None,
                    "function_cores": psutil.cpu_count(),
                    "throughput": None,
                    "throughput_time": None,
                    "throughput_process_time": None,
                    'throughput_running_time': None,
                    "random_seed": None,
                    "python_version": None,
                    "level": None,
                    "memory": None,
                    "instance_identifier": None,
                    "invocation_ntp_diff": start_overhead + end_overhead,
                    "execution_start": start_time,
                    "execution_end": end_time - start_overhead,
                    "cpu": platform.processor(),
                    "process_time": time.process_time()
                }
            }),
            "identifier": identifier
        })

# we do not trust that the time is correct for all function platforms 
# so we ask an ntp server what it's time is
def get_time():
    import time
    start = time.time()
    import ntplib
    ntpc = ntplib.NTPClient()
    retries = 0
    total_overhead = time.time() - start
    ntp_servers = ['0','1','2','3']
    for ntp_server_num in ntp_servers:
        while retries < 10:
            retries += 1
            try:
                t1 = time.time()
                ntp_response = ntpc.request(f'ntp{ntp_server_num}.cam.ac.uk')
                t2 = time.time()
                response_overhead = (t2 - t1) / 3
                res = ntp_response.tx_time - total_overhead - response_overhead
                return (res, total_overhead + response_overhead)
            except ntplib.NTPException:
                total_overhead += time.time() - t1
    return (start, total_overhead)

# invoke another lambda function using boto3, thus invoking the function
# directly and not interacting with the API gateway
# params:
# lambda_name: name of function in AWS
# invoke_payload: dict containing arguments for invoked lambda
# client: boto3 lambda client, should only be instantiated if needed
def invoke_lambda(lambda_name: str,
                  invoke_payload: dict,
                  ) -> dict:
    import time
    import json
    import boto3
    # create client for invoking other lambdas
    client = boto3.client('lambda')

    # capture the invocation start time
    start_time, start_overhead = get_time()

    try:
        # invoke the function
        response = client.invoke(
            FunctionName=lambda_name,
            Payload=json.dumps(invoke_payload),
        )

        # capture the invocation end time
        end_time, end_overhead = get_time()

        # parse json payload to dict
        payload = json.load(response['Payload'])
        # get identifier of invoked lambda
        id = payload['identifier']
        # parse the json body
        body = json.loads(payload['body'])

        # add invocation start/end times
        body[id]['invocation_start'] = start_time
        body[id]['invocation_end'] = end_time - end_overhead

        return body

    except Exception as e:
        import traceback
        import platform
        end_time, end_overhead = get_time()
        return {
            "error-"+lambda_name+'-nested_invocation-'+str(end_time): {
                "identifier": "error-"+lambda_name+'-nested_invocation-'+str(end_time),
                "uuid": None,
                "function_name": 'function1',
                "error": {"trace": traceback.format_exc(), 'message': str(e), "type": str(type(e).__name__)},
                "parent": invoke_payload['parent'],
                "sleep": None,
                "function_cores": 0,
                "throughput": None,
                "throughput_time": None,
                "throughput_process_time": None,
                'throughput_running_time': None,
                "random_seed": None,
                "python_version": None,
                "level": invoke_payload['level'],
                "memory": None,
                "instance_identifier": None,
                "execution_start": None,
                "execution_end": None,
                "invocation_ntp_diff": start_overhead + end_overhead,
                "invocation_start": start_time,
                "invocation_end": end_time - start_overhead,
                "cpu": platform.processor(),
                "process_time": time.process_time()
            }
        }



