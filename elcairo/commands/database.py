"""Database command group."""

import shutil
from pathlib import Path

import arrow
import click
import requests
from halo import Halo

from elcairo.api.elcairo import ElCairo, ElCairoEvent
from elcairo.models import EventModel, db


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
@click.pass_obj
def database(obj: dict, silent: bool) -> None:
    """Database operations."""
    obj["silent"] = silent


@database.command()
@click.pass_obj
def populate(obj: dict) -> None:
    """Populate the database."""
    silent: bool = obj["silent"]

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

    image_dir: Path = script_dir / "images"
    image_dir.mkdir(exist_ok=True)

    database_file: Path = script_dir / "elcairo.db"

    if not silent:
        spinner.succeed()
        spinner.start(f"Connecting to the new database ({database_file})")

    db.init(database_file)
    db.connect()

    if not silent:
        spinner.succeed()
        spinner.start("Creating table")

    db.create_tables([EventModel], safe=True)

    if not silent:
        spinner.succeed()
        spinner.start("Fetching data")

    elcairo: ElCairo = ElCairo()
    events_dict: dict[str, ElCairoEvent] = elcairo.get_upcoming_events_json()

    if not silent:
        spinner.succeed(f"Fetching data - Fetched: {len(events_dict)} events")
        spinner.start("Creating events")

    data_insert: list[dict] = []
    for event_uid, elcairo_event in events_dict.items():
        data_insert.append({
            "uid": event_uid,
            "name": elcairo_event.name,
            "date": str(arrow.get(elcairo_event.date)),
            "compare_date": int(arrow.get(elcairo_event.date).format("YYYYMMDDHHmm")),
            "synopsis": elcairo_event.synopsis,
            "direction": elcairo_event.extra_info.direction,
            "cast": elcairo_event.extra_info.cast,
            "genre": elcairo_event.extra_info.genre,
            "duration": elcairo_event.extra_info.duration,
            "origin": elcairo_event.extra_info.origin,
            "year": elcairo_event.extra_info.year,
            "age": elcairo_event.extra_info.age,
            "cost": elcairo_event.cost,
            "image_path": download_image(elcairo_event.image_url, event_uid, script_dir),
            "image_url": elcairo_event.image_url,
            "url": elcairo_event.url,
        })

    if not silent:
        spinner.succeed()
        spinner.start("Populating the table")

    EventModel.insert_many(data_insert).on_conflict('replace').execute()
    db.close()

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
@click.pass_obj
def clean(obj: dict, force: bool) -> None:
    """Clean the database."""
    silent: bool = obj["silent"]

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
