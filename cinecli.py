"""Print cinema of Rosario information"""
from elcairo import ElCairo
from movie import Movie


show_image = True


def show_elcairo_movies() -> None:
    """Print el cairo movies"""
    elcairo: ElCairo = ElCairo()
    movies: list[Movie] = elcairo.get_movies("01", "26", "2023")
    movie: Movie

    for movie in movies:
        if show_image:
            movie.show_image()

        movie.print()


if __name__ == "__main__":
    show_elcairo_movies()
