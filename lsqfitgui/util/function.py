"""Utilities for parsing and importing functions."""
from typing import Callable, Dict, Optional, List

import re
import importlib.util
import sympy
from numpy import ndarray


def parse_function(string: str):
    """Read function string and return function.

    Arguments:
        function: Name of the module and function.
            Example `module.py:main`
    """
    try:
        path, name = string.split(":")
        spec = importlib.util.spec_from_file_location("fcn_src", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, name)
    except Exception:
        return None


def parse_function_expression(
    fcn: Callable, parameters: Dict, x_dict_keys: Optional[List[str]] = None
) -> str:
    """Parse the fit function and posteriror to latex label."""
    try:
        expressions = {}
        for key, val in parameters.items():
            if hasattr(val, "__iter__"):
                expr = sympy.symbols(
                    " ".join([f"{key}{n}" for n, el in enumerate(val)])
                )
            else:
                expr = sympy.Symbol(key)

            expressions[key] = expr

        xx = (
            sympy.Symbol("x")
            if x_dict_keys is None
            else {key: sympy.Symbol("x") for key in x_dict_keys}
        )
        f_expr = fcn(x=xx, p=expressions)
        if isinstance(f_expr, dict):
            lines = [
                sympy.latex(sympy.Symbol(key)) + " &= " + sympy.latex(val)
                for key, val in f_expr.items()
            ]
            s = "\\begin{aligned}\n" + r" \\ ".join(lines) + "\n\\end{aligned}\n"
        elif isinstance(f_expr, (list, ndarray)):
            lines = [" & " + sympy.latex(val) for val in f_expr]
            s = "\\begin{aligned}\n" + r" \\ ".join(lines) + "\n\\end{aligned}\n"
        else:
            s = sympy.latex(f_expr)
        s = re.sub(r"\+\s+\-", "-", s)
    except Exception:
        s = None

    return s
