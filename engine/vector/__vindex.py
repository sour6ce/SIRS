from math import log
import shelve
from os import makedirs, path
from typing import Dict, Iterable, Set, Tuple

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


class VectorIndex(metaclass=Singleton):
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

    n_i: Dict[str, int] = {}  # Amount of document that a term appears
    idf: Dict[str, float] = {}  # idf value of the term

    common: int = 0  # # of document in what appears the most common term

    docs: Set[DOCID] = set()  # Set of all documents in the index
    terms: Set[str] = set()  # Set of all documents in the index

    doc_count: int = 0
    term_count: int = 0

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
        if 'common' in self.persistance.keys():
            self.common = self.persistance['common']
        if 'docs' in self.persistance.keys():
            self.docs = self.persistance['docs']
        if 'terms' in self.persistance.keys():
            self.terms = self.persistance['terms']
        if 'idf' in self.persistance.keys():
            self.idf = self.persistance['idf']
        if 'n_i' in self.persistance.keys():
            self.n_i = self.persistance['n_i']
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
                self.n_i[term] = 0

            # The term is new in the document
            if term not in self.term_by_doc[id]:
                self.n_i[term] += 1

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

            # Check if the amount of documents where the term appears
            # is the maximum of the whole collection
            self.common = max(self.n_i[term], self.common)

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

        for term in self.terms:
            self.idf[term] = log(self.common+1/self.n_i[term])

        self.persistance['doc_by_term'] = self.doc_by_term
        self.persistance['term_by_doc'] = self.term_by_doc
        self.persistance['max_freq'] = self.max_freq
        self.persistance['common'] = self.common
        self.persistance['docs'] = self.docs
        self.persistance['terms'] = self.terms
        self.persistance['idf'] = self.idf
        self.persistance['n_i'] = self.n_i
        self.persistance['whole'] = self.whole
