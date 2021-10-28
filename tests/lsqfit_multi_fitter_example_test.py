"""Tests for poly fit app."""
import pytest

from example.lsqfit_multi_fitter_example import make_fitter

from lsqfitgui import run_server


@pytest.fixture
def fit_app():
    """Provide multi fit app without running it."""
    return run_server(
        name="lsqfit basic example", fit_setup_function=make_fitter, run_app=False,
    )


def test_01_start_multi_fit_app(dash_duo, fit_app):
    """Checks if it is possible to start the multi fit app and check title."""
    dash_duo.start_server(fit_app)
    assert dash_duo.find_element("h1").text == fit_app.fit_gui.name
