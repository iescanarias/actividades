import sys
import json

REPO_FILE = 'repo.json'

try:
    # read repo descriptor
    with open(REPO_FILE, 'r') as json_file:
        content = json_file.read()
    # parse repo descriptor
    repo = json.loads(content)
    # print(f"Usando descriptor en el repositorio: {repo}")
except Exception as e:
    print(f"Error: {e}.", file=sys.stderr)
    print(f"No se ha encontrado un descriptor en el repositorio ({REPO_FILE}) o éste no es válido")
    repo = {
        "download_url": "https://github.com/...",
        "raw_url": "https://raw.githubusercontent.com/",
        "pages_url": "https://github.io/..."
    }
    print(f"Usando valores por defecto: {repo}")

# init global variables
__version__ = "0.0.1"
__raw_url__ = repo['raw_url']
__download_url__ = repo['download_url']
__pages_url__ = repo['pages_url']
__icons_url__ = f"{__raw_url__}/.actirepo/icons"
