"""
Cine El Cairo API
"""

import json
import re
from typing import Any, Container, Match, Set

import arrow
import requests
from arrow import Arrow
from bs4 import BeautifulSoup, Tag
from ics import Calendar, Event


class ElCairo:
    """
    Get El Cairo cinema shows information.
    """

    def events_to_json(self, events: Set[Event], reverse: bool = True) -> str:
        """
        Returns a json of events. The latest first. This method crawls for
        more info in the specified event url.
        """

        events_dict: dict = {}

        for event in events:
            parsed_dict: dict = {}

            parsed_dict["name"] = event.name.upper()

            parsed_dict["begin"] = self.get_date(event.begin)

            parsed_dict["urls"] = [event.url, self.modify_url(event.url)]

            if event.url:
                parsed_dict["extra_info"] = self.get_extra_info(event.url)

            parsed_dict["image_url"] = self.get_image(event.extra)

            events_dict[event.uid] = parsed_dict

        sorted_list: list = sorted(
            events_dict.items(), key=lambda x: x[1]["begin"], reverse=reverse
        )
        sorted_dict: dict = dict(sorted_list)
        return json.dumps(sorted_dict)

    ###########################################################################
    # EVENT
    ###########################################################################
    def get_todays_shows_event(self) -> Set[Event]:
        """
        Get todays movie shows events. The events are not sorted.
        """

        now: Arrow = arrow.now()

        current_events: Set[Event] = self.fetch_events(
            str(now.year).zfill(4), str(now.month).zfill(2)
        )

        todays_events: Set[Event] = set()
        for event in current_events:
            if event.begin.format("MM-DD") == now.format("MM-DD"):
                todays_events.add(event)

        return todays_events

    def get_upcoming_shows_event(self) -> Set[Event]:
        """
        Get upcoming movie shows events. The events are not sorted.
        """

        now: Arrow = arrow.now()

        year: int = now.year
        month: int = now.month

        upcoming_events: Set[Event] = set()
        current_events: Set[Event] = self.fetch_events(
            str(year).zfill(4), str(month).zfill(2)
        )
        while current_events != set():
            current_upcoming_events: Set[Event] = set()
            for event in current_events:
                if event.begin >= now:
                    current_upcoming_events.add(event)

            upcoming_events.update(current_upcoming_events)

            if month == 12:
                month = 0
                year += 1
            month += 1

            current_events = self.fetch_events(
                str(year).zfill(4), str(month).zfill(2))

        return upcoming_events

    def get_past_shows_event(self) -> Set[Event]:
        """
        Get past movie shows events. The events are not sorted.
        """

        now: Arrow = arrow.now()

        year: int = now.year
        month: int = now.month

        past_events: Set[Event] = set()
        current_events: Set[Event] = self.fetch_events(
            str(year).zfill(4), str(month).zfill(2)
        )
        while current_events != set():
            if month == 1:
                month = 13
                year -= 1
            month -= 1

            current_past_events: Set[Event] = set()
            for event in current_events:
                if event.begin <= now:
                    current_past_events.add(event)

            past_events.update(current_past_events)

            current_events = self.fetch_events(
                str(year).zfill(4), str(month).zfill(2))

        return past_events

    def get_date_shows_event(
        self, year: str | int, month: str | int, day: str | int
    ) -> Set[Event]:
        """
        Get movie shows events of a given date. The events are not sorted.
        """

        year = str(year).zfill(4)
        month = str(month).zfill(2)
        day = str(day).zfill(2)

        given_date: str = arrow.get(
            f"{year}-{month}-{day}").format("YYYY-MM-DD")

        current_events: Set[Event] = self.fetch_events(year, month)

        date_events: Set[Event] = set()
        for event in current_events:
            if event.begin.format("YYYY-MM-DD") == given_date:
                date_events.add(event)

        return date_events

    def get_until_date_shows_event(
        self, year: str | int, month: str | int, day: str | int
    ) -> Set[Event]:
        """
        Get movie shows events until a given date. The events are not sorted.
        """

        year = str(year).zfill(4)
        month = str(month).zfill(2)
        day = str(day).zfill(2)

        given_date: Arrow = arrow.get(f"{year}-{month}-{day} 23:59:59").replace(
            tzinfo="local"
        )

        upcoming_events: Set[Event] = self.get_upcoming_shows_event()
        until_date_events: Set[Event] = set()
        for event in upcoming_events:
            if event.begin <= given_date:
                until_date_events.add(event)

        return until_date_events

    def get_all_shows_event(self) -> Set[Event]:
        """
        Get all shows events. The events are not sorted.
        """
        all_events: Set[Event] = set()
        all_events.update(self.get_past_shows_event())
        all_events.update(self.get_upcoming_shows_event())

        return all_events

    ###########################################################################
    # JSON
    ###########################################################################
    def get_todays_shows_json(self, reverse: bool = True):
        """
        Get todays movie shows events as json.
        Default sort: closest shows last.
        """
        todays_events = self.get_todays_shows_event()
        return self.events_to_json(todays_events, reverse)

    def get_upcoming_shows_json(self, reverse: bool = True) -> str:
        """
        Get upcoming movie shows events as json.
        Default sort: closest shows last.
        """
        upcoming_events = self.get_upcoming_shows_event()
        return self.events_to_json(upcoming_events, reverse)

    def get_past_shows_json(self, reverse: bool = True) -> str:
        """
        Get past movie shows events.
        Default sort: closest shows last.
        """
        past_events = self.get_past_shows_event()
        return self.events_to_json(past_events, reverse)

    def get_date_shows_json(
        self, year: str | int, month: str | int, day: str | int, reverse: bool = True
    ) -> str:
        """
        Get movie shows of a given date as json.
        Default sort: closest shows last.
        """
        date_events = self.get_date_shows_event(year, month, day)
        return self.events_to_json(date_events, reverse)

    def get_until_date_shows_json(
        self, year: str | int, month: str | int, day: str | int, reverse: bool = True
    ) -> str:
        """
        Get movie shows until a given date.
        Default sort: closest shows last.
        """
        until_date_events = self.get_until_date_shows_event(year, month, day)
        return self.events_to_json(until_date_events, reverse)

    def get_all_shows_json(self, reverse: bool = True) -> str:
        """
        Get all movie shows events.
        Default sort: closest shows last.
        """
        all_events = self.get_all_shows_event()
        return self.events_to_json(all_events, reverse)

    def get_extra_info(self, url: str) -> dict:
        """
        Get the extra info inside a El Cairo's url.
        """

        extra_info: dict = {}
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
        ) as _:
            # It's not important if I cannot get some of the info.
            extra_info["failed"] = "[Error fetching extra info...]"
            return extra_info

        response_html: str = response.text

        soup = BeautifulSoup(response_html, "html.parser")

        synopsis: str = "[Nothing to show...]"
        synopsis_elem: Tag | None = soup.select_one(".sinopsis-online")
        if synopsis_elem is not None and synopsis_elem.find("p") is not None:
            synopsis = synopsis_elem.find("p").text
        extra_info["synopsis"] = synopsis

        data: dict = {}
        data_elem: Tag | None = soup.select_one(".ficha-tecnica-online")
        if data_elem is not None:
            data = self.get_extra_info_data(data_elem)
        if not data:
            data["nothing"] = "[Nothing to show...]"
        extra_info["data"] = data

        cost: str = "[Nothing to show...]"
        cost_elem: Tag | None = soup.select_one(".informacion-entradas")
        if cost_elem is not None and cost_elem.find("p") is not None:
            cost = cost_elem.find("p").text
        extra_info["cost"] = cost

        return extra_info

    @staticmethod
    def get_extra_info_data(data_elem: Tag) -> dict:
        """
        Get the extra data in the extra information.
        """
        data: dict = {}
        data_lines: list[str] = data_elem.text.split("\n")
        if len(data_lines) == 0:
            return data

        for line in data_lines:
            match = re.match(r"^(\w+): (.+)$", line)
            if not match:
                continue

            field_name: str = match.group(1)
            field_data: str = match.group(2)

            key: str = ""
            match field_name:
                case "DIRECCIÓN":
                    key = "director"
                case "ELENCO":
                    key = "cast"
                case "GÉNERO":
                    key = "genre"
                case "DURACIÓN":
                    key = "duration"
                case "ORIGEN":
                    key = "origin"
                case "AÑO":
                    key = "year"
                case "CALIFICACIÓN":
                    key = "age"

            data[key] = field_data
        return data

    @staticmethod
    def modify_url(url: Any) -> Any:
        """
        Modify the url of the movie show to be the url that shows all the shows.
        """
        return re.sub(r"\d+-\d+-\d+/(:?\d+/)?$", "", url)

    @staticmethod
    def get_image(extra_info: list[Container]) -> str:
        """
        Get the image url if the mime type is a valid image mime type
        And is supported by climage.
        """

        def check_mime(mime: str) -> Match[str] | None:
            """
            Check if the extra info of a 'cairo' type event
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
    def get_date(event_begin: Arrow) -> str:
        """
        Format the date information a return a nice show's date
        """
        date: str = event_begin.format("DD-MM-YYYY HH:mm:ss")
        human_date: str = event_begin.humanize(locale="es")

        return f"{date} ({human_date})"

    @staticmethod
    def fetch_events(year: str, month: str) -> Set[Event]:
        """
        Fetch the ics file of the year-month date.
        """
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

        cal: Calendar = Calendar(response.text)

        return cal.events
