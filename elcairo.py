"""
Cine El Cairo API
"""

import re
from typing import Container, Match

import requests
from ics import Calendar, Event
from ics.utils import Arrow

from movie import Movie


# Parsers or similar
def check_mime(mime: str) -> Match[str] | None:
    """
    Check if the extra info of a 'cairo' type event
    is a 'file' and if the mime type is correct.
    The regex is based on the information I saw in some of the El Cairo's .ics
    """
    return re.search("^ATTACH;FMTTYPE=image/(:?jpeg|png|webp)$", mime)


def get_image(extra_info: Container) -> str:
    """
    Get the image url if the mime type is a valid image mime type
    And is supported by climage.
    """
    image_url: str = ""
    for item in extra_info:
        splitted_item_str: list[str] = str(item).split(":")
        if check_mime(splitted_item_str[0]):
            image_url = splitted_item_str[1] + ":" + splitted_item_str[2]
    return image_url


def modify_info_url(info_url: str | None) -> str:
    """
    Modify the url of the event to have consistency
    """
    return re.sub(r"\d+-\d+-\d+/(:?\d+/)?$", "", info_url)


def get_date(event_begin: Arrow) -> str:
    """
    Format the date information a return a nice show's date
    """
    date: str = event_begin.format("DD-MM-YYYY HH:mm:ss")
    human_date: str = event_begin.humanize(locale="es")

    return f"{date} ({human_date})"


class ElCairo:
    """Get El Cairo cinema shows information"""

    def __init__(self, day: str | None, month: str | None, year: str | None):
        self.set_events(day, month, year)

        self.movies: list[Movie] = []
        self.set_movies()

    def set_events(self, day: str | None, month: str | None, year: str | None):
        """
        Get the events in the given date
        """
        ics_url: str = f"https://elcairocinepublico.gob.ar/cartelera-de-sala/lista/?tribe-bar-date=2023-01-27&ical=1"
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

        self.events = cal.events

    def set_movies(self):
        """
        Convert the events in the class in movies
        """

        movies_dict: dict = {}

        for event in self.events:

            show_date = get_date(event.begin)

            if event.name in movies_dict:
                movies_dict[event.name]["shows"].append(show_date)
                continue

            movie: dict = {}

            movie["shows"] = [show_date]

            movie["info_url"] = modify_info_url(event.url)

            movie["uid"] = event.uid

            movie["image_url"] = get_image(event.extra)

            movies_dict[event.name] = movie

        for movie_name in movies_dict.keys():
            self.movies.append(Movie(movie_name, movies_dict[movie_name]))

    def get_movies(self) -> list[Movie]:
        """
        Return the list of movies
        """
        return self.movies
