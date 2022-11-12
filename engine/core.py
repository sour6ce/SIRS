'''Core and abstract functionality of the IR system'''

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Iterable, NamedTuple, Set
from .tokenizer import tokenize

# TODO: A big cache system (took 250s to build the system)

class RawDocument(NamedTuple):
    '''
    Stores the document raw information (id, title, and text to index)
    '''
    doc_id: str
    title: str
    text: str

class IRDocument:
    '''
    Wrapper for a document to allow store a index terms cache and extra
    information.
    '''
    tokens: List[str]
    doc: RawDocument

    def __hash__(self) -> int:
        return hash(self.doc.doc_id)

    def __str__(self) -> str:
        return self.doc.title.capitalize()

    def __repr__(self) -> str:
        return self.doc.title.capitalize()

    def __lt__(self, __o: object) -> bool:
        if isinstance(__o, IRDocument):
            return self.doc.doc_id < __o.doc.doc_id
        else:
            return self.doc.doc_id < __o

    def __gt__(self, __o: object) -> bool:
        if isinstance(__o, IRDocument):
            return self.doc.doc_id > __o.doc.doc_id
        else:
            return self.doc.doc_id > __o


class IRIndexer():
    '''
    Default Indexer which cast a `RawDocument` into a `IRDocument` extracting the
    terms (tokens) to index.
    '''

    def index(self, doc: RawDocument) -> IRDocument:
        '''
        Main method of the class to cast.
        '''
        r = IRDocument()
        r.doc = doc
        r.tokens = list(tokenize(doc.text))
        return r

    def __call__(self, doc: RawDocument) -> IRDocument:
        '''
        Calls the `index` method.
        '''
        return self.index(doc)


class IRCollection(ABC):
    '''
    Collection of an IR system that stores the documents and terms indexed.
    
    Specific models implementations may also store extra info about the index
    structure.
    '''
    terms: Set[str] = set()
    documents: Set[IRDocument] = set()

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
        if isinstance(__o,str):
            return __o in self.terms
        if isinstance(__o,IRDocument):
            return __o in self.documents


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


class IRS():
    '''
    Main class of the engine, works as a pipeline for main operations
    in the IR system (add documents and)
    '''
    indexer: IRIndexer = IRIndexer()
    collection: IRCollection
    querifier: IRQuerifier
    ranker: IRRanker

    def __init__(self) -> None:
        self.indexer.irs = self
        self.collection.irs = self
        self.querifier.irs = self
        self.ranker.irs = self

    def add_document(self, doc: RawDocument) -> bool:
        return self.collection.add_document(self.indexer(doc))

    def add_documents(self, docs: Iterable[RawDocument]) -> bool:
        return self.collection.add_documents(
            (self.indexer(doc) for doc in docs)
        )

    def query(self, q: str) -> List[IRDocument]:
        proc_q = self.querifier(q)
        return self.ranker(
            self.collection.documents,
            lambda x: self.collection.get_relevance(proc_q, x)
        )
