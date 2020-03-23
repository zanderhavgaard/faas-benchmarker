from abstract_provider import AbstractProvider


class ProviderOpenFaas(AbstractProvider):

    def invoke_function(self,
                        name: str,
                        sleep: float = 0.0,
                        invoke_nested: dict = None) -> dict:
        pass
