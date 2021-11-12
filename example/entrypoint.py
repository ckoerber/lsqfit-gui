#!/usr/bin/env python3
# coding: utf-8
"""Entrypoint for GUI."""
from fit import generate_fit, A0

from dash import html

from lsqfitgui import FitGUI, DefaultBodyTemplate


class MyBodyTemplate(DefaultBodyTemplate):
    # Bootstrap columns: https://getbootstrap.com/docs/5.0/layout/grid/#grid-options
    sidebar_div_class = "col-xs-12 col-sm-6 col-md-6 col-xl-5 col-xxl-4"
    content_div_class = "col-xs-12 col-sm-6 col-md-6 col-xl-7 col-xxl-8"

    def get_content(self, fit, meta=None):
        """Add additional content to the default content."""
        content = super().get_content(fit, meta=meta)
        content.append(
            html.Div(
                [
                    html.H2("Comparison against initial synthetic data values"),
                    html.P("Synthetic"),
                    html.Pre(str(A0)),
                    html.P("Posterior"),
                    html.Pre(str(fit.p)),
                ]
            )
        )
        return content


def main():
    """Start the GUI for the fit."""
    fit_gui = FitGUI(
        fit_setup_function=generate_fit,
        fit_setup_kwargs={"n_poly": 4},
        meta_config=[
            {"name": "n_poly", "type": "number", "min": 1, "max": 10, "step": 1}
        ],
        template_cls=MyBodyTemplate,
    )
    fit_gui.name = "Poly fit"
    fit_gui.setup_app()
    fit_gui.run_server()


if __name__ == "__main__":
    main()
