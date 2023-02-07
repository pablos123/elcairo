"""An event is always a movie in this program"""
import json
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

            click.echo(
                f"{Style.BRIGHT}{Fore.GREEN}Nombre: {Style.RESET_ALL}{Style.BRIGHT}{movie['name']}{Style.RESET_ALL}"
            )

            if self.images:
                click.echo()
                self.echo_image(movie["image_url"], uid)

            click.echo(f"{Fore.GREEN}Fecha:{Style.RESET_ALL} {movie['begin']}")

            click.echo()

            if not self.no_extra_info:
                self.echo_extra_info(movie["extra_info"])

            if self.urls:
                click.echo(
                    f"\n{Fore.YELLOW}Más info:{Style.RESET_ALL} {movie['url']}")

                click.echo(
                    f"\n{Fore.YELLOW}Todas las funciones:{Style.RESET_ALL} {self.modify_url(movie['url'])}\n"
                )
                click.echo()

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
                return string

            out: str = ""
            lines: list[str] = [string[i: i + 80]
                                for i in range(0, len(string), 80)]
            for line in lines:
                out += f"{line}\n"

            return out.strip()

        click.echo(f"{Fore.GREEN}Sinopsis:{Style.RESET_ALL}")
        click.echo(truncate(extra_info["sinopsis"]))
        click.echo()

        click.echo(f"{Fore.GREEN}Ficha tecnica:{Style.RESET_ALL}")
        for key in extra_info["ficha_tecnica"].keys():
            if len(extra_info["ficha_tecnica"][key]) + len(key) > 80:
                click.echo(
                    f"{Fore.YELLOW}{key}:{Style.RESET_ALL}\n{truncate(extra_info['ficha_tecnica'][key])}"
                )
                continue

            click.echo(
                f"{Fore.YELLOW}{key}:{Style.RESET_ALL}{truncate(extra_info['ficha_tecnica'][key])}"
            )

        click.echo()
        valor_entrada = extra_info["valor_entrada"].strip().replace("\n", " ")
        click.echo(
            f"{Fore.GREEN}Valor entrada:{Style.RESET_ALL} {truncate(valor_entrada)}"
        )

        click.echo()

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
