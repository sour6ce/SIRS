
from typing import NamedTuple


class RawDocumentData(NamedTuple):
    '''
    Stores the document raw information (id, title, and text to index)
    '''
    doc_id: str
    title: str
    text: str
