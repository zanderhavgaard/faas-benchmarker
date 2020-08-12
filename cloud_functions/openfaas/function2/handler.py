def handle(req):

    # get start time
    start_time, start_overhead = get_time()

    # import dependencies on execution time
    import time
    import uuid
    import json
    import platform
    import psutil
    import random

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
            }
        }

        # load json to string to dict
        event = json.loads(req)


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

        # add ip address of container to uniqely differentiate container instances
        body[identifier]['instance_identifier'] = str(psutil.net_if_addrs()['eth0'][0][1])+'-'+str(platform.node())

        # add total memory of pod to metadata
        body[identifier]['memory'] = psutil.virtual_memory()[0]
        # add python version metadata
        body[identifier]['python_version'] = platform.python_version()

        #  invoke nested functions from arguments
        if 'invoke_nested' in event:
            for invoke in event['invoke_nested']:
                invoke['invoke_payload']['parent'] = identifier
                invoke['invoke_payload']['level'] = body[identifier]['level']
                nested_response = invoke_nested_function(
                    function_name=invoke['function_name'],
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

        # create return dict and parse json bodu
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(body),
            "identifier": identifier
        }

    # return json object with error if exception occurs
    except Exception as e:
        import traceback
        end_time, end_overhead = get_time()
        return {
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
        }

# we do not trust that the time is correct for all function platforms 
# so we ask an ntp server what it's time is
def get_time():
    import time
    start = time.time()
    import ntplib
    ntpc = ntplib.NTPClient()
    retries = 0
    total_overhead = time.time() - start
    while retries < 10:
        retries += 1
        try:
            t1 = time.time()
            ntp_response = ntpc.request('ntp2.cam.ac.uk')
            t2 = time.time()
            response_overhead = (t2 - t1) / 3
            res = ntp_response.tx_time - total_overhead - response_overhead
            return (res, total_overhead + response_overhead)
        except ntplib.NTPException:
            total_overhead += time.time() - t1
    return (start, total_overhead)

# invoke another openfaas function using python requests, will make use of the API gateway
# params:
# function_name: name of function in to be called at the gateway
# invoke_payload: dict containing arguments for invoked function
def invoke_nested_function(function_name: str,invoke_payload: dict) -> dict:
    # capture the invocation start time
    start_time, start_overhead = get_time()

    import time
    import json

    try:

        headers = {
            'Content-Type': 'application/json'
        }

        function_url = 'gateway.openfaas:8080'
        # strip expreiment name from function_name
        function_name = function_name.split('-').pop()
        invocation_url = f'http://{function_url}/function/{function_name}'

        # imports are expensive, so we only do them when we actually need them
        import requests

        cutoff_time = start_time + (60 * 5)

        while time.time() < cutoff_time:
            try:
                response = requests.post(
                    url=invocation_url,
                    headers=headers,
                    data=json.dumps(invoke_payload)
                )
                if response.status_code == 200:
                    break
                # if we try to invoke a cold function we might get 500's while it is starting
                elif response.status_code == 500:
                    time.sleep(1)
            except Exception as e:
                print('caught some error while doing a nested invoke,', e, str(e))

        # capture the invocation end time
        end_time, end_overhead = get_time()

        # parse response_json
        response_json = json.loads((response.content.decode()))

        # get the identifier
        id = response_json['identifier']

        # parse response body
        body = json.loads(response_json['body'])

        # add invocation metadata to response
        body[id]['invocation_start'] = start_time
        body[id]['invocation_end'] = end_time - start_overhead

        return body

    except Exception as e:
        import traceback
        import platform
        end_time, end_overhead = get_time()
        return {
            f"error-{function_name}-nested_invocation-{end_time}": {
                "identifier": f"error-{function_name}-nested_invocation-{end_time}",
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

