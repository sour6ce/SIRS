from abc import ABC, abstractmethod
from typing import Any, Iterable, List
from .__irdocument import IRDocument


class IRCollection(ABC):
    '''
    Collection of an IR system that stores the documents and terms indexed.

    Specific models implementations may also store extra info about the index
    structure.
    '''

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add_document(self, document: IRDocument) -> bool:
        '''
        Method to add a document to the collection. 

        Returns `True` if the document added successfully,
        `False` otherwise.
        '''
        pass

    @abstractmethod
    def add_documents(self, documents: Iterable[IRDocument]) -> Iterable[bool]:
        '''
        Method to add more than one document to the collection.
        Separated from the single version to allow optimization.

        Returns an `Iterable` of boolean telling which documents
        added successfully.
        '''
        pass

    @abstractmethod
    def get_relevance(self, query: Any,
                      doc: IRDocument) -> Any:
        '''
        Method to get a relevance object from a
        query with a given `IRDocument` of the system.
        '''
        pass

    def __contains__(self, __o: IRDocument | str):
        if isinstance(__o, str):
            return __o in self.terms
        if isinstance(__o, IRDocument):
            return __o in self.documents

    @abstractmethod
    def get_documents(self) -> List[IRDocument]:
        pass
