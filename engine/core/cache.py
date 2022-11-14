from abc import ABC, abstractmethod
from typing import List, Set, Tuple
from os import path
import pandas as pd
from .__irindexer import INDEX
from .__raw import DOCID


class ICache(ABC):
    dirty: bool
    filename: str
    dataCache: pd.DataFrame
    fullData: pd.DataFrame

    def __init__(
            self, fileName: str = '') -> None:
        self.dirty = False
        self.filename = fileName
        if (fileName == ''):
            self.filename = 'auto_cache.csv'
        if path.isfile(path.abspath(fileName)):
            self.dataCache = pd.read_csv(fileName, index_col='term')
            self.fullData = pd.read_csv(fileName, index_col='term')
        else:
            self.dataCache = pd.DataFrame()
            self.fullData = pd.DataFrame()

    @abstractmethod
    def add_document(self, document: Tuple[DOCID, INDEX]) -> None:
        pass

    @abstractmethod
    def add_documents(
            self, documents: List[Tuple[DOCID, INDEX]]) -> None:
        pass

    @abstractmethod
    def remove_document(self, documentId: DOCID) -> None:
        pass

    @abstractmethod
    def update_document(self, documentId: DOCID, newIndex: INDEX) -> None:
      pass

    @abstractmethod
    def save(self) -> None:
      pass
