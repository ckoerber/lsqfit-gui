"""Reads fit from pickle file and initializes dashboard."""

from argparse import ArgumentParser
from lsqfitgui.dashboard import init_dasboard
from gvar import load
from pickle import loads
import streamlit

import importlib.util


PARSER = ArgumentParser(description="Run dashboard from pickle file.")

PARSER.add_argument(
    "-i", "--input", type=str, help="Name of the pickle file to read from."
)
PARSER.add_argument(
    "-f", "--function", type=str, help="Path to python function used for fit."
)


def parse_function(string: str):
    """
    """
    path, name = string.split(":")
    spec = importlib.util.spec_from_file_location("fcn_src", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)


def main():
    """Runs inspect CLI."""
    args = PARSER.parse_args()
    fit = load(args.input)

    if not hasattr(fit, "fcn"):
        if not args.function:
            raise ValueError("You must specify the fit function.")
        fit.fcn = parse_function(args.function)
    init_dasboard(fit)


if __name__ == "__main__":
    main()
