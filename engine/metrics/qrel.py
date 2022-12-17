from abc import ABC, abstractmethod
from typing import Dict, List, NamedTuple

from ..core import DOCID


class Qrel(NamedTuple):
    query_id: str
    query: str
    relevants: Dict[DOCID, float]


class QrelGetter(ABC):
    '''
    Gives access to qrels data from a dataset.
    '''
    @abstractmethod
    def getqrels(self) -> List[Qrel]:
        pass

    def __call__(self) -> List[Qrel]:
        return self.getqrels()
