# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar, y de paso nunca la entiendo.

## Dependencies

```terminal
pip install ics icalendar climage requests colorama click arrow beautifulsoup4
```

## Run

Primero populamos la database
```terminal
python3 cinecli.py database populate
```

Despues puedo ver las pelis de hoy o las de algún día en particular.

```terminal
python3 cinecli.py --images --urls elcairo today
```

```terminal
python3 cinecli.py --images --urls elcairo day --date 16-02-2023
```

Más info
```terminal
python3 cinecli.py --help
```

Tested in linux mint 21. (python 3.10.6)

### Handy

## More info
Cada cine es un comando y un grupo de comandos de click.

Cada cine tendrá su API, cada API, cuando se consulte, devolverá un json del tipo:

```json
{
  "<movie/event identifier>": {
    "name": "<name of the movie>",
    "begin": "<string that shows when the movie start>",
    "urls": [ "<list of urls for more info>", "<url1>" ],
    "synopsis": "<movie synopsis>",
    "director": "<director>",
    "cast": "<cast>",
    "genre": "<genre>",
    "duration": "<duration>",
    "origin": "<origin>",
    "year": "<year>",
    "age": "<age restriction>",
    "cost": "<cost>",
    "image_url": "<image url to render it in the terminal>"
  }
}
```

### Example
https://github.com/pablos123/cinecli/blob/main/api_example.md

En este momento la API del cairo está impletada leyendo archivos .ics que El Cario provee en la página.
De otros cines no encontré nada parecido, así que voy a scrapear las páginas.

# Screenshots

```terminal
python3 cinecli.py --urls --images elcairo upcoming
```
![scrotFeb07193215](https://user-images.githubusercontent.com/52180403/217381710-9058e282-6213-42d6-82f3-16e1b4fecaea.png)

# Future
## General
- [X] Migrate to click framework.
- [X] Make the printer agnostic to the cinema.
- [X] Decide how to 'Standarize' the data in the extra info.
- [X] Testing, error handling. (Overall it works, if nothing breaks I'll do nothing)
- [X] Populate a sqlite db, fetching the .ics files takes too long.
- [ ] Api documentation.
- [ ] virtualenv?
- [ ] Support notifications.
- [ ] Support other cinemas.

## ElCairo
- [X] Error handling for dates without shows.
- [X] Understand a little more of what I'm retrieving with that .ics file.
- [X] Date sorting (Default: closest shows last).
- [X] Scrap the info url to get more information in the API, e.g the duration of the film.

## Showcase
- [ ] Scrap tf out.

## Arteón
- [ ] Scrap tf out.

## Monumental
- [ ] Scrap tf out.
