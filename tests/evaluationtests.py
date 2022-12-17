from unittest import TestCase
from engine.cranfield import *
from engine.metrics import *
from engine.vector import VectorIRS
from debug import profile


class CranfieldQrelLoadTest(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_read_qrels(self):
        cqg = CranfieldQrelsGetter()

        # Not empty qrels
        self.assertNotEqual(len(cqg.getqrels()), 0)

    @profile()
    def test_metric_stub(self):
        class SetStubMetric(SetBasedMetric):
            @staticmethod
            def formula(set_info: Dict[str, int]) -> float:
                return 1.0  # Return 1 as metric for each test

        irs_test = VectorIRS()

        # Cranfield dataset load
        irs_test.data_getter = CranfieldGetter()
        irs_test.add_documents((d.doc_id for d in dataset.docs_iter()))

        metric = SetStubMetric()

        qrels = CranfieldQrelsGetter().getqrels()

        result = next(metric.calculate_all(irs_test, qrels), -1)

        # Check if every qrel is in the list and has 1.0 value
        self.assertEqual(result, 1.0)
