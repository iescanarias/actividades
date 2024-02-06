#!/usr/bin/env python3

import os
import shutil
import json
import xml.etree.ElementTree as ET
import mimetypes

from __init__ import __icons_url__, __download_url__
from jinja2 import Environment, FileSystemLoader
from url_utils import normalize
from image_utils import html2png
from file_utils import get_valid_filename, is_newer_than
from pprint import pprint

ACTIVITY_FILE = 'activity.json'
SUPPORTED_TYPES = {
    'shortanswer':      'Respuesta corta',
    'multichoice':      'Opción múltiple',
    'truefalse':        'Verdadero/Falso',
    'matching':         'Emparejamiento',
    'cloze':            'Asociación',
    'ddimageortext':    'Arrastrar y soltar sobre una imagen',
    'ddmarker':         'Arrastrar y soltar marcadores',
    'essay':            'Ensayo',
    'numerical':        'Numérico'
}

mimetypes.init()

# read activity descriptor
def _read_activity(activity_path):
    # get full path to activity descriptor
    activity_file = os.path.join(activity_path, ACTIVITY_FILE)
    # read activity descriptor
    with open(activity_file, 'r') as json_file:
        content = json_file.read()
    # parse activity descriptor
    activity = json.loads(content)
    # add path to activity descriptor
    activity.update({
        'path': os.path.normpath(activity_path)
    })
    # if there are no files in activity descriptor, get all files in activity path
    if not 'files' in activity:
        activity['files'] = [ file for file in os.listdir(activity_path) if file.endswith('.xml') ]
    return activity

def _get_questions_from_file(activity_path, file):    
    # get full path to questions file and parse xml
    questions_file = os.path.join(activity_path, file)
    tree = ET.parse(questions_file)
    # search "question" tags under "quiz" tag
    types = {}
    for question in tree.findall('question'):
        # get question type
        type = question.get('type')
        # skip if question type is not supported
        if not type in SUPPORTED_TYPES:
            continue
        # check if question type is in types dictionary, and add it if not
        if not type in types:
            types[type] = []
        # add and count question
        types[type].append(question)
    # return questions
    return {
        'file': file,
        'url' : normalize(f'{__download_url__}/{activity_path}/{file}'),
        'types': types,
        'total': sum([len(type) for type in types.values()])
    }

# get questions from questions
def _get_questions(activity):
    all_questions = []
    for file in activity['files']:
        all_questions.append(_get_questions_from_file(activity['path'], file))
    return all_questions

# check if path is an activity
def _is_activity(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, ACTIVITY_FILE))

def _get_mimetype(file):
    return mimetypes.types_map[os.path.splitext(file.get('name'))[1]]

# get statement from question, processing attachments
def _get_statement(question):
    attachments = [ 
        {
            "name": file.get('name'),
            "path": file.get('path'),
            "image": f"data:{_get_mimetype(file)};{file.get('encoding')},{file.text}"
        } for file in question.find('questiontext').findall('file')
    ]
    statement = question.find('questiontext').find('text').text
    for attachment in attachments:
        statement = statement.replace(f"@@PLUGINFILE@@/{attachment.get("name")}", f"{attachment.get("image")}")
    return statement

# render question as image
def _render_image(question, destination_dir):
    type = question.get("type")
    # create question data
    question_data = {
        "type": question.get('type'),
        "name": question.find('name').find('text').text,
        "statement": _get_statement(question)
    }
    print(f"generando imagen {question_data.get("type")}: ", question_data.get("name"))
    # check question type
    match type:
        case "truefalse":
            question_data.update(
                { 
                    "answers": [
                        {
                            "text": answer.find('text').text,
                            "feedback": answer.find('feedback').find('text').text,
                            "fraction": float(answer.get('fraction'))
                        } for answer in question.findall('answer')
                    ]
                }
            )
        case "shortanswer":
            question_data.update(
                { 
                    "answers": [
                        {
                            "text": answer.find('text').text,
                            "feedback": answer.find('feedback').find('text').text,
                            "fraction": float(answer.get('fraction'))
                        } for answer in question.findall('answer')
                    ],
                    "first_answer": question.findall('answer')[0].find('text').text
                }
            )
        case _:
            return

    # render html from template
    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template(f'{question_data['type']}.template.html')
    html = template.render(question = question_data)

    # html to image
    image_filename = _get_valid_image_filename(destination_dir, question_data['name'])
    html2png(html, destination_dir, image_filename)

    return image_filename

def _get_valid_image_filename(path, name, index = 0):
    valid_name = get_valid_filename(name) + f'-{index}'
    if not os.path.exists(os.path.join(path, f'{valid_name}.png')):
        return f'{valid_name}.png'
    return _get_valid_image_filename(path, name, index + 1)

# generate images for questions
def _generate_images(activity, force = True):
    images_dir = os.path.join(activity['path'], "images")
    # if images directory exists and force is true, delete it
    if os.path.isdir(images_dir) and force:
        print("Sobreescribiendo imágenes existentes")
        shutil.rmtree(images_dir)
    # walk through all question files in activity
    for questions_file in activity['questions']:
        # create images dictionary
        images = {}
        # walk through all questions in file
        for type,questions in questions_file['types'].items():
            # walk through all questions of the same type
            for question in questions:
                # render image for question
                image_file = _render_image(question, images_dir)
                # if image was generated, add it to dictionary
                if image_file:
                    # check if question type is in images dictionary, and add it if not
                    if not type in images:
                        images[type] = []
                    # add image to dictionary
                    images[type].append(image_file)
        # add images to questions file
        questions_file['images'] = images

# create README.md files for all activities in path
def create_readmes(path, recursive, force):
    if not recursive:
        create_readme(path, force)
    else:
        for root, dirs, files in os.walk(path):
            if _is_activity(root):
                create_readme(root, force)

# create README.md file for activity (including some questions rendered as images)
def create_readme(activity_path, force = False):
    
    # check if path is an activity
    if not _is_activity(activity_path):
        raise Exception(f'{activity_path} no es una actividad')

    # read activity metadata
    activity = _read_activity(activity_path)

    # set readme and activity files
    readme_file = os.path.join(activity_path, 'README.md')

    # avoid creating README.md if it is not necessary
    if not force:
        # check if current README.md is newer than activity.json and question files, and skip if it is
        check_files = [ ACTIVITY_FILE ].extend(activity['files'])
        readme_is_old = True
        for file in check_files:
            file = os.path.join(activity_path, file)
            if is_newer_than(file, readme_file):
                readme_is_old = False
                break
        if readme_is_old:
            print(f'Ignorando actividad "{activity_path}". README.md es más reciente que {ACTIVITY_FILE} y que los archivos de preguntas {activity["questions"]}')
            return

    title(f'Creando README.md para actividad en {activity_path}...')

    # get stats and add to metadata
    questions = _get_questions(activity)
    activity['questions'] = questions

    # generate images
    _generate_images(activity, force)
    
    pprint(activity)

    # get script path
    module_path = os.path.dirname(os.path.realpath(__file__))

    # load and render template
    templates_path = os.path.join(module_path, 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template('README.activity.template.md')
    readme = template.render(activity = activity, SUPPORTED_TYPES = SUPPORTED_TYPES, icons_url = __icons_url__)

    # write to file
    print("generando README.md: ", readme_file)
    with open(readme_file, 'w') as outfile:
        outfile.write(readme)

def title(text):
    size = len(text)
    print()
    print("=" * size)
    print(text)
    print("=" * size)