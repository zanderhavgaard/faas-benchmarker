import time
import uuid
import json
import platform
import requests
import psutil


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
    function_name = 'function3'

    # whoami?
    identifier = f'{function_name}-{invocation_uuid}'

    try:
        # create a dict that will be parsed to json
        body = {
            identifier: {
                "identifier": identifier,
                "uuid": invocation_uuid
            }
        }

        # load json to string to dict
        event = json.loads(req)

        # make sure that things are working...
        if event['StatusCode'] != 200:
            raise Exception(str(event['StatusCode']))

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

        # add ip address of container to uniqely differentiate container instances
        body[identifier]['ip_address'] = psutil.net_if_addrs()['eth0'][0][1]

        # add python version metadata
        body[identifier]['python_version'] = platform.python_version()

        # add the hostname, should uniquely identify container instances
        body[identifier]['hostname'] = platform.node()
        # TODO add python version and hostname metadata to other function implementations

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

        # create return dict and parse json bodu
        return json.dumps({
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json; charset=utf-8"
            },
            "body": json.dumps(body),
            "identifier": identifier
        })

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
                    "error": {"message": str(e), "type": str(type(e))},
                    "parent": None,
                    "sleep": None,
                    "ip_address": None,
                    "python_version": None,
                    "hostname": None,
                    "level": None,
                    "execution_start": start_time,
                    "execution_end": time.time()
                }
            }),
            "identifier": identifier
        })


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
        identifier = response_json['identifier']

        # parse response body
        response_data = json.loads(response_json['body'])

        # add invocation metadata to response
        response_data[identifier]['invocation_start'] = start_time
        response_data[identifier]['invocation_end'] = end_time

        return response_data

    except Exception as e:
        return {
            "error-"+function_name+'-nested_invocation': {
                "identifier": "error-"+function_name+'-nested_invocation',
                "uuid": None,
                "error": {"message": str(e), "type": str(type(e))},
                "parent": invoke_payload['parent'],
                "sleep": None,
                "ip_address": None,
                "python_version": None,
                "hostname": None,
                "level": invoke_payload['level'],
                "execution_start": None,
                "execution_end": None,
                "invocation_start": start_time,
                "invocation_end": time.time()
            }
        }
