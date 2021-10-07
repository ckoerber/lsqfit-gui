"""Utility regarding version numbers."""
import __main__ as main
from os.path import basename

from gvar import __version__ as gvar_version
from lsqfit import __version__ as lsqfit_version
from lsqfitgui.version import __version__ as lsqfitgui_version


def get_version_string() -> str:
    """Return version string of dependencies."""
    return (
        "("
        + " | ".join(
            [
                f"gvar: {gvar_version}",
                f"lsqfit: {lsqfit_version}",
                f"lsqfitgui: {lsqfitgui_version}",
            ]
        )
        + ")"
    )


def get_entrypoint_string(filename_only: bool = True) -> str:
    """Get name of the entry point script."""
    full_name = main.__file__
    name = basename(full_name) if filename_only else full_name
    return f"Entrypoint: {name}"
