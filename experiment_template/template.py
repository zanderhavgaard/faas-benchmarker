import sys
import json
import time
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
{experiment_name}: <description>
"""

# =====================================================================================
# create the benchmarker
benchmarker = Benchmarker(experiment_name=experiment_name,
                          provider=provider,
                          client_provider=client_provider,
                          experiment_description=description,
                          env_file_path=env_file_path,
                          dev_mode=dev_mode)
# =====================================================================================


# Add the experiment logic here
# for example invoke function 1
#  benchmarker.invoke_function(function_endpoint=f'{experiment_name}1')

# =====================================================================================
# end of the experiment
benchmarker.end_experiment()
# =====================================================================================
