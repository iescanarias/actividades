from setuptools import setup, find_packages

setup(
    name = 'activities-organizer',
    version = '0.0.1',
    packages = find_packages(),  # Encuentra automáticamente paquetes en el directorio actual
    install_requires = [
        'Jinja2',
    ],
    entry_points={
        'console_scripts': [
            'run=activities-organizer.process-activities:main',
        ],
    },
    author = 'Francisco Vargas Ruiz',
    author_email = 'fvarrui@canariaseducacion.es',
    description = 'Moodle activities repo organizer',
    url = 'https://github.com/iescanarias/actividades',
)
