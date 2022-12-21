from math import log, sqrt
from os import path
from typing import Dict, Iterable, List, Set, Tuple

import numpy as np
import pandas as pd

from debug import profile
from ..core import DOCID, INDEX, IRS, IRCollection
from ..vector import VectorIRCollection


class LsiIRCollection(VectorIRCollection):

    Amat: List[List[float]] = []
    u:  List[List[float]] = []
    v:  List[List[float]] = []
    s:  List[float] = []

    def add_document(self, document: DOCID) -> None:
        super().add_document(document)
        self.loadBlockValues()

    def add_documents(self, documents: Iterable[DOCID]) -> None:
        super().add_documents(documents)
        self.loadBlockValues()
    
    def get_relevance(self, query: Dict[str, int],
                      doc: DOCID) -> float:
        if len(query) == 0:
            return .0
        return dict(self.get_relevances(query)).get(doc, 0)
        
    def get_relevances(self, query: Dict[str, int]) -> List[Tuple
                                                            [DOCID, float]]:
        if len(query) == 0:
            return .0
        k=100
        dbt = self.index.doc_by_term.keys()
        docs = self.index.docs
        u = self.u
        s = self.s
        v = self.v
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

    def loadBlockValues(self):
        dbt = self.index.doc_by_term.keys()
        docs = self.index.docs
        self.Amat = [
            [(self.index.whole[doc, term]
              if term in self.index.term_by_doc[doc].keys() else 0)
             for doc in docs] for term in dbt]
        u, s, vh = np.linalg.svd(self.Amat, full_matrices=False)
        self.u = u
        self.s = s
        self.v = np.transpose(vh)
