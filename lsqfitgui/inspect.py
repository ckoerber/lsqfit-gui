"""Reads fit from pickle file and initializes dashboard."""

from argparse import ArgumentParser
from lsqfitgui.dashboard import init_dasboard
from gvar import load
import streamlit

PARSER = ArgumentParser(description="Run dashboard from pickle file.")

PARSER.add_argument(
    "-i", "--input", type=str, help_text="Name of the pickle file to read from."
)


def main():
    """Runs inspect CLI."""
    args = PARSER.parse_args()
    fit = load(args.file)

    init_dasboard(fit)

    streamlit.run()


if __name__ == "__main__":
    main()
