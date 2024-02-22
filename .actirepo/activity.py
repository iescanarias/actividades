import os
import shutil
import json
import xml.etree.ElementTree as ET
import mimetypes
import io
import base64

from __init__ import __icons_url__, __download_url__
from jinja2 import Environment, FileSystemLoader
from url_utils import normalize, encode
from image_utils import html2png, htmlsize
from file_utils import slugify, is_newer_than, anchorify
from bs4 import BeautifulSoup
from pprint import pprint
from PIL import Image

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
ANCHORIFIED_TYPES = { key : anchorify(value) for key, value in SUPPORTED_TYPES.items() }

mimetypes.init()

def path_to_category(path):
    parts = path.split(os.sep)
    return [ part.capitalize() for part in parts ]

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
    activity['path'] = os.path.normpath(activity_path)
    # add category to activity descriptor
    activity['category'] = path_to_category(activity['path'])
    # if there are no files in activity descriptor, get all files in activity path
    if not 'files' in activity:
        activity['files'] = [ file for file in os.listdir(activity_path) if file.endswith('.xml') ]
    # if there is no limit in activity descriptor, set it to max int
    if not 'limit' in activity:
        activity['limit'] = 9999
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
            types[type] = [ question ]
        else:
            types[type].append(question)
    # return questions
    return {
        'file': file,
        'url' : normalize(f'{__download_url__}/{activity_path}/{file}'),
        'types': types,
        'total': sum([len(type) for type in types.values()])
    }

# get all questions from activity's question files
def _get_questions(activity):
    all_questions = []
    for file in activity['files']:
        all_questions.append(_get_questions_from_file(activity['path'], file))
    return all_questions

# check if path is an activity
def _is_activity(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, ACTIVITY_FILE))

# get mimetype from file
def _get_mimetype(file):
    if file is None:
        return None
    return mimetypes.types_map[os.path.splitext(file.get('name'))[1]]

# get image dimensions
def _get_image_size(file):
    if file is None:
        return None
    with Image.open(io.BytesIO(base64.decodebytes(bytes(file.text, "utf-8")))) as img:
        size = img.size
        return {
            "width": size[0],
            "height": size[1]
        }

# process attachments in question element
def _process_attachments(element):
    attachments = [ 
        {
            "name": file.get('name'),
            "path": file.get('path'),
            "type": _get_mimetype(file),
            "image": f"data:{_get_mimetype(file)};{file.get('encoding')},{file.text}"
        } for file in element.findall('file')
    ]
    html = BeautifulSoup(element.find('text').text, 'html.parser')
    for attachment in attachments:
        for img in html.find_all('img'):
            if f"@@PLUGINFILE@@{attachment.get('path')}{encode(attachment.get('name'))}" in img.get('src'):
                img['class'] = img.get('class', []) + ['img-fluid']
                img['src'] = attachment.get('image')
    return html.prettify()

# get size of text
def _drop_text_size(text):
    html = f"""
    <div style="box-sizing:border-box;">
        <div style="padding: 5px;box-sizing:border-box;background-color:rgb(220, 220, 220);border-radius:0px 10px 0px 0px;display:none;vertical-align:top;margin:5px;height: auto;width: auto;cursor:move;border:1px solid rgb(0, 0, 0);font:13px / 16.003px arial, helvetica, clean, sans-serif;">{text}</div>
        <div style="padding: 5px;user-select:none;box-sizing:border-box;background-color:rgb(220, 220, 220);border-radius:0px 10px 0px 0px;vertical-align:top;margin:5px;height: auto;width: auto;cursor:move;border:1px solid rgb(0, 0, 0);display:inline-block;font:13px / 16.003px arial, helvetica, clean, sans-serif;">{text}</div>
    </div>
    """
    size = htmlsize(html)
    return {
        "width": size[0],
        "height": size[1]
    }

