"""Cine El Cairo API"""

import re
import time
from collections.abc import Container
from dataclasses import dataclass, field
from re import Match

import arrow
import bs4
import ics
import requests

_IMAGE_MIME_RE = re.compile(r"^ATTACH;FMTTYPE=image/(?:jpeg|png|webp)$")


@dataclass
class ElCairoExtraInfo:
    direction: str = ""
    cast: str = ""
    genre: str = ""
    duration: str = ""
    origin: str = ""
    year: str = ""
    age: str = ""


@dataclass
class ElCairoEvent:
    name: str = ""
    date: str = ""
    synopsis: str = ""
    cost: str = ""
    image_url: str = ""
    url: str = ""
    image_path: str = ""
    extra_info: ElCairoExtraInfo = field(default_factory=ElCairoExtraInfo)


class ElCairo:
    """Get El Cairo's information."""

    def ics_events_to_elcairo_events(
        self, events: set[ics.Event]
    ) -> dict[str, ElCairoEvent]:
        """
        Returns a json of events.
        This method scraps for more info in the specified event url.
        """
        events_dict: dict[str, ElCairoEvent] = {}

        for event in events:
            elcairo_event_args: dict = {}

            if event.name:
                elcairo_event_args["name"] = event.name.upper()

            if event.begin:
                elcairo_event_args["date"] = str(event.begin)

            if event.extra:
                elcairo_event_args["image_url"] = self.get_image(event.extra)

            if event.url:
                elcairo_event_args["url"] = event.url

                soup: bs4.BeautifulSoup | None = self.get_soup(event.url)
                if soup is not None:
                    elcairo_event_args["synopsis"] = self.get_synopsis(soup)
                    elcairo_event_args["cost"] = self.get_cost(soup)
                    elcairo_event_args["extra_info"] = self.get_extra_info(soup)

            events_dict[event.uid] = ElCairoEvent(**elcairo_event_args)

        return events_dict

    def get_upcoming_events(self) -> set[ics.Event]:
        """Get upcoming events."""
        now: arrow.Arrow = arrow.now()

        year: int = now.year
        month: int = now.month

        upcoming_events: set[ics.Event] = set()
        current_events, error = self.fetch_events(
            str(year).zfill(4), str(month).zfill(2)
        )
        while current_events != set() or error:
            if month == 12:
                month = 0
                year += 1
            month += 1

            if error:
                current_events, error = self.fetch_events(
                    str(year).zfill(4), str(month).zfill(2)
                )
                continue

            current_upcoming_events: set[ics.Event] = set()
            for event in current_events:
                if event.begin >= now:
                    current_upcoming_events.add(event)

            upcoming_events.update(current_upcoming_events)

            current_events, error = self.fetch_events(
                str(year).zfill(4), str(month).zfill(2)
            )

        return upcoming_events

    def get_past_events(self) -> set[ics.Event]:
        """Get past events."""
        now: arrow.Arrow = arrow.now()

        year: int = now.year
        month: int = now.month

        past_events: set[ics.Event] = set()
        current_events, error = self.fetch_events(
            str(year).zfill(4), str(month).zfill(2)
        )
        while current_events != set() or error:
            if month == 1:
                month = 13
                year -= 1
            month -= 1

            if error:
                current_events, error = self.fetch_events(
                    str(year).zfill(4), str(month).zfill(2)
                )
                continue

            current_past_events: set[ics.Event] = set()
            for event in current_events:
                if event.begin <= now:
                    current_past_events.add(event)

            past_events.update(current_past_events)

            current_events, error = self.fetch_events(
                str(year).zfill(4), str(month).zfill(2)
            )

        return past_events

    def get_all_events(self) -> set[ics.Event]:
        """Get all events."""
        all_events: set[ics.Event] = set()
        all_events.update(self.get_past_events())
        all_events.update(self.get_upcoming_events())
        return all_events

    def get_upcoming_events_json(self) -> dict[str, ElCairoEvent]:
        """Get upcoming events as json."""
        upcoming_events: set[ics.Event] = self.get_upcoming_events()
        return self.ics_events_to_elcairo_events(upcoming_events)

    def get_past_events_json(self) -> dict[str, ElCairoEvent]:
        """Get past events."""
        past_events: set[ics.Event] = self.get_past_events()
        return self.ics_events_to_elcairo_events(past_events)

    def get_all_events_json(self) -> dict[str, ElCairoEvent]:
        """Get all events."""
        all_events: set[ics.Event] = self.get_all_events()
        return self.ics_events_to_elcairo_events(all_events)

    def get_soup(self, url: str) -> bs4.BeautifulSoup | None:
        """Get the beautiful soup of El Cairo's url."""
        try:
            response: requests.Response = requests.get(url, timeout=10)
            response.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
        ):
            return None

        response_html: str = response.text

        return bs4.BeautifulSoup(response_html, "html.parser")

    @staticmethod
    def get_cost(soup: bs4.BeautifulSoup) -> str:
        """Get the cost of an event inside a El Cairo's url."""
        cost: str = ""
        cost_elem: bs4.Tag | None = soup.select_one(".informacion-entradas")
        if cost_elem is not None and cost_elem.find("p") is not None:
            cost = cost_elem.find("p").text  # pyright: ignore[reportOptionalMemberAccess]
        return cost

    @staticmethod
    def get_synopsis(soup: bs4.BeautifulSoup) -> str:
        """Get the synopsis of an event inside a El Cairo's url."""
        synopsis: str = ""
        synopsis_elem: bs4.Tag | None = soup.select_one(".sinopsis-online")
        if synopsis_elem is not None and synopsis_elem.find("p") is not None:
            synopsis = synopsis_elem.find("p").text  # pyright: ignore[reportOptionalMemberAccess]
        return synopsis

    @staticmethod
    def get_extra_info(soup: bs4.BeautifulSoup) -> ElCairoExtraInfo:
        """Get the extra info inside a El Cairo's url."""
        extra_info_args: dict[str, str] = {}
        data_elem: bs4.Tag | None = soup.select_one(".ficha-tecnica-online")
        if data_elem is not None:
            data_lines: list[str] = data_elem.text.split("\n")
            if len(data_lines) == 0:
                return ElCairoExtraInfo()

            field_names: dict = {
                "DIRECCIÓN": "direction",
                "DIRECCION": "direction",
                "ELENCO": "cast",
                "GÉNERO": "genre",
                "GENERO": "genre",
                "DURACIÓN": "duration",
                "DURACION": "duration",
                "ORIGEN": "origin",
                "AÑO": "year",
                "ANO": "year",
                "CALIFICACIÓN": "age",
                "CALIFICACION": "age",
            }

            for line in data_lines:
                match = re.match(r"^ *(\w+): (.+)$", line)
                if not match:
                    continue

                field_name: str = match.group(1)
                field_data: str = match.group(2)

                key: str | None = field_names.get(field_name)
                if key is not None:
                    extra_info_args[key] = field_data

        return ElCairoExtraInfo(**extra_info_args)

    @staticmethod
    def get_image(extra_info: list[Container]) -> str:
        """Get the image url if the mime type is a valid image mime type."""

        def check_mime(mime: str) -> Match[str] | None:
            """
            Check if the extra info of a 'elcairo' type event
            is a 'file' and if the mime type is correct.
            The regex is based on the information
            I saw in some of the El Cairo's .ics
            """
            return _IMAGE_MIME_RE.search(mime)

        image_url: str = ""
        for item in extra_info:
            parts: list[str] = str(item).split(":", 1)
            if len(parts) == 2 and check_mime(parts[0]):
                image_url = parts[1]
        return image_url

    @staticmethod
    def fetch_events(year: str, month: str) -> tuple[set[ics.Event], bool]:
        """Fetch the ics file of the year-month date."""
        time.sleep(0.5)

        ics_url: str = f"https://elcairocinepublico.gob.ar/cartelera-de-sala/{year}-{month}/?ical=1"

        try:
            response = requests.get(ics_url, timeout=10)
            response.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
        ):
            return set(), True

        error: bool = False
        events: set[ics.Event] = set()
        try:
            events = ics.Calendar(response.text).events
        except ValueError:
            error = True

        return events, error
