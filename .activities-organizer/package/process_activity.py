#!/usr/bin/env python3

import os
import sys
import json
import xml.etree.ElementTree as ET
from string import Template
from jinja2 import Environment, FileSystemLoader

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
        'shortanswer': 0,
        'multichoice': 0,
        'truefalse': 0,
        'matching': 0,
    }
    for file in question_files:
        questions_file = f'{activity_path}/{file}'
        tree = ET.parse(questions_file)
        # search "question" tags under "quiz" tag
        for question in tree.findall('question'):
            # get question type
            question_type = question.get('type')
            # increment stats
            stats[question_type] += 1            
    return stats

# check if path is an activity
def _is_activity(path):
    return os.path.isdir(path) and os.path.isfile(f'{path}/activity.json')    

# create README.md file for activity
def create_readme(activity_path):
    # check if path is an activity
    if not _is_activity(activity_path):
        raise Exception(f'error: {activity_path} is not an activity')
    # read metadata
    metadata = _read_metadata(activity_path)
    # get stats
    stats = _get_stats(activity_path, metadata['questions'])
    # get script path
    module_path = os.path.dirname(os.path.realpath(__file__))
    # load template
    with open(f'{module_path}/../templates/README.template.md', 'r') as template_file:
        template = Template(template_file.read())
    # substitute values in template
    data = {
        'name': metadata['name'],
        'description': metadata['description'],
        'difficulty': metadata['difficulty'],
        'author': metadata['author']['name'] + " (" + metadata['author']['email'] + ")",
        'shortanswer': stats['shortanswer'],
        'multichoice': stats['multichoice'],
        'truefalse': stats['truefalse'],
        'matching': stats['matching'],
    }
    readme = template.safe_substitute(data)
    # write to file
    with open(f'{activity_path}/README.md', 'w') as outfile:
        outfile.write(readme)
