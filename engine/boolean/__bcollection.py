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
        
        #concat vector to the data frame and obtain data frame and vector modificated
        for q1, q2 in query0, query_bm:
            #data frame with terms vectors concated
            q1.columns.set_names('test')
            df1 = (pd.concat([df1,q1]).fillna(0).groupby('term'))
            q1 = df1['test']
            df1 = df1.drop('test')
            
            #data frame with boolean mask concated
            q2.columns.set_names('test')            
            df2 = (pd.concat([df2,q2]).fillna(0).groupby('term'))
            q2 = df2['test']
            df2 = df2.drop('test')
        
        #missing Xor annd * and 0 comprobation to relevance

        return 0
