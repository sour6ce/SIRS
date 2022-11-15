from math import sqrt
from typing import Dict, Iterable, List, Tuple
from ..core import IRCollection, IRS
from .__vcache import VectorCSVCache
from ..core import DOCID, INDEX
from os import path
import numpy as np
import pandas as pd


class VectorIRCollection(IRCollection):
    cache: VectorCSVCache = VectorCSVCache(
        path.abspath(
            path.join(path.dirname(__file__), 'vector.cache.csv')
        )
    )

    def __get_index(self, doc: DOCID) -> INDEX:
        irs: IRS = self.irs
        rd = irs.data_getter(doc)
        ind = irs.indexer(rd)
        return ind

    def add_document(self, document: DOCID) -> None:
        if document not in self.cache.fullData:
            ind = self.__get_index(document)
            self.cache.add_document((document, ind))
            self.cache.save()

    def add_documents(self, documents: Iterable[DOCID]) -> None:
        docs = np.array(list(
            (
                d for d in documents if d not in self.cache.fullData
            )
        )
        )

        n_d = list(((d, self.__get_index(d)) for d in docs))
        self.cache.add_documents(n_d)
        self.cache.save()

    def get_relevance(self, query: pd.DataFrame,
                      doc: DOCID) -> float:

        # TODO: Delete or change to tf,idf
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
            self, query: pd.DataFrame) -> List[Tuple[DOCID, float]]:
        query.columns.set_names('query')

        df0 = self.cache.fullData
        df0.index.name = 'term'
        df = pd.concat([df0, query]).fillna(
            0).groupby('term').sum()

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

    def get_documents(self) -> List[DOCID]:
        return list(self.cache.fullData.columns)
