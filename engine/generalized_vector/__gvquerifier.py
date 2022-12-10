from ast import Dict
from engine.vector.__vquerifier import VectorIRQuerifier
from ..tokenizer import tokenize
import pandas as pd
import numpy as np

#Correlación de Pearson
def get_term_correlations(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    correlations = {}
    for term1 in df.columns:
        correlations[term1] = {}
        for term2 in df.columns:
            if term1 == term2:
                continue

            # Calculate Pearson correlation
            corr = df[term1].corr(df[term2])
            correlations[term1][term2] = corr

    return correlations

'''
class GeneralizedVectorIRQuerifier(VectorIRQuerifier):
    __last = None
    
    def querify(self, query: str) -> pd.DataFrame:
        # Create dictionary of term frequencies in query
        r = {}
        for s in tokenize(query):
            r[s] = r.get(s, 0)+1

        # Convert dictionary to pandas series
        qs = pd.Series(data=r.values(), index=r.keys())
        qdf = pd.DataFrame({'query': qs})

        # Get term frequencies in documents
        df = collection.get_term_frequencies()

        # Calculate term correlations
        term_correlations = get_term_correlations(df)

        # Include correlated terms in query
        for term in qdf.index:
            # Get correlated terms for term
            correlated_terms = term_correlations[term]

            # Filter correlated terms by correlation threshold
            correlated_terms = {
                k: v for k, v in correlated_terms.items() if v >= correlation_threshold
            }

            # Add correlated terms to query with frequency equal to correlation
            for correlated_term, correlation in correlated_terms.items():
                qdf.loc[correlated_term, 'query'] = correlation

        # Sort index of query dataframe
        qdf.sort_index(inplace=True)
        qdf.index.name = 'term'

        self.__last = qdf

        return qdf
'''
class GeneralizedVectorIRQuerifier(VectorIRQuerifier):
    pass


