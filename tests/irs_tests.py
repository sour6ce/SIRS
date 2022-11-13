from itertools import islice
from datetime import datetime as dt
from unittest import TestCase
from ir_datasets import load
from ir_datasets.formats.base import *
from engine.vector import VectorIRS
from engine.cranfield import to_rawdocument


class IRSTests(TestCase):
    vec_irs = VectorIRS()

    def test_building(self):
        start = dt.now()

        print(f'\n{round((dt.now()-start).total_seconds(),3)}s: ' +
              '- Started database loading -')
        ds: BaseDocs = load('cranfield')
        print(f'{round((dt.now()-start).total_seconds(),3)}s: ' +
              '- Ended database loading -')

        print(f'{round((dt.now()-start).total_seconds(),3)}s: ' +
              '- Started IRS building -')
        self.vec_irs.add_documents((to_rawdocument(d)
                                   for d in islice(ds.docs_iter(), 100)))
        print(f'{round((dt.now()-start).total_seconds(),3)}s: ' +
              '- Ended IRS building -')
