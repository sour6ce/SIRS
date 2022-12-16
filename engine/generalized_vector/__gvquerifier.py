from sklearn.cluster import KMeans
from engine.vector.__vquerifier import VectorIRQuerifier
from ..tokenizer import tokenize
from typing import Dict, Iterable, List, Tuple
from ..core import IRCollection, IRS
from ..core import DOCID, INDEX
from os import path
import numpy as np
from scipy.stats import pearsonr
import pandas as pd

class GeneralizedVectorIRQuerifier(VectorIRQuerifier):
    __last = None
    
    def querify(self, query: str) -> pd.DataFrame:
        # Create dictionary of term frequencies in query
        term_frequencies = {}
        for s in tokenize(query):
            term_frequencies[s] = term_frequencies.get(s, 0)+1

        # Convert dictionary to pandas series
        qs = pd.Series(data=term_frequencies.values(), index=term_frequencies.keys())
        qdf = pd.DataFrame({'query': qs})
        
        # Sort index of query dataframe
        qdf.sort_index(inplace=True)
        qdf.index.name = 'term'

        self.__last = qdf

        return qdf



