# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar y de paso nunca la entiendo.

## Quickstart
### Install
```terminal
python3 -m pip install --user pipx && python3 -m pipx ensurepath && pipx install git+https://github.com/pablos123/cinecli.git
```

Requires Python >=3.10.

### Run
Populate the database:
```terminal
cinecli database populate
```

Print movie shows:
```terminal
cinecli --images --urls elcairo today
```

More commands:
```terminal
cinecli --help
```

## Linux ecosystem
### Automate the database population

### Desktop notifications
![Get notified!](https://github.com/pablos123/cinecli/wiki/Get-notified!)

## Screenshots
```terminal
python3 cinecli.py --images --urls elcairo day --date 16-02-2023
```
![some_movie](https://user-images.githubusercontent.com/52180403/219253983-7aac2088-0e9f-4818-9818-b5cbcdad3a0d.png)

## More info:
![cinecli wiki](https://github.com/pablos123/cinecli/wiki)
