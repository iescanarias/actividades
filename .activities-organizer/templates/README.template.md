---
title: {{ metadata.name }}
author: {{ metadata.author.name }} ({{ metadata.author.email }})
---

# {{ metadata.name }}

{% if metadata.difficulty == 'hard' %}
![Dificultad](https://img.shields.io/badge/Dificultad-Alta-red)
{% elif metadata.difficulty == 'medium' %}
![Dificultad](https://img.shields.io/badge/Dificultad-Media-yellow)
{% else %}
![Dificultad](https://img.shields.io/badge/Dificultad-Baja-green)
{% endif %}

{{ metadata.description }}

## Contenido

Preguntas disponibles en esta actividad:

|   | Tipo              | Cantidad                   |
| - | ----------------- | -------------------------- |
{% for type in metadata.stats %}{% set question = metadata.stats[type] %}{% if question.count > 0 %}| ![]({{ question.icon }}) | {{ question.name }} | {{ question.count }} |
{% endif %}{% endfor %}|   | **TOTAL**         | {{ metadata.total }} |

## Descargas

{% for qu in question_urls %}- [{{ qu.file }}]({{ qu.url }})
{% endfor%}

## Ejemplos

> renderizar aquí algunas preguntas