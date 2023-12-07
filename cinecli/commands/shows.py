"""Shows command group."""

import datetime
import sys

import arrow
import click

import cinecli.commands.lib.shows_functions as shows_functions


@click.group()
@click.option("-i", "--images", help="Show images.", is_flag=True, show_default=True)
@click.option(
    "-e",
    "--no-extra-info",
    help="Don't show extra info.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "-s",
    "--no-separator",
    help="Don't show the separator between movies.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "-u", "--urls/--no-urls", help="Show urls.", is_flag=True, show_default=True
)
@click.option(
    "-l", "--image-urls", help="Show images' urls.", is_flag=True, show_default=True
)
@click.option("-r", "--reverse", help="Reverse order.", is_flag=True, show_default=True)
@click.pass_context
def shows(
    ctx: click.Context,
    images: bool,
    no_extra_info: bool,
    no_separator: bool,
    urls: bool,
    image_urls: bool,
    reverse: bool,
):
    """Movie shows printer."""

    ctx.obj["images"] = images
    ctx.obj["no_extra_info"] = no_extra_info
    ctx.obj["no_separator"] = no_separator
    ctx.obj["urls"] = urls
    ctx.obj["image_urls"] = image_urls
    ctx.obj["order"] = "DESC"
    if reverse:
        ctx.obj["order"] = "ASC"
    shows_functions.cursor_init(ctx)
    shows_functions.printer_init(ctx)


@shows.command()
@click.pass_context
def today(ctx: click.Context) -> None:
    """Today's movie shows."""

    now: arrow.Arrow = arrow.now()
    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(now),
        date_int_max=shows_functions.day_end(now),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@shows.command()
@click.pass_context
def tomorrow(ctx: click.Context) -> None:
    """Tomorrow's movie shows."""

    tomorrow: arrow.Arrow = arrow.now().dehumanize("in a day")
    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(tomorrow),
        date_int_max=shows_functions.day_end(tomorrow),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@shows.command()
@click.pass_context
def week(ctx: click.Context) -> None:
    """Movie shows until next sunday."""

    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(arrow.now()),
        date_int_max=shows_functions.day_end(shows_functions.next_sunday()),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@shows.command()
@click.pass_context
def weekend(ctx: click.Context) -> None:
    """This weekend's movie shows."""

    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(
            shows_functions.next_saturday()),
        date_int_max=shows_functions.day_end(shows_functions.next_sunday()),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@shows.command()
@click.option(
    "-d",
    "--date",
    help="Print movie shows on this date.",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    required=True,
)
@click.pass_context
def day(ctx: click.Context, date: datetime.datetime) -> None:
    """Movie shows of a given date."""

    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)
    date_arrow: arrow.Arrow = arrow.get(f"{year}-{month}-{day_date}")
    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(date_arrow),
        date_int_max=shows_functions.day_end(date_arrow),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@shows.command()
@click.option(
    "-d",
    "--date",
    help="Print movie shows until this date.",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    required=True,
)
@click.pass_context
def until(ctx: click.Context, date: datetime.datetime) -> None:
    """Movie shows until a given date."""

    year: str = str(date.year).zfill(4)
    month: str = str(date.month).zfill(2)
    day_date: str = str(date.day).zfill(2)
    date_arrow: arrow.Arrow = arrow.get(f"{year}-{month}-{day_date}")
    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(arrow.now()),
        date_int_max=shows_functions.day_end(date_arrow),
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)


@shows.command()
@click.pass_context
def upcoming(ctx: click.Context) -> None:
    """Upcoming movie shows."""

    movies: list[dict] = shows_functions.query(
        cursor=ctx.obj["cursor"],
        date_int_min=shows_functions.day_start(arrow.now()),
        date_int_max=sys.maxsize,
        order=ctx.obj["order"],
    )
    ctx.obj["printer"].echo_list(movies)
