from typing import Dict
from ..core import IRQuerifier
from ..tokenizer import tokenize
import pandas as pd
import hashlib

class LsiIRQuerifier(IRQuerifier):
    __last = None

    def querify(self, query: str) -> pd.DataFrame:
        # TODO: Replace DataFrame use for dict
        r = {}
        # Creates a dictionary indexed by terms that stores the
        # frequency of the term in the query (used as weight temporarily)
        for s in tokenize(query):
            r[s] = r.get(s, 0)+1

        qs = pd.Series(data=r.values(), index=r.keys())
        qdf = pd.DataFrame({'query': qs})
        qdf.sort_index(inplace=True)
        qdf.index.name = 'term'

        self.__last = qdf

        return qdf

    def get_hash(self) -> str:
        if self.__last is None:
            return ''
        else:
            h = hashlib.sha512()
            h.update(pd.util.hash_pandas_object(self.__last).values)
            return h.hexdigest()
