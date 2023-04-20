#!/usr/bin/python3
import datetime
import json
import logging
import psutil
import time
import subprocess
import DaVinciResolveScript as davinci_resolve_script

from tqdm import tqdm


# parámetros iniciales
PARAMS_JSON_FILE_PATH = '/Users/fleyva/projects/@eyvotTest/_youtube/test-assets/params.json'
BASE_PROJECT_NAME = '00-base (Copy)'
DAVINCI_RESOLVE_APP_NAME = 'DaVinci Resolve'
DAVINCI_RESOLVE_PROCESS_NAME = 'DaVinciPanelDaemon'
SECONDS_TO_WAIT_FOR_DAVINCI_TO_OPEN = 7
SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT = 2
SECONDS_TO_WAIT_FOR_PROJECT_SAVING = 1
SECONDS_TO_WAIT_FOR_PAGE_CHANGE = 1

# davinci resolve api values
RESOLVE_INITIALIZER = 'Resolve'
PAGE_MEDIA_NAME = 'media'
PAGE_EDIT_NAME = 'edit'
PAGE_FUSION_NAME = 'fusion'

# media dirs
HORIZONTAL_VIDEO_MEDIA_DIR = 'H16.9FHD'
ASSETS_MEDIA_DIR = 'assets'
AUDIO_MEDIA_DIR = 'audio'
IMAGE_MEDIA_DIR = 'image'
VIDEO_MEDIA_DIR = 'video'

# project convenions
TIMELINE_NAME = 'H16.9FHD'
TIMELINE_NAME_CANVAS = 'H16.9FHD - Canvas'
TIMELINE_NAME_CONTENT = 'H16.9FHD - Content'
TIMELINE_NAME_HOOK = 'H16.9FHD - Hook'
TIMELINE_NAME_INTRO = 'H16.9FHD - Intro'
TIMELINE_NAME_MAIN = 'H16.9FHD - Main'
TIMELINE_NAME_SUBJECT = 'H16.9FHD - Subject'

# info messages
INFO_MESSAGE_LOADING_DAVINCI_RESOLVE = 'Abriendo DaVinci Resolve'
INFO_MESSAGE_EXITING_DAVINCI_RESOLVE = 'Cerrando DaVinci Resolve'
INFO_MESSAGE_SAVING_PROJECT  = 'Guardando cambios'

# error messages
ERROR_MESSAGE_JSON_FILE_NOT_FOUND = 'No se pudo encontrar el archivo JSON.'
ERROR_MESSAGE_JSON_SYNTAX = 'Error de sintaxis en archivo JSON.'
ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND = 'No se encontró el proyecto base en DaVinci Resolve.'
ERROR_MESSAGE_MEDIA_DIR_NOT_FOUND = 'No se encontró el directorio en el Media Pool.'
ERROR_MESSAGE_TIMELINE_NOT_FOUND = 'No se encontró el timeline en el proyecto.'

# logger config
DEBUG_MODE = True
if DEBUG_MODE:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
else:
    logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('logger')