# format bytes to human readable format
def _format_bytes(size):
    power = 2**10
    n = 0
    power_labels = { 0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB' }
    while size > power:
        size /= power
        n += 1
    return f"{size:.0f} {power_labels[n]}"

# render question as image
def _render_image(question, destination_dir):
    type = question.get("type")
    # create question data
    question_data = {
        "type": question.get('type'),
        "name": question.find('name').find('text').text,
        "statement": _process_attachments(question.find('questiontext'))
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
        case "multichoice":
            question_data.update(
                { 
                    "answers": [
                        {
                            "text": answer.find('text').text.replace('<p>', '<p style="margin:0px 0px 7.5px;margin-top:0px;margin-bottom:7.5px;box-sizing:border-box;">'),
                            "feedback": answer.find('feedback').find('text').text,
                            "fraction": float(answer.get('fraction')),
                            "letter": chr(65 + i).lower()
                        } for i, answer in enumerate(question.findall('answer'))
                    ],
                    "single": len([ answer for answer in question.findall('answer') if float(answer.get('fraction')) > 0 ]) == 1
                }
            )
        case "ddmarker":
            background_file = question.find('file')
            question_data.update(
                { 
                    "drags": [
                        {
                            "no": int(drag.find('no').text),
                            "text": drag.find('text').text
                        } for drag in question.findall('drag')
                    ],
                    "background": f"data:{_get_mimetype(background_file)};{background_file.get('encoding')},{background_file.text}",
                }
            )
        case "ddimageortext":
            background_file = question.find('file')
            question_data.update(
                { 
                    "background": f"data:{_get_mimetype(background_file)};{background_file.get('encoding')},{background_file.text}",
                    "drags": {
                        int(drag.find('no').text) : {
                            "no": int(drag.find('no').text),
                            "text": drag.find('text').text,
                            "type": "text" if drag.find('file') is None else "image",
                            "image": f"data:{_get_mimetype(drag.find('file'))};{drag.find('file').get('encoding')},{drag.find('file').text}" if drag.find('file') is not None else None,
                            "size": _drop_text_size(drag.find('text').text) if drag.find('file') is None else _get_image_size(drag.find('file')),
                            "draggroup": int(drag.find('draggroup').text)
                        } for drag in question.findall('drag')
                    },
                    "drops": {
                        int(drop.find('choice').text) : {
                            "no": int(drop.find('no').text),
                            "text": drop.find('text').text,
                            "choice": int(drop.find('choice').text),
                            "xleft": int(drop.find('xleft').text),
                            "ytop": int(drop.find('ytop').text)
                        } for drop in question.findall('drop')
                    }
                }
            )
            # add drag sizes to drops
            for choice, drop in question_data['drops'].items():
                drop['size'] = question_data['drags'][choice]['size']
            # group drags by draggroup
            question_data['draggroups'] = {}
            for drag in question_data['drags'].values():
                if not drag['draggroup'] in question_data['draggroups']:
                    question_data['draggroups'][drag['draggroup']] = [ drag['no'] ]
                else:
                    question_data['draggroups'][drag['draggroup']].append(drag['no'])
            # get max width and height for each draggroup
            question_data['draggroups_size'] = {}
            for draggroup, drags in question_data['draggroups'].items():
                max_width = 0
                max_height = 0
                for drag_no in drags:
                    drag_size = question_data['drags'][drag_no]['size']
                    if drag_size['width'] > max_width:
                        max_width = drag_size['width']
                    if drag_size['height'] > max_height:
                        max_height = drag_size['height']
                question_data['draggroups_size'][draggroup] = {
                    "width": max_width,
                    "height": max_height
                }
        case "essay":
            question_data.update(
                { 
                    "editor": question.find('responseformat').text != 'noinline',
                    "response_lines": int(question.find('responsefieldlines').text),
                    "file_upload": int(question.find('attachments').text) > 0,
                    "max_size": _format_bytes(int(question.find('maxbytes').text)) if int(question.find('maxbytes').text) > 0 else "Por defecto",
                    "max_files": int(question.find('attachments').text),
                    "file_types": question.find('filetypeslist').text.split(',') if not question.find('filetypeslist').text is None else []
                }
            )        
        case _:
            return
        
    # render html from template
    templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template(f'{question_data['type']}.template.html')
    html = template.render(question = question_data, icons_url = __icons_url__)

    # html to image
    image_filename = _get_valid_image_filename(destination_dir, question_data['name'])
    html2png(html, destination_dir, image_filename)

    # writes html to file
    #html_filename = image_filename.replace('.png', '.html')
    #with open(os.path.join(destination_dir, html_filename), 'w') as outfile:
    #    outfile.write(html)
    
    return image_filename

def _get_valid_image_filename(path, name, index = 0):
    valid_name = slugify(name) + f'_{index}'
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
            count = 0
            # walk through all questions of the same type
            for question in questions:
                # render image for question
                image_file = _render_image(question, images_dir)
                # if image was generated, add it to dictionary
                if image_file:
                    count += 1
                    # check if question type is in images dictionary, and add it if not
                    if not type in images:
                        images[type] = [ image_file ]
                    else:
                        images[type].append(image_file)
                if count >= activity['limit']:
                    break
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

    # get script path
    module_path = os.path.dirname(os.path.realpath(__file__))

    # load and render template
    templates_path = os.path.join(module_path, 'templates')
    env = Environment(loader = FileSystemLoader(templates_path, encoding='utf8'))
    template = env.get_template('README.activity.template.md')
    readme = template.render(activity = activity, SUPPORTED_TYPES = SUPPORTED_TYPES, ANCHORIFIED_TYPES = ANCHORIFIED_TYPES, icons_url = __icons_url__)

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