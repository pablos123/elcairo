"""Database command group."""

import shutil
import sqlite3
from pathlib import Path

import arrow
import click
import ics
import requests
from halo import Halo

from elcairo.api.elcairo import ElCairo, ElCairoEvent


def download_image(url: str, uid: str, script_dir: Path) -> str:
    """Download an image and returns the path to the file."""
    file_path: Path = script_dir / "images" / f"{uid}.jpeg"
    if file_path.exists():
        return str(file_path)

    try:
        response: requests.Response = requests.get(url, stream=True, timeout=3)
        response.raise_for_status()
        with Path(file_path).open("wb") as image_file:
            shutil.copyfileobj(response.raw, image_file)
    except (requests.exceptions.RequestException, OSError):
        return ""

    return str(file_path)


@click.group()
@click.option(
    "-s", "--silent/--no-silent", help="Don't print anything.", show_default=True
)
@click.pass_context
def database(ctx: click.Context, silent: bool) -> None:
    """Database operations."""
    ctx.obj["silent"] = silent


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
        with Path(ics_file).open() as file:
            calendar_text: str = file.read()
            ics.Calendar(calendar_text)
        raise click.exceptions.Exit(0)

    script_dir: Path = Path(__file__).parent.resolve()
    lock_file: Path = script_dir / "db_lock_file"
    if lock_file.exists():
        if not silent:
            click.echo("The database is being populated!")
        raise click.exceptions.Exit(1)

    spinner: Halo = Halo()
    if not silent:
        spinner.start("Locking database operations")

    lock_file.touch()

    if not silent:
        spinner.succeed()
        spinner.start("Removing old database")

    image_dir: Path = script_dir / "images"
    image_dir.mkdir(exist_ok=True)

    database_file: Path = script_dir / "elcairo.db"
    database_file.unlink(missing_ok=True)

    if not silent:
        spinner.succeed()
        spinner.start(f"Connecting to the new database ({database_file})")

    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    if not silent:
        spinner.succeed()
        spinner.start("Creating table")

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
    cursor.execute(create_query)

    if not silent:
        spinner.succeed()
        spinner.start("Fetching data")

    elcairo: ElCairo = ElCairo()
    events_dict: dict[str, ElCairoEvent] = elcairo.get_upcoming_events_json()

    if not silent:
        spinner.succeed(f"Fetching data - Fetched: {len(events_dict)} events")
        spinner.start("Creating events")

    data_insert: list[tuple] = []
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
        spinner.succeed()
        spinner.start("Populating the table")

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

    if not silent:
        spinner.succeed()
        spinner.start("Unlocking database operations")

    lock_file.unlink()

    if not silent:
        spinner.succeed()
        spinner.stop()
        click.echo("Done!")


@database.command()
@click.option(
    "-f",
    "--force/--no-force",
    help="Force operations. Don't prompt for confirmation.",
    show_default=True,
)
@click.pass_context
def clean(ctx: click.Context, force: bool) -> None:
    """Clean the database."""
    silent: bool = ctx.obj["silent"]

    script_dir: Path = Path(__file__).parent.resolve()
    lock_file: Path = script_dir / "db_lock_file"
    if lock_file.exists() and not force:
        click.confirm(
            "It seems that the database is being populated. Continue?", abort=True
        )

    spinner: Halo = Halo()
    if not silent:
        spinner.start("Cleaning database")

    database_file: Path = script_dir / "elcairo.db"

    lock_file.unlink(missing_ok=True)
    database_file.unlink(missing_ok=True)

    if not silent:
        spinner.succeed()
        spinner.stop()
        click.echo("Done!")
