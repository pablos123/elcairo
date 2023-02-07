"""
El Cairo command.
"""

import click

from apis.elcairo import ElCairo
from commands.lib.movie_printer import MoviePrinter


@click.group()
@click.pass_context
def elcairo(ctx) -> None:
    """
    Print El Cairo movie shows.
    """
    ctx.obj["printer"] = MoviePrinter(
        images=ctx.obj["images"],
        no_extra_info=ctx.obj["no_extra_info"],
        urls=ctx.obj["urls"],
    )


@elcairo.command()
@click.pass_context
def today(ctx) -> None:
    """
    Print todays movie shows.
    """

    elcairo_obj = ElCairo()
    todays_json = elcairo_obj.get_todays_shows_json()

    ctx.obj["printer"].echo_list(todays_json)


@elcairo.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Print upcoming movie shows.
    """

    elcairo_obj = ElCairo()
    upcoming_json = elcairo_obj.get_upcoming_shows_json()

    ctx.obj["printer"].echo_list(upcoming_json)


@elcairo.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def day(ctx, date) -> None:
    """
    Print movie shows of a given date.
    """

    elcairo_obj = ElCairo()
    date_json = elcairo_obj.get_date_shows_json(
        date.year, date.month, date.day)


    ctx.obj["printer"].echo_data_structure(date_json)

    ctx.obj["printer"].echo_list(date_json)


@elcairo.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def until(ctx, date) -> None:
    """
    Print movie shows until a given date.
    """

    elcairo_obj = ElCairo()
    until_json = elcairo_obj.get_until_date_shows_json(
        date.year, date.month, date.day)

    ctx.obj["printer"].echo_list(until_json)
