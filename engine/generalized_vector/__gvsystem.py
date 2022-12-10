from ..core import IRS
from .__gvcollection import GeneralizedVectorIRCollection
from .__gvquerifier import GeneralizedVectorIRQuerifier


class GeneralizedVectorIRS(IRS):
    def __init__(self) -> None:
        super().__init__()
        self.querifier = GeneralizedVectorIRQuerifier()
        self.collection = GeneralizedVectorIRCollection()