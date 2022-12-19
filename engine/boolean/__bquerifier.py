import hashlib
import json
import re
from typing import Dict, Iterable, List, NamedTuple, Set, Tuple

import sympy
from engine.core import IRQuerifier
from sympy import Symbol
from sympy.logic.boolalg import And, BooleanAtom, BooleanFunction, Not, Or

from ..stopwords import STOPWORDS

term_char_r = r"[a-zA-Z'0-9]"
term_r = term_char_r+"+"


class Token(NamedTuple):
    value: str
    type: str
    position: int


class BooleanError(Exception):
    pass


class BooleanLexer:
    tokens = {
        'term': term_r,
        'op': r"\(",
        'cp': r"\)",
        'and': "&",
        'or': r"[|]",
        'neg': r"[~]"
    }

    def lex(self, text: str) -> Iterable[Token]:
        token_list = [Token('$', 'eof', len(text))]
        for ttype, exp in self.tokens.items():
            regex = re.compile(exp)
            token_list.extend(
                Token(m[0], ttype, m.start()) for m in regex.finditer(text)
            )
        token_list.sort(key=lambda x: x.position)
        return token_list


class BooleanParser:
    ParserAtom = BooleanFunction | BooleanAtom | Symbol

    index = -1
    token_chain: List[Token]

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.token_chain = list(tokens)

    def lookahead(self) -> Token: return self.token_chain[self.index+1]

    def validate_token(
        self,
        token: int | Token,
        token_type: str | List[str]
    ) -> None:
        if isinstance(token, int):
            token = self.token_chain[token]
        if isinstance(token_type, str):
            token_type = [token_type]
        if token.type not in token_type:
            raise BooleanError(
                f"Unexpected token in position: {token.position}, got {token.value}")

    def __parse_S(self) -> ParserAtom:
        e = self.__parse_E()
        self.validate_token(self.lookahead(), 'eof')
        return e

    def __parse_E(self) -> ParserAtom:
        self.validate_token(self.lookahead(), ['op', 'term', 'neg'])
        T = self.__parse_T()
        x = self.__parse_X()
        if x is None:
            return T
        else:
            return x[0](T, x[1])

    def __parse_T(self) -> ParserAtom:
        lk = self.lookahead()
        self.validate_token(lk, ['op', 'term', 'neg'])
        if lk.type == 'neg':
            self.index += 1
            t = self.__parse_T()
            return Not(t)
        else:
            f = self.__parse_F()
            return f

    def __parse_F(self) -> ParserAtom:
        lk = self.lookahead()
        self.validate_token(lk, ['op', 'term'])
        if lk.type == 'term':
            self.index += 1
            if lk.value in STOPWORDS:
                return sympy.true
            return Symbol(lk.value)
        if lk.type == 'op':
            self.index += 1
            self.validate_token(self.lookahead(), ['op', 'term', 'neg'])
            e = self.__parse_E()
            self.validate_token(self.lookahead(), 'cp')
            self.index += 1
            return e

    def __parse_X(self) -> Tuple[BooleanFunction, ParserAtom] | None:
        lk = self.lookahead()
        if lk.type == 'and':
            self.index += 1
            func = And
            e = self.__parse_E()
            return (func, e)
        elif lk.type == 'or':
            self.index += 1
            func = Or
            e = self.__parse_E()
            return (func, e)
        elif lk.type in ['op', 'term', 'neg']:
            func = And
            e = self.__parse_E()
            return (func, e)
        return None

    def parse(self) -> BooleanFunction | Symbol:
        self.index = -1
        return self.__parse_S()


class BooleanIRQuerifier(IRQuerifier):
    __last = None

    def querify(self, query: str) -> List[Dict[str, bool]]:
        # The object used as query is a list of AND-only queries that
        # are joined by ORs. Each AND-only query is a Set of tuples
        # representing a term (first element of each tuple) and if the
        # term is in negative form or not (True or False respectively as
        # second element of the tuple)

        # Initialize parse
        bl = BooleanLexer()
        bp = BooleanParser(bl.lex(query.lower()))

        st = bp.parse()  # Gives a sympy boolean expression

        # Simplifies boolean expression
        simplification = (
            sympy.logic.boolalg.simplify_logic(
                st, form='dnf', force=True))

        queries = []

        # It may be a simple AND-only query
        if (not isinstance(simplification, sympy.logic.Or)):
            queries = [simplification]
        else:
            queries = simplification.args

        # For each AND-only query extract the
        q_syms = [
            list(
                str(q)  # Use the simplifications as str
                .replace('(', ' ')
                .replace(')', ' ')
                .replace('|', ' ')
                .replace('&', ' ')
                .replace('~', ' ~ ')
                .split()
            ) for q in queries]

        and_only_queries = []

        # For each AND-only query get the values used and if they have a
        # negation operator before (are in negative)
        for query in q_syms:
            and_values: Dict[str, bool] = {}
            for j in range(0, len(query)):
                if query[j] == '~':
                    # Skip negative operator
                    continue
                if j > 0 and query[j-1] == '~':  # Has a negative before
                    and_values[query[j]] = True
                else:
                    and_values[query[j]] = False
            and_only_queries.append(and_values)

        self.__last = and_only_queries

        return and_only_queries

    def get_hash(self) -> str:
        if self.__last is None:
            return ''
        else:
            h = hashlib.sha512()
            h.update(json.dumps(self.__last).encode())
            return h.hexdigest()
