from .__raw import DOCID
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List


class IRRanker(ABC):
    '''
    Creates a ranking/list to show the document as a search result
    from a list of this documents with their relevance function.
    '''
    @abstractmethod
    def rank(self, docs: Iterable[DOCID],
             rel_func: Callable[[DOCID], Any]) -> List[DOCID]:
        '''
        Main method of the ranking class.
        '''
        pass

    def __call__(self, docs: Iterable[DOCID],
                 rel_func: Callable[[DOCID], Any]) -> List[DOCID]:
        '''
        Calls the `rank` method.
        '''
        return self.rank(docs, rel_func)
