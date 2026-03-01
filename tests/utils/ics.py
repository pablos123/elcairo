"""Utilities for working with .ics files in tests."""

from pathlib import Path

import icalendar


def read_ics(path: str | Path) -> icalendar.Calendar:
    """Parse an .ics file and return the Calendar object."""
    with Path(path).open() as f:
        return icalendar.Calendar.from_ical(f.read())
