from itertools import islice
from os import path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.cranfield import CranfieldGetter, dataset
from engine.boolean import BooleanIRS
from engine.vector import VectorIRS
from engine.lsi import LatentSemanticIRS
from engine.core import DOCID,IRS
from datetime import datetime
from engine.tokenizer import clean_text
from config import *
import debug
from uvicorn.server import logger

# TODO: Update python docs

# Document search result DTO
class DocumentEntry(BaseModel):
    id: str
    title: str
    description: str

# Basic logging configuration
debug.setupRootLog()

logger.info("Service Starting...")
logger.info("Loading data...")

def irdoc_to_dto(doc: DOCID, irs: IRS) -> DocumentEntry:
    doc = irs.data_getter(doc)
    return DocumentEntry(
        id=doc.doc_id,
        title=clean_text(doc.title),
        description=clean_text(doc.text)
    )

# Basic logging configuration
debug.setupRootLog()
MAX_DOCUMENTS = 2000  # Cranfield has 1400 actually

# Boolean IR system
BOOL_IRS = BooleanIRS()

# Bool vector Load
BOOL_IRS.data_getter = CranfieldGetter()
BOOL_IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))
logger.info("Bool Model Loaded ...")
# Vector IR system
VEC_IRS = VectorIRS()

# Cranfield dataset load
VEC_IRS.data_getter = CranfieldGetter()
VEC_IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))
logger.info("Vector Model Loaded ...")
# LSI IR system
LSI_IRS = LatentSemanticIRS()
LSI_IRS.data_getter = CranfieldGetter()
LSI_IRS.add_documents((d.doc_id
                   for d in islice(dataset.docs_iter(), MAX_DOCUMENTS)))
LSI_IRS.collection.index.loadBlockValues()
logger.info("Latent Semantic Indexing Model Loaded ...")
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


@app.get('/lsi_model/search')
async def getLsiIRS(q:str="",page: int = 1, pagesize: int = 10)-> List[DocumentEntry]:
    results = [irdoc_to_dto(d,LSI_IRS)
               for d in islice(
                   LSI_IRS.query(q),
                   (page - 1) * pagesize, pagesize * page
               )]
    return results

@app.get('/datasets')
async def getDatasets():
    return [
        {
            'name': 'Cranfield',
            'slug': 'cranfield',
        },
    ]
    
@app.get('/models')
async def getModels():
    return [
        {
            "name": "Boolean model",
            "slug": "bool_model",
            "link": "./boolean.html",
            "description": "Information Retrieval System based on boolean queries",
            #TODO: @sour6ce - add instructions about query syntax
            "instructions": ["Enter a query in the search bar", "Click on the search button"]
        },
        {
            "name": "Vectorial model",
            "slug": "vec_model",
            "link": "vectorial.html",
            "description": "Information Retrieval System based on vectorial model",
            "instructions": ["Enter a query in the search bar", "Each keyword must be a single word", "No single numers allowed(4 now)", "Click on the search button"]
        },
        {
            "name": "Latent Semantic Index model",
            "slug": "lsi_model",
            "link": "lsi.html",
            "description": "Information Retrieval System based on Latent Semantic Index model",
            "instructions": ["Enter a query in the search bar", "Each keyword must be a single word", "No single numers allowed(4 now)", "Click on the search button"]
        },
    ]
