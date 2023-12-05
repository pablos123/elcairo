"""
Common database functions of all cinemas commands.
"""

import sqlite3


def query(
    cursor: sqlite3.Cursor, date_int_min: int, date_int_max: int, order: str
) -> list[dict]:
    """Execute query."""

    movies: list = []
    try:
        res: sqlite3.Cursor = cursor.execute(
            f"""
            SELECT * FROM movies WHERE compare_date >= {date_int_min} AND
            compare_date <= {date_int_max} ORDER BY compare_date {order};
            """
        )
        movies = [dict(row) for row in res.fetchall()]
    except sqlite3.OperationalError:
        pass

    return movies
