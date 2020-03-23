# import Abstract Base Class module
# to add abstract class functionality
from abc import ABC, abstractmethod


class AbstractProvider(ABC):

    @abstractmethod
    def invoke_function(self, name: str, sleep=0.0, invoke_nested=None):
        pass

    # TODO
    #  @abstractmethod
    #  def invoke_function_concurrently()
        #  pass
