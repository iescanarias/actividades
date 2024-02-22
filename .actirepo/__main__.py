#!/usr/bin/env python3

import argparse
import sys
import traceback
import tabulate

import activity
import repo

from __init__ import __version__
from dict_utils import trim_all_keys

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

    # declara un HelpFormatter personalizado para reemplazar el texto 'usage:' por 'Uso:'
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix='Uso: '):
            if usage is not argparse.SUPPRESS:
                args = usage, actions, groups, prefix
                self._add_item(self._format_usage, args)

    # define el parser
    parser = argparse.ArgumentParser(prog='actirepo', description='Organizador de actividades', epilog='¡Espero que te sea útil!', add_help=False, formatter_class=CustomHelpFormatter)

    # define los comandos (mutuamente excluyentes)
    commands = parser.add_argument_group('Comandos')
    commands = commands.add_mutually_exclusive_group(required=True)
    commands.add_argument('-h', '--help', action='store_true', help='Muestra esta ayuda y termina')
    commands.add_argument('-v', '--version', action='version', help='Mostrar versión', version=f'%(prog)s {__version__}')
    commands.add_argument('-l', '--list', metavar='RUTA', nargs='?', const='.', help='Listar actividades')
    commands.add_argument('-c', '--create', metavar='RUTA', nargs='?', const='.', help='Crear los metadatos de la actividad en el directorio especificado (o directorio actual si no se proporciona)')
    commands.add_argument('-i', '--images', metavar='FICHERO', help='Genera imágenes de las preguntas')
    commands.add_argument('-R', '--readme', metavar='RUTA', help='Crear README.md para actividad en el directorio especificado')

    # define las opciones adicionales a los comandos
    options = parser.add_argument_group('Opciones')
    options.add_argument('-r', '--recursive', action='store_true', help='Buscar actividades recursivamente en subdirectorios. Se puede combinar con --readme y --create')
    options.add_argument('-f', '--force', action='store_true', help='Forzar la creación de README.md aunque no sea necesario')
    options.add_argument('-H', '--html', action='store_true', help='Genera HTML de las preguntas')

    # parsea los argumentos
    args = parser.parse_args()

    # lógica según las opciones
    if args.help:
        parser.print_help()
    elif args.list:
        list_activities(args.list)
    elif args.create:
        create_activity(args.create, args.recursive)
    elif args.readme:
        create_readmes(args.readme, args.recursive, args.force)
    elif args.images:
        create_images(args.images, args.html)

if __name__ == "__main__":
    main()