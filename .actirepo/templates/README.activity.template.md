---
title: {{ activity.name }}
author: {{ activity.author.name }} ({{ activity.author.email }})
---

# {{ activity.name }}

{% if activity.difficulty == 'hard' %}
![Dificultad](https://img.shields.io/badge/Dificultad-Alta-red)
{% elif activity.difficulty == 'medium' %}
![Dificultad](https://img.shields.io/badge/Dificultad-Media-yellow)
{% elif activity.difficulty == 'easy' %}
![Dificultad](https://img.shields.io/badge/Dificultad-Baja-green)
{% else %}
![Dificultad](https://img.shields.io/badge/Desconocida-gray)
{% endif %}

{{ activity.description }}

## Contenido

Ficheros de preguntas disponibles en esta actividad:

{% for questions_file in activity.questions %}
### [{{questions_file.file}}]({{questions_file.url}})

|   | Tipo              | Cantidad                   |
| - | ----------------- | -------------------------- |
{% for type,questions in questions_file.types.items() %}| ![{{ type }}]({{ icons_url }}/{{ type }}.svg) | [{{ SUPPORTED_TYPES[type] }}](#{{ ANCHORIFIED_TYPES[type] }}) | {{ questions|length }} |
{% endfor %}|   | **TOTAL**         | {{ questions_file.total }} |

{% for type,images in questions_file.images.items() %}
#### {{SUPPORTED_TYPES[type]}}
{% if images|length > 0 %}
{% for i in range(0, [images|length, activity.limit]|min) %}
![{{images[i]}}](images/{{images[i]}})
{% endfor %}
{% else %}
Imágenes aún no disponibles.
{% endif %}
{% endfor %}

{% endfor %}
