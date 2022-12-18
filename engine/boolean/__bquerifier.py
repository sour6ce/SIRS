import hashlib
import re
from typing import Any, Iterable, List, NamedTuple, Tuple

import pandas as pd
import sympy
from engine.core import IRQuerifier
from sympy import Symbol, sympify
from sympy.logic.boolalg import And, BooleanFunction, Not, Or

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

    def __parse_S(self) -> BooleanFunction | Symbol:
        e = self.__parse_E()
        self.validate_token(self.lookahead(), 'eof')
        return e

    def __parse_E(self) -> BooleanFunction | Symbol:
        self.validate_token(self.lookahead(), ['op', 'term', 'neg'])
        T = self.__parse_T()
        x = self.__parse_X()
        if x is None:
            return T
        else:
            return x[0](T, x[1])

    def __parse_T(self) -> BooleanFunction | Symbol:
        lk = self.lookahead()
        self.validate_token(lk, ['op', 'term', 'neg'])
        if lk.type == 'neg':
            self.index += 1
            t = self.__parse_T()
            return Not(t)
        else:
            f = self.__parse_F()
            return f

    def __parse_F(self) -> BooleanFunction | Symbol:
        lk = self.lookahead()
        self.validate_token(lk, ['op', 'term'])
        if lk.type == 'term':
            self.index += 1
            return Symbol(lk.value)
        if lk.type == 'op':
            self.index += 1
            self.validate_token(self.lookahead(), ['op', 'term', 'neg'])
            e = self.__parse_E()
            self.validate_token(self.lookahead(), 'cp')
            self.index += 1
            return e

    def __parse_X(self) -> Tuple[BooleanFunction, BooleanFunction | Symbol] | None:
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
            t = self.__parse_T()
            return (func, t)
        return None

    def parse(self) -> BooleanFunction | Symbol:
        self.index = -1
        return self.__parse_S()


class BooleanIRQuerifier(IRQuerifier):
    __last = None

    def querify(self, query: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        # convert a string to a sympy structure
        # def __insertAnd(match: re.Match[query]):
        #     return ' & '.join(match.groups())
        # query = query.lower()
        # query = re.compile(r"([a-zA-Z'0-9])\s+(\(|~)").sub(__insertAnd, query)
        # query = re.compile(r"(\))s+([a-zA-Z'0-9])").sub(__insertAnd, query)
        # query = re.compile(
        #     r"([a-zA-z'0-9])\s+([a-zA-z'0-9])").sub(__insertAnd, query)
        # st = sympify(query, evaluate=False)
        bl = BooleanLexer()
        bp = BooleanParser(bl.lex(query))
        st = bp.parse()
        simplification = (
            sympy.logic.boolalg.simplify_logic(
                st, form='dnf', force=True))
        queries = []
        if (not isinstance(simplification, sympy.logic.Or)):
            queries = [simplification]
        else:
            queries = (sympy.logic.boolalg.simplify_logic(
                st, form='dnf', force=True)).args
        q_sym1 = [
            list(set(
                str(q)
                .replace('(',' ')
                .replace(')',' ')
                .replace('~',' ')
                .replace('|',' ')
                .replace('&',' ')
                .split()
                )) for q in queries]
        
        q_sym2 = [
            list(
                str(q)
                .replace('(',' ')
                .replace(')',' ')
                .replace('|',' ')
                .replace('&',' ')
                .replace('~', ' ~ ')
                .split()
            ) for q in queries]
           
        #query data frame
        #mascara de bits :'v
        q_df_bm = [pd.DataFrame({'query': pd.Series(data=[1]*len(q) ,index=q)}) for q in q_sym1]
        for q in q_df_bm:
            q.sort_index(inplace=True)
            q.index.name = 'term'
        
        #vector aparicion de palabras
        q_df=[]
        #me quito los terminos negativos
        q_sym3 = []
        for i in range(0,len(q_sym2)):
            q_dict = {}
            for j in range(0, len(q_sym2[i])):
                if q_sym2[i][j] =='~': continue
                if j>0 and q_sym2[i][j-1]=='~': continue
                else:
                    q_dict[(q_sym2[i][j])] = 1
            q_sym3.append(q_dict.keys())
        
        q_df = [pd.DataFrame({'query': pd.Series(data=[1]*len(q) ,index=q)}) for q in q_sym3]
        for q in q_df:
            q.sort_index(inplace=True)
            q.index.name = 'term'
        
        self.__last = (q_df, q_df_bm)

        return (q_df, q_df_bm)

    def get_hash(self) -> str:
        if self.__last is None:
            return ''
        else:
            h = hashlib.sha512()
            for q0, qbm in zip(self.__last[0], self.__last[1]):
                h.update(pd.util.hash_pandas_object(q0).values)
                h.update(pd.util.hash_pandas_object(qbm).values)
            return h.hexdigest()
