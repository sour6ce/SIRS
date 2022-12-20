from unittest import TestCase
from engine.boolean import BooleanIRQuerifier
from utils import *


class BooleanQueryTest(TestCase):
    def test_strict_exp_parse(self):
        exp = 'the fluid motion'

        qrf = BooleanIRQuerifier()

        qrf(exp)

    def test_strict_exp_vector(self):
        exp = 'thermodynamic & (fluids | solids)'

        qrf = BooleanIRQuerifier()

        r = qrf(exp)

        qtest0 = {('thermodynamic', False), ('fluids', False)}
        qtest1 = {('thermodynamic', False), ('solids', False)}

        self.assertSetEqual(qtest0, r[0])
        self.assertSetEqual(qtest1, r[1])

    def test_complex_exp1(self):
        exp = 'the thermodynamic (fluids | solids)'

        qrf = BooleanIRQuerifier()

        r = qrf(exp)

        qtest0 = {('thermodynamic', False), ('fluids', False)}
        qtest1 = {('thermodynamic', False), ('solids', False)}

        self.assertSetEqual(qtest0, r[0])
        self.assertSetEqual(qtest1, r[1])

    def test_complex_exp2(self):
        exp = 'thermodynamic ~fluids'

        qrf = BooleanIRQuerifier()

        r = qrf(exp)

        qtest0 = {('thermodynamic', False), ('fluids', True)}

        self.assertSetEqual(qtest0, r[0])
