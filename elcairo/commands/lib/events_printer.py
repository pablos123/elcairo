"""Print events"""

import os
import shutil
import subprocess
from pathlib import Path

import arrow
import click
from arrow import Arrow
from PIL import Image

from elcairo.api.elcairo import ElCairoEvent

DEFAULT = "[Nothing to show...]"
WIDTH = 120

RENDERERS: dict[str, list[str]] = {
    "wezterm": ["wezterm", "imgcat", "--width", "{width}", "{path}"],
    "iterm2": ["imgcat", "{path}"],
    "chafa": ["chafa", "--size={width}x", "{path}"],
    "timg": ["timg", "-g{width}x", "{path}"],
    "viu": ["viu", "-w", "{width}", "{path}"],
    "catimg": ["catimg", "-w", "{width}", "{path}"],
    "img2txt": ["img2txt", "--width={width}", "{path}"],
    "pixterm": ["pixterm", "{path}"],
    "jp2a": ["jp2a", "--width={width}", "{path}"],
}


def _detect_renderer(forced: str | None) -> str | None:
    """Return the renderer to use: forced override, then env-based, then PATH."""
    if forced is not None:
        return forced

    if os.getenv("KITTY_WINDOW_ID") or os.getenv("TERM") == "xterm-kitty":
        return "kitty"

    term_program = os.getenv("TERM_PROGRAM", "")
    if term_program == "WezTerm":
        return "wezterm"
    if term_program == "iTerm.app":
        return "iterm2"
    if term_program == "ghostty" or os.getenv("TERM") == "xterm-ghostty":
        return "kitty"

    for name in ("chafa", "timg", "viu", "catimg", "img2txt", "pixterm", "jp2a"):
        if shutil.which(name):
            return name

    return None


def _kitty_render(image_path: str) -> None:
    """Render image inline with kitty, pre-scaled to WIDTH columns."""
    temporal_img = Path("/tmp/elcairo_tmp_kitty.png")

    convert = subprocess.Popen(
        ["convert", image_path, "-resize", f"{WIDTH * 10}x", str(temporal_img)]
    )
    convert.wait()

    subprocess.run(["kitty", "+kitten", "icat", str(temporal_img)])


def _run_renderer(renderer: str, image_path: str) -> None:
    """Build and execute the renderer command."""
    if renderer == "kitty":
        _kitty_render(image_path)
        return

    template = RENDERERS[renderer]
    cmd = [part.format(path=image_path, width=str(WIDTH)) for part in template]
    subprocess.run(cmd)


def _builtin_ascii_render(image_path: str) -> None:
    """Render an image as ASCII art using Pillow. Always available as fallback."""

    # ASCII density ramp: darkest → lightest
    RAMP = " .`-_':,;^=+/\"|)\\<>)iv%xclrs{*}I?!][1taeo7zjLunT#JCwfy325Fp6mqSUZ8g4d9bKhE0X&WB@M"

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
            row += RAMP[int(pixel / 255 * (len(RAMP) - 1))]
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

        image_path: str = event.image_path or DEFAULT
        renderer = _detect_renderer(self.image_renderer)

        if renderer is None or renderer == "builtin":
            _builtin_ascii_render(image_path)
            return

        _run_renderer(renderer, image_path)

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
