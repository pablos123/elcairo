"""Functions used in the database command."""

import os
import shutil
import threading
from time import sleep

import climage
import requests
from progress.spinner import MoonSpinner


def get_ascii_image(url: str, uid: str) -> str:
    """Create a temporal file read it, remove it and return the ascii art."""

    output: str = ""
    try:
        response: requests.Response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        file_name: str = f"/tmp/{uid}.jpeg"
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
    ):
        output = "[Cannot show image...]"

    return output


def loading(task: str, thread: threading.Thread) -> None:
    """Echo a task with a spinner."""

    with MoonSpinner(task + "...  ") as spinner:
        while thread.is_alive():
            sleep(0.1)
            spinner.next()
