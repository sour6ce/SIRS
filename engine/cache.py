from typing import Dict
from .core import *
from .tokenizer import *
import pandas as pd
import numpy as np
from os import path

class ICache:
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
  def remove_document(self, documentId: str)->None:
    pass
  
  def update_document(self, documentId: str, newDocument: IRDocument) -> None:
    self.remove_document(documentId)
    self.add_document(newDocument)
    return
  
  @abstractmethod
  def save(self)->None:
    pass
  
class VectorCSVCache(ICache):
  def __init__(
          self, fileName: str = '', documents: List[IRDocument] = []) -> None:
    super().__init__(fileName, documents)
    
  def add_document(self, document: IRDocument) -> None:
    self.documents.append(document)
    self.dirty = True
    return
  
  def add_documents(self, documents: List[IRDocument]) -> None:
    self.documents = self.documents + documents
    self.dirty = len(documents) != 0
    return
  
  def remove_document(self, documentId: str) -> None:
    self.documents = [d for d in self.documents if d.doc.doc_id != documentId]
    self.dirty = True
    return
  
  def recalculateDataCache(self)->None:
    selected_columns = [i.doc.doc_id for i in self.documents]
    selected_columns = [i for i in selected_columns if i in self.fullData.columns]
    to_add_documents = [
        i for i in self.documents
        if i.doc.doc_id not in self.fullData.columns]

    def freq(doc: IRDocument):
      d: Dict[str, int] = dict()
      for term in doc.tokens:
        d[term] = d.get(term, 0+1)
      return d

    def ser(doc: IRDocument):
      f = freq(doc)
      return pd.Series(data=f.values(), index=f.keys(), dtype=int)

    new_df = pd.DataFrame({doc.doc.doc_id: ser(doc)
                          for doc in to_add_documents})
    self.fullData = pd.concat([self.fullData, new_df]).fillna(0).sort_index()
    # for addingDoc in to_add_documents:
    #   terms = addingDoc.tokens
    #   dataframeKeywords = self.fullData.index.values
    #   toAddTerms = [i for i in terms if i not in dataframeKeywords]
    #   newData = pd.DataFrame(
    #       [[0 for j in self.fullData.columns] for i in toAddTerms],
    #       columns=self.fullData.columns,
    #       index=toAddTerms
    #   )
    #   self.fullData = pd.concat([self.fullData,newData]).sort_index()
      
    #   termsOccurrences = {i:0 for i in terms}
    #   for term in terms:
    #     termsOccurrences[term] = termsOccurrences[term] + 1
        
    #   dataframeKeywordsAllSorted = self.fullData.index.values
    #   self.fullData[addingDoc.doc.doc_id] = [termsOccurrences[i]
    #                                          if i in termsOccurrences.keys() else 0
    #                                          for i in dataframeKeywordsAllSorted]
      
    # self.dataCache = self.fullData[[i.doc.doc_id for i in self.documents]]
  
  def fitCache(self)->None:
    self.fullData = self.dataCache
    self.save()
  
  def save(self)->None:
    if self.dirty:
      self.recalculateDataCache()
      self.fullData.to_csv(self.filename, index_label='term')
      self.dirty = False
    return
  
  def getVector(self, documentId: str)->dict[str,int]:
    return {x:y for x,y in self.dataCache[documentId].to_dict().items() if y!=0} 
  
  def getTermDocCount(self, term:str)->int:
    return len([i for i in self.dataCache.loc[term] if i!=0])