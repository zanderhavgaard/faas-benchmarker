import json
import requests
from pprint import pprint

code = 'YTg3NDRiNTYxYzM0OTdmYjY2MzNhYTdl'

function_name = 'changeme'
url1 = f'https://{function_name}1.azurewebsites.net/api/{function_name}1?code={code}'
url2 = f'https://{function_name}2.azurewebsites.net/api/{function_name}2?code={code}'
url3 = f'https://{function_name}3.azurewebsites.net/api/{function_name}3?code={code}'

#  url1 = f'http://localhost:7071/api/changeme1'
#  url2 = f'http://localhost:7072/api/changeme2'
#  url3 = f'http://localhost:7073/api/changeme3'

headers = {
    'Content-Type': 'application/json'
}
body = {
    "StatusCode": 200,
    "sleep": 1.0,
    "invoke_nested": [
        {
            "function_name": f"{function_name}2",
            "invoke_payload": {
                "StatusCode": 200,
                "sleep": 0.2,
                "invoke_nested": [
                    {
                        "function_name": f"{function_name}3",
                        "invoke_payload": {
                            "StatusCode": 200,
                            "sleep": 0.2
                        },
                        "code": code
                    },
                    {
                        "function_name": f"{function_name}3",
                        "invoke_payload": {
                            "StatusCode": 200,
                            "sleep": 0.2
                        },
                        "code": code
                    }
                ]
            },
            "code": code
        }
    ]
}

response1 = requests.post(
    url=url1,
    headers=headers,
    data=json.dumps(body)
)

print('invoking function1')
print(url1)
print(response1)
pprint(response1.json())

#  body = {
#  "StatusCode": 200,
#  "sleep": 0.5
#  }

response2 = requests.post(
    url=url2,
    headers=headers,
    data=json.dumps(body)
)

print('invoking function2')
print(url2)
print(response2)
pprint(response2.json())

#  body = {
#  "StatusCode": 200,
#  "sleep": 0.5
#  }

response3 = requests.post(
    url=url3,
    headers=headers,
    data=json.dumps(body)
)

print('invoking function3')
print(url3)
print(response3)
pprint(response3.json())
