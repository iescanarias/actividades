#!/usr/bin/env python3

import argparse
import sys
import traceback
import tabulate

import activity
import repo

from __init__ import __version__
from dict_utils import trim_all_keys

def show_version():
    print(f"Versión: {__version__}")

def list_activities(directory="."):
    activities = repo.list_activities(directory)
    print(f'Listando actividades en {directory}: ...')
    if not activities:
        print("No hay actividades")
        return
    activities = trim_all_keys(activities, ['name', 'description', 'category', 'path'])
    headers = [ 'Nombre', 'Descripción', 'Categoría', 'Directorio' ]
    rows =  [x.values() for x in activities]
    print(tabulate.tabulate(rows, headers, tablefmt='grid', maxcolwidths=50))
    print(f'Total: {len(activities)} actividad(es) encontrada(s)')

def create_activity(directory=".", recursive=True):
    print(f"Crear actividad en el directorio {directory}: ...")  
    # TODO Reemplaza con la lógica para crear actividad

def create_readmes(directory, recursive=True, force=False):
    try:
        activity.create_readmes(directory, recursive, force)
    except Exception as e:
        traceback.print_exc(e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        
def create_images(questions_file, html):
    try:
        activity.create_images(questions_file, html)
    except Exception as e:
        traceback.print_exc(e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Organizador de actividades")

    # define options
    parser.add_argument('-v', '--version', action='store_true', help='Mostrar versión')
    parser.add_argument('-l', '--list', metavar='RUTA', nargs='?', const='.', help='Listar actividades')
    parser.add_argument('-c', '--create', metavar='RUTA', nargs='?', const='.', help='Crear los metadatos de la actividad en el directorio especificado (o directorio actual si no se proporciona)')
    parser.add_argument('-R', '--readme', metavar='RUTA', help='Crear README.md para actividad en el directorio especificado')
    parser.add_argument('-r', '--recursive', action='store_true', help='Buscar actividades recursivamente en subdirectorios. Se puede combinar con --readme y --create')
    parser.add_argument('-f', '--force', action='store_true', help='Forzar la creación de README.md aunque no sea necesario')
    parser.add_argument('-i', '--images', metavar='FICHERO', help='Genera imágenes de las preguntas')
    parser.add_argument('-H', '--html', action='store_true', help='Genera HTML de las preguntas')

    # parse arguments
    args = parser.parse_args()

    # Lógica según las opciones
    if args.version:
        show_version()
    elif args.list is not None:
        list_activities(args.list)
    elif args.create is not None:
        create_activity(args.create, args.recursive)
    elif args.readme:
        create_readmes(args.readme, args.recursive, args.force)
    elif args.images is not None:
        create_images(args.images, args.html)

if __name__ == "__main__":
    main()