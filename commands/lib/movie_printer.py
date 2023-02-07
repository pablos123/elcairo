"""An event is always a movie in this program"""
import json
import os
import shutil

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
            if name == "":
                name = "[No name...]"

            begin: str = movie["begin"]
            if begin == "":
                begin = "[No beginning...]"

            click.echo(
                f"{Style.BRIGHT}{Style.BRIGHT}{name}{Style.RESET_ALL}   {begin}")

            if self.images:
                click.echo()
                self.echo_image(movie["image_url"], uid)

            if not self.no_extra_info:
                click.echo()
                self.echo_extra_info(movie["extra_info"])

            if self.urls:
                click.echo()
                self.echo_urls(movie["urls"])

            click.echo()

    @staticmethod
    def echo_extra_info(extra_info: dict) -> None:
        """
        Show extra info.
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

        click.echo(
            f"{Style.DIM}{truncate(extra_info['synopsis'])}{Style.RESET_ALL}\n")

        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}")
        for key in extra_info["data"].keys():
            value = extra_info["data"][key]

            field: str = ""
            match key:
                case "director":
                    field = "Dirección"
                case "cast":
                    field = "Elenco"
                case "genre":
                    field = "Género"
                case "duration":
                    field = "Duración"
                case "origin":
                    field = "Origen"
                case "year":
                    field = "Año"
                case "age":
                    field = "Calificación"

            print_field = f"{field}: "
            if len(value) + len(print_field) > 80:
                value = truncate(value)
                print_field = f"{field}:\n"

            click.echo(f"{Fore.YELLOW}{print_field}{Style.RESET_ALL}{value}")

        click.echo(f"{Style.BRIGHT}{80*'*'}{Style.RESET_ALL}\n")

        cost: str = extra_info["cost"].strip().replace("\n", " ")
        click.echo(f"{Fore.GREEN}Valor:{Style.RESET_ALL} {truncate(cost)}")

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
        if len(urls) == 0:
            return

        click.echo(f"{Fore.YELLOW}Más info:{Style.RESET_ALL}")
        for url in urls:
            click.echo(url)

    @staticmethod
    def echo_data_structure(movie: dict) -> None:
        """
        Echo a raw movie dict.
        """
        click.echo(movie)
