from math import sqrt
from typing import Dict, Iterable, List, Tuple
from ..core import IRCollection, IRS
from ..core import DOCID, INDEX
from engine.vector.__vcollection import VectorIRCollection
from os import path
import numpy as np
import pandas as pd
import math

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

    def generalizedModelModification(self,df0):
        for doc in df0:
            new_doc = [0]*len(doc)
            for i, weight in enumerate(doc):
                new_doc += weight * get_ki(i)
                
            # TODO: update column with new_doc
        
        
    
    def from_bin_to_num(bool_vector):
        return sum(
            (bit_activated * 2**i for i, bit_activated in enumerate(bool_vector))
        ) 
    
    def corpus_minterms(self,df0) -> Iterable[Tuple[List[bool], int]]:
        """
        different minterms of the entire corpus, returned in tuple form:
        (minterm m_r, r)
        """
        
        df1 = df0.astype(bool)
        df1.drop(df1.columns[pd.duplicates], axis=1)
        
        return map(
            lambda bool_doc: 
                (bool_doc, 1+from_bin_to_num(bool_doc)), 
            df1
        )
        
    def doc_matches_minterm(doc, m_r):
        for i, freq in enumerate(doc):
            match_at_i = freq and m_r[i] or not freq and not m_r[i]
            if not match_at_i:
                return False
            
        return True
        
    
    def get_correlation_factor(self,i, m_r):
        """look formula in book"""
        c_ir = 0
        for doc in df0.columns:
            if doc_matches_minterm(doc, m_r):
                c_ir += df0[doc][i]
                
        return c_ir
                
        
    def get_zeroes_vector_with_1_in(self,r, number_of_terms):
        """(it falls from the tree)"""
        vector = [0]*number_of_terms
        vector[r] = 1
        return vector
    
    def get_ki(self,i):
        up =0
        down = 0
        
        for m_r, r in corpus_minterms(df0):
            c_ir = get_correlation_factor(i, m_r)
            m_r_vector = get_zeroes_vector_with_1_in(r-1)
            
            if m_r[i]:
                up += c_ir * m_r_vector
                down += c_ir*c_ir 
            
        down = math.sqrt(down)
        
        ki = up/down
        return ki

    def get_relevances(
            self, query: pd.DataFrame) -> List[Tuple[DOCID, float]]:
        query.columns.set_names('query')

        df0 = self.cache.fullData
        
        
        df0 = generalizedModelModification(self,df0)

        maxfr = df0.max()
        ni = df0.astype(bool).sum(axis=1)
        N = len(df0.columns)
        idf = ni/N
        idf = idf.pow(-1)
        idf = np.log(idf)

        df0 /= maxfr  # tf  NOTE oe gabriel xq esto no esta mal (signo de interrogacion)

        maxfrq = query.max()
        query /= maxfrq
        query *= 1-A
        query += A

        df = (pd.concat([df0, query]).fillna(0).groupby('term').sum().T*(idf)).T

        query = df['query']

        dup_df = df * df
        dup_df = dup_df.sum()

        nd_df = np.sqrt(dup_df)
        nq_df = nd_df['query']

        df.drop('query', axis=1, inplace=True)
        mult_df = query@df

        nd_df.drop('query', inplace=True)
        r: pd.DataFrame = mult_df/nd_df
        r /= nq_df

        r.sort_values(inplace=True, ascending=False)

        return [(k, v) for k, v in r.items()]

