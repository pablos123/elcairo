"""
Print El Cairo cinema shows information
"""

import click

from .commands.database import database
from .commands.elcairo import day, today, tomorrow, until, upcoming, week, weekend


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
@click.option("--reverse", help="Reverse order.", is_flag=True, show_default=True)
@click.pass_context
def cinecli(ctx, images, no_extra_info, no_separator, urls, reverse):
    """
    Command line interface for El Cairo cinema.
    """
    ctx.obj["images"] = images
    ctx.obj["no_extra_info"] = no_extra_info
    ctx.obj["no_separator"] = no_separator
    ctx.obj["reverse"] = reverse
    ctx.obj["urls"] = urls


cinecli.add_command(database)
cinecli.add_command(day)
cinecli.add_command(today)
cinecli.add_command(tomorrow)
cinecli.add_command(until)
cinecli.add_command(upcoming)
cinecli.add_command(week)
cinecli.add_command(weekend)


def main():
    """
    Execute cinecli
    """
    cinecli(obj={})
