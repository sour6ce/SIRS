from ..core import IRS
from .__bcollection import BooleanIRCollection
from .__bquerifier import BooleanIRQuerifier


class BooleanIRS(IRS):
    def __init__(self) -> None:
        super().__init__()
        self.querifier = BooleanIRQuerifier()
        self.collection = BooleanIRCollection()