import unicodedata
import re
import os

"""
Returns a valid filename by removing invalid characters and replacing slashes with underscores.
Args:
    name (str): The input filename.
Returns:
    str: The valid filename.
Raises:
    Exception: If the resulting filename is empty or contains only dots or double dots.
"""
def get_valid_filename(name):
    s = str(name).strip().replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_").replace(" ", "_").replace("\t", "_").replace("\n", "_").replace("\r", "_").replace("\f", "_").replace("\v", "_").replace("\0", "_").replace("\b", "_").replace("\a", "_").replace("\e", "_")
    s = re.sub(r"(?u)[^- \w.]", "", s)
    if s in {"", ".", ".."}:
        raise Exception(f"Error: {name} is not a valid filename")
    return s

"""
Check if file1 is newer than file2
Returns True if file1 is a file and file2 is a file and file1 is newer than file2.
"""
def is_newer_than(file1, file2):
    return os.path.isfile(file1) and os.path.getmtime(file2) < os.path.getmtime(file1)

"""
Taken from https://github.com/django/django/blob/master/django/utils/text.py
Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
dashes to single dashes. Remove characters that aren't alphanumerics,
underscores, or hyphens. Convert to lowercase. Also strip leading and
trailing whitespace, dashes, and underscores.
"""
def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def anchorify(value):
    return re.sub(r'[^\w\s-]', '', value.lower()).replace(" ", "-")
