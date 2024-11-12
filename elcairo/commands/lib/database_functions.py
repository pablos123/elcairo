"""Functions used in the database command."""

import shutil
from pathlib import Path

import requests


def download_image(url: str, uid: str, script_dir: Path) -> str:
    """Download an image and returns the path to the file."""
    file_path: Path | None = None

    try:
        response: requests.Response = requests.get(url, stream=True, timeout=3)
        response.raise_for_status()
        file_path = script_dir / "images" / f"{uid}.jpeg"
        with Path(file_path).open("wb") as image_file:
            shutil.copyfileobj(response.raw, image_file)
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.RequestException,
        OSError,
    ):
        pass

    return str(file_path) if file_path is not None else ""