def get_current_timestamp():
    """
    Devuelve un string con el timestamp actual en formato YYMMAA.
    Returns:
        str: El timestamp actual en formato YYMMAA.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime('%y%m%d')
    return timestamp


def json_to_dict(json_file_path):
    """
    Carga un diccionario a partir de un archivo json.
    Args:
        json_file_path (str): La ruta del archivo json.
    Returns:
        dict: El diccionario cargado a partir del archivo json.
    Raises:
        Exception: Si la ruta del archivo no existe.
        Exception: Si hay un error en la sintaxis del archivo json.
    """
    try:
        with open(json_file_path, 'r') as archivo_json:
            diccionario = json.load(archivo_json)
    except FileNotFoundError:
        raise Exception(ERROR_MESSAGE_JSON_FILE_NOT_FOUND + '\n' + json_file_path)
    except json.decoder.JSONDecodeError:
        raise Exception(ERROR_MESSAGE_JSON_SYNTAX + '\n' + json_file_path)
    
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


def import_to_media_pool_dir(media_paths, media_pool_dir, media_pool_handler):
    """
    Importa toda la media compatible dentro de una lista de rutas del disco duro, a un
    directorio determinado del media pool.
    Args:
        media_paths (list): Rutas de los archivos media a importar.
        media_pool_dir (str): Nombre del directorio destino dentro del media pool.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    Returns:
        list: Lista de MediaPoolItems que fueron agregados al media pool.
    Raises:
        Exception: Si no existe el directorio dentro del media pool.
    """
    root_dir = media_pool_handler.GetRootFolder()
    root_subdirs = root_dir.GetSubFolderList()
    horizontal_video_dir = None
    for subdir in root_subdirs:
        if subdir.GetName() == HORIZONTAL_VIDEO_MEDIA_DIR:
            horizontal_video_dir = subdir
    if not horizontal_video_dir:
        raise Exception(ERROR_MESSAGE_MEDIA_DIR_NOT_FOUND + '\n' + HORIZONTAL_VIDEO_MEDIA_DIR)
    horizontal_video_subdirs = horizontal_video_dir.GetSubFolderList()
    assets_dir = None
    for subdir in horizontal_video_subdirs:
        if subdir.GetName() == ASSETS_MEDIA_DIR:
            assets_dir = subdir
    if not assets_dir:
        raise Exception(ERROR_MESSAGE_MEDIA_DIR_NOT_FOUND + '\n' + ASSETS_MEDIA_DIR)
    assets_subdirs = assets_dir.GetSubFolderList()
    target_dir = None
    for subdir in assets_subdirs:
        if subdir.GetName() == media_pool_dir:
            target_dir = subdir
    if not target_dir:
        raise Exception(ERROR_MESSAGE_MEDIA_DIR_NOT_FOUND + '\n' + media_pool_dir)
    media_pool_handler.SetCurrentFolder(target_dir)
    items = media_pool_handler.ImportMedia(media_paths)
    return items

def switch_to_page(page_name, resolve_handler):
    """
    Cambia a una determinada página del flujo de edición de davinci resolve.
    Args:
        page_name (str): Nombre de la página a la que se desea cambiar.
        media_pool_dir (obj): Objeto para controlar davinci resolve del api de davinci resolve.
    """
    message = 'Abriendo Página ' + page_name.capitalize()
    resolve_handler.OpenPage(page_name)
    wait_for(SECONDS_TO_WAIT_FOR_PAGE_CHANGE, message)

def choose_suffix_to_project_name(name, project_handler):
    """
    Determina un sufijo adecuado para el nombre del proyecto.
    En caso de que se desee poner a un proyecto un nombre ocupado por otro proyecto,
    el sufijo irá cambiando de forma numérica incremental:
    _01, _02, _03, etc.
    Args:
        name (str): Nombre deseado para el proyecto.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
    Returns:
        str: Nombre con sufijo adecuado para el proyecto.
    """
    i = 1
    parts = name.split('_')
    suffix = parts[-1]
    project_names = project_handler.GetProjectListInCurrentFolder()
    while name in project_names:
        i += 1
        suffix = f'_{i:02d}'
        name = '_'.join(parts[:-1]) + suffix
    return name


def switch_to_timeline(timeline_name, project_handler):
    """
    Cambia a un determinado timeline del proyecto abierto en davinci resolve.
    Args:
        timeline_name (str): Nombre del timeline al que se desea cambiar.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
    """
    number_of_timelines = project_handler.GetTimelineCount()
    logger.info(f'Timelines Number: {number_of_timelines}')
    hook_timeline = None
    for timeline_index in range(1, number_of_timelines+1):
        # davinci resolve a pesar de referirse com índice en su método GetTimelineByIndex,
        # en realidad no usa índices, es el número directamente del timeline comenzando
        # por uno y hasta llegar al número retornado por GetTimelineCount
        current_timeline = project_handler.GetTimelineByIndex(timeline_index)
        if current_timeline.GetName() == timeline_name:
            hook_timeline = current_timeline
            break
    if not hook_timeline:
        raise Exception(ERROR_MESSAGE_TIMELINE_NOT_FOUND + '\n' + timeline_name)
    project_handler.SetCurrentTimeline(hook_timeline)
    logger.info(f'Selected Timeline Name: {timeline_name}')

def create_hook(highlights_times, video_items, project_handler, media_pool_handler):
    """
    Crear el gancho inicial del video a partir de una lista de rangos de tiempo,
    cada elemento de la lista, a su vez es otra lista que solo pueden tener
    2 valores cadena en formato hh:mm:ss, el inicio y el fin del rango del tiempo.
    El inicio es el primer elemento de la lista y el fin es el segungo elemento de
    la lista.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
    """
    # 1. cambiarse a línea de tiempo del hook
    switch_to_timeline(TIMELINE_NAME_HOOK, project_handler)
    # 2. agregar un clip al timeline a partir de uno video del media pool
    media_pool_handler.AppendToTimeline([{ "mediaPoolItem": video_items[3], "startFrame" : 1, "endFrame" : 30*5}])
    # 3. agregar highlight clips al timeline
    logger.info(f'Hook Hightlights Timeranges: {highlights_times}')
    pass


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
        + '_gameplay_01'
    project_name = choose_suffix_to_project_name(project_name, project_manager)
    project = project_manager.LoadProject(BASE_PROJECT_NAME)

    # verificar si existe proyecto de configuración inicial
    if project is None:
        if params['autoclose']:
            wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
            resolve.Quit()
        raise Exception(ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND + '\n' + BASE_PROJECT_NAME)
    project.SetName(project_name)
    logger.info(f'Project Name: {project_name}')
    media_pool = project.GetMediaPool()
    assets_dirs = params['gameplay_details']['assets']

    # ##################
    # proceso de edición
    # ##################

    # importar media
    switch_to_page(PAGE_EDIT_NAME, resolve)
    logger.info(f'Media Items to Load: {assets_dirs}')
    audio_items = import_to_media_pool_dir(assets_dirs['audio'], AUDIO_MEDIA_DIR, media_pool)
    image_items = import_to_media_pool_dir(assets_dirs['image'], IMAGE_MEDIA_DIR, media_pool)
    video_items = import_to_media_pool_dir(assets_dirs['video'], VIDEO_MEDIA_DIR, media_pool)
    logger.info(f'Media Pool Items Loaded: {audio_items}, {image_items}, {video_items}')
    # crear hook del video
    hook_timeranges = params['gameplay_details']['hook']
    create_hook(hook_timeranges, video_items, project, media_pool)

    # guardar cambios
    project_manager.SaveProject()
    if params['autoclose']:
        wait_for(SECONDS_TO_WAIT_FOR_PROJECT_SAVING, INFO_MESSAGE_SAVING_PROJECT)
        project_manager.CloseProject(project)
        wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
        resolve.Quit()


if __name__ == '__main__':
    main()
