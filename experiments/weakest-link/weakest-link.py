import sys
import json
import time
from pprint import pprint
from benchmarker import Benchmarker

# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = sys.argv[1]

# unique identifier string tying this experiment together with the
# experiments conducted for the other cloud providers in this round
experiment_meta_identifier = sys.argv[2]

# name of cloud function provider for this experiment
provider = sys.argv[3]

# name of the client provider
client_provider = sys.argv[4]

# relative path to experiment.env file
env_file_path = sys.argv[5]

# dev_mode
dev_mode = eval(sys.argv[6]) if len(sys.argv) > 6 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment tests the relationship
between cloud functions that invoke each other.
The experiment is conducted by first invoking function 1 and function 2 such that
they are hot. Then we invoke function 1, with a nested invocation dict, such that
function1 will invoke function2 which will invoke function 3. We then expect that
of the total time of the nested invocation that function3 will account for the majority
of the response time, as should be the only cold start. We then wait for all of the functions
to become cold and repeat the invocations a number of times.
"""

# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          experiment_meta_identifier=experiment_meta_identifier,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode)
# =====================================================================================

# how many times we repeat the experiment
iterations = 5

# setup convenient function names
fx1 = f'{experiment_name}1'
fx2 = f'{experiment_name}2'
fx3 = f'{experiment_name}3'

# delay between iteration, in order to wait for all of the functions to become cold
delay = benchmarker.get_delay_between_experiment_iterations()

for i in range(iterations):

    print(f'Running experiment iteration {i} ...')

    # invoke function 1 and 2 such that they are hot
    hot_response1 = benchmarker.invoke_function(function_endpoint=fx1)
    print('Response from prewarming function 1')
    pprint(hot_response1)
    hot_response2 = benchmarker.invoke_function(function_endpoint=fx2)
    print('Response from prewarming function 2')
    pprint(hot_response2)

    # setup nested invocations
    nested = [
        {
            "function_name": f"{experiment_name}2",
            "invoke_payload": {
                "StatusCode": 200,
                "invoke_nested": [
                    {
                        "function_name": f"{experiment_name}3",
                        "invoke_payload": {
                            "StatusCode": 200,
                        }
                    }
                ]
            }
        }
    ]

    # invoke function 1, that will invoke function 2, which will invoke funcion 3
    # we expect that only function3 will be a cold start, and thus the majority of the response time
    weakest_link_response = benchmarker.invoke_function(
        function_endpoint=fx1, invoke_nested=nested)

    print('Response from the nested invocation:')
    pprint(weakest_link_response)

    if i < (iterations - 1):
        print(f'Now waiting {delay} seconds before running next iteration ...')
        time.sleep(delay)
    else:
        print('Done running weakest link experiment.')

# =====================================================================================
# end of the experiment
benchmarker.end_experiment()
# =====================================================================================
