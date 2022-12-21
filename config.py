'''
    Configuration file of the project. All the configurable values are here.
'''
from typing import NamedTuple
from engine.core import IRS
from engine.cranfield import CranfieldGetter, CranfieldQrelsGetter
from engine.boolean import BooleanIRS
from engine.vector import VectorIRS
from engine.lsi import LatentSemanticIRS


class Model(NamedTuple):
    name: str
    slug: str
    type: type[IRS]
    dec: str
    instructions: str

# region Configuration


# Dataset Configuration
DATASET = {
    'name': 'Cranfield',
    'slug': 'cranfield',
    'getter': CranfieldGetter,
    'qrels': CranfieldQrelsGetter
}


# Models definition
MODELS = [
    Model(
        name='Boolean Model', slug='bool_model', type=BooleanIRS,
        dec="System based on boolean queries",
        instructions=["Enter a query in the search bar",
                      "Click on the search button",
                      "Allows operators &, | and ~ for building boolean expressions"]),
    Model(
        name='Vectorial Model', slug='vec_model', type=VectorIRS,
        dec="System based on vectorial model.",
        instructions=["Enter a query in the search bar",
                      "Click on the search button"]),
    Model(
        name='Latent Semantic Index Model', slug='lsi_model',
        type=LatentSemanticIRS, dec="System based on vectorial model.",
        instructions=["Enter a query in the search bar",
                      "Click on the search button"])]
