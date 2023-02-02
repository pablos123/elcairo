"""
Cine El Cairo API
"""

import json
import re
from typing import Container, Match, Set

import arrow
import requests
from ics import Calendar, Event
from ics.utils import Arrow


class ElCairo:
    """
    Get El Cairo cinema shows information.
    """

    def events_to_json(self, events: Set[Event]) -> str:
        """
        Returns a json of events. The latest first.
        """

        events_dict: dict = {}

        for event in events:
            parsed_dict: dict = {}

            parsed_dict["name"] = event.name.upper()

            parsed_dict["begin"] = self.get_date(event.begin)

            # El Cairo events does not have an `end` date,
            # is always the same as the `begin` date.
            # parsed_dict["end"] = event.end.format("DD-MM-YYYY HH:mm:ss")

            parsed_dict["url"] = event.url

            parsed_dict["image_url"] = self.get_image(event.extra)

            events_dict[event.uid] = parsed_dict

        sorted_list: list = sorted(
            events_dict.items(), key=lambda x: x[1]["begin"], reverse=True
        )
        sorted_dict: dict = dict(sorted_list)
        return json.dumps(sorted_dict)

    def get_todays_shows_event(self) -> Set[Event]:
        """
        Get todays movie shows events. The events are not sorted.
        """

        now: Arrow = Arrow.now()

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

        now: Arrow = Arrow.now()

        year, month = (now.year, now.month)

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

        now: Arrow = Arrow.now()

        year, month = (now.year, now.month)

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

        year: str = str(year).zfill(4)
        month: str = str(month).zfill(2)
        day: str = str(day).zfill(2)

        given_date: Arrow = arrow.get(
            f"{year}-{month}-{day}").format("YYYY-MM-DD")

        current_events: Set[Event] = self.fetch_events(year, month)

        date_events: Set[Event] = set()
        for event in current_events:
            if event.begin.format("YYYY-MM-DD") == given_date:
                date_events.add(event)

        return date_events

    def get_until_date_shows_event(
        self, year: str | int, month: str | int, day: str | int
    ) -> str:
        """
        Get movie shows events until a given date. The events are not sorted.
        """

        year: str = str(year).zfill(4)
        month: str = str(month).zfill(2)
        day: str = str(day).zfill(2)

        given_date: Arrow = arrow.get(
            f"{year}-{month}-{day}").format("YYYY-MM-DD")

        upcoming_events: Set[Event] = self.get_upcoming_shows_event()
        until_date_events: Set[Event] = set()
        for event in upcoming_events:
            if event.begin.format("YYYY-MM-DD") <= given_date:
                until_date_events.add(event)

        return until_date_events

    def get_all_shows_event(self) -> Set[Event]:
        """
        Get all shows events. The events are not sorted.
        """
        all_events: Set = set()
        all_events.update(self.get_past_shows_event())
        all_events.update(self.get_upcoming_shows_event())

        return all_events

    def get_todays_shows_json(self):
        """
        Get todays movie shows events as json.
        The events are sorted by date, the latest first.
        """
        todays_events = self.get_todays_shows_event()
        return self.events_to_json(todays_events)

    def get_upcoming_shows_json(self) -> str:
        """
        Get upcoming movie shows events as json.
        The events are sorted by date, the latest first.
        """
        upcoming_events = self.get_upcoming_shows_event()
        return self.events_to_json(upcoming_events)

    def get_past_shows_json(self) -> str:
        """
        Get past movie shows events.
        The events are sorted by date, the latest first.
        """
        past_events = self.get_past_shows_event()
        return self.events_to_json(past_events)

    def get_date_shows_json(
        self, year: str | int, month: str | int, day: str | int
    ) -> str:
        """
        Get movie shows of a given date as json.
        The events are sorted by date, the latest first.
        """
        date_events = self.get_date_shows_event(year, month, day)
        return self.events_to_json(date_events)

    def get_until_date_shows_json(
        self, year: str | int, month: str | int, day: str | int
    ) -> str:
        """
        Get movie shows until a given date.
        The events are sorted by date, the latest first.
        """
        until_date_events = self.get_until_date_shows_event(year, month, day)
        return self.events_to_json(until_date_events)

    def get_all_shows_json(self) -> str:
        """
        Get all movie shows events.
        The events are sorted by date, the latest first.
        """
        all_events = self.get_all_shows_event()
        return self.events_to_json(all_events)

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
