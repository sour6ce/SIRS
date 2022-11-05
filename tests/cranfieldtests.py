from unittest import TestCase
from ir_datasets import load
from ir_datasets.formats.base import *


class CranfieldLoadTest(TestCase):
    def test_docs(self):
        ds = load('cranfield')
        d = next(ds.docs_iter())
        self.assertEqual(d.title.replace('\n', ' '), 'experimental' +
                         ' investigation of the aerodynamics of a wing' +
                         ' in a slipstream .')

    def test_queries(self):
        ds = load('cranfield')
        q = next(ds.queries_iter())
        self.assertEqual(q.text.replace('\n', ' '),
                         'what similarity laws must be obeyed when' +
                         ' constructing aeroelastic models of heated' +
                         ' high speed aircraft .')

    def test_qrels(self):
        ds = load('cranfield')
        qr = next(ds.qrels_iter())
        self.assertTupleEqual((qr.query_id, qr.doc_id), ('1', '184'))
