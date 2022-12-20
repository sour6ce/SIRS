from math import log, sqrt
from os import path
from typing import Dict, Iterable, List, Set, Tuple

import numpy as np
import pandas as pd

from debug import profile
from ..core import DOCID, INDEX, IRS, IRCollection
from .__lindex import LsiIndex


class LsiIRCollection(IRCollection):
    index: LsiIndex = LsiIndex(name="freq")

    def __get_index(self, doc: DOCID) -> INDEX:
        irs: IRS = self.irs
        rd = irs.data_getter(doc)
        ind = irs.indexer(rd)
        return ind

    def add_document(self, document: DOCID) -> None:
        self.index.add_document(document, self.__get_index(document))
        self.index.update_cache()

    def add_documents(self, documents: Iterable[DOCID]) -> None:
        for doc in documents:
            self.index.add_document(doc, self.__get_index(doc))
        self.index.update_cache()
    
    def get_documents(self) -> List[DOCID]:
        return list(self.index.docs)
    
    def get_relevance(self, query: Dict[str, int],
                      doc: DOCID) -> float:
        pass
        
    def get_relevances(self,query: Dict[str,int]) -> List[Tuple[DOCID, float]]:
        k=100
        dbt = self.index.doc_by_term.keys()
        docs = self.index.docs
        u = self.index.u
        s = self.index.s
        v = self.index.v
        uk = u[:,:k]
        vk = v[:,:k]
        skinv = np.linalg.inv(np.diag(s[:k]))
        A = 0.5
        dbt = self.index.doc_by_term.keys()
        docs = self.index.docs
        qt =[[((query[term]) if term in query.keys() else 0) for term in dbt]]
        ukskinv = np.matmul(uk,skinv)
        qk = np.matmul(qt,ukskinv)
        res = {}
        it=0
        for doc in docs:
            res[doc] = self.sim(qk[0],vk[it])
            it = it+1
            
        sorted_keys = sorted(res, key=lambda x: res[x], reverse=True)
        return [(i,res[i]) for i in sorted_keys]
    
    def sim(self,q:Iterable[float],d:Iterable[float]):
        normd = 0
        normq = 0
        mult = 0
        for i in range(len(q)):
            normd += d[i]*d[i]
            normq += q[i]*q[i]
            mult += q[i]*d[i]
        normd = sqrt(normd)
        normq = sqrt(normq)
        return mult/(normd*normq)