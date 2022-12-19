from ..core import IRS
from .__lcollection import VectorIRCollection
from .__lquerifier import LsiIRQuerifier


class LatentSemanticIRS(IRS):
    def __init__(self) -> None:
        super().__init__()
        self.querifier = LsiIRQuerifier()
        self.collection = VectorIRCollection()