
# required for function definition
import azure.functions as func

# check if this functionapp has been invoked before
if 'instance_identifier' not in locals():
    import uuid
    instance_identifier = str(uuid.uuid4())


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # req: HTTPRequest provided by azure

    # get start time
    start_time, start_overhead = get_time()

    import time
    import logging
    import json
    import uuid
    import psutil
    import random
    import platform

    # we create an UUID to ensure that the function has
    # to do some arbitrary computation such that responses cannot
    # be cached, as well for identifying unique invocations
    invocation_uuid = str(uuid.uuid4())
    # unique name of this function
    function_name = 'function2'

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

        # parse request json
        req_json = json.loads(req.get_body())


        if 'parent' not in req_json:
            # if first in chain mark as root
            body[identifier]['parent'] = 'root'
        else:
            body[identifier]['parent'] = req_json['parent']

        # set level if root in invocation tree
        if 'level' not in req_json:
            body[identifier]['level'] = 0
        else:
            body[identifier]['level'] = req_json['level'] + 1

        # if request contains a sleep argument, then sleep for that amount
        # and log the amount of time slept
        if 'sleep' in req_json:
            time.sleep(req_json['sleep'])
            body[identifier]['sleep'] = req_json['sleep']

        if 'throughput_time' in req_json:
            random.seed(req_json['throughput_time'] * 100)
            process_time_start = time.process_time()
            throughput_start = time.time()
            throughput = []

            while(time.time()-throughput_start < req_json['throughput_time']):
                throughput.append(random.random())
            throughput_process_time = time.process_time() - process_time_start

            body[identifier]['throughput_running_time'] = time.time() - \
                throughput_start
            body[identifier]['throughput'] = len(throughput)
            body[identifier]['throughput_time'] = req_json['throughput_time']
            body[identifier]['throughput_process_time'] = throughput_process_time
            body[identifier]['random_seed'] = req_json['throughput_time'] * 100
      

        # add python version metadata
        body[identifier]['python_version'] = platform.python_version()
        # add total memory of pod to metadata
        body[identifier]['memory'] = psutil.virtual_memory()[0]
        # log instance identifier
        body[identifier]['instance_identifier'] = instance_identifier

        #  invoke nested functions from arguments
        if 'invoke_nested' in req_json:
            for invoke in req_json['invoke_nested']:
                invoke['invoke_payload']['parent'] = identifier
                invoke['invoke_payload']['level'] = body[identifier]['level']
                nested_response = invoke_nested_function(
                    function_name=invoke['function_name'],
                    invoke_payload=invoke['invoke_payload'],
                    code=invoke['code']
                )
                # add each nested invocation to response body
                for id in nested_response.keys():
                    body[id] = nested_response[id]


        # for azure functions we have to follow the response form
        # that azure provides, so we add an extra key to body that
        # contains the function identifier
        body['identifier'] = identifier

        # set the response status code
        status_code = 200

        # set the response headers
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        body[identifier]['cpu'] = platform.processor()
        body[identifier]['process_time'] = time.process_time()

        # get the end time and tne overhead
        end_time, end_overhead = get_time()
        # add timings and return
        body[identifier]['execution_start'] = start_time
        body[identifier]['execution_end'] = end_time - start_overhead
        body[identifier]['invocation_ntp_diff'] = start_overhead + end_overhead


        # create the azure functions response
        response = func.HttpResponse(body=json.dumps(body),
                                     status_code=status_code,
                                     headers=headers,
                                     charset='utf-8'
                                     )

        # return the HTTPResponse
        return response
    # return httpResponse with error if exception occurs
    except Exception as e:
        import traceback
        end_time, end_overhead = get_time()
        error_body = {
            "identifier": identifier,
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
        }
        return func.HttpResponse(body=json.dumps(error_body),
                                 status_code=200,
                                 headers={
                                     "Content-Type": "application/json; charset=utf-8"},
                                 charset='utf-8'
                                 )


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
                response_overhead = (t2 - t1) / 2
                res = ntp_response.tx_time - total_overhead - response_overhead
                return (res, total_overhead + response_overhead)
            except ntplib.NTPException:
                total_overhead += time.time() - t1
    return (start, total_overhead)

def invoke_nested_function(function_name: str,
                           invoke_payload: dict,
                           code: str
                           ) -> dict:
    import time
    import json

    # capture the invocation start time
    start_time, start_overhead = get_time()

    try:
        headers = {
            'Content-Type': 'application/json'
        }

        function_app_name = f'https://{function_name}.azurewebsites.net'

        invocation_url = f'{function_app_name}/api/{function_name}?code={code}'

        import requests
        response = requests.post(
            url=invocation_url,
            headers=headers,
            data=json.dumps(invoke_payload)
        )

        # capture the invocation end time
        end_time, end_overhead = get_time()

        # parse json payload to dict
        body = json.loads(response.content.decode())
        # get identifier of invoked lambda
        id = body['identifier']

        # add invocation start/end times
        body[id]['invocation_start'] = start_time
        body[id]['invocation_end'] = end_time - end_overhead

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

