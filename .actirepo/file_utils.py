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
def is_valid_filename(name):
    s = str(name).strip().replace("/", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise Exception(f"Error: {name} is not a valid filename")
    return s

# 
"""
Check if file1 is newer than file2
Returns True if file1 is a file and file2 is a file and file1 is newer than file2.
"""
def is_newer_than(file1, file2):
    return os.path.isfile(file1) and os.path.getmtime(file2) < os.path.getmtime(file1)