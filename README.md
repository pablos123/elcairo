# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar, y de paso nunca la entiendo.

## Dependencias

```terminal
pip install ics icalendar climage requests colorama click arrow beautifulsoup4
```

## Run

```terminal
python3 cinecli.py --help
```

Tested in linux mint 21. (python 3.10.6)

## More info
Cada cine es un comando y un grupo de comandos de click.

Cada cine tendrá su API, cada API, cuando se consulten, devolverá un json del tipo:

```terminal
{
  "14896-1676068200-1676068200@elcairocinepublico.gob.ar": {
    "name": "AFTERSUN",
    "begin": "10-02-2023 22:30:00 (en 3 días)",
    "urls": [
      "https://elcairocinepublico.gob.ar/pelicula-de-sala/aftersun/2023-02-10/",
      "https://elcairocinepublico.gob.ar/pelicula-de-sala/aftersun/"
    ],
    "extra_info": {
      "synopsis": "Sophie reflexiona sobre la alegría compartida y la melancolía privada de unas vacaciones que hizo con su padre 20 años atrás. Los recuerdos reales e imaginarios llenan los espacios entre las imágenes mientras intenta reconciliar al padre que conoció con el hombre que no conoció.",
      "data": {
        "director": "Charlotte Wells ",
        "cast": "Paul Mescal, Francesca Corio, Celia Rowlson-Hall, Kayleigh Coleman, Sally Messham, Harry Perdios, Ethan Smith ",
        "genre": "Drama",
        "duration": "98’",
        "origin": "Estados Unidos, Reino Unido ",
        "year": "2022 ",
        "age": "SAM13 (Para Mayores de 13 años) "
      },
      "cost": "$250\nEst. y Jub $200"
    },
    "image_url": "https://elcairocinepublico.gob.ar/wp-content/uploads/2023/01/Aftersun-01.jpg"
  },
  "14855-1676061000-1676061000@elcairocinepublico.gob.ar": {
    "name": "BAHÍA BLANCA",
    "begin": "10-02-2023 20:30:00 (en 3 días)",
    "urls": [
      "https://elcairocinepublico.gob.ar/pelicula-de-sala/bahia-blanca/2023-02-10/",
      "https://elcairocinepublico.gob.ar/pelicula-de-sala/bahia-blanca/"
    ],
    "extra_info": {
      "synopsis": "Mario, docente universitario, utiliza una investigación sobre el escritor Ezequiel Martínez Estrada para huir de su pasado. Establecido en Bahía Blanca, el lugar parece ser ideal para el olvido, pero un encuentro con un viejo amigo desencadena el peor de los peligros.",
      "data": {
        "director": "Rodrigo Caprotti  ",
        "cast": "Guillermo Pfening, Elisa Carricajo, Javier Drolas, Marcelo Subiotto, Ailin Salas, Violeta Palukas, Julia Martínez Rubio ",
        "genre": "Drama",
        "duration": "82'",
        "origin": "Argentina ",
        "year": "2020 ",
        "age": "SAM16 (Para Mayores de 16 años) "
      },
      "cost": "$250\nEst. y Jub. $200"
    },
    "image_url": "https://elcairocinepublico.gob.ar/wp-content/uploads/2023/01/Bahía-Blanca-04.jpg"
  },
  "14880-1676052000-1676052000@elcairocinepublico.gob.ar": {
    "name": "HOLY SPIDER",
    "begin": "10-02-2023 18:00:00 (en 2 días)",
    "urls": [
      "https://elcairocinepublico.gob.ar/pelicula-de-sala/holy-spider/2023-02-10/",
      "https://elcairocinepublico.gob.ar/pelicula-de-sala/holy-spider/"
    ],
    "extra_info": {
      "synopsis": "Irán, 2001. Una periodista investiga una serie de femicidios en los barrios peligrosos de la ciudad santa de Mashhad. Descubre que las autoridades locales no trabajan en resolver los casos. Los crímenes son obra de un hombre que ataca a prostitutas y asegura purificar la ciudad de sus pecados. ",
      "data": {
        "director": "Ali Abbasi ",
        "cast": "Zar Amir-Ebrahimi, Mehdi Bajestani, Arash Ashtiani, Forouzan Jamshidnejad, Mesbah Taleb, Alice Rahimi, Sara Fazilat, Sina Parvaneh, Nima Akbarpour, Firouz Agheli ",
        "genre": "Drama, Suspenso",
        "duration": "117'",
        "origin": "Dinamarca ",
        "year": "2022 ",
        "age": "SAM16 (Para Mayores de 16 años) "
      },
      "cost": "$250\nEst. y Jub. $200"
    },
    "image_url": "https://elcairocinepublico.gob.ar/wp-content/uploads/2023/01/Holy-Spider-01.jpeg"
  }
}
```
En este momento la API del cairo está impletada leyendo archivos .ics que El Cario provee en la página.
De otros cines todavía no encontré nada parecido.
Tal vez use un crawler en algún momento con alguno para ver que onda y vea si puedo resolver algo.

Si alguien encuentra algún archivo .ics de otros cines la mejor.

# Screenshots

```terminal
python3 cinecli.py --images elcairo day --date 09-02-2023
```
![scrotFeb07021701](https://user-images.githubusercontent.com/52180403/217154847-96c0583c-9356-4e2d-bf7d-cbb785666479.png)

```terminal
python3 cinecli.py --urls --no_extra_info elcairo upcoming
```
![scrotFeb07021901](https://user-images.githubusercontent.com/52180403/217155123-2cce5075-0047-483f-bf32-f329959552da.png)

# Future
## General
- [X] Migrate to click framework.
- [X] Make the printer agnostic to the cinema.
- [X] Decide how to 'Standarize' the data in the extra info.
- [X] Testing, error handling. (Overall it works, if nothing breaks I'll do nothing)
- [ ] Api documentation.
- [ ] virtualenv?
- [ ] Populate a sqlite db, fetching the .ics files takes too long.
- [ ] Support notifications.
- [ ] Support other cinemas.

## ElCairo
- [X] Error handling for dates without shows.
- [X] Understand a little more of what I'm retrieving with that .ics file.
- [X] Date sorting (Default: closest shows last).
- [X] Crawl the info url to get more information in the API, e.g the duration of the film.
