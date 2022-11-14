from typing import Dict
from ..core import IRQuerifier
from ..tokenizer import tokenize
import pandas as pd

class VectorIRQuerifier(IRQuerifier):
    def querify(self, query: str) -> pd.DataFrame:
        r = {}
        # Creates a dictionary indexed by terms that stores the
        # frequency of the term in the query (used as weight temporarily)
        for s in tokenize(query):
            r[s] = r.get(s, 0)+1

        qs = pd.Series(data=r.values(), index=r.keys())
        qdf = pd.DataFrame({'query': qs})

        return qdf
