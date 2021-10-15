# -*- coding: utf-8 -*-
"""Setup file for lsqfitgui."""
from lsqfitgui.version import __version__

__author__ = "@ckoerber, @millernb"

from os import path

from setuptools import setup, find_packages

CWD = path.abspath(path.dirname(__file__))

with open(path.join(CWD, "README.md"), encoding="utf-8") as inp:
    LONG_DESCRIPTION = inp.read()

with open(path.join(CWD, "requirements.txt"), encoding="utf-8") as inp:
    REQUIREMENTS = [el.strip() for el in inp.read().split(",")]


setup(
    name="lsqfitgui",
    version=__version__,
    python_requires=">=3.6",
    description="GUI for lsqfits.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=__author__,
    packages=find_packages(exclude=["docs", "tests", "example"]),
    package_data={"": ["lsqfitgui/assets/*.js"]},
    install_requires=REQUIREMENTS,
    entry_points={"console_scripts": ["lsqfitgui=lsqfitgui.scripts.entrypoint:main"]},
)
