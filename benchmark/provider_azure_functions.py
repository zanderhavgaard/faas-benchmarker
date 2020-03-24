from provider_abstract import AbstractProvider


class AzureFunctionsProvider(AbstractProvider):

    def invoke_function(self,
                        name: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:
        pass
