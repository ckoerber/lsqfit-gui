"""Lsqfit GUI."""
from dash import Dash
from lsqfitgui.frontend.dashboard import get_layout


def run_server(fit, name: str = "Lsqfit GUI", debug: bool = True, **kwargs):
    """Provide dashboard for lsqfitgui."""
    """Initialize the app."""
    app = Dash(name)
    app.layout = get_layout(fit, **kwargs)
    app.run_server(debug=debug)
