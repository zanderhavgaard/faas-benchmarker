from provider_abstract import AbstractProvider


class AzureFunctionsProvider(AbstractProvider):

    def __init__(self, env_file_path: str) -> AzureFunctionProvider:

        # load azurw functions specific invocation url and credentials
        self.load_env_vars(env_file_path)

        # http headers, contains data type
        self.headers = {
            'Content-Type': 'application/json'
        }


    # load .env file and parse values
    def load_env_vars(self, env_file_path: str) -> None:
        dotenv.load_dotenv(dotenv_path=env_file_path)
        self.function_app_url = os.getenv('function_app_url)')
        self.function_key = os.getenv('function_key')

    # for azure functions the name refers to the function name
    # the functions are available under
    # https://<funtion_app_name>/api/<function_name>?code=<function_key>
    def invoke_function(self,
                        name: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:

        # paramters, the only required paramter is the statuscode
        params = {
            "StatusCode": 200
        }

        # add optional sleep parameter if present
        if sleep != 0.0:
            params['sleep'] = sleep

        # add optional dict describing nested invocations, if presente
        if invoke_nested != None:
            params['invoke_nested'] = invoke_nested

        # log start time of invocation
        start_time = time.time()

        # create url of function to invoke
        invoke_url = f'https://{self.function_app_url}/api/{name}?code={self.function_key}'

        # invoke the function
        response = requests.post(
            url=invoke_url,
            headers=self.headers,
            data=json.dumps(params)
        )

        # log the end time of the invocation
        end_time = time.time()

        # parse response json
        response_data = response.json()

        # parse reponse body json
        response_data['body'] = json.loads(response_data['body'])

        # get the identifer
        identifier = response_data['identifier']

        # add start / end times to body
        response_data['body'][identifier]['invocation_start'] = start_time
        response_data['body'][identifier]['invocation_end'] = end_time

        return response_data
