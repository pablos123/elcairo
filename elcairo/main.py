"""Print El Cairo cinema movie shows information."""

import importlib.metadata

import click

from elcairo.commands.database import database
from elcairo.commands.shows import shows


def version() -> str:
    """Command line interface for El Cairo cinema."""
    metadata = importlib.metadata.metadata("elcairo")
    project = metadata["Name"]
    author = metadata["author-email"]
    elcairo_version = metadata["Version"]
    return f"{project} version {elcairo_version} by {author}"


@click.group()
@click.version_option(message=version())
@click.pass_context
def elcairo(ctx: click.Context):
    """elcairo command group."""


elcairo.add_command(database)
elcairo.add_command(shows)


def main():
    """Execute elcairo."""
    elcairo(obj={})
