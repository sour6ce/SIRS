from math import sqrt
from typing import Dict, Iterable, List, Tuple
from ..core import IRCollection, IRS
from ..core import DOCID, INDEX
from engine.vector.__vcollection import VectorIRCollection
from os import path
import numpy as np
import pandas as pd

class GeneralizedVectorIRCollection(VectorIRCollection):
    def __init__(self):
        super().__init__()
        self.k1 = 1.2  # Parámetro de ajuste k1
        self.k3 = 1000  # Parámetro de ajuste k3
        self.b = 0.75  # Parámetro de sesgo del documento
        self.avdl = 0  # Tamaño promedio de los documentos en el corpus

    def get_relevance(self, query: pd.DataFrame, doc: DOCID) -> float:
        df = self.cache.fullData

        query.index.name = 'term'
        d_vec = df[df[doc] != 0][doc]  # Document related vector
        d_vec.index.name = 'term'
        df = pd.concat([d_vec, query]).fillna(0).groupby('term').sum()

        d_vec = np.array(df[0])
        q_vec = np.array(df['query'])

        doclen = len(d_vec)  # Document length
        qtf = q_vec[0]  # Term frequency in query

        invdl = 1/doclen  # Inverse document length

        # Calculate BM25 score
        sim = (self.k1 + 1)*qtf*(self.k3 + 1)*invdl/((self.k1*((1-self.b) + self.b*doclen/self.avdl) + qtf)*(self.k3 + tf))

        return sim
    
    def get_relevances(self, query: pd.DataFrame) -> List[Tuple[DOCID, float]]:
        query.columns.set_names('query')

        df0 = self.cache.fullData

        maxfr = df0.max()
        ni = df0.astype(bool).sum(axis=1)
        N = len(df0.columns)
        idf = ni/N
        idf = idf.pow(-1)
        idf = np.log(idf)

        df0 /= maxfr  # tf

        df = (pd.concat([df0, query]).fillna(0).groupby('term').sum().T*(idf)).T

        query = df['query']

        # Calculate BM25 scores for each document
        scores = []
        for doc in df.columns:
            d_vec = df[doc]  # Document vector
            doclen = len(d_vec)  # Document length
            qtf = query[0]  # Term frequency in query

            invdl = 1/doclen  # Inverse document length

            # Calculate BM25 score
            sim = (self.k1 + 1)*qtf*(self.k3 + 1)*invdl/((self.k1*((1-self.b) + self.b*doclen/self.avdl) + qtf)*(self.k3 + tf))
            scores.append((doc, sim))

        scores.sort(key=lambda x: x[1], reverse=True)

        return scores
