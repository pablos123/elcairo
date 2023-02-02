"""
El Cairo command.
"""

import click

from apis.elcairo import ElCairo
from commands.lib.movie_printer import MoviePrinter

printer = MoviePrinter()


@click.group()
@click.pass_context
def elcairo(ctx) -> None:
    """
    Print El Cairo movie shows.
    """


@elcairo.command()
@click.pass_context
def today(ctx) -> None:
    """
    Print todays movie shows.
    """

    elcairo_obj = ElCairo()
    todays_json = elcairo_obj.get_todays_shows_json()

    printer.echo_list(todays_json, ctx.obj["images"])


@elcairo.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Print upcoming movie shows.
    """

    elcairo_obj = ElCairo()
    upcoming_json = elcairo_obj.get_upcoming_shows_json()

    printer.echo_list(upcoming_json, ctx.obj["images"])
