"""
Cine El Cairo API
"""

import json
import re
import time

import arrow
import bs4
import ics
import requests

from typing import TYPE_CHECKING
from typing import Container, Match


class ElCairo:
    """Get El Cairo's movie shows information."""

    def events_to_json(self, events: set[ics.Event]) -> str:
        """
        Returns a json of events.
        This method scraps for more info in the specified event url.
        """

        events_dict: dict = {}

        for event in events:
            parsed_dict: dict = {
                "name": "",
                "date": "",
                "synopsis": "",
                "cost": "",
                "cast": "",
                "direction": "",
                "genre": "",
                "duration": "",
                "origin": "",
                "year": "",
                "age": "",
                "image_url": "",
                "urls": [],
            }

            if event.name:
                parsed_dict["name"] = event.name.upper()

            if event.begin:
                parsed_dict["date"] = str(event.begin)

            if event.url:
                parsed_dict["urls"] = [event.url, self.modify_url(event.url)]

            if event.url:
                parsed_dict.update(self.get_extra_info(event.url))

            if event.extra:
                parsed_dict["image_url"] = self.get_image(event.extra)

            events_dict[event.uid] = parsed_dict

        return json.dumps(events_dict)

    def get_upcoming_shows_event(self) -> set[ics.Event]:
        """Get upcoming movie shows events."""

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

    def get_past_shows_event(self) -> set[ics.Event]:
        """Get past movie shows events."""

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

    def get_all_shows_event(self) -> set[ics.Event]:
        """Get all movie shows events."""

        all_events: set[ics.Event] = set()
        all_events.update(self.get_past_shows_event())
        all_events.update(self.get_upcoming_shows_event())

        return all_events

    def get_upcoming_shows_json(self) -> str:
        """Get upcoming movie shows events as json."""

        upcoming_events: set[ics.Event] = self.get_upcoming_shows_event()
        return self.events_to_json(upcoming_events)

    def get_past_shows_json(self) -> str:
        """Get past movie shows events."""

        past_events: set[ics.Event] = self.get_past_shows_event()
        return self.events_to_json(past_events)

    def get_all_shows_json(self) -> str:
        """Get all movie shows events."""

        all_events: set[ics.Event] = self.get_all_shows_event()
        return self.events_to_json(all_events)

    def get_extra_info(self, url: str) -> dict:
        """Get the extra info inside a El Cairo's url."""

        extra_info: dict = {}

        try:
            response: requests.Response = requests.get(url, timeout=10)
            response.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
        ):
            # It's not important if I cannot get some of the info.
            return extra_info

        response_html: str = response.text

        soup: bs4.BeautifulSoup = bs4.BeautifulSoup(response_html, "html.parser")

        synopsis: str = ""
        synopsis_elem: bs4.Tag | None = soup.select_one(".sinopsis-online")
        if synopsis_elem is not None and synopsis_elem.find("p") is not None:
            synopsis = synopsis_elem.find("p").text
        extra_info["synopsis"] = synopsis

        data_elem: bs4.Tag | None = soup.select_one(".ficha-tecnica-online")
        if data_elem is not None:
            extra_info.update(self.get_extra_info_data(data_elem))

        cost: str = ""
        cost_elem: bs4.Tag | None = soup.select_one(".informacion-entradas")
        if cost_elem is not None and cost_elem.find("p") is not None:
            cost = cost_elem.find("p").text
        extra_info["cost"] = cost

        return extra_info

    @staticmethod
    def get_extra_info_data(data_elem: bs4.Tag) -> dict:
        """Get the extra data in the extra information."""

        data: dict = {}
        data_lines: list[str] = data_elem.text.split("\n")
        if len(data_lines) == 0:
            return data

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
                data[key] = field_data
        return data

    @staticmethod
    def modify_url(url: str) -> str:
        """Modify the url of the movie show to be the url that shows all the shows."""

        return re.sub(r"\d+-\d+-\d+/(:?\d+/)?$", "", url)

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
            return re.search("^ATTACH;FMTTYPE=image/(:?jpeg|png|webp)$", mime)

        image_url: str = ""
        for item in extra_info:
            splitted_item_str: list[str] = str(item).split(":")
            if check_mime(splitted_item_str[0]):
                image_url = splitted_item_str[1] + ":" + splitted_item_str[2]
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
        ) as get_error:
            raise get_error

        error: bool = False
        events: set[ics.Event] = set()
        try:
            events = ics.Calendar(response.text).events
        except ValueError:
            error = True

        return events, error
