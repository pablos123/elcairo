# cinecli

CLI que muestra las películas que van a pasar en el cine El Cairo de Rosario.

La página web tiene una interfaz muy poco intuitiva y nunca la entiendo.

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
(Pensé en soportar otros cines de la ciudad pero ninguno tiene siquiera una página relativamente prolija como para hacer scrapping. No voy a soportar otros cines.)

## Screenshots
```
cinecli --images day --date 09-12-2023
```
![image](https://github.com/pablos123/cinecli/assets/52180403/2b7a24fd-2e0b-4962-af66-66f03433f42a)

```
cinecli --image_urls --urls week
```
![image](https://github.com/pablos123/cinecli/assets/52180403/89484244-a826-4fa0-8e58-76efb732eeff)
