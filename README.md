# cinecli

CLI para ver las películas que van a pasar en el cine El Cairo de Rosario.

La página tiene una interfaz muy poco intuitiva y nunca la entiendo, esto viene
a ayudarme siempre que quiero ver qué películas van a pasar.

## Quickstart
### Install
```
pip install git+https://github.com/pablos123/cinecli.git && cinecli database populate
```
> Requires Python >=3.10.

### Run
```
cinecli --help
```

I thought of supporting other cinemas but none of them provides a clean web interface to even do some scrapping. I will not support other cinemas.

## Screenshots
```
cinecli --no_separator --no_extra_info weekend
```
![image](https://github.com/pablos123/cinecli/assets/52180403/7bfa9e9b-5ff0-4172-b6ea-997f9c953b66)

```
cinecli --images day --date 09-12-2023
```
![image](https://github.com/pablos123/cinecli/assets/52180403/2b7a24fd-2e0b-4962-af66-66f03433f42a)

```
cinecli --image_urls --urls week
```
![image](https://github.com/pablos123/cinecli/assets/52180403/89484244-a826-4fa0-8e58-76efb732eeff)
