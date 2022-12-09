from typing import Tuple
import sympy
#from sympy import symbols
from sympy import sympify
from engine.core import IRQuerifier
import pandas as pd
import re
import hashlib
    

class BooleanIRQuerifier(IRQuerifier):
    __last = None

    def querify(self, query: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        #convert a string to a sympy structure
        def __insertAnd(match: re.Match[query]):
            return ' & '.join(match.groups())
        query = query.lower()
        query = re.compile(r"([a-zA-z'0-9])\s+(\(|~)").sub(__insertAnd, query)
        query = re.compile(r"(\))s+([a-zA-z'0-9])").sub(__insertAnd, query)
        query = re.compile(
            r"([a-zA-z'0-9])\s+([a-zA-z'0-9])").sub(__insertAnd, query)
        st = sympify(query, evaluate=False)
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
