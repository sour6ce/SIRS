from abc import ABC, abstractmethod
from typing import List, NamedTuple
DOCID = str


class RawDocumentData(NamedTuple):
    '''
    Stores the document raw information (id, title, and text to index)
    '''
    doc_id: DOCID
    title: str
    text: str


class RawDataGetter(ABC):
    '''
    Gives access to document data from an id.
    '''
    @abstractmethod
    def getdata(self, doc: DOCID) -> RawDocumentData:
        pass

    def __call__(self, doc: DOCID) -> RawDocumentData:
        return self.getdata(doc)

    @abstractmethod
    def getall(self) -> List[DOCID]:
        pass


def ifx(did: DOCID) -> bool:
    return did.startswith('ID:')


def fx(did: DOCID) -> DOCID:
    return did if ifx(did) else f'ID:{did}'


def dfx(did: DOCID) -> DOCID:
    return did if not ifx(did) else did[3:]
