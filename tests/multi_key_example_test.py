"""Tests for poly fit app."""
import pytest

from example.multi_key_example import get_fit

from lsqfitgui import run_server


@pytest.fixture
def gui():
    """Provide poly fit app without running it."""
    return run_server(name="lsqfit basic example", fit=get_fit(), run_app=False,)


def test_01_start_poly_fit_app(dash_duo, gui):
    """Checks if it is possible to start the polyfit app and check title."""
    dash_duo.start_server(gui.app)
    assert dash_duo.find_element("h1").text == gui.name
