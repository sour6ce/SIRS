from itertools import islice
from typing import Callable, Iterable, List
from ..core import DOCID, IRRanker


class VectorIRRanker(IRRanker):
    def rank(
            self, docs: Iterable[DOCID],
            rel_func: Callable[[DOCID], float]
    ) -> List[DOCID]:
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
