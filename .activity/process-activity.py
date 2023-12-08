#!/usr/bin/env python3

import json
import sys
import os
import xml.etree.ElementTree as ET
from string import Template

# get script name
script = sys.argv[0]

# get script arguments
args = sys.argv[1:]

# get script path
script_path = os.path.dirname(os.path.realpath(script))

# check arguments
if len(args) != 1:
    print(f'usage: python {script} <activity path>')
    sys.exit(1)

# get activity path from arguments
activity_path = args[0]

# check if dir exists
if not os.path.isdir(activity_path):
    print(f'error: activity path {activity_path} does not exist or is not a directory')
    sys.exit(1)

# read file
activity_file = f'{activity_path}/activity.json'
with open(activity_file, 'r') as json_file:
    data = json_file.read()

# parse file
obj = json.loads(data)

# read questions file
stats = {
    'shortanswer': 0,
    'multichoice': 0,
    'truefalse': 0,
    'matching': 0,
    'fill_in_the_blank': 0,
    'essay': 0,
    'long_answer': 0,
}
for file in obj['questions']:
    questions_file = f'{activity_path}/{file}'
    tree = ET.parse(questions_file)
    # search "question" tags under "quiz" tag
    for question in tree.findall('question'):
        # get question type
        question_type = question.get('type')
        # increment stats
        stats[question_type] += 1

print(stats)

# load template
with open(f'{script_path}/README.template.md', 'r') as template_file:
    template = Template(template_file.read())

# substitute values in template
readme = template.safe_substitute({
    'name': obj['name'],
    'description': obj['description'],
    'difficulty': obj['difficulty'],
    'author': obj['author']['name'] + " (" + obj['author']['email'] + ")",
    'short_answer': stats['shortanswer'],
    'multiple_choice': stats['multichoice'],
    'true_false': stats['truefalse'],
    'matching': stats['matching'],
})

# write to file
with open(f'{activity_path}/README.md', 'w') as outfile:
    outfile.write(readme)
