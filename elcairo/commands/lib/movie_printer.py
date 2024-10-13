"""Print movies"""

import os
import subprocess

import arrow
import click

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from arrow import Arrow


class EscapeSecs:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"


DEFAULT = "[Nothing to show...]"
WIDTH = 120


def truncate(string: str, start_len: int = 0):
    """
    Truncate a string to only be WIDTH characters long.
    start_len represents the length of a title for the string.
    """
    first_line_len: int = WIDTH - start_len

    if len(string) <= first_line_len:
        return string.replace("\n", " ").strip()

    out: str = ""
    lines: list[str] = [string[0:first_line_len]]
    lines.extend(
        [string[i : i + WIDTH] for i in range(first_line_len, len(string), WIDTH)]
    )
    for line in lines:
        out += f"{line}\n"

    return out.strip()


class MoviePrinter:
    """Movie printing utilities for echoing with click."""

    def __init__(
        self,
        images: bool,
        extra_info: bool,
        separator: bool,
        urls: bool,
        image_urls: bool,
    ):
        self.images = images
        self.extra_info = extra_info
        self.separator = separator
        self.urls = urls
        self.image_urls = image_urls

    def echo_list(self, movies: list[dict]) -> None:
        """Print a list of movies."""

        if movies == []:
            return

        for movie in movies:
            click.echo()

            if self.separator:
                click.echo(f"{WIDTH * '*'}\n")

            self.echo_title(movie)

            if self.images:
                self.echo_image(movie)

            if self.image_urls:
                self.echo_image_url(movie)

            if self.extra_info:
                self.echo_extra_info(movie)

            if self.urls:
                self.echo_urls(movie)

            click.echo()

    @staticmethod
    def echo_title(movie: dict) -> None:
        """Echo the movie title with the date of the show."""

        def get_nice_date(event_date: str) -> str:
            """Format the date information a return a nice show's date"""

            if not event_date:
                return DEFAULT

            arrow_date: Arrow = arrow.get(event_date)
            format_date: str = arrow_date.format(
                "dddd DD-MM-YYYY HH:mm:ss", locale="es"
            ).capitalize()
            human_date: str = arrow_date.humanize(locale="es")

            return f"{format_date} ({human_date})"

        name: str = movie["name"] or DEFAULT

        date: str = get_nice_date(movie["date"])

        title_len: int = len(f"{name}    {date}")

        click.echo(
            f"{EscapeSecs.BOLD}{' ' * (int((WIDTH - title_len) / 2))}{EscapeSecs.UNDERLINE}{EscapeSecs.GREEN}{name}{EscapeSecs.RESET}    {EscapeSecs.BOLD}{EscapeSecs.UNDERLINE}{EscapeSecs.BLUE}{date}{EscapeSecs.RESET}"
        )

    @staticmethod
    def echo_image(movie: dict) -> None:
        """Echo an image only works for wezterm terminal emulator."""

        image: str = movie["image"] or DEFAULT
        if os.getenv("TERM_PROGRAM") == "WezTerm":
            subprocess.run(["wezterm", "imgcat", "--width", str(WIDTH), f"{image}"])
        else:
            click.echo("Images are only supported inside wezterm terminal emulator.")

    @staticmethod
    def echo_image_url(movie: dict) -> None:
        """Echo the image url."""

        image_url: str = movie["image_url"] or DEFAULT
        click.echo(f"\n{image_url}")

    @staticmethod
    def echo_extra_info(movie: dict) -> None:
        """Echo extra info."""

        def echo_extra_info_data(
            data: str,
            title: str,
            color: str = EscapeSecs.YELLOW,
        ) -> None:
            """Echo data in the extra info."""

            if not data:
                data = DEFAULT

            click.echo(f"{color}{title}{EscapeSecs.RESET}{truncate(data, len(title))}")

        synopsis = movie["synopsis"] or DEFAULT

        click.echo(f"\n{EscapeSecs.ITALIC}{truncate(synopsis)}{EscapeSecs.RESET}\n")

        click.echo(f"{WIDTH * '-'}")

        echo_extra_info_data(movie["direction"], "Dirección: ")
        echo_extra_info_data(movie["cast"], "Elenco: ")
        echo_extra_info_data(movie["genre"], "Género: ")
        echo_extra_info_data(movie["duration"], "Duración: ")
        echo_extra_info_data(movie["origin"], "Origen: ")
        echo_extra_info_data(movie["year"], "Año: ")
        echo_extra_info_data(movie["age"], "Calificación: ")
        echo_extra_info_data(movie["cost"], "Valor: ")

        click.echo(f"{WIDTH * '-'}")

    @staticmethod
    def echo_urls(movie: dict) -> None:
        """Add new lines to the urls list."""

        click.echo(f"\n{EscapeSecs.YELLOW}URLS:{EscapeSecs.RESET}")
        if not movie["urls"]:
            click.echo(DEFAULT)

        click.echo(movie["urls"].replace(" ", "\n"))
