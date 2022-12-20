from math import log
import shelve
from os import makedirs, path
from typing import Dict, Iterable, Set, Tuple, List
import numpy as np
from engine.core import DOCID, INDEX


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = kwargs.get("name", "root")
        if (cls, name) not in cls._instances:
            cls._instances[cls, name] = super(
                Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls, name]


class LsiIndex(metaclass=Singleton):
    # Shelve config data
    index_dir: str
    name: str
    persistance: shelve.Shelf

    __dirty: bool = False

    # Index specific
    doc_by_term: Dict[str, Dict[DOCID, int]] = {}
    term_by_doc: Dict[DOCID, Dict[str, int]] = {}
    whole: Dict[Tuple[DOCID, str], int] = {}

    # Most frequent term frequency for each document
    max_freq: Dict[DOCID, int] = {}

    docs: Set[DOCID] = set()  # Set of all documents in the index
    terms: Set[str] = set()  # Set of all documents in the index

    doc_count: int = 0
    term_count: int = 0
    
    Amat: List[List[float]] = []
    u:  List[List[float]] = []
    v:  List[List[float]] = []
    s:  List[float] = []

    def __init__(self, *, name: str) -> None:
        self.name = name

        self.index_dir = path.abspath(
            path.join(path.dirname(__file__), 'index'))
        makedirs(self.index_dir, exist_ok=True)

        self.persistance = shelve.open(
            path.join(self.index_dir, name),
            writeback=True)

        if 'doc_by_term' in self.persistance.keys():
            self.doc_by_term = self.persistance['doc_by_term']
        if 'term_by_doc' in self.persistance.keys():
            self.term_by_doc = self.persistance['term_by_doc']
        if 'max_freq' in self.persistance.keys():
            self.max_freq = self.persistance['max_freq']
        if 'docs' in self.persistance.keys():
            self.docs = self.persistance['docs']
        if 'terms' in self.persistance.keys():
            self.terms = self.persistance['terms']
        if 'whole' in self.persistance.keys():
            self.whole = self.persistance['whole']

        self.doc_count = len(self.term_by_doc.keys())
        self.term_count = len(self.doc_by_term.keys())

    def add_document(self, id: DOCID, ind: INDEX):
        '''
        Add a document to the index.
        '''
        if id in self.term_by_doc:
            return

        self.term_by_doc[id] = {}

        self.max_freq[id] = 0

        for term in ind:
            # New term in collection
            if term not in self.doc_by_term.keys():
                self.term_count += 1
                self.terms.add(term)

            # Frequency of the term is 0+1 the old frequency or 1
            # if is the first time seen in the document
            term_docs = self.doc_by_term.get(term, {})
            freq = term_docs.get(id, 0)+1
            term_docs[id] = term_docs.get(id, 0)+1
            self.doc_by_term[term] = term_docs

            self.term_by_doc[id][term] = freq
            self.whole[id, term] = freq

            # Check if the frequency of this term is the maximum of
            # all terms in the document
            self.max_freq[id] = max(self.max_freq[id], freq)

        # If max_freq still 0 it means the document was empty
        self.__dirty = self.max_freq[id] != 0
        if self.max_freq[id] != 0:
            self.doc_count += 1
            self.docs.add(id)
        else:
            self.term_by_doc.pop(id)
            self.max_freq.pop(id)

            return

    def get_frequency(self, doc: DOCID, term: str):
        return self.whole[doc, term]

    def get_dbyt(self):
        return self.doc_by_term

    def get_tbyd(self):
        return self.term_by_doc

    def update_cache(self):
        if not self.__dirty:
            return

        self.persistance['doc_by_term'] = self.doc_by_term
        self.persistance['term_by_doc'] = self.term_by_doc
        self.persistance['max_freq'] = self.max_freq
        self.persistance['docs'] = self.docs
        self.persistance['terms'] = self.terms
        self.persistance['whole'] = self.whole


    def loadBlockValues(self): 
        dbt = self.doc_by_term.keys()
        docs = self.docs
        self.Amat = [[(self.whole[doc, term] if term in self.term_by_doc[doc].keys() else 0) for doc in docs] for term in dbt]
        u,s,vh = np.linalg.svd(self.Amat, full_matrices=False)
        self.u = u
        self.s = s
        self.v = np.transpose(vh)