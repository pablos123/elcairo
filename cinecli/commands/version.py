import click

from ..__version__ import __version__

@click.command()
def version() -> None:
    """
    Print version and exit.
    """
    click.echo(__version__)
