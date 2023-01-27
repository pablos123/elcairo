"""Print Rosario's cinemas shows information"""

from colorama import Back, Fore, Style

from elcairo import ElCairo
from movie import Movie

show_image = True


def show_movies(movies: list[Movie]) -> None:
    """
    Print a list of movies
    """
    for movie in movies:
        print(f"{Back.WHITE}{Fore.BLACK}{80*'-'}\n")
        if show_image:
            movie.show_image()
        movie.print()


def elcairo_movies() -> None:
    """
    Print el cairo movie shows
    """
    elcairo: ElCairo = ElCairo("01", "01", "2023")
    movies: list[Movie] = elcairo.get_movies()

    show_movies(movies)


if __name__ == "__main__":
    # Each cinema will have a different way to get the information I think.
    # I cannot assume some sort of protocol, so each cinema will have a class
    # to gather the information
    elcairo_movies()
