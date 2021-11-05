"""Tests for poly fit app."""
import pytest
import json

from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from example.fit import generate_fit

from lsqfitgui import run_server


META_CONFIG = [{"name": "n_poly", "type": "number", "min": 1, "max": 10, "step": 1}]
FIT_SETUP_KWARGS = {"n_poly": 4}


@pytest.fixture
def poly_fit_gui():
    """Provide poly fit app without running it."""
    return run_server(
        name="Poly fit",
        fit_setup_function=generate_fit,
        fit_setup_kwargs=FIT_SETUP_KWARGS,
        meta_config=META_CONFIG,
        use_default_content=True,
        run_app=False,
    )


def test_01_start_poly_fit_app(dash_duo, poly_fit_gui):
    """Checks if it is possible to start the polyfit app and check title."""
    dash_duo.start_server(poly_fit_gui.app)
    assert dash_duo.find_element("h1").text == poly_fit_gui.name


def test_02_check_forms(dash_duo, poly_fit_gui):
    """Checks if all forms are present and have values as expected."""
    dash_duo.start_server(poly_fit_gui.app)

    expected_forms = [("meta", "n_poly", str(FIT_SETUP_KWARGS["n_poly"]))] + [
        ("prior", f"{key}-{kind}", str(value))
        for key, dist in poly_fit_gui.fit.prior.items()
        for kind, value in zip(("mean", "sdev"), (dist.mean, dist.sdev))
    ]

    input_elements = dash_duo.driver.find_elements(By.TAG_NAME, "input")

    forms = []
    for element in input_elements:
        idx = json.loads(element.get_attribute("id"))
        forms.append((idx["type"], idx["name"], element.get_attribute("value")))

    assert expected_forms == forms


def test_03_update_prior(dash_duo, poly_fit_gui):
    """Checks if updating the prior updates the fit."""
    dash_duo.start_server(poly_fit_gui.app)

    initial_fit = poly_fit_gui.initial_fit

    key = list(initial_fit.prior.keys())[0]
    value = initial_fit.prior[key].sdev + 1
    value_str = f"{value:1.2f}"

    # find element by xpath/placeholder is easier than by id because of dict
    form = dash_duo.driver.find_element(By.XPATH, f'//input[@placeholder="{key}-sdev"]')
    dash_duo.clear_input(form)
    form.send_keys(value_str)
    form.send_keys(Keys.RETURN)
    # There is proably a better way for doing this...
    sleep(1)

    assert poly_fit_gui.fit.prior[key].sdev == value


def test_05_update_meta(dash_duo, poly_fit_gui):
    """Checks if updating the meta updates the fit."""
    dash_duo.start_server(poly_fit_gui.app)

    n_poly_new = 5

    # find element by xpath/placeholder is easier than by id because of dict
    form = dash_duo.driver.find_element(By.XPATH, '//input[@placeholder="n_poly"]')
    dash_duo.clear_input(form)
    form.send_keys(str(n_poly_new))
    form.send_keys(Keys.RETURN)

    WebDriverWait(dash_duo.driver, 2).until(
        EC.presence_of_element_located(
            (By.XPATH, f'//input[@placeholder="a{n_poly_new-1}-mean"]')
        )
    )

    assert len(poly_fit_gui.fit.prior) == n_poly_new
