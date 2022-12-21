from ..core import IRS
from .__lcollection import LsiIRCollection
from ..vector import VectorIRS


class LatentSemanticIRS(VectorIRS):
    RELEVANCE_FILTER: float = .5

    def __init__(self) -> None:
        super().__init__()
        self.collection = LsiIRCollection()
