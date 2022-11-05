from itertools import islice
from math import sqrt
from typing import Callable, Dict, Iterable, List
from engine.core import IRDocument, IRTerm, IRCollection, IRQuerifier, IRRanker, IRS
from engine.tokenizer import tokenize


class VectorIRCollection(IRCollection):
    def add_document(self, document: IRDocument) -> bool:
        if document in self.documents:
            # The document is already in the collection
            return False
        for term in document.tokens:
            # Includes the term in the set of terms in the collection
            self.terms.add(term)

            # Includes the document in the set of documents in the collection
            self.documents.add(document)

            # Get a unique term (document as parameter may came with term that
            # has the same text but it's not the same in the collection). This
            # allows to change a unique object instance each time the same
            # string comes as term
            term = next((t for t in self.terms if t == term), term)

            # The document should store a dictionary with the frequency of
            # each term

            # Get the dictionary stored of an empty one if not created and
            # set it
            document.terms: Dict[IRTerm, int] = getattr(document, 'terms', {})
            # Get the frequency of a term in that document or zero if first
            # occurrence and increase it in one
            document.terms[term] = document.terms.get(term, 0) + 1

            # Similar to the two lines above, each term will stores a
            # dictionary with their frequency in each document.
            term.documents: Dict[IRDocument, int] = getattr(
                document, 'documents', {})
            term.documents[document] = term.documents.get(document, 0)+1

    def add_documents(self, documents: Iterable[IRDocument]) -> Iterable[bool]:
        return [self.add_document(d) for d in documents]

    def get_relevance(self, query: Dict[IRTerm, int],
                      doc: IRDocument) -> float:

        # TODO: Use weighted values (tf,idf,etc) instead of just frequency

        # Use only the terms in the query
        ts = (t for t in query.keys())

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
    def querify(self, query: str) -> Dict[IRTerm, int]:
        r = {}
        # Creates a dictionary indexed by terms that stores the
        # frequency of the term in the query (used as weight temporarily)
        for s in tokenize(query):
            r[IRTerm(s)] = r.get(IRTerm(s), 0)+1
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
        n_index = next((i for i, v in l if v <= .0), len(l))

        # Get only the documents from the sorted tuple list while the
        # first not relevant document has not been reached
        l = [d for _, d in islice(l, n_index)]

        return l


class VectorIRS(IRS):
    ranker = VectorIRRanker()
    collection = VectorIRCollection()
    querifier = VectorIRQuerifier()
