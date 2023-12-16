from setuptools import setup, find_packages
from __init__ import __version__

setup(
    name = 'actirepo',
    version = __version__,
    packages = find_packages(),  # Encuentra automáticamente paquetes en el directorio actual
    install_requires = [
        'Jinja2',
        'Pillow',
        'html2image'
    ],
    entry_points={
        'console_scripts': [
            'run=.activities-organizer.process-activities:main',
        ],
    },
    author = 'Francisco Vargas Ruiz',
    author_email = 'fvarrui@canariaseducacion.es',
    description = 'Moodle activities repo organizer',
    url = 'https://github.com/iescanarias/actividades',
)
