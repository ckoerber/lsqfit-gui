"""Tests for poly fit app."""
import pytest
import json

from example.fit import generate_fit

from lsqfitgui import run_server


META_CONFIG = [{"name": "n_poly", "type": "number", "min": 1, "max": 10, "step": 1}]
FIT_SETUP_KWARGS = {"n_poly": 4}


@pytest.fixture
def poly_fit_app():
    """Provide poly fit app without running it."""
    return run_server(
        name="Poly fit",
        fit_setup_function=generate_fit,
        fit_setup_kwargs=FIT_SETUP_KWARGS,
        meta_config=META_CONFIG,
        use_default_content=True,
        run_app=False,
    )


def test_01_start_poly_fit_app(dash_duo, poly_fit_app):
    """Checks if it is possible to start the polyfit app and check title."""
    dash_duo.start_server(poly_fit_app)
    assert dash_duo.find_element("h1").text == poly_fit_app.fit_gui.name


def test_02_check_forms(dash_duo, poly_fit_app):
    """Checks if all forms are present and have values as expected."""
    dash_duo.start_server(poly_fit_app)

    expected_forms = [("meta", "n_poly", str(FIT_SETUP_KWARGS["n_poly"]))] + [
        ("prior", f"{key}-{kind}", str(value))
        for key, dist in poly_fit_app.fit_gui.fit.prior.items()
        for kind, value in zip(("mean", "sdev"), (dist.mean, dist.sdev))
    ]

    input_elements = dash_duo.driver.find_elements_by_tag_name("input")

    forms = []
    for element in input_elements:
        idx = json.loads(element.get_attribute("id"))
        forms.append((idx["type"], idx["name"], element.get_attribute("value")))

    assert expected_forms == forms
