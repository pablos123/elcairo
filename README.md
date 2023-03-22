# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar y de paso nunca la entiendo.

Esto viene a salvarme las papas porque cuando quiero me fijo que hay y organizo para ver una lipe.

## Quickstart
### Install

```terminal
sudo apt install python3.10-venv
python3 -m pip install --user pipx && python3 -m pipx ensurepath
pipx install git+https://github.com/pablos123/cinecli.git && cinecli database populate
```
> Requires Python >=3.10.

### Run
```terminal
cinecli --help
```

## Linux ecosystem
### Automate the database population
![Automate population!](https://github.com/pablos123/cinecli/wiki/Automate-population!)

### Desktop notifications
![Get notified!](https://github.com/pablos123/cinecli/wiki/Get-notified!)

## More info:
![cinecli wiki](https://github.com/pablos123/cinecli/wiki)

**Update**
```terminal
pipx uninstall cinecli && pipx install git+https://github.com/pablos123/cinecli.git && cinecli database populate
```

**Uninstall**
```terminal
pipx uninstall cinecli
```

**`pipx` docs**

https://pypa.github.io/pipx/installation/

I thought of supporting other cinemas but none of them provides a clean web interface to even do some scrapping. I will not support other cinemas.

## Screenshots
```terminal
cinecli --images --urls day --date 16-02-2023
```
![some_movie](https://user-images.githubusercontent.com/52180403/219253983-7aac2088-0e9f-4818-9818-b5cbcdad3a0d.png)
