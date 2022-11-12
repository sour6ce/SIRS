from itertools import islice
from math import sqrt
from os import path
from typing import Callable, Dict, Iterable, List
from engine.core import IRDocument, IRCollection, IRQuerifier, IRRanker, IRS
from engine.tokenizer import tokenize
from engine.cache import VectorCSVCache
import numpy as np


class VectorIRCollection(IRCollection):
    cache: VectorCSVCache = VectorCSVCache(
        path.abspath(
            path.join(path.dirname(__file__), 'vector.cache.csv')
        )
    )

    def add_document(self, document: IRDocument) -> bool:
        if document.doc.doc_id in self.cache.fullData:
            return False
        self.cache.add_document(document)
        self.cache.save()
        return True

    def add_documents(self, documents: Iterable[IRDocument]) -> Iterable[bool]:
        docs = np.array(list(documents))
        r = np.array([d.doc.doc_id not in self.cache.fullData for d in docs])

        n_d = list((d for d, new in zip(docs, r) if new))
        self.cache.add_documents(n_d)
        self.cache.save()
        return r

    def get_relevance(self, query: Dict[str, int],
                      doc: IRDocument) -> float:

        # TODO: Use weighted values (tf,idf,etc) instead of just frequency

        d_vec = self.cache.fullData[doc.doc.doc_id]  # Document related vector
        q_vec = np.array((query.get(word, 0)
                         for word in d_vec.index))  # Query related vector

        mult = np.sum(d_vec*q_vec)  # Dot product

        n_q = sqrt(np.sum(q_vec*q_vec))  # Query vector distance
        n_d = sqrt(np.sum(d_vec*d_vec))  # Document vector distance

        if abs(n_d) <= 1e-8:
            return -1

        sim = mult/(n_d*n_q)

        return sim


class VectorIRQuerifier(IRQuerifier):
    def querify(self, query: str) -> Dict[str, int]:
        r = {}
        # Creates a dictionary indexed by terms that stores the
        # frequency of the term in the query (used as weight temporarily)
        for s in tokenize(query):
            r[s] = r.get(s, 0)+1
        return r


class VectorIRRanker(IRRanker):
    def rank(
            self, docs: Iterable[IRDocument],
            rel_func: Callable[[IRDocument], float]
    ) -> List[IRDocument]:
        docs = list(docs)  # List out of the documents

        # List of the same size with relevance
        rel = [rel_func(d) for d in docs]

        # Zip both lists into tuples (relevance,document) for sorting
        l = list(zip(rel, docs))
        l.sort(reverse=True)

        # Gets the first index where the relevance is zero or less
        # (first not relevant document)
        n_index = next((i for i, (r, _) in enumerate(l) if r <= .0), len(l))

        # Get only the documents from the sorted tuple list while the
        # first not relevant document has not been reached
        l = [d for _, d in islice(l, n_index)]

        return l


class VectorIRS(IRS):
    ranker = VectorIRRanker()
    collection = VectorIRCollection()
    querifier = VectorIRQuerifier()
