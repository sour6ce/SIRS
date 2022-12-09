from itertools import islice
import logging
from os import path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.cranfield import CranfieldGetter, dataset
from engine.boolean import BooleanIRS
from engine.core import DOCID
from datetime import datetime
from engine.tokenizer import clean_text
from config import *
import debug


# Document search result DTO
class DocumentEntry(BaseModel):
    id: str
    title: str
    description: str


# Basic logging configuration
debug.setupRootLog()

# Basic vector IR system
IRS = BooleanIRS()

# Cranfield dataset load
IRS.data_getter = CranfieldGetter()
MAX_DOCUMENTS = 2000  # Cranfield has 1400 actually
IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))


def irdoc_to_dto(doc: DOCID) -> DocumentEntry:
    doc = IRS.data_getter(doc)
    return DocumentEntry(
        id=doc.doc_id,
        title=clean_text(doc.title),
        description=clean_text(doc.text)
    )


# FastAPI app
app = FastAPI(debug=DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/search')
# Main route to queries
async def root(q: str, page: int = 1, pagesize: int = 10) -> List[DocumentEntry]:
    results = [irdoc_to_dto(d)
               for d in islice(
                   IRS.query(q),
                   (page - 1) * pagesize, pagesize * page)]
    return results
