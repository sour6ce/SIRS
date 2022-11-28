from typing import Any
import sympy
from sympy.abc import x, y, z
#from sympy import symbols
from sympy import sympify
from engine.core import IRQuerifier
import panda as pd
    

class BooleanIRQuerifier(IRQuerifier):
    def querify(self, query: str) -> Any:
        #convert a string to a sympy structure
        st = sympify(query, evaluate=False)
        queries = (sympy.logic.boolalg.simplify_logic(st,form='dnf', force =True)).args
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
            list(set(
                str(q)
                .replace('(',' ')
                .replace(')',' ')
                .replace('|',' ')
                .replace('&',' ')
                .split()
                )) for q in queries]
           
        #query data frame
        #mascara de bits :'v
        q_df_bm = [pd.DataFrame({'query': pd.Series(data=[1]*len(q) ,index=q)}) for q in q_sym1]
        
        #vector aparicion de palabras
        q_df=[]
        #me quito los terminos negativos
        q_sym3 = ''
        for i in range(0,len(q_sym2)):
            q_dict = []
            for j in range(0, len(q_sym2[i])):
                if q_sym2[i][j] =='~': continue
                if j>0 and q_sym2[i][j-1]=='~': continue
                else:
                    q_dict.append((q_sym2[i][j]))
            q_sym3.append(q_dict)
        
        q_df = [pd.DataFrame({'query': pd.Series(data=[1]*len(q) ,index=q)}) for q in q_sym3]
        
        return(q_df, q_df_bm)
        