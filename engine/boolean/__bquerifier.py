from typing import Any
import sympy
from sympy.abc import x, y, z
#from sympy import symbols
from sympy import sympify
from engine.core import IRQuerifier
    

class BooleanIRQuerifier(IRQuerifier):
    def querify(self, query: str) -> Any:
        #convert a string to a sympy structure
        st = sympify(query, evaluate=False)
        return (sympy.logic.boolalg.simplify_logic(st,form='dnf', force =True)).args