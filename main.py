from itertools import islice
import logging
from os import path
from typing import List
from typing_extensions import Self
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.core import IRDocument
from engine.cranfield import to_rawdocument
from engine.vector import VectorIRS
from datetime import datetime
from ir_datasets import load
import time
DEBUG = True


# Document search result DTO
class DocumentEntry(BaseModel):
    id: str
    title: str
    description: str

    @staticmethod
    def from_irdocumet(doc: IRDocument) -> Self:
        return DocumentEntry(
            id=doc.doc.doc_id,
            title=doc.doc.title.replace('\n', ' ')
            .replace(' .', '.').capitalize(),
            description=doc.doc.text
        )


# Basic logging configuration
log_file = path.abspath(path.join(
    path.dirname(__file__),
    'logs',
    (str(datetime.now())+'.log').replace(' ', '-').replace(':', '-')
))
logging.basicConfig(filename=log_file, filemode='w',
    level=logging.DEBUG if DEBUG else logging.WARNING)

# Basic vector IR system
IRS = VectorIRS()

# Cranfield dataset load
MAX_DOCUMENTS = 100
cran = load('cranfield')
IRS.add_documents((to_rawdocument(d)
                   for d in islice(cran.docs_iter(), MAX_DOCUMENTS)))

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
    return [DocumentEntry.from_irdocumet(d) for d in islice(IRS.query(q), (page-1)*pagesize, pagesize*page)]
