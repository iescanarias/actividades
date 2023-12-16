import os

from process_activity import _is_activity, _read_metadata, get_num_questions

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
            metadata = _read_metadata(root)
            total = get_num_questions(root)
            activity = {
                "name": metadata['name'],
                "description": metadata['description'],
                "total": total,
            }
            acitivies_list.append(activity)

    print(acitivies_list)

create_index("..")