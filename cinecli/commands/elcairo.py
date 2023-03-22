"""
El Cairo command group.
"""

import os
import sqlite3
import sys

import arrow
import click
from arrow import Arrow

from .lib.database_utils import query_eq, query_leq
from .lib.movie_printer import MoviePrinter

TODAY: int = int(arrow.now().format("YYYYMMDD"))


def cursor_printer_init(ctx):
    """
    Initialize the cursor and the printer
    """
    script_dir = os.path.realpath(os.path.dirname(__file__))
    database_file = os.path.join(script_dir, "cinecli.db")

    if not os.path.exists(database_file):
        click.echo("Create the database first!...")
        ctx.exit(1)

    connection = sqlite3.connect(database_file)

    connection.row_factory = sqlite3.Row
    ctx.obj["cursor"] = connection.cursor()

    ctx.obj["printer"] = MoviePrinter(
        images=ctx.obj["images"],
        no_extra_info=ctx.obj["no_extra_info"],
        no_separator=ctx.obj["no_separator"],
        urls=ctx.obj["urls"],
    )


def get_next_sunday() -> int:
    """
    Returns the int representation of the next sunday.
    """
    date = arrow.now()
    while date.weekday() != 6:
        date = date.dehumanize("in a day")
    return int(date.format("YYYYMMDD"))


def get_next_saturday() -> int:
    """
    Returns the int representation of the next saturday.
    """
    date = arrow.now()
    while date.weekday() != 5:
        date = date.dehumanize("in a day")
    return int(date.format("YYYYMMDD"))


@click.command()
@click.pass_context
def today(ctx) -> None:
    """
    Print todays movie shows.
    """
    cursor_printer_init(ctx)
    movies: list = query_eq(ctx.obj["cursor"], TODAY)
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def tomorrow(ctx) -> None:
    """
    Print tomorrow movie shows.
    """
    cursor_printer_init(ctx)
    date_int: int = int(arrow.now().dehumanize("in a day").format("YYYYMMDD"))
    movies: list = query_eq(ctx.obj["cursor"], date_int)
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def week(ctx) -> None:
    """
    Print the movie shows until the next sunday.
    """
    cursor_printer_init(ctx)
    date_int: int = get_next_sunday()
    movies: list = query_leq(
        ctx.obj["cursor"], date_int_min=TODAY, date_int_max=date_int
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def weekend(ctx) -> None:
    """
    Print the movie shows until the next sunday.
    """
    cursor_printer_init(ctx)

    date_int_min: int = get_next_saturday()
    date_int_max: int = get_next_sunday()
    movies: list = query_leq(
        ctx.obj["cursor"], date_int_min=date_int_min, date_int_max=date_int_max
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def day(ctx, date) -> None:
    """
    Print movie shows of a given date.
    """
    cursor_printer_init(ctx)
    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)

    date_arrow: Arrow = arrow.get(f"{year}-{month}-{day_date}")
    date_int: int = int(date_arrow.format("YYYYMMDD"))
    movies: list = query_eq(ctx.obj["cursor"], date_int)
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def until(ctx, date) -> None:
    """
    Print movie shows until a given date.
    """
    cursor_printer_init(ctx)
    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)

    date_arrow: Arrow = arrow.get(f"{year}-{month}-{day_date}")
    date_int: int = int(date_arrow.format("YYYYMMDD"))
    movies: list = query_leq(
        ctx.obj["cursor"], date_int_min=TODAY, date_int_max=date_int
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Print upcoming movie shows.
    """
    cursor_printer_init(ctx)
    movies: list = query_leq(
        ctx.obj["cursor"], date_int_min=TODAY, date_int_max=sys.maxsize
    )
    ctx.obj["printer"].echo_list(movies)
