from typing import Iterable, List
from .__ircollection import IRCollection
from .__irindexer import IRIndexer
from .__raw import RawDataGetter, DOCID, fx
from .__irquerifier import IRQuerifier
from .__irranker import IRRanker

class IRS():
    '''
    Main class of the engine, works as a pipeline for main operations
    in the IR system (add documents and)
    '''
    __indexer: IRIndexer = IRIndexer()
    __collection: IRCollection
    __querifier: IRQuerifier
    __ranker: IRRanker
    __data_getter: RawDataGetter

    @property
    def indexer(self) -> IRIndexer:
        return self.__indexer

    @indexer.setter
    def indexer(self, value) -> None:
        self.__indexer = value
        self.__indexer.irs = self

    @property
    def collection(self) -> IRCollection:
        return self.__collection

    @collection.setter
    def collection(self, value) -> None:
        self.__collection = value
        self.__collection.irs = self

    @property
    def querifier(self) -> IRQuerifier:
        return self.__querifier

    @querifier.setter
    def querifier(self, value) -> None:
        self.__querifier = value
        self.__querifier.irs = self

    @property
    def ranker(self) -> IRCollection:
        return self.__ranker

    @ranker.setter
    def ranker(self, value) -> None:
        self.__ranker = value
        self.__ranker.irs = self

    @property
    def data_getter(self) -> IRCollection:
        return self.__data_getter

    @data_getter.setter
    def data_getter(self, value) -> None:
        self.__data_getter = value
        self.__data_getter.irs = self

    def add_document(self, doc: DOCID) -> bool:
        return self.collection.add_document(fx(doc))

    def add_documents(self, docs: Iterable[DOCID]) -> bool:
        coll = self.collection
        return coll.add_documents([fx(d) for d in list(docs)])

    def query(self, q: str) -> List[DOCID]:
        proc_q = (self.querifier)(q)
        return self.ranker(
            self.collection.get_documents(),
            lambda x: self.collection.get_relevance(proc_q, x)
        )
