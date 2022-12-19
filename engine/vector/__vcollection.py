from math import log, sqrt
from os import path
from typing import Dict, Iterable, List, Set, Tuple

import numpy as np
import pandas as pd

from debug import profile
from ..core import DOCID, INDEX, IRS, IRCollection
from .__vindex import VectorIndex


class VectorIRCollection(IRCollection):
    index: VectorIndex = VectorIndex(name="freq")

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

    def get_tf(self, term: str, doc: DOCID):
        '''
        Return the tf value of a term in a document.
        '''
        return self.index.whole[doc, term] / self.index.max_freq[doc]

    def get_ni(self, term: str):
        '''
        Return the number of documents where the term is. For non-indexed terms return 0.
        '''
        return self.index.n_i.get(term, 0)

    def get_idf(self, term: str):
        '''
        Return the idf value of a term. For non-indexed terms return 0
        '''
        return self.index.idf.get(term, 0)

    def get_relevance(self, query: Dict[str, int],
                      doc: DOCID) -> float:

        # TODO: Adjust for query format change

        A = .5  # Query smoother

        doc_index = self.index.term_by_doc[doc]

        # Get all the terms that are in the document or the query
        terms: Set[str] = set(self.index.term_by_doc[doc].keys())

        for term in query.keys():
            terms.add(term)

        norm_q = 0
        norm_d = 0

        max_q = max(query.values())  # max frequency in the query

        # Calculate the multiplication of weights
        mult = 0
        for term in terms:
            m = 1
            # Multiplicate weights and calculate query's norm
            if term in query:
                v = (A+(1-A)*(query[term]/max_q))*self.get_idf(term)
                m *= v
                norm_q += v*v
            else:
                m = 0

            # Multiplicate weights and calculate query's norm
            if term in doc_index:
                v = self.get_tf(term, doc)*self.get_idf(term)
                m *= v
                norm_d += v*v
            else:
                m = 0

            mult += m

        norm_d = sqrt(norm_d)
        norm_q = sqrt(norm_q)

        # Final cosine similitude
        return mult/(norm_d*norm_q)

    def get_relevances(
            self, query: pd.DataFrame) -> List[Tuple[DOCID, float]]:
        query: Dict[str, int] = {term: query.loc[term]
                                 ['query'] for term in query.index}

        r = list({doc_id: self.get_relevance(query, doc_id)
                  for doc_id in self.index.docs}.items())
        r.sort(key=lambda x: x[1], reverse=True)

        return r

    def get_documents(self) -> List[DOCID]:
        return list(self.index.docs)
