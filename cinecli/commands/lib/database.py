"""
Common database functions of all cinemas commands.
"""

import sqlite3


def query_leq(
        cursor: sqlite3.Cursor, date_int_min: int, date_int_max: int, order: str
) -> list:
    """
    Execute query.
    """
    movies: list = []
    try:
        res = cursor.execute(
            f"""
            SELECT * FROM movies WHERE compare_date >= {date_int_min} AND
            compare_date <= {date_int_max} ORDER BY compare_date {order};
            """
        )
        movies = [dict(row) for row in res.fetchall()]
    except sqlite3.OperationalError:
        pass

    return movies


def query_eq(cursor: sqlite3.Cursor, date_int: int, order: str) -> list:
    """
    Execute query.
    """
    movies: list = []
    try:
        res = cursor.execute(
            f"""
            SELECT * FROM movies WHERE compare_date = {date_int}
            ORDER BY compare_date {order};
            """
        )
        movies = [dict(row) for row in res.fetchall()]
    except sqlite3.OperationalError:
        pass

    return movies
