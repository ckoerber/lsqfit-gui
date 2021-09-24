#!/usr/bin/env python3
# coding: utf-8
"""Entrypoint for GUI."""
from fit import generate_fit

from lsqfitgui import run_server


def main():
    """Starts the GUI for the fit."""
    run_server(
        name="Poly fit",
        fit_setup_function=generate_fit,
        fit_setup_kwargs={"n_poly": 4},
        meta_config=[
            {"name": "n_poly", "type": "number", "min": 1, "max": 10, "step": 1}
        ],
    )


if __name__ == "__main__":
    main()
