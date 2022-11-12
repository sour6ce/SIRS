from .core import *
from .tokenizer import *
import pandas as pd

class ICache:
  dirty: bool
  filename: str
  documents: List[RawDocument]
  dataCache: pd.DataFrame
  fullData: pd.DataFrame
  
  def __init__(self,fileName: str = '', documents: List[RawDocument] = [])->None:
    self.dirty = False
    self.filename = fileName
    self.documents = documents
    if(fileName == ''):
      self.dataCache = pd.DataFrame()
      self.fullData = pd.DataFrame()
      self.filename = 'auto_cache.csv'
    else:
      self.dataCache = pd.read_csv(fileName)
      self.fullData = pd.read_csv(fileName)
    
    
  @abstractmethod 
  def add_document(self, document: RawDocument)->None:
    pass
  
  @abstractmethod
  def remove_document(self, documentId: str)->None:
    pass
  
  def update_document(self, documentId:str, newDocument: RawDocument)->None:
    self.remove_document(documentId)
    self.add_document(newDocument)
    return
  
  @abstractmethod
  def save(self)->None:
    pass
  
class VectorCSVCache(ICache):
  def __init__(self, fileName: str = '', documents: List[RawDocument] = []) -> None:
    super().__init__(fileName, documents)
    
  def add_document(self, document: RawDocument) -> None:
    self.documents.append(document)
    self.dirty = True
    return
  
  def add_document(self, document: List[RawDocument]) -> None:
    self.documents = self.documents + document
    self.dirty = True
    return
  
  def remove_document(self, documentId: str) -> None:
    self.documents = [d for d in self.documents if d.doc_id != documentId]
    self.dirty = True
    return
  
  def recalculateDataCache(self)->None:
    selected_columns = [i.doc_id for i in self.documents]
    selected_columns = [i for i in selected_columns if i in self.fullData.columns]
    to_add_documents = [i for i in self.documents if i.doc_id not in self.dataCache.columns]
    for addingDoc in to_add_documents:
      terms = tokenize(addingDoc.text)
      dataframeKeywords = self.fullData.index.values
      toAddTerms = [i for i in terms if i not in dataframeKeywords]
      newData = pd.DataFrame([[0 for j in self.fullData.columns] for i in toAddTerms], columns=self.fullData.columns,index=toAddTerms)
      self.fullData = pd.concat([self.fullData,newData]).sort_index()
      
      termsOccurences = {i:0 for i in terms}
      for term in terms:
        termsOccurences[term] = termsOccurences[term] + 1
        
      dataframeKeywordsAllSorted = self.fullData.index.values
      self.fullData[addingDoc.doc_id] = [termsOccurences[i] if i in termsOccurences.keys else 0 for i in dataframeKeywordsAllSorted]
      
    self.dataCache = self.dataCache[[i.doc_id for i in self.documents]]
  
  def fitCache(self)->None:
    self.fullData = self.dataCache
    self.save()
  
  def save(self)->None:
    if self.dirty:
      self.recalculateDataCache()
      self.fullData.to_csv(self.filename)
      self.dirty = False
    return
  
  def getVector(self, documentId: str)->dict[str,int]:
    return {x:y for x,y in self.dataCache[documentId].to_dict().items() if y!=0} 
  
  def getTermDocCount(self, term:str)->int:
    return len([i for i in self.dataCache.loc[term] if i!=0])