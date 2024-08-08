"""Functions used in the database command."""

import os
import shutil
import threading
from time import sleep

import requests
from progress.spinner import MoonSpinner


def download_image(url: str, uid: str, script_dir: str) -> str:
    """Download an image."""

    try:
        response: requests.Response = requests.get(url, stream=True, timeout=3)
        response.raise_for_status()
        file_name: str = os.path.join(script_dir, "images", f"{uid}.jpeg")
        with open(file_name, "wb") as image_file:
            shutil.copyfileobj(response.raw, image_file)
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.RequestException,
        OSError,
    ):
        file_name = ""

    return file_name


def loading(task: str, thread: threading.Thread) -> None:
    """Echo a task with a spinner."""

    with MoonSpinner(task + "...  ") as spinner:
        while thread.is_alive():
            sleep(0.1)
            spinner.next()
