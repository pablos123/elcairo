import click

import importlib.metadata

@click.command()
def version() -> None:
    """
    Print version and exit.
    """
    metadata = importlib.metadata.metadata("cinecli")
    project = metadata["Name"]
    author = metadata["author-email"]
    version = metadata ["Version"]
    click.echo(f"{project} version {version} by {author}")
