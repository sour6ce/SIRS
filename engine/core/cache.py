from abc import ABC, abstractmethod
from typing import List
from os import path
import pandas as pd
from .__irdocument import IRDocument


class ICache(ABC):
  dirty: bool
  filename: str
  documents: List[IRDocument]
  dataCache: pd.DataFrame
  fullData: pd.DataFrame

  def __init__(
          self, fileName: str = '', documents: List[IRDocument] = []) -> None:
    self.dirty = False
    self.filename = fileName
    self.documents = documents
    if (fileName == ''):
      self.filename = 'auto_cache.csv'
    if path.isfile(path.abspath(fileName)):
      self.dataCache = pd.read_csv(fileName, index_col='term')
      self.fullData = pd.read_csv(fileName, index_col='term')
    else:
      self.dataCache = pd.DataFrame()
      self.fullData = pd.DataFrame()

  @abstractmethod
  def add_document(self, document: IRDocument) -> None:
    pass

  @abstractmethod
  def add_documents(self, documents: List[IRDocument]) -> None:
    pass

  @abstractmethod
  def remove_document(self, documentId: str) -> None:
    pass

  def update_document(self, documentId: str, newDocument: IRDocument) -> None:
    self.remove_document(documentId)
    self.add_document(newDocument)
    return

  @abstractmethod
  def save(self) -> None:
    pass
