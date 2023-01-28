"""Print Rosario's cinemas shows information"""

import sys
from datetime import date, datetime

import click
from colorama import Back, Fore, Style

from elcairo import ElCairo
from movie import Movie


def show_movies(movies: list[Movie], show_image: bool) -> None:
    """
    Print a list of movies
    """
    for movie in movies:
        print(f"{Back.WHITE}{Fore.BLACK}{80*'-'}{Style.RESET_ALL}\n")
        if show_image:
            click.echo(movie.get_image())
        click.echo(movie.get_info())


@click.group()
@click.option(
    "--date",
    help="Show movies since this date.",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    default=str(date.today().strftime("%d-%m-%Y")),
    show_default=True,
)
@click.option(
    "--images", help="Show images.", type=bool, default=True, show_default=True
)
@click.pass_context
def cinecli(ctx, date, images):
    """
    Command line interface for Rosario's cinemas shows information
    """
    ctx.obj["images"] = images

    ctx.obj["day"] = date.day
    ctx.obj["month"] = date.month
    ctx.obj["year"] = date.year

@cinecli.command()
@click.pass_context
def all(ctx) -> None:
    """
    Print all cinemas movie shows.
    """
    pass

@cinecli.command()
@click.pass_context
def elcairo(ctx) -> None:
    """
    Print el cairo movie shows.
    """

    elcairo_class: ElCairo = ElCairo(
        ctx.obj["day"], ctx.obj["month"], ctx.obj["year"])

    movies: list[Movie] = elcairo_class.get_movies()

    show_movies(movies, ctx.obj["images"])


if __name__ == "__main__":
    # Each cinema will have a different way to get the information I think.
    # I cannot assume some sort of protocol, so each cinema will have a class
    # to gather the information
    cinecli(obj={})
