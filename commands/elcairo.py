"""
El Cairo command.
"""

import os
import sqlite3

import arrow
import click
from arrow import Arrow

from commands.lib.movie_printer import MoviePrinter


class NoDataBase(Exception):
    """
    Exception for execution without database.
    """


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

    date_int: int = int(arrow.now().format("YYYYMMDD"))

    res = ctx.obj["cursor"].execute(
        f"SELECT * FROM movies WHERE cinema='elcairo' AND compare_date = {date_int};"
    )

    todays_shows = [dict(row) for row in res.fetchall()]

    ctx.obj["printer"].echo_list(todays_shows)


@elcairo.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Print upcoming movie shows.
    """

    date_int: int = int(arrow.now().format("YYYYMMDD"))

    res = ctx.obj["cursor"].execute(
        f"SELECT * FROM movies WHERE cinema='elcairo' AND compare_date >= {date_int};"
    )

    upcoming_shows = [dict(row) for row in res.fetchall()]

    ctx.obj["printer"].echo_list(upcoming_shows)


@elcairo.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def day(ctx, date) -> None:
    """
    Print movie shows of a given date.
    """

    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)

    date_arrow: Arrow = arrow.get(f"{year}-{month}-{day_date}")

    date_int: int = int(date_arrow.format("YYYYMMDD"))

    res = ctx.obj["cursor"].execute(
        f"SELECT * FROM movies WHERE cinema='elcairo' AND compare_date = {date_int};"
    )

    day_shows = [dict(row) for row in res.fetchall()]

    ctx.obj["printer"].echo_list(day_shows)


@elcairo.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def until(ctx, date) -> None:
    """
    Print movie shows until a given date.
    """

    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)

    date_arrow: Arrow = arrow.get(f"{year}-{month}-{day_date}")

    date_int: int = int(date_arrow.format("YYYYMMDD"))

    res = ctx.obj["cursor"].execute(
        f"SELECT * FROM movies WHERE cinema='elcairo' AND compare_date <= {date_int};"
    )

    day_shows = [dict(row) for row in res.fetchall()]

    ctx.obj["printer"].echo_list(day_shows)
