'''Cranfield Specific Implementations for IR system'''

from typing import Set, Type
from ..core import *
from ir_datasets.datasets.cranfield import CranfieldDoc, TrecQrel
from ir_datasets.indices.base import Docstore
from ir_datasets import load, Dataset
from ..metrics.qrel import Qrel, QrelGetter

dataset: Dataset = load('cranfield')

docstore: Docstore = dataset.docs_store()


def get_cran_text(c_doc: CranfieldDoc) -> str:
    '''
    Get what is the text that is supposed to index from the Cranfield
    document.
    '''
    # In this case besides the text (that includes the title) we're adding
    # the authors and the extra data from bibliography
    return c_doc.text+'\n\n'+c_doc.author+'\n\n'+c_doc.bib


def to_rawdocument(c_doc: CranfieldDoc) -> RawDocumentData:
    '''
    Casts a CranfieldDoc to RawDocumentData used by IR engine.
    This is necessary to customize the text to index.
    '''
    return RawDocumentData(
        doc_id=c_doc.doc_id,
        title=c_doc.title,
        text=get_cran_text(c_doc)
    )


class CranfieldGetter(RawDataGetter):
    def getdata(self, doc: DOCID) -> RawDocumentData:
        return to_rawdocument(docstore.get(dfx(doc)))
    
    def getall(self) -> List[DOCID]:
        return [d.doc_id for d in dataset.docs_iter()]


class CranfieldQrelsGetter(QrelGetter):
    def __init__(self) -> None:
        self.__class__.queries = {str(k+1): q.text
                                  for k, q in enumerate(dataset.queries_iter())}

    @classmethod
    def __getqtext(cls, qid: str) -> str:
        return cls.queries[qid]

    def getqrels(self) -> List[Qrel]:
        qmarks: Set[str] = set()
        proc_qrels: Dict[str, Qrel] = {}

        for qrel in dataset.qrels_iter():
            qrel: TrecQrel
            
            if qrel.relevance==-1: continue

            if qrel.query_id in qmarks:
                proc_qrels[qrel.query_id].relevants[fx(
                    qrel.doc_id)] = (qrel.relevance)/4.0
                continue

            qmarks.add(qrel.query_id)
            proc_qrels[qrel.query_id] = Qrel(
                qrel.query_id,
                self.__getqtext(qrel.query_id),
                {qrel.doc_id: (qrel.relevance)/4.0}
            )

        return [x for x in proc_qrels.values()]
