import logging
import time
import json
import uuid
import requests
import psutil
import azure.functions as func
import traceback
import random
import platform

if 'instance_identifier' not in locals():
    instance_identifier = str(uuid.uuid4())


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # req: HTTPRequest provided by azure

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
            },
        }

        # parse request json
        req_json = json.loads(req.get_body())

        

        # make sure that things are working...
        if req_json['StatusCode'] != 200:
            raise StatusCodeException('StatusCode: '+str(req_json['StatusCode']))


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
        else:
            body[identifier]['sleep'] = 0.0
        
        if 'throughput_time' in req_json:
            random.seed(req_json['throughput_time'] * 100)
            process_time_start = time.process_time()
            throughput_start = time.time()
            throughput = []

            while(time.time()-throughput_start < req_json['throughput_time']):
                throughput.append(random.random())
            throughput_process_time = time.process_time() - process_time_start

            body[identifier]['throughput'] = len(throughput)
            body[identifier]['throughput_time'] = req_json['throughput_time']
            body[identifier]['throughput_process_time'] = throughput_process_time
            body[identifier]['random_seed'] = req_json['throughput_time'] * 100
        else:
            body[identifier]['throughput'] = 0.0
            body[identifier]['throughput_time'] = None
            body[identifier]['throughput_process_time'] = None
            body[identifier]['random_seed'] = None

        
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

        # add timings and return
        body[identifier]['execution_start'] = start_time
        body[identifier]['execution_end'] = time.time()
        body[identifier]['cpu'] = platform.processor()
        body[identifier]['process_time'] = time.process_time()

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
        error_body = {
            "identifier": identifier,
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
        }
        return func.HttpResponse(body=json.dumps(error_body),
                                 status_code=200,
                                 headers={
                                     "Content-Type": "application/json; charset=utf-8"},
                                 charset='utf-8'
                                 )


def invoke_nested_function(function_name: str,
                           invoke_payload: dict,
                           code: str
                           ) -> dict:

    # capture the invocation start time
    start_time = time.time()

    try:
        headers = {
            'Content-Type': 'application/json'
        }

        function_app_name = f'https://{function_name}-python.azurewebsites.net'

        invocation_url = f'{function_app_name}/api/{function_name}?code={code}'

        response = requests.post(
            url=invocation_url,
            headers=headers,
            data=json.dumps(invoke_payload)
        )

        # capture the invocation end time
        end_time = time.time()

        # parse json payload to dict
        body = json.loads(response.content.decode())
        # get identifier of invoked lambda
        id = body['identifier']

        # add invocation start/end times
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

