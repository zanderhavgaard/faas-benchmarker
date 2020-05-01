from provider_openfaas import OpenFaasProvider as provider
from pprint import pprint

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

# add fault dict to cloudfunctions
                                                                     





experiment_name = 'function'
function = 'function1'
sleep = 0.1
invoke_nested = [
    {
        "function_name": f"{experiment_name}3",
        "invoke_payload": {
            "StatusCode": 200,
            "sleep": 0.2,
            "invoke_nested": [
                {
                    "function_name": f"{experiment_name}1",
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
                            "function_name": f"{experiment_name}2",
                            "invoke_payload": {
                                "StatusCode": 200,
                                "sleep": 0.4
                                }
                            } #,
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
            "sleep": 0.2
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
                    "function_name": f"{experiment_name}1",
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


provider = provider('/home/thomas/Msc/faas-benchmarker/DB_interface/.test_env')
# test = provider.invoke_function(function)
# pprint(test)
# print()
response_dict = provider.invoke_function(function,sleep,invoke_nested)
# print(list(response_dict))

pprint(response_dict)
# for x in list(response_dict):
#     pprint(response_dict[x])
#     print()