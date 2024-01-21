#!/usr/bin/env python3

import sys
import argparse
import process_activity
from importlib import reload
from __init__ import __version__

def show_version():
    print(f"Versión: {__version__}")

def list_activities():
    print("Lista de actividades: ...")  # Reemplaza con la lógica para listar actividades

def create_activity(directory=".", recursive=True):
    print(f"Crear actividad en el directorio {directory}: ...")  # Reemplaza con la lógica para crear actividad

def create_readmes(directory, recursive=True, force=False):
    #try:
        process_activity.create_readmes(directory, recursive, force)
    #except Exception as e:
    #    print(f"Error: {e}", file=sys.stderr)
    #    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Organizador de actividades")

    # define options
    parser.add_argument('-v', '--version', action='store_true', help='Mostrar versión')
    parser.add_argument('-l', '--list', action='store_true', help='Listar actividades')
    parser.add_argument('-c', '--create', metavar='RUTA', nargs='?', const='.', help='Crear los metadatos de la actividad en el directorio especificado (o directorio actual si no se proporciona)')
    parser.add_argument('--readme', metavar='RUTA', help='Crear README.md para actividad en el directorio especificado')
    parser.add_argument('-r', '--recursive', action='store_true', help='Buscar actividades recursivamente en subdirectorios. Se puede combinar con --readme y --create')
    parser.add_argument('-f', '--force', action='store_true', help='Forzar la creación de README.md aunque no sea necesario')

    # parse arguments
    args = parser.parse_args()

    # Lógica según las opciones
    if args.version:
        show_version()
    elif args.list:
        list_activities()
    elif args.create is not None:
        create_activity(args.create, args.recursive)
    elif args.readme:
        create_readmes(args.readme, args.recursive, args.force)

if __name__ == "__main__":
    main()