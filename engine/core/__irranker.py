
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List
from .__irdocument import IRDocument


class IRRanker(ABC):
    '''
    Creates a ranking/list to show the document as a search result
    from a list of this documents with their relevance function.
    '''
    @abstractmethod
    def rank(self, docs: Iterable[IRDocument],
             rel_func: Callable[[IRDocument], Any]) -> List[IRDocument]:
        '''
        Main method of the ranking class.
        '''
        pass

    def __call__(self, docs: Iterable[IRDocument],
                 rel_func: Callable[[IRDocument], Any]) -> List[IRDocument]:
        '''
        Calls the `rank` method.
        '''
        return self.rank(docs, rel_func)
