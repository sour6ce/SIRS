from math import sqrt
from typing import Dict, Iterable, List, Set
from ..core import IRCollection, IRS
from .__vcache import VectorCSVCache
from ..core import DOCID, INDEX
from os import path
import numpy as np


class VectorIRCollection(IRCollection):
    cache: VectorCSVCache = VectorCSVCache(
        path.abspath(
            path.join(path.dirname(__file__), 'vector.cache.csv')
        )
    )

    def __get_index(self, doc: DOCID) -> INDEX:
        irs: IRS = self.irs
        rd = irs.data_getter(doc)
        ind = irs.indexer(rd)
        return ind

    def add_document(self, document: DOCID) -> None:
        if document not in self.cache.fullData:
            ind = self.__get_index(document)
            self.cache.add_document((document, ind))
            self.cache.save()

    def add_documents(self, documents: Iterable[DOCID]) -> None:
        docs = np.array(list(
            (
                d for d in documents if d not in self.cache.fullData
            )
        )
        )

        n_d = list(((d, self.__get_index(d)) for d in docs))
        self.cache.add_documents(n_d)
        self.cache.save()

    def get_relevance(self, query: Dict[str, int],
                      doc: DOCID) -> float:

        # TODO: Use weighted values (tf,idf,etc) instead of just frequency

        d_vec = self.cache.fullData[doc]  # Document related vector
        q_vec = np.fromiter(
            (query.get(word, 0) for word in d_vec.index),
            dtype=int)  # Query related vector

        mult = np.sum(d_vec*q_vec)  # Dot product

        n_q = sqrt(np.sum(q_vec*q_vec))  # Query vector distance
        n_d = sqrt(np.sum(d_vec*d_vec))  # Document vector distance

        if abs(n_d) <= 1e-8:
            return -1

        sim = mult/(n_d*n_q)

        return sim

    def get_documents(self) -> List[DOCID]:
        return list(self.cache.fullData.columns)
