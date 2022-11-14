from itertools import islice
import logging
from os import path
from typing import List
from typing_extensions import Self
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.cranfield import CranfieldGetter, dataset
from engine.vector import VectorIRS
from engine.core import DOCID
from datetime import datetime
DEBUG = True


# Document search result DTO
class DocumentEntry(BaseModel):
    id: str
    title: str
    description: str


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
IRS.data_getter = CranfieldGetter()
MAX_DOCUMENTS = 100
IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))


def irdoc_to_dto(doc: DOCID) -> DocumentEntry:
    doc = IRS.data_getter(doc)
    return DocumentEntry(
        id=doc.doc_id,
        title=doc.title.replace('\n', ' ')
        .replace(' .', '.').capitalize(),
        description=doc.text
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
    return [irdoc_to_dto(d) for d in islice(IRS.query(q), (page-1)*pagesize, pagesize*page)]
