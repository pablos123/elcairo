"""Functions used in the shows command."""

import sqlite3
from pathlib import Path

import arrow
import click

from elcairo.api.elcairo import ElCairoEvent, ElCairoExtraInfo
from elcairo.commands.lib.events_printer import ElCairoEventsPrinter


def create_elcairo_event(row: dict) -> ElCairoEvent:
    extra_info: ElCairoExtraInfo = ElCairoExtraInfo(
        direction=row["direction"],
        cast=row["cast"],
        genre=row["genre"],
        duration=row["duration"],
        origin=row["origin"],
        year=row["year"],
        age=row["age"],
    )
    return ElCairoEvent(
        name=row["name"],
        date=row["date"],
        synopsis=row["synopsis"],
        cost=row["cost"],
        image_url=row["image_url"],
        image_path=row["image_path"],
        url=row["url"],
        extra_info=extra_info,
    )


def query(
    cursor: sqlite3.Cursor, date_int_min: int, date_int_max: int, order: str
) -> list[ElCairoEvent]:
    """Execute query."""
    events: list[ElCairoEvent] = []
    try:
        res: sqlite3.Cursor = cursor.execute(
            "SELECT * FROM events WHERE compare_date >= ? AND compare_date <= ? ORDER BY compare_date "
            + order,
            (date_int_min, date_int_max),
        )
        events = [create_elcairo_event(dict(row)) for row in res.fetchall()]
    except sqlite3.OperationalError:
        pass

    return events


def cursor_init(obj: dict) -> None:
    """Initialize the cursor and the printer."""
    script_dir: Path = Path(__file__).parent.resolve()
    database_file: Path = script_dir / ".." / "elcairo.db"

    if not database_file.exists():
        click.echo("Create the database first!")
        raise click.exceptions.Exit(1)

    connection = sqlite3.connect(database_file)
    click.get_current_context().with_resource(connection)

    connection.row_factory = sqlite3.Row
    obj["cursor"] = connection.cursor()


def printer_init(obj: dict) -> None:
    """Initialize the printer given the click args passed."""
    obj["printer"] = ElCairoEventsPrinter(
        name=obj["name"],
        date=obj["date"],
        image=obj["image"],
        image_url=obj["image_url"],
        synopsis=obj["synopsis"],
        extra_info=obj["extra_info"],
        url=obj["url"],
        separator=obj["separator"],
        image_renderer=obj["image_renderer"],
    )


def next_sunday() -> arrow.Arrow:
    """Arrow object of next sunday."""
    date: arrow.Arrow = arrow.now()
    while date.weekday() != 6:
        date = date.shift(days=1)
    return date.floor("day")


def next_saturday() -> arrow.Arrow:
    """Arrow object of the next saturday."""
    date: arrow.Arrow = arrow.now()
    while date.weekday() != 5:
        date = date.shift(days=1)
    return date.floor("day")


def day_start(date: arrow.Arrow) -> int:
    """Integer representation of the start of the day of date."""
    return int(date.floor("day").format("YYYYMMDDHHmm"))


def day_end(date: arrow.Arrow) -> int:
    """Integer representation of the end of the day of date."""
    return int(date.ceil("day").format("YYYYMMDDHHmm"))
