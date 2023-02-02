# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar, y de paso nunca la entiendo.

## Dependencias

```terminal
pip install ics icalendar climage requests colorama click
```

## Run

```terminal
python3 cinecli.py --help
```

Tested in linux mint 21.

## More info
Cada cine es un comando y un grupo de comandos de click.

Cada cine tendrá su API, cada API, cuando se consulten, devolverá un json del tipo:

```terminal
{
  <otros eventos>
  ...
  "<id unico del evento>": {
    "name": "BAHÍA BLANCA",
    "begin": "02-02-2023 20:30:00 (en 19 horas)",
    "url": "https://<sarasa>",
    "image_url": "https://<sarasa>"
  }
  ...
  <otros eventos>
}
```
En este momento la API del cairo está impletada leyendo archivos .ics que El Cario provee en la página.
De otros cines todavía no encontré nada parecido.
Tal vez use un crawler en algún momento con algúno para ver que onda y vea si puedo resolver algo.

Si alguien encuentra algún archivo .ics de otros cines la mejor.


# Future
## General
- [X] Migrate to click framework
- [ ] Populate a sqlite db, fetching the .ics files takes too long.
- [ ] Testing
- [ ] Support other cinemas

## ElCairo
- [X] Error handling for dates without shows.
- [X] Understand a little more of what I'm retrieving with that .ics file
- [X] Date sorting
- [X] Crawl the info url to get more information in the API, e.g the duration of the film
