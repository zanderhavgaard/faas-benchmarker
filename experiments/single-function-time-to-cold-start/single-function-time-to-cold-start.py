import sys
import json
from pprint import pprint
from benchmarker import Benchmarker

# =====================================================================================
# Read cli arguments from calling script

# name of the terraform experiment
experiment_name = sys.argv[1]

# name of cloud function provider for this experiment
provider = sys.argv[2]

# name of the client provider
client_provider = sys.argv[3]

# relative path to experiment.env file
env_file_path = sys.argv[4]

# dev_mode
dev_mode = eval(sys.argv[5]) if len(sys.argv) > 5 else False

# =====================================================================================

# describe experiment, should be verbose enough to figure
# out what the experiment does and what it attempts to test
description = f"""
{experiment_name}: This experiment tests the time it takes for
a single function instance to no longer be available due to inactivity.
The experiment is conducted by first invoking a single function 6 times,
the first time to make sure that the function instane is created, the the following
5 times to create a baseline for a 'hot' invocation.
Then the function is invoked continually with increasing delay between invocations,
until the function is a cold start for each invocation with that delay.
This process is then repeated and averaged.
"""

# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          provider=provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode)
# =====================================================================================

fx_num = 1
fx = f'{experiment_name}{fx_num}'

# invoke function to make that it is hot
initial_cold_start_response = benchmarker.invoke_function(function_endpoint=fx)

# invoke function 5 times to get a baseline for a hot function invocation time
hot_invocation_baseline_responses = []
for i in range(4):
    hot_invocation_baseline_responses.append(
        benchmarker.invoke_function(function_endpoint=fx)
    )


# =====================================================================================
# end of the experiment
benchmarker.end_experiment()
# =====================================================================================
