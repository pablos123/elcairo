"""Print El Cairo cinema movie shows information."""

import importlib.metadata

import click

from cinecli.commands.database import database
from cinecli.commands.shows import shows


def version() -> str:
    """Command line interface for El Cairo cinema."""
    metadata = importlib.metadata.metadata("cinecli")
    project = metadata["Name"]
    author = metadata["author-email"]
    cinecli_version = metadata["Version"]
    return f"{project} version {cinecli_version} by {author}"


@click.group()
@click.version_option(message=version())
@click.pass_context
def cinecli(ctx: click.Context):
    """cinecli command group."""


cinecli.add_command(database)
cinecli.add_command(shows)


def main():
    """Execute cinecli."""

    cinecli(obj={})
