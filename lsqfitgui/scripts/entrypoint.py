"""Entrypoint script for launching dash apps."""
from typing import Optional

import click

from gvar import load

from lsqfitgui import run_server
from lsqfitgui.util.function import parse_function


@click.command()
@click.argument("fit-file", type=str)
@click.option("--function", "-f", help="Python module/function used for fit.")
@click.option(
    "--host", help="Address to host the app on.", default="localhost", type=str
)
@click.option("--port", help="Port to host the app on.", default=8000, type=int)
def main(
    fit_file: str,
    function: Optional[str] = None,
    host: str = "localhost",
    port: int = 8000,
):
    """Run lsqfitgui server importing a pickle file.

    Arguments:
        fit_file: Pickle file pointing to a fit.
        function: Module/function string to use.
    """
    fit = load(fit_file)

    if function is not None:
        function = parse_function(function)
        fit.fcn = function

    if not hasattr(fit, "fcn"):
        raise ValueError(
            "Fit function not present in pickle file."
            " You may provide an external function using the flag."
        )

    run_server(fit, host=host, port=port)


if __name__ == "__main__":
    main()
