"""Database command group."""

import shutil
import sqlite3
from pathlib import Path

import arrow
import click
import ics
import requests

from elcairo.api.elcairo import ElCairo, ElCairoEvent


def download_image(url: str, uid: str, script_dir: Path) -> str:
    """Download an image and returns the path to the file."""
    file_path: Path | None = None

    try:
        response: requests.Response = requests.get(url, stream=True, timeout=3)
        response.raise_for_status()
        file_path = script_dir / "images" / f"{uid}.jpeg"
        with Path(file_path).open("wb") as image_file:
            shutil.copyfileobj(response.raw, image_file)
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.RequestException,
        OSError,
    ):
        pass

    return str(file_path) if file_path is not None else ""


@click.group()
@click.option(
    "-s", "--silent/--no-silent", help="Don't print anything.", show_default=True
)
@click.option(
    "-f",
    "--force/--no-force",
    help="Force operations. Don't prompt in clean command.",
    show_default=True,
)
@click.pass_context
def database(ctx: click.Context, silent: bool, force: bool) -> None:
    """Database operations."""
    ctx.obj["silent"] = silent
    ctx.obj["force"] = force


@database.command()
@click.option(
    "-i",
    "--ics-file",
    help="Read from a .ics instead of calling the API."
    " (Just for testing .ics files. This will not populate the DB.)",
    type=click.Path(exists=True),
    required=False,
)
@click.pass_context
def populate(ctx: click.Context, ics_file: click.Path) -> None:
    """Populate the database."""
    silent: bool = ctx.obj["silent"]

    if ics_file:
        if not silent:
            click.echo(f"Reading .ics file {ics_file}...")
        with Path(str(ics_file)).open() as file:
            calendar_text: str = file.read()
            ics.Calendar(calendar_text)
        raise click.exceptions.Exit(0)

    script_dir: Path = Path(__file__).parent.resolve()
    lock_file: Path = script_dir / "db_lock_file"
    if lock_file.exists():
        if not silent:
            click.echo("The database is being populated!")
        raise click.exceptions.Exit(1)

    # Lock database operations
    lock_file.touch()

    image_dir: Path = script_dir / "images"
    image_dir.mkdir(exist_ok=True)

    database_file: Path = script_dir / "elcairo.db"
    database_file.unlink(missing_ok=True)

    connection = sqlite3.connect(database_file)

    cursor = connection.cursor()

    create_query = """
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        compare_date INT NOT NULL,
        synopsis TEXT NOT NULL,
        direction TEXT NOT NULL,
        cast TEXT NOT NULL,
        genre TEXT NOT NULL,
        duration TEXT NOT NULL,
        origin TEXT NOT NULL,
        year TEXT NOT NULL,
        age TEXT NOT NULL,
        cost TEXT NOT NULL,
        image_path TEXT NOT NULL,
        image_url TEXT NOT NULL,
        url TEXT NOT NULL
    );"""

    if not silent:
        click.echo(f"Using database {database_file}")
        click.echo("Creating the table...")

    cursor.execute(create_query)

    elcairo: ElCairo = ElCairo()

    if not silent:
        click.echo("Fetching data...")

    events_dict: dict[str, ElCairoEvent] = elcairo.get_upcoming_events_json()

    if not silent:
        click.echo(f"Fetched {events_dict.__len__()} events...")
        click.echo("Creating events...")

    data_insert: list = []
    for event_uid, elcairo_event in events_dict.items():
        event = (
            elcairo_event.name,
            str(arrow.get(elcairo_event.date)),
            int(arrow.get(elcairo_event.date).format("YYYYMMDDHHmm")),
            elcairo_event.synopsis,
            elcairo_event.extra_info.direction,
            elcairo_event.extra_info.cast,
            elcairo_event.extra_info.genre,
            elcairo_event.extra_info.duration,
            elcairo_event.extra_info.origin,
            elcairo_event.extra_info.year,
            elcairo_event.extra_info.age,
            elcairo_event.cost,
            download_image(elcairo_event.image_url, event_uid, script_dir),
            elcairo_event.image_url,
            elcairo_event.url,
        )
        data_insert.append(event)

    if not silent:
        click.echo("Populating the table...")

    cursor.executemany(
        """
        INSERT INTO events (
            'name',
            'date',
            'compare_date',
            'synopsis',
            'direction',
            'cast',
            'genre',
            'duration',
            'origin',
            'year',
            'age',
            'cost',
            'image_path',
            'image_url',
            'url'
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        data_insert,
    )

    connection.commit()

    # Unlock database operations
    lock_file.unlink()


@database.command()
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Clean the database."""
    silent: bool = ctx.obj["silent"]
    force: bool = ctx.obj["force"]

    if not silent:
        click.echo("Cleaning database...")

    script_dir: Path = Path(__file__).parent.resolve()
    lock_file: Path = script_dir / "db_lock_file"
    if lock_file.exists() and not force:
        click.confirm(
            "It seems that the database is being populated. Continue?", abort=True
        )

    database_file: Path = script_dir / "elcairo.db"

    lock_file.unlink(missing_ok=True)
    database_file.unlink(missing_ok=True)

    if not silent:
        click.echo("Database cleaned!")
