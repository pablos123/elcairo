"""
Setup function
"""

from setuptools import setup

from cinecli.version import __version__

setup(
    name="cinecli",
    version=__version__,
    description="Cli program that shows movies available for watching in El Cario cinema",
    author="Pablo Saavedra",
    url="https://github.com/pablos123/cinecli",
    author_email="pablosaavedra123@gmail.com",
    py_modules=[
        "cinecli.main",
        "cinecli.commands",
        "cinecli.commands.version",
        "cinecli.commands.elcairo",
        "cinecli.commands.database",
        "cinecli.commands.lib",
        "cinecli.commands.lib.movie_printer",
        "cinecli.commands.lib.database",
        "cinecli.api",
        "cinecli.api.elcairo",
    ],
    python_requires=">=3.10",
    install_requires=[
        "ics",
        "icalendar",
        "climage",
        "requests",
        "colorama",
        "click",
        "arrow",
        "beautifulsoup4",
        "progress",
    ],
    entry_points={
        "console_scripts": [
            "cinecli = cinecli.main:main",
        ]
    },
)
