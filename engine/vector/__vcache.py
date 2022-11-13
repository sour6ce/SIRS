from typing import Dict, List
from ..core.cache import ICache
from ..core import IRDocument
import pandas as pd

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