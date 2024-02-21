import os
import json

from activity import _is_activity, _read_activity

REPO_FILE = 'repo.json'

def list_activities(repo_path="."):
    if not os.path.isdir(repo_path):
        raise Exception(f'Error: {repo_path} no es un directorio')
    activities = []
    # walk throuth all directories
    for root, dirs, files in os.walk(repo_path):
        # check if is an activity
        if _is_activity(root):
            # get metadata
            metadata = _read_activity(root)
            activities.append(metadata)
    return activities

def create_index(repo_path):
    # check if path exsists
    if not os.path.isdir(repo_path):
        raise Exception(f'Error: {repo_path} no es un directorio')    
    acitivies_list = []
    # walk throuth all directories
    for root, dirs, files in os.walk(repo_path):
        # check if is an activity
        if _is_activity(root):
            # get metadata
            metadata = _read_activity(root)
            # total = get_num_questions(root)
            activity = {
                "name": metadata['name'],
                "description": metadata['description'],
                # "total": total,
            }
            acitivies_list.append(activity)
    print(acitivies_list)

# read repo metadata
def read_repo(repo_path):
    # get full path to activity descriptor
    repo_file = os.path.join(repo_path, REPO_FILE)
    # read activity descriptor
    with open(repo_file, 'r') as json_file:
        content = json_file.read()
    # parse activity descriptor
    return json.loads(content)

# create_index("..")