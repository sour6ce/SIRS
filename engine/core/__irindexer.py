from typing import List
from .__raw import *
from ..tokenizer import tokenize
INDEX = List[str]

class IRIndexer():
    '''
    Default Indexer which cast a `RawDocumentData` into a `IRDocument` extracting the
    terms (tokens) to index.
    '''

    def index(self, doc: RawDocumentData) -> INDEX:
        '''
        Main method of the class to cast.
        '''
        return list(tokenize(doc.text))

    def __call__(self, doc: RawDocumentData) -> INDEX:
        '''
        Calls the `index` method.
        '''
        return self.index(doc)
