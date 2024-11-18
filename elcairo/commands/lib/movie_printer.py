"""Print movies"""

import os
import subprocess

import arrow
import click
from arrow import Arrow

DEFAULT = "[Nothing to show..]"
WIDTH = 120


def truncate(string: str, start_len: int = 0):
    """
    Truncate a string to only be WIDTH characters long.
    start_len represents the length of a title for the string.
    """
    first_line_len: int = WIDTH - start_len

    if string.__len__() <= first_line_len:
        return string.replace("\n", " ").strip()
    out: str = ""
    lines: list[str] = [string[0:first_line_len]]
    lines.extend(
        [string[i : i + WIDTH] for i in range(first_line_len, string.__len__(), WIDTH)]
    )
    for line in lines:
        out += f"{line}\n"

    return out.strip()


class MoviePrinter:
    """Movie printing utilities for echoing with click."""

    def __init__(
        self,
        name: bool,
        date: bool,
        images: bool,
        image_url: bool,
        synopsis: bool,
        extra_info: bool,
        url: bool,
        separator: bool,
    ):
        self.name = name
        self.date = date
        self.images = images
        self.image_url = image_url
        self.synopsis = synopsis
        self.extra_info = extra_info
        self.url = url
        self.separator = separator

    def echo_list(self, movies: list[dict] | None = None) -> None:
        """Print a list of movies."""

        if not movies:
            return

        for movie in movies:
            if self.separator:
                click.echo(f"{WIDTH * '*'}")

            if (
                self.name
                or self.date
                or self.images
                or self.image_url
                or self.synopsis
                or self.extra_info
                or self.url
                or self.separator
            ):
                click.echo()

            if self.name or self.date:
                self.echo_title(movie, self.name, self.date)

            if self.images:
                if self.name or self.date:
                    click.echo()
                self.echo_image(movie)

            if self.image_url:
                if self.name or self.date or self.images:
                    click.echo()
                self.echo_image_url(movie)

            if self.synopsis:
                if self.name or self.date or self.images or self.image_url:
                    click.echo()
                self.echo_synopsis(movie)

            if self.extra_info:
                self.echo_extra_info(movie)

            if self.url:
                if not self.extra_info and (
                    self.name or self.date or self.images or self.image_url
                ):
                    click.echo()
                self.echo_url(movie)

            if (
                self.images
                or self.image_url
                or self.synopsis
                or self.extra_info
                or self.url
                or self.separator
            ):
                click.echo()

        if self.separator:
            click.echo(f"{WIDTH * '*'}")

        if not (
            self.images
            or self.image_url
            or self.synopsis
            or self.extra_info
            or self.url
            or self.separator
        ):
            click.echo()

    @staticmethod
    def echo_title(movie: dict, name: bool = True, date: bool = True) -> None:
        """Echo the movie title with the date of the show."""

        if not name and not date:
            return

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

        name_styled: str = ""
        date_styled: str = ""
        title_len: int = 0

        if name:
            name_str: str = movie["name"] or DEFAULT
            title_len += name_str.__len__()
            name_styled: str = click.style(
                name_str, fg="green", bold=True, underline=True
            )

        if date:
            date_str: str = get_nice_date(movie["date"])
            title_len += date_str.__len__()
            date_styled: str = click.style(
                date_str, fg="blue", bold=True, underline=True
            )

        title_len += 4

        space_for_center = f"{' ' * (int((WIDTH - title_len) / 2))}"

        click.echo(f"{space_for_center}{name_styled}    {date_styled}")

    @staticmethod
    def echo_synopsis(movie: dict) -> None:
        synopsis = movie["synopsis"] or DEFAULT
        click.secho(truncate(synopsis), italic=True)

    @staticmethod
    def echo_extra_info(movie: dict) -> None:
        """Echo extra info."""

        def echo_extra_info_data(
            name: str,
            data: str,
        ) -> None:
            """Echo data in the extra info."""

            if not data:
                data = DEFAULT

            click.echo(
                f"{click.style(name, fg="yellow")}{truncate(data, name.__len__())}"
            )

        click.echo(f"{WIDTH * '-'}")

        echo_extra_info_data("Dirección: ", movie["direction"])
        echo_extra_info_data("Elenco: ", movie["cast"])
        echo_extra_info_data("Género: ", movie["genre"])
        echo_extra_info_data("Duración: ", movie["duration"])
        echo_extra_info_data("Origen: ", movie["origin"])
        echo_extra_info_data("Año: ", movie["year"])
        echo_extra_info_data("Calificación: ", movie["age"])
        echo_extra_info_data("Valor: ", movie["cost"])

        click.echo(f"{WIDTH * '-'}")

    @staticmethod
    def echo_image(movie: dict) -> None:
        """Echo an image. Only works for wezterm terminal emulator."""

        image: str = movie["image"] or DEFAULT
        if os.getenv("TERM_PROGRAM") == "WezTerm":
            subprocess.run(["wezterm", "imgcat", "--width", str(WIDTH), f"{image}"])
        else:
            click.echo("Images are only supported inside wezterm terminal emulator.")

    @staticmethod
    def echo_image_url(movie: dict) -> None:
        """Echo the image url."""

        if not movie["image_url"]:
            click.echo(f"{DEFAULT}")
            return

        image_url: str = f"({movie['image_url']})"
        space_for_center: str = f"{' ' * (int((WIDTH - image_url.__len__()) / 2))}"
        click.echo(f"{space_for_center}{image_url}")

    @staticmethod
    def echo_url(movie: dict) -> None:
        """Echo url."""

        url: str = movie["url"] or DEFAULT
        click.echo(
            f"{click.style("URL:", fg="yellow")} {click.style(url, italic=True)}"
        )
