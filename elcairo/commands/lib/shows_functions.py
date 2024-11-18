"""Functions used in the shows command."""

import sqlite3
from pathlib import Path

import arrow
import click

from elcairo.commands.lib.movie_printer import MoviePrinter


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
    script_dir: Path = Path(__file__).parent.resolve()
    database_file: Path = script_dir / ".." / "elcairo.db"

    if not database_file.exists():
        click.echo("Create the database first!")
        raise click.exceptions.Exit(1)

    connection = sqlite3.connect(database_file)

    connection.row_factory = sqlite3.Row
    ctx.obj["cursor"] = connection.cursor()


def printer_init(ctx: click.Context) -> None:
    """Initialize the MoviePrinter given the click args passed."""
    ctx.obj["printer"] = MoviePrinter(
        name=ctx.obj["name"],
        date=ctx.obj["date"],
        images=ctx.obj["images"],
        image_url=ctx.obj["image_url"],
        synopsis=ctx.obj["synopsis"],
        extra_info=ctx.obj["extra_info"],
        url=ctx.obj["url"],
        separator=ctx.obj["separator"],
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
    """Integer representation of the start of the day of date."""
    return int(date.floor("day").format("YYYYMMDDHHmm"))


def day_end(date: arrow.Arrow) -> int:
    """Integer representation of the end of the day of date."""
    return int(date.ceil("day").format("YYYYMMDDHHmm"))
