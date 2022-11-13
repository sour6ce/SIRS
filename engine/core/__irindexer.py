from .__raw import *
from .__irdocument import *
from ..tokenizer import tokenize


class IRIndexer():
    '''
    Default Indexer which cast a `RawDocumentData` into a `IRDocument` extracting the
    terms (tokens) to index.
    '''

    def index(self, doc: RawDocumentData) -> IRDocument:
        '''
        Main method of the class to cast.
        '''
        r = IRDocument()
        r.doc = doc
        r.tokens = list(tokenize(doc.text))
        return r

    def __call__(self, doc: RawDocumentData) -> IRDocument:
        '''
        Calls the `index` method.
        '''
        return self.index(doc)
