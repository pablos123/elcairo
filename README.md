# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar, y de paso nunca la entiendo.

El programita lee un archivo .ics y hace cosas, nos vi.

Si alguien me quiere pasar algún link a un .ics de otros cines la mejor,
ya pensaré formas de agarrar de otros lados de última, no encontré mucho más.

## Dependencias

```terminal
pip install ics icalendar climage requests colorama click
```

## Run

```terminal
python3 cinecli.py --help
```

Tested in linux mint 21.

# Future
- [x] Make just one print for movie title
- [x] Take a date as parameter yo show only that day, defaulting to today's
- [x] Migrate to click framework 
- [ ] Error handling for dates without shows. 
- [ ] Understand a little more of what I'm retrieving with that .ics file
- [ ] Date sorting
- [ ] More error handling
- [ ] Testing
- [ ] Support other cinemas 
