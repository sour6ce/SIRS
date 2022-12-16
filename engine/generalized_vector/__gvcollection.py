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

    def get_relevance(self, query: pd.DataFrame,
                      doc: DOCID) -> float:

        # TODO: Delete or change to tf,idf
        df = self.cache.fullData
        df = self.generalizedModelModification(df)
        
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

    def generalizedModelModification(self, df0):
        arr = np.array(df0)
        new_arr = np.zeros(arr.shape)
        
        for i in range(arr.shape[1]):
            new_arr[:, i] = np.multiply(arr[:, i], self.get_ki(i, arr))
        
        #update column with new_arr
        df0[df0.columns] = new_arr
        return new_arr
                
        
        
    
    def from_bin_to_num(bool_vector):
        bool_vector = np.array(bool_vector)
        exponents = np.arange(len(bool_vector))
        powers = np.power(2, exponents)
        return np.sum(np.dot(powers, bool_vector))

    
    def corpus_minterms(self,df0) -> Iterable[Tuple[List[bool], int]]:
        # different minterms of the entire corpus, returned in tuple form:
        # (minterm m_r, r)
        
        # convertir df0 a tipo booleano y eliminar las columnas duplicadas
        df1 = (df0.astype(bool)).drop_duplicates(axis=1)
        
        return map(
            lambda bool_doc: 
                (bool_doc, 1+ self.from_bin_to_num(bool_doc)), 
            df1
        )
        
    def doc_matches_minterm(doc, m_r):
        #Convertimos doc y m_r en arrays de numpy
        doc_arr = np.array(doc)
        m_r_arr = np.array(m_r)
        
        #aplicamos XOR para ver si existe diferencia entre los arrays
        #si existe entonces algun componente de diff sera True
        diff = np.logical_xor(doc_arr, m_r_arr)
        
        return not np.any(diff)

        
    #este metodo devuelve el factor de correlacion
    def get_correlation_factor(self, i, m_r, df0):
        """look formula in book"""
        # Obtenemos un vector con todas las columnas del dataframe df0
        doc_columns = df0.columns
        
        # Creamos un vector de booleanos que indica para cada columna si se corresponde con el término m_r
        matches_mask = np.array([self.doc_matches_minterm(doc, m_r) for doc in doc_columns])
        
        # Seleccionamos solo las columnas que se corresponden con el término m_r
        matching_columns = df0[doc_columns[matches_mask]]
        
        # Calculamos la suma de los valores de la fila i en las columnas seleccionadas
        c_ir = matching_columns[i].sum()
        
        return c_ir
             
    #Este metodo genera un vector con 0 y un 1 en la posicion r
    def get_zeroes_vector_with_1_in(self, r, number_of_terms):
        """(it falls from the tree)"""
        vector = np.zeros(number_of_terms)
        vector[r] = 1
        return vector
    
    #este metodo genera el coeficiente de correlacion ki
    def get_ki(self, i, df0):
        up = np.zeros(df0.shape[1])
        down = 0

        for m_r, r in self.corpus_minterms(df0):
            c_ir = self.get_correlation_factor(i, m_r, df0)
            m_r_vector = self.get_zeroes_vector_with_1_in(r-1, df0.shape[1])

            if m_r[i]:
                up += c_ir * m_r_vector
                down += c_ir*c_ir

        down = np.sqrt(down)

        ki = up/down
        return ki

    def get_relevances(
            self, query: pd.DataFrame) -> List[Tuple[DOCID, float]]:
        query.columns.set_names('query')

        df0 = self.cache.fullData        
        
        df0 = self.generalizedModelModification(self,df0)

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

