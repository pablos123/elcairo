"""
El Cairo command.
"""

import json
import os
import shutil
import sqlite3

import click
import climage
import requests

from apis.elcairo import ElCairo


def get_ascii_image(url: str, uid: str) -> str:
    """
    Creates a temporal file reads it and return the ascii art.
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

    return output


def get_string_urls(urls: list[str]) -> str:
    """
    Return a concatenation of the info urls of the movie.
    """

    return " ".join(urls)


@click.group()
def database() -> None:
    """
    Database methods.
    """


@database.command()
def populate() -> None:
    """
    Populate the database.
    """
    if os.path.exists("./cinecli.db"):
        try:
            os.remove("./cinecli.db")
        except OSError as _:
            click.echo("Cannot remove cinecli.db, try again...")

    connection = sqlite3.connect("cinecli.db")
    cursor = connection.cursor()

    create_query: str = """
    CREATE TABLE IF NOT EXISTS movies (
        movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        synopsis TEXT NOT NULL,
        direction TEXT NOT NULL,
        cast TEXT NOT NULL,
        genre TEXT NOT NULL,
        duration TEXT NOT NULL,
        origin TEXT NOT NULL,
        year TEXT NOT NULL,
        age TEXT NOT NULL,
        cost TEXT NOT NULL,
        image TEXT NOT NULL,
        urls TEXT NOT NULL,
        cinema TEXT NOT NULL
    );"""

    cursor.execute(create_query)

    elcairo: ElCairo = ElCairo()
    events_dict = json.loads(elcairo.get_upcoming_shows_json())

    data_insert: list = []

    for uid, movie_data in events_dict.items():
        event = (
            movie_data["name"],
            movie_data["date"],
            movie_data["synopsis"],
            movie_data["direction"],
            movie_data["cast"],
            movie_data["genre"],
            movie_data["duration"],
            movie_data["origin"],
            movie_data["year"],
            movie_data["age"],
            movie_data["cost"],
            get_ascii_image(movie_data["image_url"], uid),
            get_string_urls(movie_data["urls"]),
            "elcairo",
        )
        data_insert.append(event)

    cursor.executemany(
        """
        INSERT INTO movies (
            'name',
            'date',
            'synopsis',
            'direction',
            'cast',
            'genre',
            'duration',
            'origin',
            'year',
            'age',
            'cost',
            'image',
            'urls',
            'cinema')
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        data_insert,
    )

    connection.commit()


@database.command()
def clean() -> None:
    """
    Clean the database.
    """
    if os.path.exists("./cinecli.db"):
        try:
            os.remove("./cinecli.db")
        except OSError as _:
            click.echo("Cannot remove cinecli.db, try again...")
