"""
El Cairo command group.
"""

import os
import sqlite3
import sys

import arrow
import click
from arrow import Arrow

from .lib.database import query
from .lib.movie_printer import MoviePrinter


def cursor_printer_init(ctx):
    """
    Initialize the cursor and the printer.
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


def next_sunday() -> Arrow:
    """
    Arrow object of next sunday.
    """
    date = arrow.now()
    while date.weekday() != 6:
        date = date.dehumanize("in a day")
    return date.floor("day")


def next_saturday() -> Arrow:
    """
    Arrow object of the next saturday.
    """
    date = arrow.now()
    while date.weekday() != 5:
        date = date.dehumanize("in a day")
    return date.floor("day")


def day_start(date: Arrow) -> int:
    """
    Int representation of the start of the day of date.
    """
    return int(date.floor("day").format("YYYYMMDDHHmm"))


def day_end(date: Arrow) -> int:
    """
    Int representation of the end of the day of date.
    """
    return int(date.ceil("day").format("YYYYMMDDHHmm"))


@click.command()
@click.pass_context
def today(ctx) -> None:
    """
    Today's movie shows.
    """
    cursor_printer_init(ctx)
    now = arrow.now()
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(now),
        date_int_max=day_end(now),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def tomorrow(ctx) -> None:
    """
    Tomorrow's movie shows.
    """
    cursor_printer_init(ctx)
    tomorrow = arrow.now().dehumanize("in a day")
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(tomorrow),
        date_int_max=day_end(tomorrow),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def week(ctx) -> None:
    """
    Movie shows until next sunday.
    """
    cursor_printer_init(ctx)
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(arrow.now()),
        date_int_max=day_end(next_sunday()),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def weekend(ctx) -> None:
    """
    This weekend's movie shows.
    """
    cursor_printer_init(ctx)
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(next_saturday()),
        date_int_max=day_end(next_sunday()),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def day(ctx, date) -> None:
    """
    Movie shows of a given date.
    """
    cursor_printer_init(ctx)
    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)
    date_arrow: Arrow = arrow.get(f"{year}-{month}-{day_date}")
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(date_arrow),
        date_int_max=day_end(date_arrow),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.option("--date", type=click.DateTime(formats=["%d-%m-%Y"]), required=True)
@click.pass_context
def until(ctx, date) -> None:
    """
    Movie shows until a given date.
    """
    cursor_printer_init(ctx)
    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)
    date_arrow: Arrow = arrow.get(f"{year}-{month}-{day_date}")
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(arrow.now()),
        date_int_max=day_end(date_arrow),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@click.command()
@click.pass_context
def upcoming(ctx) -> None:
    """
    Upcoming movie shows.
    """
    cursor_printer_init(ctx)
    movies: list = query(
        cursor=ctx.obj["cursor"],
        date_int_min=day_start(arrow.now()),
        date_int_max=sys.maxsize,
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)
