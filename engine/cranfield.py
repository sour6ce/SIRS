'''Cranfield Specific Implementations for IR system'''

from .core import *
from ir_datasets.datasets.cranfield import CranfieldDoc


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
