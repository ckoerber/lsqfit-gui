#!/usr/bin/env python3
# coding: utf-8
"""Entrypoint for GUI."""
from fit import generate_fit, A0

from dash import html

from lsqfitgui import run_server


def get_additional_content(fit):
    """Generate aditional dash html elements based on a fit object."""
    return html.Div(
        [
            html.H2("Comparison against initial synthetic data values"),
            html.P("Synthetic"),
            html.Pre(str(A0)),
            html.P("Posterior"),
            html.Pre(str(fit.p)),
        ]
    )


def main():
    """Start the GUI for the fit."""
    run_server(
        name="Poly fit",
        fit_setup_function=generate_fit,
        fit_setup_kwargs={"n_poly": 4},
        meta_config=[
            {"name": "n_poly", "type": "number", "min": 1, "max": 10, "step": 1}
        ],
        use_default_content=True,
        get_additional_content=get_additional_content,
    )


if __name__ == "__main__":
    main()
