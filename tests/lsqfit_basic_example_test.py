"""Tests for poly fit app."""
import pytest

from example.lsqfit_basic_example import generate_fit

from lsqfitgui import run_server


META_CONFIG = [{"name": "n_exp", "type": "number", "min": 1, "max": 10, "step": 1}]
FIT_SETUP_KWARGS = {"n_exp": 4}


@pytest.fixture
def basic_fit_gui():
    """Provide poly fit app without running it."""
    return run_server(
        name="lsqfit basic example",
        fit_setup_function=generate_fit,
        fit_setup_kwargs=FIT_SETUP_KWARGS,
        meta_config=META_CONFIG,
        run_app=False,
    )


def test_01_start_poly_fit_app(dash_duo, basic_fit_gui):
    """Checks if it is possible to start the polyfit app and check title."""
    dash_duo.start_server(basic_fit_gui.app)
    assert dash_duo.find_element("h1").text == basic_fit_gui.name
