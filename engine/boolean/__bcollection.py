from math import sqrt
from typing import List, Tuple
from ..vector import VectorIRCollection
from os import path
import numpy as np
import pandas as pd
from ..core import DOCID

class BooleanIRCollection(VectorIRCollection):

    def get_relevance(self, query: pd.DataFrame,
                      doc: DOCID) -> float:

        df = self.cache.fullData

        query.index.name = 'term'
        d_vec = df[df[doc] != 0][doc]  # Document related vector
        # ds = pd.Series(data=[d for d in d_vec], index=[i for i in d_vec.index])
        # ddf = pd.DataFrame({'doc': ds})
        d_vec.index.name = 'term'
        df = pd.concat([d_vec, query]).fillna(0).groupby('term').sum()

        d_vec = np.array(df[0])
        q_vec = np.array(df['query'])

        mult = np.sum(d_vec*q_vec)  # Dot product

        n_q = sqrt(np.sum(q_vec*q_vec))  # Query vector distance
        n_d = sqrt(np.sum(d_vec*d_vec))  # Document vector distance

        if abs(n_d) <= 1e-8:
            return -1

        sim = mult/(n_d*n_q)

        return sim

    def get_relevances(
            self, query: Tuple[List[pd.DataFrame],List[pd.DataFrame]]) -> List[Tuple[DOCID, float]]:
        
        #cache vector data
        df0 = self.cache.fullData
        #matrix turned to boolean
        df1= df0.astype(bool)
        #terms vectors
        query0 = query[0]
        #boolean mask vectors
        query_bm = query[1]        
        
        # documents that match the query
        docs = set()

        # concat vector to the data frame and obtain data frame and vector modified
        for q1, q2 in zip(query0, query_bm):
            terms_size = q2.size

            # data frame with boolean mask aligned
            align = df1.align(q2, fill_value=0, axis=0)
            df_normal: pd.DataFrame = align[0]
            q2 = align[1]

            # data frame with terms vectors aligned
            q1 = df_normal.align(q1, fill_value=0, axis=0)[1]

            # Repeat every vector query to match the size in columns
            q1_r = pd.concat([q1]*df_normal.shape[1], axis=1)
            q2_r = pd.concat([q2]*df_normal.shape[1], axis=1)

            # XOR on term values (term vector)
            r_xor = np.logical_not(np.logical_xor(
                df_normal.astype(int),
                np.asarray(q1_r.astype(int))
            ))
            # Check with AND against the mask to see every term that is ok
            r_total = np.logical_and(
                r_xor.astype(int),
                np.asarray(q2_r.astype(int)))

            # Count of term that are ok for each document
            r_total: pd.Series = r_total.sum()
            r_total = r_total[r_total == terms_size]

            docs.update(r_total.index)

        return [(d, 1.0) for d in docs]
