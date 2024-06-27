"""Print movies"""

import arrow
import click
from arrow import Arrow
from colorama import Back, Fore, Style

DEFAULT = "[Nothing to show...]"


def truncate(string: str, start_len: int = 0):
    """
    Truncate a string to only be 80 characters long.
    start_len represents the lenght of a title for the string.
    """
    first_line_len: int = 80 - start_len

    if len(string) <= first_line_len:
        return string.replace("\n", " ").strip()

    out: str = ""
    lines: list[str] = [string[0:first_line_len]]
    lines.extend([string[i : i + 80] for i in range(first_line_len, len(string), 80)])
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
                click.echo(f"{Back.WHITE}{Fore.BLACK}{80*'-'}{Style.RESET_ALL}\n")

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

        click.echo(f"{Style.BRIGHT}{Style.BRIGHT}{name}{Style.RESET_ALL}   {date}")

    @staticmethod
    def echo_image(movie: dict) -> None:
        """Echo an image."""

        image: str = movie["image"] or DEFAULT
        click.echo(f"\n{image}")

    @staticmethod
    def echo_image_url(movie: dict) -> None:
        """Echo an image."""

        image_url: str = movie["image_url"] or DEFAULT
        click.echo(f"\n{image_url}")

    @staticmethod
    def echo_extra_info(movie: dict) -> None:
        """Echo extra info."""

        def echo_extra_info_data(
            data: str,
            title: str,
            color: str = Fore.YELLOW,
        ) -> None:
            """Echo data in the extra info."""

            if not data:
                data = DEFAULT

            click.echo(f"{color}{title}{Style.RESET_ALL}{truncate(data, len(title))}")

        synopsis = movie["synopsis"] or DEFAULT

        click.echo(f"\n{Style.DIM}{truncate(synopsis)}{Style.RESET_ALL}\n")

        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}")

        echo_extra_info_data(movie["direction"], "Dirección: ")
        echo_extra_info_data(movie["cast"], "Elenco: ")
        echo_extra_info_data(movie["genre"], "Género: ")
        echo_extra_info_data(movie["duration"], "Duración: ")
        echo_extra_info_data(movie["origin"], "Origen: ")
        echo_extra_info_data(movie["year"], "Año: ")
        echo_extra_info_data(movie["age"], "Calificación: ")

        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}\n")

        echo_extra_info_data(movie["cost"], "Valor: ", Fore.GREEN)

    @staticmethod
    def echo_urls(movie: dict) -> None:
        """Add new lines to the urls list."""

        click.echo(f"\n{Fore.YELLOW}Más info:{Style.RESET_ALL}")
        if not movie["urls"]:
            click.echo(DEFAULT)

        click.echo(movie["urls"].replace(" ", "\n"))
