#!/usr/bin/env python3


import os
import json
import xml.etree.ElementTree as ET

from __init__ import __icons_url__, __raw_url__
from jinja2 import Environment, FileSystemLoader
from urllib.parse import quote
from time_utils import is_newer_than

# read activity descriptor
def _read_metadata(activity_path):
    # read file
    activity_file = os.path.join(activity_path, 'activity.json')
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
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, 'activity.json'))

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

def create_readmes(path, recursive, force):
    path = os.path.normpath(path)
    if _is_activity(path):
        create_readme(path, force)
    if recursive:
        for file in os.listdir(path):
            file = os.path.normpath(os.path.join(path, file))
            if os.path.isdir(file) and not file.startswith('.'):
                create_readmes(file, recursive, force)

# create README.md file for activity
def create_readme(activity_path, force = False):
    
    # check if path is an activity
    if not _is_activity(activity_path):
        raise Exception(f'Error: {activity_path} no es una actividad')

    # read metadata
    metadata = _read_metadata(activity_path)

    # set readme and activity files
    readme_file = os.path.join(activity_path, 'README.md')
    activity_file = os.path.join(activity_path, 'activity.json')

    if not force:
        # check if current README.md is newer than activity.json and question files, and skip if it is
        check_files = [ os.path.basename(activity_file) ]
        check_files.extend(metadata['questions'])
        readme_is_old = True
        for file in check_files:
            file = os.path.join(activity_path, file)
            if is_newer_than(file, readme_file):
                readme_is_old = False
                break
        if readme_is_old:
            print(f'Ignorando actividad "{activity_path}". README.md es más reciente que activity.json y que los archivos de preguntas {metadata["questions"]}')
            return

    print('Creando README.md para actividad en', activity_path, '...')

    # get stats and add to metadata
    stats = _get_stats(activity_path, metadata['questions'])
    metadata['stats'] = stats
    metadata['total'] = sum([x['count'] for x in stats.values()])

    # get script path
    module_path = os.path.dirname(os.path.realpath(__file__))

    # question download urls
    question_urls = []
    for question in metadata['questions']:
        question_file = quote(os.path.join(activity_path, question).replace('\\', '/'))
        question_url = {
            "file": question,
            "url" : f'{__raw_url__}/{question_file}'
        }
        question_urls.append(question_url)

    # load and render template
    templates_path = os.path.join(module_path, 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template('README.template.md')
    readme = template.render(metadata = metadata, question_urls = question_urls)

    # write to file
    with open(readme_file, 'w') as outfile:
        outfile.write(readme)
