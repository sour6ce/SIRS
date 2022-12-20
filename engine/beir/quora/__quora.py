'''BEIR-Quora Specific Implementations for IR system'''

from typing import Set, Type
from ...core import *
from ir_datasets.datasets.beir import GenericDoc, TrecQrel
from ir_datasets.indices.base import Docstore
from ir_datasets import load, Dataset
from ...metrics.qrel import Qrel, QrelGetter

dataset: Dataset = load('beir/quora/test')

docstore: Docstore = dataset.docs_store()


def get_quora_text(c_doc: GenericDoc) -> str:
    '''
    Get what is the text that is supposed to index from the dataset
    document.
    '''
    # In this case besides the text (that includes the title) we're adding
    # the authors and the extra data from bibliography
    return c_doc.text


def to_rawdocument(c_doc: GenericDoc) -> RawDocumentData:
    '''
    Casts a CranfieldDoc to RawDocumentData used by IR engine.
    This is necessary to customize the text to index.
    '''
    return RawDocumentData(
        doc_id=c_doc.doc_id,
        title='ID: '+c_doc.doc_id,
        text=get_quora_text(c_doc)
    )


class BeirQuoraGetter(RawDataGetter):
    def getdata(self, doc: DOCID) -> RawDocumentData:
        return to_rawdocument(docstore.get((doc)))

    def getall(self) -> List[DOCID]:
        return [d.doc_id for d in islice(dataset.docs_iter(), 70000)]


class BeirQuoraQrelsGetter(QrelGetter):
    def __init__(self) -> None:
        self.__class__.queries = {q.query_id: q.text
                                  for q in dataset.queries_iter()}

    @classmethod
    def __getqtext(cls, qid: str) -> str | None:
        return cls.queries.get(qid, None)

    def getqrels(self) -> List[Qrel]:
        qmarks: Set[str] = set()
        proc_qrels: Dict[str, Qrel] = {}

        for qrel in dataset.qrels_iter():
            qrel: TrecQrel

            qtext = self.__getqtext(qrel.query_id)

            if qtext is None:
                continue

            if qrel.query_id in qmarks:
                proc_qrels[qrel.query_id].relevants[(
                    qrel.doc_id)] = (qrel.relevance)
                continue

            qmarks.add(qrel.query_id)
            proc_qrels[qrel.query_id] = Qrel(
                qrel.query_id,
                self.__getqtext(qrel.query_id),
                {qrel.doc_id: (qrel.relevance)}
            )

        return [x for x in proc_qrels.values()]
