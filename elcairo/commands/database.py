"""Database command group."""

import sqlite3
from pathlib import Path

import arrow
import click
import ics

import elcairo.commands.lib.database_functions as database_functions
from elcairo.api.elcairo import ElCairo, ElCairoEvent


@click.group()
@click.option(
    "-s", "--silent/--no-silent", help="Don't print anything.", show_default=True
)
@click.option(
    "-f",
    "--force/--no-force",
    help="Force operations. Don't show prompts in clean command.",
    show_default=True,
)
@click.pass_context
def database(ctx: click.Context, silent: bool, force: bool) -> None:
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

    if not silent:
        click.echo("Populating the database...")

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
    CREATE TABLE IF NOT EXISTS movies (
        movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        image TEXT NOT NULL,
        image_url TEXT NOT NULL,
        urls TEXT NOT NULL
    );"""

    if not silent:
        click.echo(f"Using database {database_file}")
        click.echo("Creating the table...")

    cursor.execute(create_query)

    if not silent:
        click.echo("Fetching data...")

    elcairo: ElCairo = ElCairo()
    events_dict: dict[str, ElCairoEvent] = elcairo.get_upcoming_shows_json()

    if not silent:
        click.echo("Fetching data...")
        click.echo(f"Fetched {len(events_dict)} movies...")

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
            database_functions.download_image(
                elcairo_event.image_url, event_uid, script_dir
            ),
            elcairo_event.image_url,
            " ".join(elcairo_event.urls),
        )
        data_insert.append(event)

    if not silent:
        click.echo("Creating events...")

    cursor.executemany(
        """
        INSERT INTO movies (
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
            'image',
            'image_url',
            'urls'
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        data_insert,
    )

    if not silent:
        click.echo("Populating the table...")

    connection.commit()

    # Unlock database operations
    lock_file.unlink()


@database.command()
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Clean the database."""
    silent = ctx.obj["silent"]

    if not silent:
        click.echo("Cleaning database...")

    script_dir: Path = Path(__file__).parent.resolve()
    lock_file: Path = script_dir / "db_lock_file"
    if lock_file.exists():
        click.confirm(
            "It seems that the database is being populated. Continue?", abort=True
        )

    database_file: Path = script_dir / "elcairo.db"

    database_file.unlink(missing_ok=True)
    lock_file.unlink(missing_ok=True)

    if not silent:
        click.echo("Database cleaned!")
