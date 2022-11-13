from ..core import IRS
from .__vcollection import VectorIRCollection
from .__vquerifier import VectorIRQuerifier
from .__vranker import VectorIRRanker


class VectorIRS(IRS):
    ranker = VectorIRRanker()
    collection = VectorIRCollection()
    querifier = VectorIRQuerifier()
