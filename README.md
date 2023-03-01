# cinecli

Estoy yendo 2 veces por semana al Cairo y siempre voy a la página con una interfaz de mierda a fijarme
que es lo que van a pasar, y de paso nunca la entiendo.

## Quickstart
### Dependencies
```terminal
pip install ics icalendar climage requests colorama click arrow beautifulsoup4 progress
```

### Run
Populate the database:
```terminal
python3 cinecli.py database populate
```

Show movie shows:
```terminal
python3 cinecli.py --images --urls elcairo today
```

More commands:
```terminal
python3 cinecli.py --help
```

## Desktop notifications
![Get notified!](https://github.com/pablos123/cinecli/wiki/Get-notified!)

## Screenshots
```terminal
python3 cinecli.py --images elcairo day --date 16-02-2023
```
![scrotFeb15233631](https://user-images.githubusercontent.com/52180403/219253983-7aac2088-0e9f-4818-9818-b5cbcdad3a0d.png)

## More info:
![cinecli wiki](https://github.com/pablos123/cinecli/wiki)

Tested in linux mint 21. (python 3.10.6)
