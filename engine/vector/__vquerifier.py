from typing import Dict
from ..core import IRQuerifier
from ..tokenizer import tokenize


class VectorIRQuerifier(IRQuerifier):
    def querify(self, query: str) -> Dict[str, int]:
        r = {}
        # Creates a dictionary indexed by terms that stores the
        # frequency of the term in the query (used as weight temporarily)
        for s in tokenize(query):
            r[s] = r.get(s, 0)+1
        return r
