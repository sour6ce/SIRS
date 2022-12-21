from ..core import IRS
from .__vcollection import VectorIRCollection
from .__vquerifier import VectorIRQuerifier


class VectorIRS(IRS):
    RELEVANCE_FILTER: float = .25

    def __init__(self) -> None:
        super().__init__()
        self.querifier = VectorIRQuerifier()
        self.collection = VectorIRCollection()
