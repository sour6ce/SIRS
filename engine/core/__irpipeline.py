from typing import Iterable, List
from .__ircollection import IRCollection
from .__irindexer import IRIndexer
from .__raw import RawDocumentData
from .__irquerifier import IRQuerifier
from .__irranker import IRRanker
from .__irdocument import IRDocument


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

    def add_document(self, doc: RawDocumentData) -> bool:
        return self.collection.add_document(self.indexer(doc))

    def add_documents(self, docs: Iterable[RawDocumentData]) -> bool:
        return self.collection.add_documents(
            (self.indexer(doc) for doc in docs)
        )

    def query(self, q: str) -> List[IRDocument]:
        proc_q = self.querifier(q)
        return self.ranker(
            self.collection.documents,
            lambda x: self.collection.get_relevance(proc_q, x)
        )
