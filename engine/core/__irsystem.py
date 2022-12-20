from itertools import islice
from typing import Any, Dict, Iterable, List, Tuple
from .__ircollection import IRCollection
from .__irindexer import IRIndexer, INDEX
from .__raw import RawDataGetter, DOCID, fx
from .__irquerifier import IRQuerifier
from .__raw import dfx


class IRS():
    '''
    Main class of the engine, works as a pipeline for main operations
    in the IR system (add documents and)
    '''
    __indexer: IRIndexer = IRIndexer()
    __collection: IRCollection
    __querifier: IRQuerifier
    __data_getter: RawDataGetter

    # Buffer to store results of a query
    _query_buffer: Dict[str, List[Tuple[DOCID, float]]] = {}

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
    def data_getter(self) -> IRCollection:
        return self.__data_getter

    @data_getter.setter
    def data_getter(self, value) -> None:
        self.__data_getter = value
        self.__data_getter.irs = self

    def add_document(self, doc: DOCID) -> None:
        self.collection.add_document(fx(doc))
        self._query_buffer.clear()

    def add_documents(self, docs: Iterable[DOCID]) -> None:
        coll = self.collection
        coll.add_documents([fx(d) for d in list(docs)])
        self._query_buffer.clear()

    def index_doc(self, doc: DOCID) -> INDEX:
        rd = self.data_getter(dfx(doc))
        ind = self.indexer(rd)
        return ind

    def query(self, q: str) -> List[DOCID]:
        '''
        Get a ranking of documents from a query as a text.
        '''
        r = self.pre_query(q)

        # Filter relevance >=0
        n_index = next((i for i, (_, rel) in enumerate(r) if rel <= .0), len(r))
        rank = [d for d, _ in islice(r, n_index)]

        return rank

    def pre_query(self, q) -> List[Tuple[DOCID, Any]]:
        '''
        Connect the Querifier to the Collection in order to get
        '''
        proc_q = (self.querifier)(q)

        q_hash = self.querifier.get_hash()

        r = []

        # Search first in the buffer
        if (q_hash in self._query_buffer.keys()):
            r = self._query_buffer[q_hash]
        else:
            # Calculates relevance of all documents
            r = [(dfx(id), r)
                 for id, r in self.collection.get_relevances(proc_q)]
            # Update the buffer
            self._query_buffer[q_hash] = r
        return r
