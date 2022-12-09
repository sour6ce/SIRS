
from abc import ABC, abstractmethod
from typing import Any


class IRQuerifier(ABC):
    '''
    Cast a text natural query into an object that the `IRCollection`
    should understand. 
    '''
    @abstractmethod
    def querify(self, query: str) -> Any:
        '''
        Main method of the class to cast.
        '''
        pass

    def __call__(self, query: str) -> Any:
        '''
        Calls the `querify` method.
        '''
        return self.querify(query)

    @abstractmethod
    def get_hash(self) -> str:
        '''
        Method to get a hash to identify the last query querified.
        Used for engine optimizations.
        '''
        pass
