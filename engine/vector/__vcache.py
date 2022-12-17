from typing import Dict, List, Tuple
from ..core.cache import ICache
import pandas as pd
from ..core import DOCID, INDEX

class VectorCSVCache(ICache):
  __indexes: Dict[DOCID, INDEX] = {}

  def __init__(
          self, fileName: str = '') -> None:
    super().__init__(fileName)
    # Filter out blank documents
    self.dataCache = self.dataCache.loc[:, (self.dataCache > 0.0).any(axis=0)]
    self.fullData = self.fullData.loc[:, (self.dataCache > 0.0).any(axis=0)]
    
  def add_document(self, document: Tuple[DOCID, INDEX]) -> None:
    if document[0] not in self.fullData.columns:
      self.documents.append(document[0])
      self.__indexes[document[0]] = document[1]
      self.dirty = True
  
  def add_documents(self, documents: List[Tuple[DOCID, INDEX]]) -> None:
    documents = [(d, i) for d, i in documents if d not in self.fullData.columns]
    self.__indexes.update(documents)
    self.dirty = len(documents) != 0
    return
  
  def remove_document(self, documentId: DOCID) -> None:
    # TODO: remove document implementation in cache
    raise NotImplementedError()

  def update_document(self, documentId: DOCID, newIndex: INDEX) -> None:
    # TODO: update document implementation in cache
    raise NotImplementedError()
  
  def recalculateDataCache(self)->None:
    to_add_documents = list(self.__indexes.keys())

    def freq(doc: DOCID):
      d: Dict[str, int] = dict()
      for term in self.__indexes[doc]:
        d[term] = d.get(term, 0+1)
      return d

    def ser(doc: DOCID):
      f = freq(doc)
      return pd.Series(data=f.values(), index=f.keys(), dtype=int)

    new_df = pd.DataFrame({doc: ser(doc)
                          for doc in to_add_documents})
    # Filter out blank documents
    new_df = new_df.loc[:, (new_df > 0.0).any(axis=0)]
    new_df.index.name = 'term'
    self.fullData = pd.concat([self.fullData, new_df]).fillna(0).sort_index()
    self.__indexes = {}
  
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