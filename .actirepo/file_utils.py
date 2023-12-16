import re
import os

# check if a filename is valid
def get_valid_filename(name):
    s = str(name).strip().replace("/", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise Exception(f"Error: {name} no es un nombre de archivo válido")
    return s

# check if file1 is newer than file2
def is_newer_than(file1, file2):
    return os.path.isfile(file1) and os.path.getmtime(file2) < os.path.getmtime(file1)