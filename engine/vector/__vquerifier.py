import json
from typing import Dict
from ..core import IRQuerifier
from ..tokenizer import tokenize
import hashlib

class VectorIRQuerifier(IRQuerifier):
    __last = None

    def querify(self, query: str) -> Dict[str, int]:
        r = {}
        # Creates a dictionary indexed by terms that stores the
        # frequency of the term in the query (used as weight temporarily)
        for s in tokenize(query):
            r[s] = r.get(s, 0)+1

        self.__last = r

        return r

    def get_hash(self) -> str:
        if self.__last is None:
            return ''
        else:
            h = hashlib.sha512()
            h.update(json.dumps(self.__last).encode())
            return h.hexdigest()
