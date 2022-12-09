from typing import Any, Iterable
from unittest import TestCase
import pandas as pd


def match_dataframe(
        test: TestCase, df: pd.DataFrame, *_, indexes: Iterable[Any],
        values: Iterable[Any] | None = None, strict: bool = False):
    check = indexes
    if values is not None:
        check = list(zip(check, values))
    else:
        check = list(zip(check, (None for _ in check)))

    if strict:
        test.assertEqual(
            len(df),
            len(check),
            "The dataframe given has other indexes")

    for k, v in check:
        if v is not None:
            test.assertEqual(
                df[k],
                v, f"The dataframe given doesn't store value {v} at index {k}")
        else:
            df[k]
