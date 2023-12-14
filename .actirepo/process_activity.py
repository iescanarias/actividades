#!/usr/bin/env python3


import os
import shutil
import json
import xml.etree.ElementTree as ET

from __init__ import __icons_url__, __raw_url__
from jinja2 import Environment, FileSystemLoader
from urllib.parse import quote
from time_utils import is_newer_than
from image_utils import html2png
from file_utils import get_valid_filename

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

def _render_image(question, destination_dir):
    type = question.get("type")
    question_data = {}
    match type:
        case "truefalse":
            print("generando imagen truefalse")
            question_data = {
                "type": question.get('type'),
                "name": question.find('name').find('text').text,
                "statement": question.find('questiontext').find('text').text,
                "answers": [
                    {
                        "text": a.find('text').text,
                        "feedback": a.find('feedback').find('text').text,
                        "fraction": float(a.get('fraction'))
                    } for a in question.findall('answer')
                ]
            }
        #case "shortanswer":
        #    print("generando imagen shortanswer")
        case _:
            #print("Tipo de pregunta desconocida", type)
            return

    # render html from template
    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template(f'{question_data['type']}.template.html')
    html = template.render(question = question_data)

    # html to image
    image_file = get_valid_filename(f'{question_data['name']}.png')
    html2png(html, destination_dir, image_file)

# get stats from questions
def _generate_images(activity_path, question_files, force = True):
    images_dir = os.path.join(activity_path, "images")
    # if images directory exists and force is true, delete it
    if os.path.isdir(images_dir) and force:
        print("Sobreescribiendo imágenes existentes")
        shutil.rmtree(images_dir)
    # walk through all question files
    for file in question_files:
        questions_file = os.path.join(activity_path, file)
        # parse Moodle XML file
        tree = ET.parse(questions_file)
        # search "question" tags under "quiz" tag
        for question in tree.findall('question'):
            # convertir a texto
            print(ET.tostring(question, encoding='unicode', method='xml'))
            # render image for question
            _render_image(question, images_dir)

def create_readmes(path, recursive, force):
    if not recursive:
        create_readme(path, force)
    else:
        for root, dirs, files in os.walk(path):
            if _is_activity(root):
                create_readme(root, force)

# create README.md file for activity
def create_readme(activity_path, force = False):
    
    # check if path is an activity
    if not _is_activity(activity_path):
        raise Exception(f'{activity_path} no es una actividad')

    # read metadata
    metadata = _read_metadata(activity_path)

    # set readme and activity files
    readme_file = os.path.join(activity_path, 'README.md')
    activity_file = os.path.join(activity_path, 'activity.json')

    # avoid creating README.md if it is not necessary
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
    template = env.get_template('README.activity.template.md')
    readme = template.render(metadata = metadata, question_urls = question_urls)

    # write to file
    with open(readme_file, 'w') as outfile:
        outfile.write(readme)

    # generate images
    _generate_images(activity_path, metadata['questions'], force)

# get number of questions
def get_num_questions(activity_path):
    metadata = _read_metadata(activity_path)
    stats = _get_stats(activity_path, metadata['questions'])
    total = sum([stat['count'] for stat in stats.values()])
    return total

