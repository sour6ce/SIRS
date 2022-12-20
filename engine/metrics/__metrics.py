from abc import ABC, abstractmethod
from logging import DEBUG, Logger
import logging
from time import time
from typing import Dict, Iterable, List, Set, Tuple, Type

from ..core import DOCID, IRS, dfx, fx
from .qrel import Qrel


class IRSMetric(ABC):
    def calculate_all(self, irs: IRS, qrels: Iterable[Qrel]) -> Iterable[float]:
        '''
        Given the qrels run each test in the system and calculate the metric 
        for each test. Return an iteration through each result in the same
        respective order that the qrels given.
        '''
        for q in qrels:
            yield self.calculate(irs, q)

    @abstractmethod
    def calculate(self, irs: IRS, qrel: Qrel) -> float:
        '''
        Given a qrel run the test in the system and calculate the metric.
        Return the result.
        '''
        pass

    def __call__(self, irs: IRS, qrels: Iterable[Qrel]) -> Iterable[float]:
        return self.calculate_all(irs, qrels)


class SetBasedMetric(IRSMetric, ABC):
    '''
    A set based metric is a metric that can be calculate by the size of the
    next sets:

    - RR: Relevant documents recovered in the query
    - NR: Relevant documents not recovered in the query
    - RI: Not relevant documents recovered in the query
    - NI: Not relevant documents not recovered in the query
    - REL: Relevant documents in the query
    - REC: Recovered documents in the query
    - IRR: Not relevant documents in the query
    - NREC: Not recovered documents in the query

    This metrics has two common parameters. As the similitude and the relevance
    are floating point values in the ranges [`-1`,`1`] and [`0`,`1`]
    respectively, two threshold values are defined as constructor parameters:

    - `recovery_threshold` (default `0.0001`): Used to define what is the
    minimum similitude value to have a document with the query to be considered
    as recovered.
    - `relevant_threshold` (default `0.4`): Used to define what is the
    minimum relevance value to have a document in the qrels to be considered
    as relevant.
    '''

    def __init__(self, *,
                 recovery_threshold: float = .0,
                 relevant_threshold: float = .4,
                 **kwargs
                 ) -> None:
        self.__rec_t = recovery_threshold
        self.__rel_t = relevant_threshold

        super().__init__()

    @staticmethod
    @abstractmethod
    def formula(set_info: Dict[str, int]) -> float:
        '''
        Formula for metric calculation given the size of the sets.

        Every kind of set has his own key in `set_info` with its size.
        (RR,NR,RI,NI,REL,REC,IRR,NREC)
        '''
        pass

    def calculate(self, irs: IRS, qrel: Qrel) -> float:
        recovered: Set[DOCID] = set()
        relevant: Set[DOCID] = set()

        for did, sim in irs.pre_query(qrel.query):
            if sim > self.__rec_t:
                recovered.add(dfx(did))

        for did, rel in qrel.relevants.items():
            if rel > self.__rel_t and fx(did) in irs.collection.get_documents():
                relevant.add(dfx(did))

        set_info = {
            'RR': len(recovered.intersection(relevant)),
            'NR': len(relevant.difference(recovered)),
            'RI': len(recovered.difference(relevant)),
            'NI': len(irs.collection.get_documents()
                      )-len(recovered.union(relevant)),
            'REL': len(relevant),
            'REC': len(recovered),
            'IRR': len(irs.collection.get_documents()
                       )-len(relevant),
            'NREC': len(irs.collection.get_documents()
                        )-len(recovered)
        }
        r = self.formula(set_info)

        return r


class PrecisionMetric(SetBasedMetric):
    @staticmethod
    def formula(si: Dict[str, int]) -> float:
        return 1.0 if si['REC'] == 0 else si['RR']/si['REC']


class RecoveryMetric(SetBasedMetric):
    @staticmethod
    def formula(si: Dict[str, int]) -> float:
        return 1.0 if si['REL'] == 0 else si['RR']/si['REL']


class FMetric(SetBasedMetric, ABC):
    pass


def FMetricBuild(beta: float) -> Type[FMetric]:
    '''
    Function that builds an `FMetricClass` child classes based on parameter `beta`.
    '''
    class _FMetric(FMetric):
        @staticmethod
        def formula(set_info: Dict[str, int]) -> float:
            prec = PrecisionMetric.formula(set_info)
            rec = RecoveryMetric.formula(set_info)
            if prec == 0 or rec == 0:
                return .0
            return (1+beta**2) / ((1/prec)+(beta**2/rec))

    return _FMetric


F1Metric = FMetricBuild(beta=1)


class TimeMetric(IRSMetric):
    '''
    Metric to evaluate how many seconds it takes to do a query.
    '''

    def calculate(self, irs: IRS, qrel: Qrel) -> float:
        st = time()
        irs.pre_query(qrel.query)
        end = time()

        exec_time = round((end-st), 4)

        return exec_time
