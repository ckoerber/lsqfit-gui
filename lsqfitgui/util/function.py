"""Utilities for parsing and importing functions."""
from typing import Callable, Dict

import re
import importlib.util
import sympy


def parse_function(string: str):
    """Read function string and return function.

    Arguments:
        function: Name of the module and function.
            Example `module.py:main`
    """
    path, name = string.split(":")
    spec = importlib.util.spec_from_file_location("fcn_src", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)


def parse_function_expression(fcn: Callable, parameters: Dict) -> str:
    """Parse the fit function and posteriror to latex label."""
    expressions = {}
    for key, val in parameters.items():
        if hasattr(val, "__iter__"):
            expr = sympy.symbols(" ".join([f"{key}{n}" for n, el in enumerate(val)]))
        else:
            expr = sympy.Symbol(key)

        expressions[key] = expr

    try:
        f_expr = fcn(
            x=sympy.Symbol("x"), p={key: expr for key, expr in expressions.items()}
        )
        s = sympy.latex(f_expr)
        s = re.sub(r"\+\s+\-", "-", s)
    except Exception:
        s = None

    return s
