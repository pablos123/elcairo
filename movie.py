"""An event is always a movie in this program"""
import re
import shutil

from colorama import Fore, Back, Style
import climage
from ics import Event
import requests


def check_mime(mime: str) -> bool:
    """
    Check if the extra info is a 'file' and if the mime type is correct
    The regex is working just for this type of url, let's call it 'cairo' type,
    I don't have others .ics for now and I'll support just Cine El Cairo for now
    """
    return re.search("^ATTACH;FMTTYPE=image/(:?jpeg|png|webp)$", mime)


def get_image(extra_info) -> str:
    """
    Get the image url if the mime type is a valid image mime type
    And is supported by climage
    """
    image_url: str = ""
    for item in extra_info:
        splitted_item_str: list[str] = item.__str__().split(":")
        if check_mime(splitted_item_str[0]):
            image_url = splitted_item_str[1] + ":" + splitted_item_str[2]
    return image_url


class Movie:
    """A movie is event information with methods to print information"""

    def __init__(self, event: Event):
        # To use it in the temporal image name
        self.uid: str = event.uid

        self.name: str = event.name
        self.info_url: str = event.url

        self.begin: str = event.begin.format("DD-MM-YYYY HH:mm:ss")
        self.begin_humanize: str = event.begin.humanize(locale="es")

        self.image_url = get_image(event.extra)

    def print(self) -> None:
        """Print the movie information"""

        print(f"{Fore.GREEN}Nombre: {Style.RESET_ALL} {self.name}")

        print(
            Fore.RED
            + "Empieza: "
            + Style.RESET_ALL
            + self.begin
            + " ("
            + self.begin_humanize
            + ")"
        )

        print(Fore.YELLOW + "Mas info: " + Style.RESET_ALL + self.info_url)

        print("\n")

    def show_image(self) -> None:
        """Creates a temporal file reads it and shows it"""

        try:
            if self.image_url:
                response = requests.get(self.image_url, stream=True)
                if response.status_code == 200:
                    file_name = f"/tmp/{self.uid}.jpeg"
                    with open(file_name, "wb") as image_file:
                        shutil.copyfileobj(response.raw, image_file)
                        ascii_image = climage.convert(file_name)
                        print(ascii_image)
                else:
                    print("")
            else:
                print("")

        except OSError as _:
            print("")
