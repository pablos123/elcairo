"""Shows command group."""

import datetime
import sys
from pathlib import Path

import arrow
import click

import elcairo.commands.lib.shows_functions as shows_functions
from elcairo.api.elcairo import ElCairoEvent


@click.group()
@click.option(
    "-t", "--name/--no-name", help="Print name.", default=True, show_default=True
)
@click.option(
    "-d", "--date/--no-date", help="Print date.", default=True, show_default=True
)
@click.option("-i", "--image/--no-image", help="Print image.", show_default=True)
@click.option(
    "-l",
    "--image-url/--no-image-url",
    help="Print image's url.",
    show_default=True,
)
@click.option(
    "-s",
    "--synopsis/--no-synopsis",
    help="Print synopsis.",
    default=True,
    show_default=True,
)
@click.option(
    "-e",
    "--extra-info/--no-extra-info",
    help="Print extra info.",
    default=True,
    show_default=True,
)
@click.option("-u", "--url/--no-url", help="Show url.", show_default=True)
@click.option(
    "-p",
    "--separator/--no-separator",
    help="Print separator.",
    show_default=True,
)
@click.option(
    "-r",
    "--reverse/--no-reverse",
    help="Print in reverse order.",
    show_default=True,
)
@click.option(
    "-R",
    "--image-renderer",
    type=click.Choice(
        ["kitty", "wezterm", "iterm2", "chafa", "timg", "viu", "catimg", "img2txt", "pixterm", "jp2a", "builtin"],
        case_sensitive=False,
    ),
    default=None,
    help="Force a specific image renderer. [default: auto]",
)
@click.pass_obj
def shows(
    obj: dict,
    name: bool,
    date: bool,
    image: bool,
    image_url: bool,
    synopsis: bool,
    extra_info: bool,
    url: bool,
    separator: bool,
    reverse: bool,
    image_renderer: str | None,
):
    """Events printer."""

    script_dir: Path = Path(__file__).parent.resolve()
    lock_file: Path = script_dir / "db_lock_file"
    if lock_file.exists():
        click.echo("The database is being populated!")
        raise click.exceptions.Exit(1)

    obj["name"] = name
    obj["date"] = date
    obj["image"] = image
    obj["image_url"] = image_url
    obj["synopsis"] = synopsis
    obj["extra_info"] = extra_info
    obj["url"] = url
    obj["separator"] = separator
    obj["order"] = "DESC"
    if reverse:
        obj["order"] = "ASC"
    obj["image_renderer"] = image_renderer
    shows_functions.cursor_init(obj)
    shows_functions.printer_init(obj)


@shows.command()
@click.pass_obj
def today(obj: dict) -> None:
    """Today's events."""
    now: arrow.Arrow = arrow.now()
    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(now),
        date_int_max=shows_functions.day_end(now),
        order=obj["order"],
    )
    obj["printer"].echo_list(events)


@shows.command()
@click.pass_obj
def tomorrow(obj: dict) -> None:
    """Tomorrow's events."""
    tomorrow: arrow.Arrow = arrow.now().shift(days=1)
    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(tomorrow),
        date_int_max=shows_functions.day_end(tomorrow),
        order=obj["order"],
    )
    obj["printer"].echo_list(events)


@shows.command()
@click.pass_obj
def week(obj: dict) -> None:
    """Events until next sunday."""
    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(arrow.now()),
        date_int_max=shows_functions.day_end(shows_functions.next_sunday()),
        order=obj["order"],
    )
    obj["printer"].echo_list(events)


@shows.command()
@click.pass_obj
def weekend(obj: dict) -> None:
    """This weekend's events."""

    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(shows_functions.next_saturday()),
        date_int_max=shows_functions.day_end(shows_functions.next_sunday()),
        order=obj["order"],
    )
    obj["printer"].echo_list(events)


@shows.command()
@click.option(
    "-d",
    "--date",
    help="Print events on this date.",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    required=True,
)
@click.pass_obj
def day(obj: dict, date: datetime.datetime) -> None:
    """Events of a given date."""
    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)
    date_arrow: arrow.Arrow = arrow.get(f"{year}-{month}-{day_date}")
    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(date_arrow),
        date_int_max=shows_functions.day_end(date_arrow),
        order=obj["order"],
    )
    obj["printer"].echo_list(events)


@shows.command()
@click.option(
    "-d",
    "--date",
    help="Print events until this date.",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    required=True,
)
@click.pass_obj
def until(obj: dict, date: datetime.datetime) -> None:
    """Events until a given date."""

    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)
    date_arrow: arrow.Arrow = arrow.get(f"{year}-{month}-{day_date}")
    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(arrow.now()),
        date_int_max=shows_functions.day_end(date_arrow),
        order=obj["order"],
    )
    obj["printer"].echo_list(events)


@shows.command()
@click.pass_obj
def upcoming(obj: dict) -> None:
    """Upcoming events."""
    events: list[ElCairoEvent] = shows_functions.query(
        cursor=obj["cursor"],
        date_int_min=shows_functions.day_start(arrow.now()),
        date_int_max=sys.maxsize,
        order=obj["order"],
    )
    obj["printer"].echo_list(events)
