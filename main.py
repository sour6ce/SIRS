from itertools import islice
from typing import List, NamedTuple
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.cranfield import CranfieldGetter, CranfieldQrelsGetter
from engine.boolean import BooleanIRS
from engine.vector import VectorIRS
from engine.lsi import LatentSemanticIRS
from engine.core import DOCID, IRS
from engine.tokenizer import clean_text
from debug import *
from config import *
from uvicorn.server import logger


# TODO: Update python docs

# Document search result DTO


class DocumentEntry(BaseModel):
    id: str
    title: str
    description: str


logger.info("Service Starting...")
logger.info("Loading data...")


def irdoc_to_dto(doc: DOCID) -> DocumentEntry:
    doc = getter(doc)
    return DocumentEntry(
        id=doc.doc_id,
        title=clean_text(doc.title),
        description=clean_text(doc.text)
    )


getter = DATASET['getter']()
docs = getter.getall()
INITIALIZED_MODELS = {}

for m in MODELS:
    irs = m.type()
    irs.data_getter = getter
    irs.add_documents(docs)

    INITIALIZED_MODELS[m.slug] = irs
    logger.info(f"{m.name} Loaded...")


# FastAPI app
app = FastAPI(debug=DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# endregion

# region Endpoints


@app.get('/{model}/search', response_model=List[DocumentEntry])
# Main route to queries
async def root(model: str, q: str = "", page: int = 1, pagesize: int = 10):
    if len(q) == 0:
        return []
    results = [irdoc_to_dto(d)
               for d in islice(
                   INITIALIZED_MODELS[model].query(q),
                   (page - 1) * pagesize, pagesize * page)]
    return results


@app.get('/doc/{doc_id}', response_model=DocumentEntry)
async def get_doc(doc_id: str) -> DocumentEntry:
    return irdoc_to_dto(doc_id)


@app.get('/datasets')
async def getDatasets():
    return [{'name': DATASET['name'], 'slug':DATASET['slug']}]


@app.get('/models')
async def getModels():
    ms = MODELS.copy()
    r = []
    for m in ms:
        m = m._asdict().copy()
        m['link'] = f'./{m["slug"]}.html'
        m.pop('type')
        r.append(m)
    return r
# endregion
