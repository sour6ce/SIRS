from itertools import islice
from math import sqrt
from os import path
from typing import Callable, Dict, Iterable, List
from engine.core import IRDocument, IRCollection, IRQuerifier, IRRanker, IRS
from engine.tokenizer import tokenize
from engine.cache import VectorCSVCache


class VectorIRCollection(IRCollection):
    cache: VectorCSVCache = VectorCSVCache(
        path.abspath(
            path.join(path.dirname(__file__), 'vector.cache.csv')
        )
    )
    def add_document(self, document: IRDocument) -> bool:
        self.cache.add_document(document)
        self.cache.recalculateDataCache()

    def add_documents(self, documents: Iterable[IRDocument]) -> Iterable[bool]:
        self.cache.add_documents(list(documents))
        self.cache.recalculateDataCache()

    def get_relevance(self, query: Dict[str, int],
                      doc: IRDocument) -> float:

        # TODO: Use weighted values (tf,idf,etc) instead of just frequency

        # Use only the terms in the query
        ts = [t for t in query.keys()]

        q_vec = [query[t] for t in ts]  # Query related vector
        d_vec = [doc.terms.get(t, 0) for t in ts]  # Document related vector

        mult = sum((x*y for x, y in zip(q_vec, d_vec)))  # Dot product

        n_q = sqrt(sum((x*x for x in q_vec)))  # Query vector distance
        n_d = sqrt(sum((x*x for x in d_vec)))  # Document vector distance

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
