"""
El Cairo command group.
"""

import os
import sqlite3
import sys
from sqlite3.dbapi2 import Connection

import arrow
import click
from arrow import Arrow

from .lib.database_utils import query_eq, query_leq
from .lib.movie_printer import MoviePrinter

TODAY: int = int(arrow.now().format("YYYYMMDD"))


@click.group()
@click.pass_context
def elcairo(ctx) -> None:
    """
    Print El Cairo movie shows.
    """
    script_dir: str = os.path.realpath(os.path.dirname(__file__))
    database_file: str = os.path.join(script_dir, "cinecli.db")

    if not os.path.exists(database_file):
        click.echo("Create the database first!...")
        ctx.exit(1)

    connection: Connection = sqlite3.connect(database_file)

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
    movies: list = query_eq(ctx.obj["cursor"], "elcairo", TODAY)
    ctx.obj["printer"].echo_list(movies)


@elcairo.command()
@click.pass_context
def tomorrow(ctx) -> None:
    """
    Print tomorrow movie shows.
    """
    date_int: int = int(arrow.now().dehumanize(
        "next sunday").format("YYYYMMDD"))
    movies: list = query_eq(ctx.obj["cursor"], "elcairo", date_int)
    ctx.obj["printer"].echo_list(movies)


@elcairo.command()
@click.pass_context
def week(ctx) -> None:
    """
    Print the movie shows until the next sunday.
    """

    def get_next_sunday() -> int:
        """
        Returns the int representation of the next sunday.
        """
        date = arrow.now()
        while date.weekday() != 0:
            date = date.dehumanize("in a day")
        return int(date.format("YYYYMMDD"))

    date_int: int = get_next_sunday()
    movies: list = query_leq(
        ctx.obj["cursor"], "elcairo", date_int_min=TODAY, date_int_max=date_int
    )
    ctx.obj["printer"].echo_list(movies)


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
    movies: list = query_eq(ctx.obj["cursor"], "elcairo", date_int)
    ctx.obj["printer"].echo_list(movies)


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
    movies: list = query_leq(
        ctx.obj["cursor"], "elcairo", date_int_min=TODAY, date_int_max=date_int
    )
    ctx.obj["printer"].echo_list(movies)


@elcairo.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Print upcoming movie shows.
    """
    movies: list = query_leq(
        ctx.obj["cursor"], "elcairo", date_int_min=TODAY, date_int_max=sys.maxsize
    )
    ctx.obj["printer"].echo_list(movies)
