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

'''
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
#Correlacion de K-Means
def get_term_correlations(df: pd.DataFrame, n_clusters: int = 10) -> Dict[str, Dict[str, float]]:
    # Calculate term correlations using K-means clustering
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(df)

    # Create dictionary to store term correlations
    term_correlations = {}

    # Iterate over all terms in dataframe
    for term in df.index:
        # Get cluster index for term
        cluster_index = kmeans.predict([df.loc[term]])[0]

        # Get cluster center for term
        cluster_center = kmeans.cluster_centers_[cluster_index]

        # Get other terms in same cluster
        cluster_terms = df[kmeans.labels_ == cluster_index].index

        # Calculate correlations for term
        correlations = {}
        for ct in cluster_terms:
            # Calculate correlation coefficient between term and ct
            coef = pearsonr(df.loc[term], df.loc[ct])[0]
            
            # Store correlation coefficient in dictionary
            correlations[ct] = coef

        # Add term correlations to dictionary
        term_correlations[term] = correlations

    return term_correlations


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

        # Set the average of correlation, it could be change, the values are between 0 and 1
        correlation_threshold = 0.8
        
        # Calculate term correlationsss
        term_correlations = get_term_correlations(qs)

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



