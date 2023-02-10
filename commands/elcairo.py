"""
El Cairo command.
"""

import os
import sqlite3

import click

from apis.elcairo import ElCairo
from commands.lib.movie_printer import MoviePrinter


class NoDataBase(Exception):
    """
    Exception for execution without database.
    """

    pass


@click.group()
@click.pass_context
def elcairo(ctx) -> None:
    """
    Print El Cairo movie shows.
    """

    try:
        if not os.path.exists("./cinecli.db"):
            raise NoDataBase
    except NoDataBase as _:
        click.echo("Create the database first! Aborting...")

    connection = sqlite3.connect("cinecli.db")
    connection.row_factory = sqlite3.Row
    ctx.obj["cursor"] = connection.cursor()

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

    elcairo_obj: ElCairo = ElCairo()
    todays_json: dict = elcairo_obj.get_todays_shows_json()

    ctx.obj["printer"].echo_list(todays_json)


@elcairo.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Print upcoming movie shows.
    """

    res = ctx.obj["cursor"].execute(
        "SELECT * FROM movies WHERE cinema='elcairo'")

    upcoming_shows = [dict(row) for row in res.fetchall()]

    ctx.obj["printer"].echo_list(upcoming_shows)


@elcairo.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def day(ctx, date) -> None:
    """
    Print movie shows of a given date.
    """

    elcairo_obj: ElCairo = ElCairo()
    date_json: dict = elcairo_obj.get_date_shows_json(
        date.year, date.month, date.day)

    ctx.obj["printer"].echo_list(date_json)


@elcairo.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def until(ctx, date) -> None:
    """
    Print movie shows until a given date.
    """

    elcairo_obj: ElCairo = ElCairo()
    until_json: dict = elcairo_obj.get_until_date_shows_json(
        date.year, date.month, date.day
    )

    ctx.obj["printer"].echo_list(until_json)
