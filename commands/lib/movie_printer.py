"""An event is always a movie in this program"""
import json
import os
import shutil

import click
import climage
import requests
from colorama import Back, Fore, Style


def truncate(string: str, start_len: int = 0):
    """
    Truncate a string to only be 80 characters long.
    start_len represents the lenght of a title for the string.
    """
    first_line_len = 80 - start_len

    if len(string) <= first_line_len:
        return string.replace("\n", " ").strip()

    out: str = ""
    lines: list[str] = [string[0:first_line_len]]
    lines.extend([string[i: i + 80]
                 for i in range(first_line_len, len(string), 80)])
    for line in lines:
        out += f"{line}\n"

    return out.strip()


class MoviePrinter:
    """
    Movie printing utilities for echoing with click.
    """

    def __init__(self, images: bool, no_extra_info: bool, urls: bool):
        self.images = images
        self.no_extra_info = no_extra_info
        self.urls = urls

    def echo_list(self, movies_json: str) -> None:
        """
        Print a list of movies
        """

        movies: dict = json.loads(movies_json)

        default = "[Nothing to show...]"
        for uid, movie in movies.items():
            click.echo(f"{Back.WHITE}{Fore.BLACK}{80*'-'}{Style.RESET_ALL}\n")

            name: str = default
            if "name" in movie and movie["name"] != "":
                name = movie["name"]

            begin: str = default
            if "begin" in movie and movie["begin"] != "":
                begin = movie["begin"]

            click.echo(
                f"{Style.BRIGHT}{Style.BRIGHT}{name}{Style.RESET_ALL}   {begin}")

            if self.images:
                click.echo()
                if "image_url" in movie and movie["image_url"] != "":
                    self.echo_image(movie["image_url"], uid)
                else:
                    click.echo(default)

            if not self.no_extra_info:
                click.echo()
                if "extra_info" in movie and movie["extra_info"] != {}:
                    self.echo_extra_info(movie["extra_info"])
                else:
                    click.echo(default)

            if self.urls:
                click.echo()
                if "urls" in movie and movie["urls"] != []:
                    self.echo_urls(movie["urls"])
                else:
                    click.echo(default)

            click.echo()

    def echo_extra_info(self, extra_info: dict) -> None:
        """
        Show extra info.
        """

        default = "[Nothing to show...]"

        synopsis = default
        if "synopsis" in extra_info and extra_info["synopsis"] != "":
            synopsis = extra_info["synopsis"]

        click.echo(f"{Style.DIM}{truncate(synopsis)}{Style.RESET_ALL}\n")

        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}")

        self.echo_extra_info_title(extra_info, "direction", "Dirección: ")
        self.echo_extra_info_title(extra_info, "cast", "Elenco: ")
        self.echo_extra_info_title(extra_info, "genre", "Género: ")
        self.echo_extra_info_title(extra_info, "duration", "Duración: ")
        self.echo_extra_info_title(extra_info, "origin", "Origen: ")
        self.echo_extra_info_title(extra_info, "year", "Año: ")
        self.echo_extra_info_title(extra_info, "age", "Calificación: ")

        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}\n")

        self.echo_extra_info_title(extra_info, "cost", "Valor: ", Fore.GREEN)

    @staticmethod
    def echo_extra_info_title(
        extra_info: dict,
        key: str,
        title: str,
        color: str = Fore.YELLOW,
    ) -> None:
        """
        Show a title in the extra info.
        """

        data = "[Nothing to show...]"
        if key in extra_info and extra_info[key] != "":
            data = extra_info[key]

        click.echo(
            f"{color}{title}{Style.RESET_ALL}{truncate(data, len(title))}")

    @staticmethod
    def echo_image(url: str, uid: str) -> None:
        """
        Creates a temporal file reads it and
        print the image through click.echo.
        """
        output: str = ""
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            file_name = f"/tmp/{uid}.jpeg"
            with open(file_name, "wb") as image_file:
                shutil.copyfileobj(response.raw, image_file)
                output = climage.convert(file_name)
            os.remove(file_name)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException,
            OSError,
        ) as _:
            output = "[Cannot show image...]"

        click.echo(output)

    @staticmethod
    def echo_urls(urls: list[str]) -> None:
        """
        Echo the list of ulrs for the movie.
        """

        click.echo(f"{Fore.YELLOW}Más info:{Style.RESET_ALL}")
        for url in urls:
            click.echo(url)

    @staticmethod
    def echo_data_structure(movie: dict) -> None:
        """
        Echo a raw movie dict.
        """
        click.echo(movie)
