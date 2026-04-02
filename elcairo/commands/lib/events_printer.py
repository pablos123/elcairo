"""Print events"""

import os
import shutil
import subprocess

import arrow
import click
from arrow import Arrow
from PIL import Image

from elcairo.api.elcairo import ElCairoEvent

DEFAULT = "[Nothing to show...]"
WIDTH = 120

RENDERERS: dict[str, str] = {
    "wezterm": "wezterm imgcat --width {width}",
    "chafa": "chafa --size={width}x",
    "catimg": "catimg -w {width}",
    "jp2a": "jp2a --width={width}",
}


def detect_renderer() -> str:
    """Return the renderer to use: first env-based, then PATH."""
    term_program = os.getenv("TERM_PROGRAM", "")
    if term_program == "WezTerm":
        return "wezterm"

    for name in ("chafa", "catimg", "jp2a"):
        if shutil.which(name):
            return name

    return "builtin"


def builtin_ascii_render(image_path: str) -> None:
    """Render an image as ASCII art using Pillow. Always available as fallback."""

    # ASCII density ramp: darkest → lightest
    ramp = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception:
        click.echo(f"Could not open image: {image_path}")
        return

    # ASCII chars are roughly twice as tall as wide, so halve the row count
    char_width = WIDTH
    aspect = img.height / img.width
    char_height = max(1, int(char_width * aspect * 0.45))

    img = img.resize((char_width, char_height))
    gray = img.convert("L")

    for y in range(char_height):
        row = ""
        for x in range(char_width):
            pixel = gray.getpixel((x, y))
            row += ramp[int(pixel / 255 * (len(ramp) - 1))]
        click.echo(row)


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


class ElCairoEventsPrinter:
    """Echo ElCairoEvents."""

    def __init__(
        self,
        name: bool,
        date: bool,
        image: bool,
        image_url: bool,
        synopsis: bool,
        extra_info: bool,
        url: bool,
        separator: bool,
        image_renderer: str | None = None,
    ):
        self.name = name
        self.date = date
        self.image = image
        self.image_url = image_url
        self.synopsis = synopsis
        self.extra_info = extra_info
        self.url = url
        self.separator = separator
        self.image_renderer = image_renderer

    def echo_list(self, events: list[ElCairoEvent] | None = None) -> None:
        """Print a list of events."""

        if not events:
            return

        for event in events:
            if self.separator:
                click.echo(f"{WIDTH * '*'}")

            if (
                self.name
                or self.date
                or self.image
                or self.image_url
                or self.synopsis
                or self.extra_info
                or self.url
                or self.separator
            ):
                click.echo()

            if self.name or self.date:
                self.echo_title(event, self.name, self.date)

            if self.image:
                if self.name or self.date:
                    click.echo()
                self.echo_image(event)

            if self.image_url:
                if self.name or self.date or self.image:
                    click.echo()
                self.echo_image_url(event)

            if self.synopsis:
                if self.name or self.date or self.image or self.image_url:
                    click.echo()
                self.echo_synopsis(event)

            if self.extra_info:
                self.echo_extra_info(event)

            if self.url:
                if not self.extra_info and (
                    self.name or self.date or self.image or self.image_url
                ):
                    click.echo()
                self.echo_url(event)

            if (
                self.image
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
            self.image
            or self.image_url
            or self.synopsis
            or self.extra_info
            or self.url
            or self.separator
        ):
            click.echo()

    @staticmethod
    def echo_title(event: ElCairoEvent, name: bool = True, date: bool = True) -> None:
        """Echo the event title with the date of the show."""

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
            name_str: str = event.name or DEFAULT
            title_len += len(name_str)
            name_styled: str = click.style(
                name_str, fg="green", bold=True, underline=True
            )

        if date:
            date_str: str = get_nice_date(event.date)
            title_len += len(date_str)
            date_styled: str = click.style(
                date_str, fg="blue", bold=True, underline=True
            )

        title_len += 4

        space_for_center = f"{' ' * (int((WIDTH - title_len) / 2))}"

        click.echo(f"{space_for_center}{name_styled}    {date_styled}")

    @staticmethod
    def echo_synopsis(event: ElCairoEvent) -> None:
        synopsis = event.synopsis or DEFAULT
        click.secho(truncate(synopsis), italic=True)

    @staticmethod
    def echo_extra_info(event: ElCairoEvent) -> None:
        """Echo extra info."""

        def echo_extra_info_data(
            name: str,
            data: str,
        ) -> None:
            """Echo data in the extra info."""

            if not data:
                data = DEFAULT

            click.echo(f"{click.style(name, fg='yellow')}{truncate(data, len(name))}")

        click.echo(f"{WIDTH * '-'}")

        echo_extra_info_data("Dirección: ", event.extra_info.direction)
        echo_extra_info_data("Elenco: ", event.extra_info.cast)
        echo_extra_info_data("Género: ", event.extra_info.genre)
        echo_extra_info_data("Duración: ", event.extra_info.duration)
        echo_extra_info_data("Origen: ", event.extra_info.origin)
        echo_extra_info_data("Año: ", event.extra_info.year)
        echo_extra_info_data("Calificación: ", event.extra_info.age)
        echo_extra_info_data("Valor: ", event.cost)

        click.echo(f"{WIDTH * '-'}")

    def echo_image(self, event: ElCairoEvent) -> None:
        """Echo an image using the best available renderer."""

        if not event.image_path:
            return click.echo(f"{DEFAULT}")

        image_path: str = event.image_path
        renderer = self.image_renderer or detect_renderer()

        if renderer == "wezterm" and os.getenv("TERM_PROGRAM") != "WezTerm":
            click.echo("Image renderer 'wezterm' requires a WezTerm terminal.")
            return

        if renderer == "builtin":
            builtin_ascii_render(image_path)
            return

        width = WIDTH * 2 if renderer == "catimg" else WIDTH

        cmd_list = RENDERERS[renderer].format(width=width).split()
        cmd_list.append(image_path)
        try:
            subprocess.run(cmd_list)
        except FileNotFoundError:
            click.echo(f"Image renderer '{renderer}' not found.")

    @staticmethod
    def echo_image_url(event: ElCairoEvent) -> None:
        """Echo image url."""

        if not event.image_url:
            click.echo(f"{DEFAULT}")
            return

        image_url: str = f"({click.style(event.image_url, italic=True)})"
        space_for_center: str = f"{' ' * (int((WIDTH - len(image_url)) / 2))}"
        click.echo(f"{space_for_center}{image_url}")

    @staticmethod
    def echo_url(event: ElCairoEvent) -> None:
        """Echo url."""

        url: str = event.url or DEFAULT
        click.echo(
            f"{click.style('URL:', fg='yellow')} {click.style(url, italic=True)}"
        )
