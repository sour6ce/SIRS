from itertools import islice
from os import path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.cranfield import CranfieldGetter, dataset
from engine.boolean import BooleanIRS
from engine.vector import VectorIRS
from engine.core import DOCID,IRS
from datetime import datetime
from engine.tokenizer import clean_text
from config import *
import debug

#TODO: add numbers to boolean model
# Document search result DTO
class DocumentEntry(BaseModel):
    id: str
    title: str
    description: str

# Basic logging configuration
debug.setupRootLog()

def irdoc_to_dto(doc: DOCID) -> DocumentEntry:
    doc = IRS.data_getter(doc)
    return DocumentEntry(
        id=doc.doc_id,
        title=clean_text(doc.title),
        description=clean_text(doc.text)
    )

# Basic logging configuration
debug.setupRootLog()

# Boolean IR system
BOOL_IRS = BooleanIRS()

# Bool vector Load
BOOL_IRS.data_getter = CranfieldGetter()
MAX_DOCUMENTS = 2000  # Cranfield has 1400 actually
BOOL_IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))

# Vector IR system
VEC_IRS = VectorIRS()

# Cranfield dataset load
VEC_IRS.data_getter = CranfieldGetter()
MAX_DOCUMENTS = 2000  # Cranfield has 1400 actually
VEC_IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))

# FastAPI app
app = FastAPI(debug=DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/bool_model/search')
# Main route to queries
async def root(q: str = "", page: int = 1, pagesize: int = 10) -> List[DocumentEntry]:
    if len(q) == 0: return []
    results = [irdoc_to_dto(d, BOOL_IRS)
               for d in islice(
                   BOOL_IRS.query(q),
                   (page - 1) * pagesize, pagesize * page)]
    return results

@app.get('/doc/{doc_id}')
async def get_doc(doc_id: str) -> DocumentEntry:
    return irdoc_to_dto(doc_id)

@app.get('/vec_model/search')

async def getVecIRS(q: str = "", page: int = 1, pagesize: int = 10) -> List[DocumentEntry]:
    results = [irdoc_to_dto(d, VEC_IRS)
               for d in islice(
                   VEC_IRS.query(q),
                   (page - 1) * pagesize, pagesize * page)]
    return results

@app.get('/datasets')
async def getDatasets():
    return [
        {
            'name': 'Cranfield',
            'slug': 'cranfield',
        },
        {
            'name': 'Testing Dataset',
            'slug': 'tst-dataset',
        },
    ]
