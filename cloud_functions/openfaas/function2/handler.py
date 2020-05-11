import time
import uuid
import json
import platform
import requests
import psutil
import traceback
import random


def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """

    # get start time
    start_time = time.time()

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
                "function_name": function_name
            }
        }

        # load json to string to dict
        event = json.loads(req)

        # make sure that things are working...
        if event['StatusCode'] != 200:
            raise StatusCodeException('StatusCode: '+str(event['StatusCode']))

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
        else:
            body[identifier]['sleep'] = 0.0
        
        if 'throughput_time' in event:
            random.seed(event['throughput_time'] * 100)
            process_time_start = time.process_time()
            throughput_start = time.time()
            throughput = []

            while(time.time()-throughput_start < event['throughput_time']):
                throughput.append(random.random())
            throughput_process_time = time.process_time() - process_time_start

            body[identifier]['throughput_running_time'] = time.time() - throughput_start
            body[identifier]['throughput'] = len(throughput)
            body[identifier]['throughput_time'] = event['throughput_time']
            body[identifier]['throughput_process_time'] = throughput_process_time
            body[identifier]['random_seed'] = event['throughput_time'] * 100
        else:
            body[identifier]['throughput'] = 0.0
            body[identifier]['throughput_running_time'] = None
            body[identifier]['throughput_time'] = None
            body[identifier]['throughput_process_time'] = None
            body[identifier]['random_seed'] = None 

        # add ip address of container to uniqely differentiate container instances
        body[identifier]['instance_identifier'] = str(
            psutil.net_if_addrs()['eth0'][0][1])+'-'+str(platform.node())

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

        # add timings and return
        body[identifier]['execution_start'] = start_time
        body[identifier]['execution_end'] = time.time()
        body[identifier]['cpu'] = platform.processor()
        body[identifier]['process_time'] = time.process_time()

        # create return dict and parse json bodu
        return json.dumps({
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(body),
            "identifier": identifier
        })
    # return json object with error if exception occurs
    except Exception as e:
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
                    "error": {"trace": traceback.format_exc(), 'message': str(e), "type": str(type(e).__name__ )},
                    "parent": None,
                    "sleep": None,
                    "throughput": None,
                    "throughput_time": None,
                    "throughput_process_time": None,
                    'throughput_running_time': None,
                    "random_seed": None,
                    "python_version": None,
                    "level": None,
                    "memory": None,
                    "instance_identifier": None,
                    "execution_start": start_time,
                    "execution_end": time.time(),
                    "cpu": platform.processor(),
                    "process_time": time.process_time()
                }
            }),
            "identifier": identifier
        })

# invoke another openfaas function using python requests, will make use of the API gateway
# params:
# function_name: name of function in to be called at the gateway
# invoke_payload: dict containing arguments for invoked function


def invoke_nested_function(function_name: str,
                           invoke_payload: dict
                           ) -> dict:

    # capture the invocation start time
    start_time = time.time()

    try:

        headers = {
            'Content-Type': 'application/json'
        }

        #  function_url = f'{function_name}'
        # TODO change
        function_url = 'gateway.openfaas:8080'
        function_number = function_name[len(function_name)-1:]

        invocation_url = f'http://{function_url}/function/function{function_number}'

        response = requests.post(
            url=invocation_url,
            headers=headers,
            data=json.dumps(invoke_payload)
        )

        # capture the invocation end time
        end_time = time.time()

        # parse response_json
        response_json = json.loads((response.content.decode()))

        # get the identifier
        id = response_json['identifier']

        # parse response body
        body = json.loads(response_json['body'])

        # add invocation metadata to response
        body[id]['invocation_start'] = start_time
        body[id]['invocation_end'] = end_time

        return body

    except Exception as e:
        end_time = time.time()
        return {
            "error-"+function_name+'-nested_invocation-'+str(end_time): {
                "identifier": "error-"+function_name+'-nested_invocation-'+str(end_time),
                "uuid": None,
                "function_name": 'function1',
                "error": {"trace": traceback.format_exc(), 'message': str(e), "type": str(type(e).__name__ )},
                "parent": invoke_payload['parent'],
                "sleep": None,
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
                "invocation_start": start_time,
                "invocation_end": end_time,
                "cpu": platform.processor(),
                "process_time": time.process_time()
            }
        }

class StatusCodeException(Exception):
    pass
