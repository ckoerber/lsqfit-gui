"""Tests for poly fit app."""
import pytest

from example.lsqfit_stability_example import generate_fit

from lsqfitgui import run_server


@pytest.fixture
def stability_fit_gui():
    """Provide poly fit app without running it."""
    return run_server(
        name="lsqfit stability example", fit=generate_fit(), run_app=False,
    )


def test_01_start_poly_fit_app(dash_duo, stability_fit_gui):
    """Checks if it is possible to start the polyfit app and check title."""
    dash_duo.start_server(stability_fit_gui.app)
    assert dash_duo.find_element("h1").text == stability_fit_gui.name
