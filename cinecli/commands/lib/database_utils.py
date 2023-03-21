"""
Common database functions of all cinemas commands.
"""

import sqlite3


def query_leq(
    cursor: sqlite3.Cursor, date_int_min: int, date_int_max: int
) -> list:
    """
    Execute query.
    """
    movies: list = []
    try:
        res = cursor.execute(
            f"""
            SELECT * FROM movies WHERE compare_date >= {date_int_min} AND
            compare_date <= {date_int_max};
            """
        )
        movies = [dict(row) for row in res.fetchall()]
    except sqlite3.OperationalError as _:
        pass

    return movies


def query_eq(cursor: sqlite3.Cursor, date_int: int) -> list:
    """
    Execute query.
    """
    movies: list = []
    try:
        res = cursor.execute(
            f"""
            SELECT * FROM movies WHERE compare_date = {date_int};
            """
        )
        movies = [dict(row) for row in res.fetchall()]
    except sqlite3.OperationalError as _:
        pass

    return movies
