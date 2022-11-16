from itertools import islice
from typing import Iterable, List
from .__ircollection import IRCollection
from .__irindexer import IRIndexer
from .__raw import RawDataGetter, DOCID, fx
from .__irquerifier import IRQuerifier
import cProfile as prof
from os import path
from datetime import datetime
import os
import pstats as st


class IRS():
    '''
    Main class of the engine, works as a pipeline for main operations
    in the IR system (add documents and)
    '''
    __indexer: IRIndexer = IRIndexer()
    __collection: IRCollection
    __querifier: IRQuerifier
    __data_getter: RawDataGetter

    @property
    def indexer(self) -> IRIndexer:
        return self.__indexer

    @indexer.setter
    def indexer(self, value) -> None:
        self.__indexer = value
        self.__indexer.irs = self

    @property
    def collection(self) -> IRCollection:
        return self.__collection

    @collection.setter
    def collection(self, value) -> None:
        self.__collection = value
        self.__collection.irs = self

    @property
    def querifier(self) -> IRQuerifier:
        return self.__querifier

    @querifier.setter
    def querifier(self, value) -> None:
        self.__querifier = value
        self.__querifier.irs = self

    @property
    def data_getter(self) -> IRCollection:
        return self.__data_getter

    @data_getter.setter
    def data_getter(self, value) -> None:
        self.__data_getter = value
        self.__data_getter.irs = self

    def add_document(self, doc: DOCID) -> bool:
        return self.collection.add_document(fx(doc))

    def add_documents(self, docs: Iterable[DOCID]) -> bool:
        coll = self.collection
        return coll.add_documents([fx(d) for d in list(docs)])

    def query(self, q: str) -> List[DOCID]:
        # Profiler initialization
        proc_q = (self.querifier)(q)
        prof_dir = path.abspath(path.join(path.dirname(
            __file__), 'profiles'))
        os.makedirs(prof_dir, exist_ok=True)
        prof_filename = path.join(
            prof_dir, (f'{datetime.now()}.prof').replace(':', '.').replace(
                '-', '.'))
        prof_file = open(prof_filename, mode='w')
        pr = prof.Profile()

        pr.enable()  # Start Profiling

        # Calculates relevance of all documents
        r = self.collection.get_relevances(proc_q)

        # Filter relevance >=0
        n_index = next((i for i, (_, rel) in enumerate(r) if rel <= .0), len(r))
        r = [d for d, _ in islice(r, n_index)]

        pr.disable()  # End profiling

        # Write profiler stats
        st.Stats(pr, stream=prof_file).sort_stats(
            st.SortKey.CUMULATIVE).print_stats(150)

        prof_file.close()

        return r
