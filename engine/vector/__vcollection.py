from math import sqrt
from typing import Dict, Iterable, List, Set
from ..core import IRCollection
from .__vcache import VectorCSVCache
from ..core import IRDocument
from os import path
import numpy as np


class VectorIRCollection(IRCollection):
    cache: VectorCSVCache = VectorCSVCache(
        path.abspath(
            path.join(path.dirname(__file__), 'vector.cache.csv')
        )
    )
    docsid: Set[str] = set()
    documents: List[IRDocument] = []

    def add_document(self, document: IRDocument) -> bool:
        id = document.doc.doc_id
        if id not in self.docsid:
            self.docsid.add(id)
            self.documents.append(document)
        if id in self.cache.fullData:
            return False
        self.cache.add_document(document)
        self.cache.save()
        return True

    def add_documents(self, documents: Iterable[IRDocument]) -> Iterable[bool]:
        docs = np.array(list(documents))
        r = np.array([d.doc.doc_id not in self.cache.fullData for d in docs])

        for d in docs:
            id: int = d.doc.doc_id
            if id not in self.docsid:
                self.docsid.add(id)
                self.documents.append(d)

        n_d = list((d for d, new in zip(docs, r) if new))
        self.cache.add_documents(n_d)
        self.cache.save()
        return r

    def get_relevance(self, query: Dict[str, int],
                      doc: IRDocument) -> float:

        # TODO: Use weighted values (tf,idf,etc) instead of just frequency

        d_vec = self.cache.fullData[doc.doc.doc_id]  # Document related vector
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

    def get_documents(self) -> List[IRDocument]:
        return self.documents
