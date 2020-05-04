from provider_openfaas import OpenFaasProvider as provider
from pprint import pprint
# from sets import Set

# class invocation:

#     # def __init__(self,response:dict):
#     #     return 0

#     def get_responses(self,responses:dict) -> list:
#         parsed_responses = []

#         def __rec_aux(self,parse,acc) -> list:
#             if()


# _____ ___  ____   ___             __ _              _   _
# |_   _/ _ \|  _ \ / _ \           / _(_)_  __   ___ | |_| |__   ___ _ __
#   | || | | | | | | | | |  _____  | |_| \ \/ /  / _ \| __| '_ \ / _ \ '__|
#   | || |_| | |_| | |_| | |_____| |  _| |>  <  | (_) | |_| | | |  __/ |
#   |_| \___/|____/ \___/          |_| |_/_/\_\  \___/ \__|_| |_|\___|_|

#       _                 _  __                  _   _
#   ___| | ___  _   _  __| |/ _|_   _ _ __   ___| |_(_) ___  _ __  ___
#  / __| |/ _ \| | | |/ _` | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | (__| | (_) | |_| | (_| |  _| |_| | | | | (__| |_| | (_) | | | \__ \
#  \___|_|\___/ \__,_|\__,_|_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/



experiment_name = 'function'
function = 'function1'
sleep = 0.1
invoke_nested = [
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2,
            "invoke_nested": [
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2
                    }
                },
                {
                    "function_name": f"{experiment_name}1",
                    "invoke_payload": {
                        "StatusCode": 502,
                        "sleep": 0.2,
                        "invoke_nested": [
                            {
                                "function_name": f"{experiment_name}4",
                                "invoke_payload": {
                                    "StatusCode": 200,
                                    "sleep": 0.4
                                }
                            }  # ,
                            # {
                            # "function_name": f"{experiment_name}3",
                            # "invoke_payload": {
                            #     "StatusCode": 200,
                            #     "sleep": 0.4
                            #     }
                            # }
                        ]
                    }
                }
            ]
        }
    },
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": "test"
        }
    }
]

invoke_nested2 = [
    {
        "function_name": f"{experiment_name}1",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2,
            "invoke_nested": [
                {
                    "function_name": f"{experiment_name}4",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2
                    }
                },
                {
                    "function_name": f"{experiment_name}1",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2
                    }
                }
            ]
        }
    },

]

invoke_nested3 = [
    {
        "function_name": f"{experiment_name}2",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2,
            "invoke_nested": [
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2
                    }
                },
                {
                    "function_name": f"{experiment_name}3",
                    "invoke_payload": {
                        "StatusCode": 200,
                        "sleep": 0.2,
                        "invoke_nested": [
                            {
                                "function_name": f"{experiment_name}4",
                                "invoke_payload": {
                                    "StatusCode": 200,
                                    "sleep": 0.2
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
]


provider = provider('/home/thomas/Msc/faas-benchmarker/benchmark/DB_interface/.test_env')
# test = provider.invoke_function(function)
# pprint(test)
print()
response_dict = provider.invoke_function('function1', 0.0, invoke_nested2)
pprint(response_dict)
root = response_dict['root_identifier']
t = type(response_dict[root]['error']['message'])

print(t)
print(type(t))

pprint(response_dict)
for x in list(response_dict):
    print(x,'->',response_dict[x])
    print()


