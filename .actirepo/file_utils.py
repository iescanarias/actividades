import re

def get_valid_filename(name):
    s = str(name).strip().replace("/", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise Exception(f"Error: {name} no es un nombre de archivo válido")
    return s
