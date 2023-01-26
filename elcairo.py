"""Cine El Cairo API"""

from ics import Calendar, Event
from movie import Movie
import requests


class ElCairo:
    """El cairo api, just get movies information"""

    def get_movies(self, day: str, month: str, year: str) -> list[Movie]:
        """
        Get movies from a given day, month, year
        All the movies that the ics got, I don't know how the euristics works
        """

        ics_url: str = f"https://elcairocinepublico.gob.ar/cartelera-de-sala/mes/?tribe-bar-date={year}-{month}-{day}&ical=1&tribe_display=month"

        cal: Calendar = Calendar(requests.get(ics_url).text)

        movies: list[Movie] = []

        event: Event

        for event in cal.events:
            movies.append(Movie(event))

        return movies
