from typing import Iterable
from .stopwords import STOPWORDS
import re

multi_space = re.compile(r'\s\s+')
tokens = re.compile(r"[a-zA-Z'0-9]+")


def clean_text(text: str) -> str:
    return multi_space.sub(' ', text.strip().replace('\t', ' ')
                           .replace('\n', ' ').replace('-', ' ')
                           .replace(' .', '.').capitalize())


def tokenize(text: str) -> Iterable[str]:
    clean = clean_text(text).lower()
    r = (
        word.replace("'", '')
        for word in (r.group() for r in tokens.finditer(clean))
        if word not in STOPWORDS and word.replace("'", '') not in STOPWORDS)
    return r
