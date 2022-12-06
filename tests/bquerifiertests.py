from unittest import TestCase
from engine.boolean import BooleanIRQuerifier
from utils import *


class BooleanQueryTest(TestCase):
    def test_strict_exp_parse(self):
        exp = 'thermodynamic & (fluids | solids)'

        qrf = BooleanIRQuerifier()

        qrf(exp)

    def test_strict_exp_vector(self):
        exp = 'thermodynamic & (fluids | solids)'

        qrf = BooleanIRQuerifier()

        r = qrf(exp)

        qtest0 = ['thermodynamic', 'fluids']
        qtest1 = ['thermodynamic', 'solids']

        match_dataframe(
            self, r[0][0]['query'],
            indexes=qtest0,
            values=(1 for _ in qtest0),
            strict=True
        )
        match_dataframe(
            self, r[1][0]['query'],
            indexes=qtest0,
            values=(1 for _ in qtest0),
            strict=True
        )
        match_dataframe(
            self, r[0][1]['query'],
            indexes=qtest1,
            values=(1 for _ in qtest1),
            strict=True
        )
        match_dataframe(
            self, r[1][1]['query'],
            indexes=qtest1,
            values=(1 for _ in qtest1),
            strict=True
        )

    def test_complex_exp1(self):
        exp = 'thermodynamic (fluids | solids)'

        qrf = BooleanIRQuerifier()

        r = qrf(exp)

        qtest0 = ['thermodynamic', 'fluids']
        qtest1 = ['thermodynamic', 'solids']

        match_dataframe(
            self, r[0][0]['query'],
            indexes=qtest0,
            values=(1 for _ in qtest0),
            strict=True
        )
        match_dataframe(
            self, r[1][0]['query'],
            indexes=qtest0,
            values=(1 for _ in qtest0),
            strict=True
        )
        match_dataframe(
            self, r[0][1]['query'],
            indexes=qtest1,
            values=(1 for _ in qtest1),
            strict=True
        )
        match_dataframe(
            self, r[1][1]['query'],
            indexes=qtest1,
            values=(1 for _ in qtest1),
            strict=True
        )

    def test_complex_exp2(self):
        exp = 'thermodynamic ~fluids'

        qrf = BooleanIRQuerifier()

        r = qrf(exp)

        qtest0 = ['thermodynamic']
        qtest1 = ['thermodynamic', 'fluids']

        match_dataframe(
            self,
            r[0][0]['query'],
            indexes=qtest0,
            strict=True
        )
        match_dataframe(
            self,
            r[1][0]['query'],
            indexes=qtest1,
            strict=True
        )
