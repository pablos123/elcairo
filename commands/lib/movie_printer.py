"""An event is always a movie in this program"""
import json
import re
import shutil
from typing import Any

import click
import climage
import requests
from colorama import Back, Fore, Style
from ics import Event


class MoviePrinter:
    """
    Movie printing utilities for echoing with click.
    """

    def echo_list(self, movies_json: str, show_image: bool) -> None:
        """
        Print a list of movies
        """

        movies: dict = json.loads(movies_json)

        for uid in movies.keys():
            movie = movies[uid]
            click.echo(f"{Back.WHITE}{Fore.BLACK}{80*'-'}{Style.RESET_ALL}\n")
            click.echo(
                f"{Style.BRIGHT}{Fore.GREEN}Nombre: {Style.RESET_ALL}{Style.BRIGHT}{movie['name']}{Style.RESET_ALL}\n"
            )
            if show_image:
                self.echo_image(movie["image_url"], uid)

            click.echo(f"{Fore.RED}Fecha:{Style.RESET_ALL} {movie['begin']}\n")
            click.echo(
                f"\n{Fore.YELLOW}Más info:{Style.RESET_ALL} {movie['url']}\n")
            click.echo(
                f"\n{Fore.YELLOW}Todas las funciones:{Style.RESET_ALL} {self.modify_url(movie['url'])}\n"
            )

    @staticmethod
    def echo_image(url: str, uid: str) -> None:
        """Creates a temporal file reads it and print the image through click.echo."""
        output: str = ""
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            file_name = f"/tmp/{uid}.jpeg"
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

        click.echo(output)

    @staticmethod
    def modify_url(url: Any) -> Any:
        """
        Modify the url of the movie to be the url that shows all the shows.
        """
        return re.sub(r"\d+-\d+-\d+/(:?\d+/)?$", "", url)
