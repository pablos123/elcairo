"""An event is always a movie in this program"""
import re
import shutil

import climage
import requests
from colorama import Back, Fore, Style
from ics import Event


class Movie:
    """
    A movie is a name, a group of event hours, an image (for now just urls) and an info url
    with methods to print information.
    """

    def __init__(self, movie_name: str, movie_info: dict):

        self.name: str = movie_name

        # To use it in the temporal image name
        self.uid: str = movie_info["uid"]

        self.info_url: str = movie_info["info_url"]

        self.shows: list[str] = movie_info["shows"]

        self.image_url: str = movie_info["image_url"]

    def print(self) -> None:
        """Print the movie information"""

        print(f"{Fore.GREEN}Nombre: {Style.RESET_ALL} {self.name}")

        print(f"{Fore.RED}Shows: {Style.RESET_ALL}")

        print("\n".join(self.shows))

        print(f"{Fore.YELLOW}Más info: {Style.RESET_ALL} {self.info_url}\n")

    def show_image(self) -> None:
        """Creates a temporal file reads it and shows it"""
        output: str = ""
        if self.image_url:
            try:
                response = requests.get(self.image_url, stream=True, timeout=10)
                response.raise_for_status()
                file_name = f"/tmp/{self.uid}.jpeg"
                with open(file_name, "wb") as image_file:
                    shutil.copyfileobj(response.raw, image_file)
                    output = climage.convert(file_name)
            except (
                requests.exceptions.HTTPError,
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.RequestException,
                OSError,
            ) as _:

                output = "[Cannot show image...]\n"

        print(output)
