from unittest import TestCase
from engine.tokenizer import *


class TokenizerTest(TestCase):
    def test_cleaner(self):
        raw_text = ' class Person():\n\tname   :str  '
        self.assertEqual(clean_text(raw_text), 'Class person(): name :str')

    def test_tokenize(self):
        raw_text = " the comparative     span  \n loading curves, together with" + \
            " supporting evidence    "
        self.assertListEqual(list(tokenize(raw_text)),
                             [
            'comparative', 'span', 'loading', 'curves',
            'supporting', 'evidence'
        ])
