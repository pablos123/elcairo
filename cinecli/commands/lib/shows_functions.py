"""Functions used in the shows command."""

import os
import sqlite3

import arrow
import click

from cinecli.commands.lib.movie_printer import MoviePrinter


def query(
    cursor: sqlite3.Cursor, date_int_min: int, date_int_max: int, order: str
) -> list[dict]:
    """Execute query."""

    movies: list = []
    try:
        res: sqlite3.Cursor = cursor.execute(
            f"""
            SELECT * FROM movies WHERE compare_date >= {date_int_min} AND
            compare_date <= {date_int_max} ORDER BY compare_date {order};
            """
        )
        movies = [dict(row) for row in res.fetchall()]
    except sqlite3.OperationalError:
        pass

    return movies


def cursor_init(ctx: click.Context) -> None:
    """Initialize the cursor and the printer."""

    script_dir = os.path.realpath(os.path.dirname(__file__))
    database_file = os.path.join(script_dir, "..", "cinecli.db")

    if not os.path.exists(database_file):
        click.echo("Create the database first!...")
        ctx.exit(1)

    connection = sqlite3.connect(database_file)

    connection.row_factory = sqlite3.Row
    ctx.obj["cursor"] = connection.cursor()


def printer_init(ctx: click.Context) -> None:
    ctx.obj["printer"] = MoviePrinter(
        images=ctx.obj["images"],
        no_extra_info=ctx.obj["no_extra_info"],
        no_separator=ctx.obj["no_separator"],
        urls=ctx.obj["urls"],
        image_urls=ctx.obj["image_urls"],
    )


def next_sunday() -> arrow.Arrow:
    """Arrow object of next sunday."""

    date: arrow.Arrow = arrow.now()
    while date.weekday() != 6:
        date = date.dehumanize("in a day")
    return date.floor("day")


def next_saturday() -> arrow.Arrow:
    """Arrow object of the next saturday."""

    date: arrow.Arrow = arrow.now()
    while date.weekday() != 5:
        date = date.dehumanize("in a day")
    return date.floor("day")


def day_start(date: arrow.Arrow) -> int:
    """Int representation of the start of the day of date."""

    return int(date.floor("day").format("YYYYMMDDHHmm"))


def day_end(date: arrow.Arrow) -> int:
    """Int representation of the end of the day of date."""

    return int(date.ceil("day").format("YYYYMMDDHHmm"))
