#!/usr/bin/env python3

import os
import sys
import json
import xml.etree.ElementTree as ET
from string import Template
from jinja2 import Environment, FileSystemLoader
from __init__ import __icons_url__

# read activity descriptor
def _read_metadata(activity_path):
    # read file
    activity_file = f'{activity_path}/activity.json'
    with open(activity_file, 'r') as json_file:
        data = json_file.read()
    # parse file
    return json.loads(data)

# get stats from questions
def _get_stats(activity_path, question_files):
    stats = {
        'shortanswer': { 'count': 0, 'icon': f'{__icons_url__}/shortanswer.svg', 'name': 'Respuesta corta'},
        'multichoice': { 'count': 0, 'icon': f'{__icons_url__}/multichoice.svg', 'name': 'Opción múltiple'},
        'truefalse': { 'count': 0, 'icon': f'{__icons_url__}/truefalse.svg', 'name': 'Verdadero/Falso'},
        'matching': { 'count': 0, 'icon': f'{__icons_url__}/matching.svg', 'name': 'Emparejamiento'},
        'cloze': { 'count': 0, 'icon': f'{__icons_url__}/cloze.svg', 'name': 'Asociación'},
        'ddimageortext': { 'count': 0, 'icon': f'{__icons_url__}/ddimageortext.svg', 'name': 'Arrastrar y soltar sobre una imagen'},
        'ddmarker': { 'count': 0, 'icon': f'{__icons_url__}/ddmarker.svg', 'name': 'Arrastrar y soltar marcadores'},
        'essay': { 'count': 0, 'icon': f'{__icons_url__}/essay.svg', 'name': 'Ensayo'},
        'numerical': { 'count': 0, 'icon': f'{__icons_url__}/numerical.svg', 'name': 'Numérico'},
    }
    for file in question_files:
        questions_file = f'{activity_path}/{file}'
        tree = ET.parse(questions_file)
        # search "question" tags under "quiz" tag
        for question in tree.findall('question'):
            # get question type
            question_type = question.get('type')
            # increment stats
            if question_type in stats: 
                stats[question_type]['count'] += 1 
    return stats

# check if path is an activity
def _is_activity(path):
    return os.path.isdir(path) and os.path.isfile(f'{path}/activity.json')

# get stats from questions
def _generate_images(activity_path, question_files):
    stats = {
        'shortanswer': False,
        'multichoice': False,
        'truefalse': { 'count': 0, 'icon': f'{__icons_url__}/truefalse.svg', 'name': 'Verdadero/Falso'},
        'matching': { 'count': 0, 'icon': f'{__icons_url__}/matching.svg', 'name': 'Asociación'},
    }
    for file in question_files:
        questions_file = f'{activity_path}/{file}'
        tree = ET.parse(questions_file)
        # search "question" tags under "quiz" tag
        for question in tree.findall('question'):
            # get question type
            question_type = question.get('type')
            # increment stats
            stats[question_type].count += 1            
    return stats

# create README.md file for activity
def create_readme(activity_path):

    # check if path is an activity
    if not _is_activity(activity_path):
        raise Exception(f'Error: {activity_path} no es una actividad')

    # read metadata
    metadata = _read_metadata(activity_path)

    # get stats and add to metadata
    stats = _get_stats(activity_path, metadata['questions'])
    metadata['stats'] = stats
    metadata['total'] = sum([x['count'] for x in stats.values()])

    # get script path
    module_path = os.path.dirname(os.path.realpath(__file__))

    # load and render template
    templates_path = os.path.join(module_path, 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template('README.template.md')
    readme = template.render(metadata = metadata)    

    # write to file
    with open(f'{activity_path}/README.md', 'w') as outfile:
        outfile.write(readme)
