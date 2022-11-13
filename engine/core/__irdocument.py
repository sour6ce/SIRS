from typing import List
from .__raw import *


class IRDocument:
    '''
    Wrapper for a document to allow store a index terms cache and extra
    information.
    '''
    tokens: List[str]
    doc: RawDocumentData

    def __hash__(self) -> int:
        return hash(self.doc.doc_id)

    def __str__(self) -> str:
        return self.doc.title.capitalize()

    def __repr__(self) -> str:
        return self.doc.title.capitalize()

    def __lt__(self, __o: object) -> bool:
        if isinstance(__o, IRDocument):
            return self.doc.doc_id < __o.doc.doc_id
        else:
            return self.doc.doc_id < __o

    def __gt__(self, __o: object) -> bool:
        if isinstance(__o, IRDocument):
            return self.doc.doc_id > __o.doc.doc_id
        else:
            return self.doc.doc_id > __o

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, IRDocument):
            return __o.doc.doc_id == self.doc.doc_id
        return False

    def __neq__(self, __o: object) -> bool:
        return not (self == __o)
