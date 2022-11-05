from datetime import datetime
import logging
from os import path
from typing_extensions import Self
from fastapi import FastAPI
from pydantic import BaseModel
from engine.core import IRDocument


class DocumentEntry(BaseModel):
    id: str
    title: str

    @staticmethod
    def from_irdocumet(doc: IRDocument) -> Self:
        return DocumentEntry(id=doc.doc.doc_id, title=doc.doc.title)


DEBUG = True

logging.basicConfig(filename=(path.join(path.dirname(
    __file__), 'logs', str(datetime.now())+'.log'), 'w'), filemode='w',
    level=logging.DEBUG if DEBUG else logging.WARNING)

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'API Test'}
