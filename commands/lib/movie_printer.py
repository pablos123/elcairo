"""An event is always a movie in this program"""
import json
import os
import re
import shutil
from typing import Any

import click
import climage
import requests
from colorama import Back, Fore, Style


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

        for uid in movies.keys():
            movie = movies[uid]

            click.echo(f"{Back.WHITE}{Fore.BLACK}{80*'-'}{Style.RESET_ALL}\n")

            name: str = movie["name"]
            if name == 0:
                name = "[No name...]"

            begin: str = movie["begin"]
            if begin == 0:
                begin = "[No beginning...]"

            click.echo(
                f"{Style.BRIGHT}{Style.BRIGHT}{name}{Style.RESET_ALL}   {begin}")

            if self.images:
                click.echo()
                self.echo_image(movie["image_url"], uid)

            click.echo()

            if not self.no_extra_info:
                self.echo_extra_info(movie["extra_info"])

            if self.urls:
                click.echo(
                    f"{Fore.YELLOW}Más info:{Style.RESET_ALL} {movie['url']}")

                click.echo(
                    f"{Fore.YELLOW}Todas las funciones:{Style.RESET_ALL} {self.modify_url(movie['url'])}\n"
                )

    @staticmethod
    def echo_extra_info(extra_info: dict) -> None:
        """
        Show extra info. Ficha tecnica is a dict.
        """

        if "failed" in extra_info:
            click.echo(extra_info["failed"])
            return

        def truncate(string: str):
            """
            Truncate a string to only be 80 characters long.
            """
            if len(string) <= 80:
                return string.strip()

            out: str = ""
            lines: list[str] = [string[i: i + 80]
                                for i in range(0, len(string), 80)]
            for line in lines:
                out += f"{line}\n"

            return out.strip()

        # Sinopsis
        click.echo(
            f"{Style.DIM}{truncate(extra_info['sinopsis'])}{Style.RESET_ALL}\n")

        # Extra info
        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}")
        for key in extra_info["ficha_tecnica"].keys():
            value = extra_info["ficha_tecnica"][key]
            if len(value) + len(key) > 80:
                click.echo(
                    f"{Fore.YELLOW}{key.capitalize()}:{Style.RESET_ALL}\n{truncate(value)}"
                )
                continue

            click.echo(
                f"{Fore.YELLOW}{key.capitalize()}: {Style.RESET_ALL}{truncate(value)}"
            )
        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}\n")

        # Valor
        valor_entrada: str = extra_info["valor_entrada"].strip().replace(
            "\n", " ")
        click.echo(
            f"{Fore.GREEN}Valor:{Style.RESET_ALL} {truncate(valor_entrada)}\n")

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
            output = "[Cannot show image...]\n"

        click.echo(output)

    @staticmethod
    def modify_url(url: Any) -> Any:
        """
        Modify the url of the movie to be the url that shows all the shows.
        """
        return re.sub(r"\d+-\d+-\d+/(:?\d+/)?$", "", url)
