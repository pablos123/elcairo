"""Database command group."""

import json
import os
import sqlite3
import threading
import functools
import ics

import arrow
import click

import cinecli.commands.lib.database_functions as database_functions
from cinecli.api.elcairo import ElCairo


@click.group()
@click.option(
    "-s", "--silent", help="Don't print anything.", is_flag=True, show_default=True
)
@click.pass_context
def database(ctx: click.Context, silent: bool) -> None:
    """Database operations."""

    if not silent:
        click.echo("📽️ Executing tasks 📽️")

    ctx.obj["silent"] = silent

    def bye_msg(silent: bool):
        if not silent:
            click.echo("📽️ All finished 📽️")

    bye_call = functools.partial(bye_msg, silent)
    ctx.call_on_close(bye_call)


@database.command()
@click.option(
    "-i",
    "--ics-file",
    help="Read from a .ics instead of calling the API. (Just for testing .ics files. This will not populate the DB.)",
    type=click.Path(exists=True),
    required=False,
)
@click.pass_context
def populate(ctx: click.Context, ics_file: click.Path) -> None:
    """Populate the database."""

    if ics_file:
        with open(str(ics_file), "r") as file:
            calendar_text: str = file.read()
            ics.Calendar(calendar_text)
        ctx.exit(0)

    script_dir: str = os.path.realpath(os.path.dirname(__file__))
    database_file: str = os.path.join(script_dir, "cinecli.db")
    if os.path.exists(database_file):
        try:
            os.remove(database_file)
        except OSError:
            if not ctx.obj["silent"]:
                click.echo("Cannot remove cinecli.db, try again...")
            ctx.exit(1)

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

    if not ctx.obj["silent"]:
        click.echo(f"Using database {database_file}")
        click.echo("Creating the table...")

    cursor.execute(create_query)

    def get_events(events_dict: dict):
        elcairo: ElCairo = ElCairo()
        events_dict.update(json.loads(elcairo.get_upcoming_shows_json()))

    events_dict: dict = {}
    thread_fetch: threading.Thread = threading.Thread(
        target=get_events, args=(events_dict,)
    )

    thread_fetch.start()

    if not ctx.obj["silent"]:
        # This will wait for thread to finish
        database_functions.loading("Fetching data", thread_fetch)

    # If you go silent wait for the thread, anyway close the thread safely
    thread_fetch.join()

    if not ctx.obj["silent"]:
        click.echo(f"Fetched {len(events_dict)} movies...")

    def create_events(events_dict: dict, data_insert: list):
        for uid, movie_data in events_dict.items():
            event = (
                movie_data["name"],
                str(arrow.get(movie_data["date"])),
                int(arrow.get(movie_data["date"]).format("YYYYMMDDHHmm")),
                movie_data["synopsis"],
                movie_data["direction"],
                movie_data["cast"],
                movie_data["genre"],
                movie_data["duration"],
                movie_data["origin"],
                movie_data["year"],
                movie_data["age"],
                movie_data["cost"],
                database_functions.get_ascii_image(
                    movie_data["image_url"], uid),
                movie_data["image_url"],
                " ".join(movie_data["urls"]),
            )
            data_insert.append(event)

    data_insert: list = []
    thread_events: threading.Thread = threading.Thread(
        target=create_events,
        args=(
            events_dict,
            data_insert,
        ),
    )

    thread_events.start()

    if not ctx.obj["silent"]:
        database_functions.loading("Creating events", thread_events)

    thread_events.join()

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

    if not ctx.obj["silent"]:
        click.echo("Populating the table...")

    connection.commit()


@database.command()
@click.pass_context
def clean(ctx: click.Context) -> None:
    """Clean the database."""

    if not ctx.obj["silent"]:
        click.echo("Deleting the database...")

    script_dir: str = os.path.realpath(os.path.dirname(__file__))
    database_file: str = os.path.join(script_dir, "cinecli.db")
    if not os.path.exists(database_file):
        if not ctx.obj["silent"]:
            click.echo("The database does not exists!")
        ctx.exit(1)

    try:
        os.remove(database_file)
    except OSError:
        if not ctx.obj["silent"]:
            click.echo("Cannot remove cinecli.db, try again...")
        ctx.exit(1)
