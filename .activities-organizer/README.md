# Activities Organizer

Aplicación Python que organiza un repositorio con preguntas de Moodle en formato XML.

## ¿Cómo funciona?

Busca las carpetas que contengan el fichero `activity.json` y la considera una actividad. Luego, a partir de los metadatos del fichero `activity.json` y el fichero de preguntas en formato Moodle XML (`questions`), genera un fichero `README.md` con la descripción de la actividad, un enlace de descarga a los ficheros de preguntas XML y 1 captura de pantalla por cada tipo de pregunta.

> Las capturas de pantalla se guardan en el directorio `images`.

Ejemplo de `activity.json`:

```json
{
    "name": "El microprocesador",
    "description": "Preguntas tipo test, de asociación y de respuesta corta sobre el microprocesador",
    "difficulty": "hard",
    "author": {
        "name": "Francisco Vargas Ruiz",
        "email": "fvarrui@canariaseducacion.es"
    },
    "questions": [ "questions.xml" ]
}
```

## ¿Cómo lo uso?

Debes ubicarte en el directorio raíz del repositorio de preguntas.

### Instalar las dependencias

La primera vez es necesario instalar las dependencias:

```bash
pip install -r requirements.txt
```

### Mostrar la ayuda

```bash
$ python .activities-organizer --help
usage: python .activities-organizer [-h] [-v] [-l] [-c [RUTA]] [--readme RUTA] [-r]

Organizador de actividades

options:
  -h, --help            show this help message and exit
  -v, --version         Mostrar versión
  -l, --list            Listar actividades
  -c [RUTA], --create [RUTA]
                        Crear los metadatos de la actividad en el directorio especificado (o directorio actual si no se proporciona)
  --readme RUTA         Crear README.md para actividad en el directorio especificado
  -r, --recursive       Buscar actividades recursivamente en subdirectorios. Se puede combinar con --readme y --create
```

### Listar las actividades del repositorio

Muestra un listado de todas las actividades disponibles en el repositorio, incluyendo estadísticas del número de preguntas por tipo.

### Generar el README de la actividad

Ejecuta el siguiente comando para generar el fichero `README.md` en el directorio indicado:

```bash
python [-X utf8] .activity-organizer [--recursive] --readme RUTA
```

Si se especifica la opción `--recursive`, la búsqueda de actividades será recursiva a partir de la `RUTA` indicada, por lo que si se indica el directorio raíz del repo, se generarán los ficheros README de todas las actividades. 

Si el fichero README existe y es anterior a los cambios realizados en la actividad (metadatos o ficheros de preguntas XML), se volverán a generar el README  y las imágenes. En caso contrario, no se harán cambios.

> Es necesario incluir la opción `-X utf8` en Windows debido a problemas en la codificación.

### Crear los metadatos

Es posible generar un fichero de metadatos `activity.json` para las actividades, que luego sólo será necesario rellenar:

```bash
python .activity-organizer [--recursive] -c [RUTA] 
```

Si no se especifica la `RUTA`, el fichero se genera en el directorio actual.

Si se especifica la opción `--recursive`, la aplicación buscará ficheros XML de forma recursiva a partir de la `RUTA` , considerándolos ficheros de preguntas, y generará en el mismo directorio el fichero `activity.json` en caso de que no exista.

#### Ejemplo

Suponiendo que el directorio de la actividad se llame `cableado` y que exista el fichero de preguntas `preguntas-cableado.xml`, el fichero `activity.json` generado sería:

```json
{
    "name": "Cableado",
    "description": "<descripción de la actividad>",
    "difficulty": "easy|medium|hard",
    "author": {
        "name": "<tu nombre>",
        "email": "<tu email>"
    },
    "questions": [ "preguntas-cableado.xml" ]
}
```

## Información relacionada

### Plantillas

Las plantillas utilizadas para generar el README y el HTML de las preguntas para luego renderizarlas en PNG se encuentran en el directorio `templates`.

#### Vista previa de las preguntas en HTML

El código HTML de la vista previa de las preguntas se extrajo de Moodle utilizando [PageRip](https://chromewebstore.google.com/detail/pagerip-html-+-css-extrac/bkahkocegdkgicmmfpkoeipjmjaeohfn), una extensión de Google Chrome que permite extraer fragmentos de páginas HTML incluyendo el CSS en línea.
