"""Shows command group."""

import datetime
import sys

import arrow
import click

import elcairo.commands.lib.shows_functions as shows_functions


@click.group()
@click.option("-i", "--images/--no-images", help="Show images.", show_default=True)
@click.option(
    "-e",
    "--extra-info/--no-extra-info",
    help="Show extra info.",
    default=True,
    show_default=True,
)
@click.option(
    "-s",
    "--separator/--no-separator",
    help="Show the separator between movies.",
    show_default=True,
)
@click.option("-u", "--urls/--no-urls", help="Show urls.", show_default=True)
@click.option(
    "-l",
    "--image-urls/--no-image-urls",
    help="Show images' urls.",
    show_default=True,
)
@click.option(
    "-r",
    "--reverse/--no-reverse",
    help="Reverse order.",
    show_default=True,
)
@click.pass_context
def shows(
    ctx: click.Context,
    images: bool,
    extra_info: bool,
    separator: bool,
    urls: bool,
    image_urls: bool,
    reverse: bool,
):
    """Movie shows printer."""

    ctx.obj["images"] = images
    ctx.obj["extra_info"] = extra_info
    ctx.obj["separator"] = separator
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
        date_int_min=shows_functions.day_start(shows_functions.next_saturday()),
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
