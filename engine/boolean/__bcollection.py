from typing import List, Set, Tuple

from ..core import DOCID
from ..vector import VectorIRCollection


class BooleanIRCollection(VectorIRCollection):
    def get_relevance(self, query: List[Set[Tuple[str, bool]]],
                      doc: DOCID) -> float:

        doc_index = self.index.term_by_doc[doc]

        # Check if the document is valid for at least a subquery
        for sub_q in query:
            valid = True
            for term, neg in sub_q.items():
                # If the term is in the document shouldn't be a negative
                # value ~(1^1)=1, and if it's not should be a negative value
                # ~(0^0)=1. ENters the if conflict is found.
                if not ((term in doc_index) ^ neg):
                    valid = False
                    break
            if valid:
                return 1.0
        return .0

    def get_relevances(
            self, query: List[Set[Tuple[str, bool]]]) -> List[Tuple[DOCID, float]]:

        r = list({doc_id: self.get_relevance(query, doc_id)
                  for doc_id in self.index.docs}.items())
        r.sort(key=lambda x: x[1], reverse=True)

        return r
