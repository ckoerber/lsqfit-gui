"""Utilities for parsing and importing functions."""

import importlib.util


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
