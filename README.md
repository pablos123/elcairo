# cinecli

CLI para ver las películas que van a pasar en el cine El Cairo de Rosario.

La página tiene una interfaz muy poco intuitiva y nunca la entiendo, esto viene
a ayudarme siempre que quiero ver qué películas van a pasar.

## Quickstart
### Install

```terminal
pip install git+https://github.com/pablos123/cinecli.git && cinecli database populate
```
> Requires Python >=3.10.

### Run
```terminal
cinecli --help
```
**Update**
```terminal
pip install -f git+https://github.com/pablos123/cinecli.git
```

**Uninstall**
```terminal
pip uninstall cinecli
```

I thought of supporting other cinemas but none of them provides a clean web interface to even do some scrapping. I will not support other cinemas.

## Screenshots
```terminal
cinecli --images --urls day --date 16-02-2023
```
![some_movie](https://user-images.githubusercontent.com/52180403/219253983-7aac2088-0e9f-4818-9818-b5cbcdad3a0d.png)
