#!/usr/bin/python3
import datetime
import psutil
import time
import subprocess
import DaVinciResolveScript as davinci_resolve_script

from tqdm import tqdm


# parámetros iniciales
PARAMS_JSON_FILE_PATH = '/Users/fleyva/Desktop/video-script-assets/params.json'
BASE_PROJECT_NAME = '00-base (Copy)'
DAVINCI_RESOLVE_APP_NAME = 'DaVinci Resolve'
DAVINCI_RESOLVE_PROCESS_NAME = 'DaVinciPanelDaemon'
SECONDS_TO_WAIT_FOR_DAVINCI_TO_OPEN = 7
SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT = 2
SECONDS_TO_WAIT_FOR_PROJECT_SAVING = 1

# davinci resolve api values
RESOLVE_INITIALIZER = 'Resolve'

# info messages
INFO_MESSAGE_LOADING_DAVINCI_RESOLVE = 'Abriendo DaVinci Resolve'
INFO_MESSAGE_EXITING_DAVINCI_RESOLVE = 'Cerrando DaVinci Resolve'
INFO_MESSAGE_SAVING_PROJECT          = '       Guardando cambios'

# error messages
ERROR_MESSAGE_JSON_FILE_NOT_FOUND = 'No se pudo encontrar el archivo JSON.'
ERROR_MESSAGE_JSON_SYNTAX = 'Error de sintaxis en archivo JSON.'
ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND = 'No se encontró el proyecto base en DaVinci Resolve.'


"""
TODO: Función para crear Estructura
* Crear estrucrtura de líneas de tiempo necesarias
  - Bin "H16.9FHD" dentro del root o master del Media Pool
  - Línea del tiempo "H16.9FHD" delntro del bin recién creado
  - Línea del tiempo "H16.9FHD - Main" dentro del bin recién creado
  - Línea del tiempo "H16.9FHD - Canvas" dentro del bin recién creado
  - Línea del tiempo "H16.9FHD - Content" dentro del bin recién creado
  - Línea del tiempo "H16.9FHD - Hook" dentro del bin recién creado
  - Línea del tiempo "H16.9FHD - Intro" dentro del bin recién creado
  - Línea del tiempo "H16.9FHD - Subject" dentro del bin recién creado
"""


"""
TODO: Función para realizar los Imports
* Realizar imports partiendo de un documento JSON de Parámetros
  - Importar video de gameplay al Media Pool en ./assets/video/
  - Importar video de grabación al Media Pool en ./assets/video/
  - Importar video de intro al Media Pool en ./assets/video
  - Importar video de outro al Media Pool en ./assets/video
  - Importar audio de grabación al Media Pool en ./assets/audio/
  - Importar marca de agua al Media Pool en ./assets/image/
"""


"""
TODO: Función para crear el Hook
* Crear gancho del video
  - Obtener array de rangos de tiempo de los highlights desde el JSON de Parámetros
  - Agregar partes específicas del video de gameplay al incio de la línea del tiempo (las que se parametrizaron)
"""


def get_current_timestamp():
    """
    Devuelve un string con el timestamp actual en formato YYMMAA.
    Returns:
        str: El timestamp actual en formato YYMMAA.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime('%y%m%d')
    return timestamp


import json

def json_to_dict(json_file_path):
    """
    Carga un diccionario a partir de un archivo json.
    Args:
        json_file_path (str): La ruta del archivo json.
    Returns:
        dict: El diccionario cargado a partir del archivo json.
    Raises:
        FileNotFoundError: Si la ruta del archivo no existe.
        json.decoder.JSONDecodeError: Si hay un error en la sintaxis del archivo json.
    """
    try:
        with open(json_file_path, 'r') as archivo_json:
            diccionario = json.load(archivo_json)
    except FileNotFoundError:
        raise Exception(ERROR_MESSAGE_JSON_FILE_NOT_FOUND + '\nDetalles: ' + json_file_path)
    except json.decoder.JSONDecodeError:
        raise Exception(ERROR_MESSAGE_JSON_SYNTAX + '\nDetalles: ' + json_file_path)
    
    return diccionario


def wait_for(seconds, message):
    """
    Pausa la ejecución por una cantidad de segundos específica.
    Args:
        seconds (int): Cantidad de segundos a esperar.
        message (str): Mensaje a mostrar durante la espera.
    """
    for _ in tqdm(range(seconds), desc=message):
        time.sleep(1)


def open_davinci_resolve():
    """
    Ejecuta la App de DaVinci Resolve si no estpa abierta.
    """
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == DAVINCI_RESOLVE_PROCESS_NAME:
            return
    subprocess.run(["open", "-a", DAVINCI_RESOLVE_APP_NAME])
    wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_OPEN, INFO_MESSAGE_LOADING_DAVINCI_RESOLVE)


def main():
    # abrir davinci resolve
    open_davinci_resolve()

    # create project
    resolve = davinci_resolve_script.scriptapp(RESOLVE_INITIALIZER)
    project_manager = resolve.GetProjectManager()
    current_project = project_manager.GetCurrentProject()
    project_manager.CloseProject(current_project)
    params = json_to_dict(PARAMS_JSON_FILE_PATH)
    project_name = get_current_timestamp()\
        + '_' + params['gameplay_details']['videogame_keyname']\
        + '_gameplay'
    project = project_manager.LoadProject(BASE_PROJECT_NAME)

    # verificar si existe proyecto de configuración inicial
    if project is None:
        if params['autoclose']:
            wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
            resolve.Quit()
        raise Exception(ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND + '\nDetalles: ' + BASE_PROJECT_NAME)
    project.SetName(project_name)

    # guardar cambios
    project_manager.SaveProject()
    if params['autoclose']:
        wait_for(SECONDS_TO_WAIT_FOR_PROJECT_SAVING, INFO_MESSAGE_SAVING_PROJECT)
        project_manager.CloseProject(project)
        wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
        resolve.Quit()


if __name__ == '__main__':
    main()
