import boto3
import time
import json
import uuid


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

    # make sure that things are working...
    if event['StatusCode'] != 200:
        raise Exception("Something went wrong ...")

    # create a dict that will be parsed to json
    # and returned to the client
    response = {
        "StatusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": {
            identifier: {
                "uuid": invocation_uuid
            }
        },
        # tells us which function was the root of a tree of nested function invocations
        "invocation_root_identifier": identifier,
    }

    # if request contains a sleep argument, then sleep for that amount
    # and log the amount of time slept
    if 'sleep' in event:
        time.sleep(event['sleep'])
        response['data'][identifier]['sleep'] = event['sleep']
    else:
        response['data'][identifier]['sleep'] = 0.0

    # invoke nested lambdas from arguments
    if 'invoke_nested' in event:
        # invoke nested will contain a list of dicts specifying how invoke nested functions
        # create client for invoking other lambdas
        lambda_client = boto3.client('lambda')
        # execute each nested lambda invocation command
        for invoke in event['invoke_nested']:
            invoke_lambda(
                lambda_name=invoke['lambda_name'],
                invoke_payload=invoke['invoke_payload'],
                client=lambda_client,
                invocation_type=invoke['invocation_type'],
            )

    # add invocation metadata to response
    if context is None:
        # add dummy data
        response['data'][identifier]['memory'] = 128
        response['data'][identifier]['log_stream_name'] = "foobar"
    else:
        # add memory allocation / size of lambda instance
        response['data'][identifier]['memory'] = context.memory_limit_in_mb
        # add unique lambda instance identifier
        response['data'][identifier]['log_stream_name'] = context.log_stream_name

    # add timings and return
    response['data'][identifier]['execution_start'] = start_time
    response['data'][identifier]['execution_end'] = time.time()

    # if debugging return as json str
    if __name__ == "__main__":
        print(json.dumps(response))
    else:
        # return response to invoker,
        # AWS converts response to json for us
        return response


# invoke another lambda function using boto3, thus invoking the function
# directly and not interacting with the API gateway
# params:
# lambda_name: name of function in AWS
# inke_payload: dict containing arguments for invoked lambda
# client: boto3 lambda client, should only be instantiated if needed
# invocation_type: string that specfifies whether the client lambda should wait for the response
#   values should be either: 'Event' for asynchronous or 'RequestResponse' for synchronous
#   default is synchronous
def invoke_lambda(lambda_name: str,
                  invoke_payload: dict,
                  client: boto3.client,
                  invocation_type='RequestResponse') -> dict:

    # capture the invocation start time
    start_time = time.time()

    # invoke the function
    response = client.invoke(
        FunctionName=lambda_name,
        InvocationType=invocation_type,
        Payload=json.dumps(invoke_payload),
    )

    # capture the invocation end time
    end_time = time.time()

    # parse json payload to dict
    payload = json.load(response['Payload'])

    # add invocation start/end times to the payload dict for easy parsing by the final client
    payload['data'][payload['identifier']
                    ]['invocation_start'] = start_time
    payload['data'][payload['identifier']]['invocation_end'] = end_time

    return response


# call the method if running locally
if __name__ == "__main__":

    # simplest invoke
    #  test_event = {"StatusCode": 200}

    # invoke with sleep
    #  test_event = {"StatusCode": 200, 'sleep': 2.5}

    # invoke with nested invocations
    #  test_event = {"StatusCode": 200,
    #  "invoke_nested": [
    #  {
    #  "lambda_name": "function2",
    #  "invoke_payload": {
    #  "StatusCode": 200,
    #  "sleep": 2.5,
    #  },
    #  "invocation_type": "RequestResponse"
    #  },
    #  {
    #  "lambda_name": "function3",
    #  "invoke_payload": {
    #  "StatusCode": 200,
    #  },
    #  "invocation_type": "RequestResponse"
    #  },
    #  ],
    #  }
    test_context = None
    lambda_handler(test_event, test_context)
