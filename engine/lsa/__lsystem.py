from ..core import IRS
from .__lcollection import VectorIRCollection
from .__lquerifier import LsaIRQuerifier


class LatentSemanticIRS(IRS):
    def __init__(self) -> None:
        super().__init__()
        self.querifier = LsaIRQuerifier()
        self.collection = VectorIRCollection()
