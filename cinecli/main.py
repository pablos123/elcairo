"""Print El Cairo cinema shows information."""

import click

from cinecli.commands.database import database
from cinecli.commands.shows import (
    day,
    today,
    tomorrow,
    until,
    upcoming,
    week,
    weekend,
)
from cinecli.commands.version import version


@click.group()
@click.option("--images", help="Show images.", is_flag=True, show_default=True)
@click.option(
    "--no_extra_info", help="Don't show extra info.", is_flag=True, show_default=True
)
@click.option(
    "--no_separator",
    help="Don't show the separator between movies.",
    is_flag=True,
    show_default=True,
)
@click.option("--urls", help="Show urls.", is_flag=True, show_default=True)
@click.option(
    "--image_urls", help="Show images' urls.", is_flag=True, show_default=True
)
@click.option("--reverse", help="Reverse order.", is_flag=True, show_default=True)
@click.pass_context
def cinecli(
    ctx: click.Context,
    images: bool,
    no_extra_info: bool,
    no_separator: bool,
    urls: bool,
    image_urls: bool,
    reverse: bool,
):
    """Command line interface for El Cairo cinema."""

    ctx.obj["images"] = images
    ctx.obj["no_extra_info"] = no_extra_info
    ctx.obj["no_separator"] = no_separator
    ctx.obj["urls"] = urls
    ctx.obj["image_urls"] = image_urls
    ctx.obj["order"] = "DESC"
    if reverse:
        ctx.obj["order"] = "ASC"


cinecli.add_command(database)
cinecli.add_command(day)
cinecli.add_command(today)
cinecli.add_command(tomorrow)
cinecli.add_command(until)
cinecli.add_command(upcoming)
cinecli.add_command(week)
cinecli.add_command(weekend)
cinecli.add_command(version)


def main():
    """Execute cinecli."""

    cinecli(obj={})
