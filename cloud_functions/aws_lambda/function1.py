import boto3
import time
import json
import uuid
import platform
import traceback
import random


def lambda_handler(event: dict, context: dict) -> dict:
    # event contains json parameters
    # context contains metadata of the lambda instance
    #   --> provided by AWS

    # get start time
    start_time = time.time()

    # we create an UUID to ensure that the function has
    # to do some arbitrary computation such that responses cannot
    # be cached, as well for identifying unique invocations
    invocation_uuid = str(uuid.uuid4())

    # unique name of this function
    function_name = 'function1'

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
            # create client for invoking other lambdas
            lambda_client = boto3.client('lambda')
            # execute each nested lambda invocation command
            for invoke in event['invoke_nested']:
                invoke['invoke_payload']['parent'] = identifier
                invoke['invoke_payload']['level'] = body[identifier]['level']
                nested_response = invoke_lambda(
                lambda_name=invoke['function_name'],
                invoke_payload=invoke['invoke_payload'],
                client=lambda_client,
                )
                # add each nested invocation to response body
                for id in nested_response.keys():
                    body[id] = nested_response[id]


        # add timings and return
        body[identifier]['execution_start'] = start_time
        body[identifier]['execution_end'] = time.time()
        body[identifier]['cpu'] = platform.processor()
        body[identifier]['process_time'] = time.process_time()

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
# invoke another lambda function using boto3, thus invoking the function
# directly and not interacting with the API gateway
# params:
# lambda_name: name of function in AWS
# invoke_payload: dict containing arguments for invoked lambda
# client: boto3 lambda client, should only be instantiated if needed
def invoke_lambda(lambda_name: str,
                  invoke_payload: dict,
                  client: boto3.client
                  ) -> dict:

    # capture the invocation start time
    start_time = time.time()

    try:
        # invoke the function
        response = client.invoke(
            FunctionName=lambda_name,
            Payload=json.dumps(invoke_payload),
        )

        # capture the invocation end time
        end_time = time.time()

        # parse json payload to dict
        payload = json.load(response['Payload'])
        # get identifier of invoked lambda
        id = payload['identifier']
        # parse the json body
        body = json.loads(payload['body'])

        # add invocation start/end times
        body[id]['invocation_start'] = start_time
        body[id]['invocation_end'] = end_time
        

        return body
    
    except Exception as e:
        end_time = time.time()
        return {
            "error-"+lambda_name+'-nested_invocation-'+str(end_time): {
                "identifier": "error-"+lambda_name+'-nested_invocation-'+str(end_time),
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




# call the method if running locally
#  if __name__ == "__main__":

    #  simplest invoke
    #  test_event = {"StatusCode": 200}

    #  invoke with sleep
    #  test_event = {"StatusCode": 200, 'sleep': 1.5}

    #  invoke with nested invocations
    #  test_event = {"StatusCode": 200,
    #  "invoke_nested": [
    #  {
    #  "function_name": "dev2-python",
    #  "invoke_payload": {
    #  "StatusCode": 200,
    #  "sleep": 0.5,
    #  },
    #  "invocation_type": "RequestResponse"
    #  },
    #  {
    #  "function_name": "dev3-python",
    #  "invoke_payload": {
    #  "StatusCode": 200,
    #  },
    #  "invocation_type": "RequestResponse"
    #  },
    #  ],
    #  }

    #  test_context = None

    #  response = lambda_handler(test_event, test_context)
    #  print(response)
