from typing import Iterable
from .stopwords import STOPWORDS
import re

multi_space = re.compile(r'\s\s+')
tokens = re.compile(r"[a-zA-Z'0-9]+")


def clean_text(text: str) -> str:
    return multi_space.sub(' ', text.strip().lower().replace('\t', ' ')
                           .replace('\n', ' ').replace('-', ' '))


def tokenize(text: str) -> Iterable[str]:
    r = (word for word in (r.group()
         for r in tokens.finditer(clean_text(text))) if word not in STOPWORDS)
    return r
