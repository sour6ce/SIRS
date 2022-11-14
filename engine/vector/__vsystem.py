from ..core import IRS
from .__vcollection import VectorIRCollection
from .__vquerifier import VectorIRQuerifier
from .__vranker import VectorIRRanker


class VectorIRS(IRS):
    def __init__(self) -> None:
        super().__init__()
        self.querifier = VectorIRQuerifier()
        self.collection = VectorIRCollection()
        self.ranker = VectorIRRanker()
