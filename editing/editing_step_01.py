#!/usr/bin/python3
import ast
import datetime
import json
import logging
import psutil
import time
import re
import subprocess
import DaVinciResolveScript as davinci_resolve_script

from pynput.mouse import Button, Controller
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
SECONDS_TO_WAIT_FOR_PLAYHEAD_REPOSITION = 1

# davinci resolve api values
RESOLVE_INITIALIZER = 'Resolve'
PAGE_MEDIA_NAME = 'media'
PAGE_EDIT_NAME = 'edit'
PAGE_FUSION_NAME = 'fusion'
TRACK_TYPE_AUDIO = 'audio'
TRACK_TYPE_VIDEO = 'video'
ONLY_VIDEO_MEDIA_TYPE = 1
ONLY_AUDIO_MEDIA_TYPE = 2

# media dirs
HORIZONTAL_VIDEO_MEDIA_DIR = 'H16.9FHD'
ASSETS_MEDIA_DIR = 'assets'
AUDIO_MEDIA_DIR = 'audio'
IMAGE_MEDIA_DIR = 'image'
VIDEO_MEDIA_DIR = 'video'

# project convenions
FPS = 30
NOT_OVERLAPPING_FRAME = 1
TIMELINE_NAME = 'H16.9FHD'
TIMELINE_NAME_CANVAS = 'H16.9FHD - Canvas'
TIMELINE_NAME_CONTENT = 'H16.9FHD - Content'
TIMELINE_NAME_HOOK = 'H16.9FHD - Hook'
TIMELINE_NAME_INTRO = 'H16.9FHD - Intro'
TIMELINE_NAME_MAIN = 'H16.9FHD - Main'
TIMELINE_NAME_SUBJECT = 'H16.9FHD - Subject'
ASSET_AUDIO_NAME_MICRO = 'micro.mp3'
ASSET_IMAGE_NAME_WATERMARK = 'watermark.png'
ASSET_VIDEO_NAME_CAMERA = 'camera.mov'
ASSET_VIDEO_NAME_CAMFRAME = 'camframe.mov'
ASSET_VIDEO_NAME_GAMEPLAY = 'gameplay.mov'
ASSET_VIDEO_NAME_INTRO = 'intro.mov'
ASSET_VIDEO_NAME_OUTRO = 'outro.mov'
HOOK_TRACK_GAMEPLAY = 'gameplay'
HOOK_TRACK_CAMERA = 'camera'
HOOK_TRACK_CAMFRAME = 'camframe'
HOOK_TRACK_MIC = 'mic'
HOOK_TRACK_TITLE = 'title'
INTRO_TRACK = 'intro'
SUBJECT_TRACK_GAMEPLAY = 'gameplay'
SUBJECT_TRACK_CAMERA = 'camera'
SUBJECT_TRACK_CAMFRAME = 'camframe'
SUBJECT_TRACK_MIC = 'mic'
CONTENT_TRACK_GAMEPLAY = 'gameplay'
OUTRO_TRACK = 'outro'
MAIN_CANVAS_TRACK = 'canvas'
MAIN_CONTENT_TRACK = 'content'
START_TIMECODE = '01:00:00:00'
START_FRAME = 0
CAMERA_PROPERTIES = [
    ('ZoomX', 0.285),
    ('ZoomY', 0.285),
    ('CropLeft', 420),
    ('CropRight', 420),
    ('AnchorPointX', 1082)]
CAMFRAME_PROPERTIES = [
    ('CompositeMode', 6)]

# mouse manual actions
MANUAL_ACTIONS_SECONDS_OF_DELAY = 4 # es alto para evitar conflictos con el autosaving
MANUAL_ACTIONS_FOR_HOOK = """
L Click {"x":1250, "y":43}
L Click {"x":1261, "y":45}
L Click {"x":807, "y":912}
R Click {"x":823, "y":912}
L Click {"x":858, "y":926}
L Click {"x":816, "y":673}
R Click {"x":825, "y":675}
L Click {"x":836, "y":682}
L Click {"x":822, "y":737}
R Click {"x":838, "y":734}
L Click {"x":855, "y":744}
L Click {"x":730, "y":861}
L Click {"x":1332, "y":44}
"""

# info messages
INFO_MESSAGE_LOADING_DAVINCI_RESOLVE = 'Abriendo DaVinci Resolve'
INFO_MESSAGE_EXITING_DAVINCI_RESOLVE = 'Cerrando DaVinci Resolve'
INFO_MESSAGE_SAVING_PROJECT  = 'Guardando cambios'
INFO_MESSAGE_REPOSITIONING_PLAYHEAD  = 'Reposicionando PlayHead'
INFO_MESSAGE_PROCESSING_MANUAL_ACTIONS = 'Procesando Acciones Manuales Simuladas'
INFO_MESSAGE_WAIT_FOR_USER_INPUT = 'Presione cualquier tecla para continuar...'

# error messages
ERROR_MESSAGE_JSON_FILE_NOT_FOUND = 'No se pudo encontrar el archivo JSON.'
ERROR_MESSAGE_JSON_SYNTAX = 'Error de sintaxis en archivo JSON.'
ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND = 'No se encontró el proyecto base en DaVinci Resolve.'
ERROR_MESSAGE_MEDIA_DIR_NOT_FOUND = 'No se encontró el directorio en el Media Pool.'
ERROR_MESSAGE_TIMELINE_NOT_FOUND = 'No se encontró el timeline en el proyecto.'
ERROR_MESSAGE_ASSET_NOT_FOUND = 'No se encontró el asset en la lista dada.'
ERROR_MESSAGE_INCORREC_TIMESTRIG_FORMAT = 'Formato de timestring hh:mm:ss incorrecto.'

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


def process_manual_actions(actions):
    mouse = Controller()
    clicks = actions.split('\n')
    clicks = list(filter(bool, clicks)) # eliminar cadenaas vacías
    logger.info(f'Manual Actions to Process: {clicks}')
    for click in tqdm(clicks, desc=INFO_MESSAGE_PROCESSING_MANUAL_ACTIONS, unit='click'):
        time.sleep(MANUAL_ACTIONS_SECONDS_OF_DELAY)
        click = click.strip()
        if click.startswith('L'):
            button = Button.left
        elif click.startswith('R'):
            button = Button.right
        else:
            continue
        coords = eval(click[7:])
        mouse.position = (coords['x'], coords['y'])
        mouse.click(button, 1)


def wait_for_user_input():
    print(INFO_MESSAGE_WAIT_FOR_USER_INPUT)
    input()


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
    logger.info(f'Timeline Video Tracks: {hook_timeline.GetTrackCount(TRACK_TYPE_VIDEO)}')
    logger.info(f'Timeline Audio Tracks: {hook_timeline.GetTrackCount(TRACK_TYPE_AUDIO)}')


def get_asset_by_name(name, media_pool_items):
    """
    Obtiene un media pool item buscándolo por su nombre.
    Args:
        name (str): Nombre del asset a obtener.
        media_pool_items (list): Lista de assets donde se realizará la búsqueda.
    Returns:
        obj: Media Pool Item del asset buscado.
    Raises:
        Exception: Si el asset no ha sido encontrado.
    """
    number_of_items = len(media_pool_items)
    for item_index in range(number_of_items):
        current_asset = media_pool_items[item_index]
        if current_asset.GetName() == name:
            logger.info(f'asset {name} loaded {dir(current_asset)}')
            return current_asset
    raise Exception(ERROR_MESSAGE_ASSET_NOT_FOUND + '\n' + name)


def timestring_to_second(timestring):
    """
    Obtiene el número del último segundo dada una cadena de tiempo en formato hh:mm:ss.
    Es decir, una cadena que indica una duración de 1 hora con 20 minutos y 43 segundos
    sería "01:20:43" y el último segundo sería el "3703".
    Args:
        timestring (str): Cadena que representa una duración de tiempo en formato hh:mm:ss.
    Returns:
        int: Número del último segundo del timestring.
    Raises:
        Exception: Si no se da un timestring en formaato adecuado.
    """
    timestring_regex = re.compile("^([0-9]{2}):([0-5][0-9]):([0-5][0-9])$")
    match = timestring_regex.match(timestring)
    if not match:
        raise Exception(ERROR_MESSAGE_INCORREC_TIMESTRIG_FORMAT + '\n' + timestring)
    h, m, s = timestring.split(':')
    last_second = int(h) * 3600 + int(m) * 60 + int(s)
    return last_second


def reset_playhead_position(project_handler):
    """
    Reestablece el PlayHead a la posición inicial de la línea del tiempo actual.
    Args:
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
    """
    current_timeline = project_handler.GetCurrentTimeline()
    current_timeline.SetCurrentTimecode(START_TIMECODE)
    wait_for(SECONDS_TO_WAIT_FOR_PLAYHEAD_REPOSITION, INFO_MESSAGE_REPOSITIONING_PLAYHEAD)


def get_track_index(track_name, project_handler, track_type):
    """
    Si no se encuentra, por defecto retorna la primera.
    """
    current_timeline = project_handler.GetCurrentTimeline()
    track_index = 1
    track_count = current_timeline.GetTrackCount(track_type)
    for index in range(1, track_count+1):
        current_track_name = current_timeline.GetTrackName(track_type, index)
        if current_track_name == track_name:
            track_index = index
            break
    return track_index


def generate_clip_info_list_from_highlights(clip, highlights, track, project_handler,
                                            media_type=None, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene una lista de directorios con información del media clip entendible por
    DaVinci Resolve. Esta información detalla qué partes del clip dado se agregarán
    a la línea del tiempo actual.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        highlights (list): Rangos de tiempo por convetir a clip info.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_type (int): Valor opcional entero para usar constantes media type del api de davinci resolve.
        track_type (str): Valor opcional cadena para usar constantes track type del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    clips_info = []
    for highlight in highlights:
        start_timestring = highlight[0] # el primer elemento siempre es el inicio
        end_timestring = highlight[1] # el segundo elemento siempre es el final
        start_frame = timestring_to_second(start_timestring)*FPS
        end_frame = timestring_to_second(end_timestring)*FPS - NOT_OVERLAPPING_FRAME
        track_index = get_track_index(track, project_handler, track_type)
        clip_info = {
            'mediaPoolItem': clip,
            'trackIndex': track_index,
            'startFrame' : start_frame,
            'endFrame' : end_frame }
        if media_type:
            clip_info['mediaType'] = media_type
        clips_info.append(clip_info)
        logger.info(f'preparing {(end_frame - start_frame + NOT_OVERLAPPING_FRAME) / 30}' + \
                    f'sec of {clip.GetName()} clip to add to {track} track')
    return clips_info


def generate_camframe_clip_info(camframe_clip, highlights, track, project_handler):
    """
    Obtiene una lista de directorios con información del media clip entendible por
    DaVinci Resolve. Esta información detalla cuántos clips de marco de cámara se
    necesitarán para el hook del video, incluso si solo se necesita una segmento del
    mismo.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        highlights (list): Rangos de tiempo por convetir a clip info.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    hook_total_seconds = 0
    for highlight in highlights:
        start_timestring = highlight[0] # el primer elemento siempre es el inicio
        end_timestring = highlight[1] # el segundo elemento siempre es el final
        start_second = timestring_to_second(start_timestring)
        end_second = timestring_to_second(end_timestring)
        hook_total_seconds += end_second - start_second
    
    hook_total_frames = hook_total_seconds * FPS
    logger.info(f'hook_total_frames {hook_total_frames}')
    camframe_long_timestring = camframe_clip.GetClipProperty("duration")
    camframe_timestring = ':'.join(camframe_long_timestring.split(':')[:-1])
    camframe_total_seconds = timestring_to_second(camframe_timestring)
    camframe_total_frames = camframe_total_seconds * FPS
    logger.info(f'camframe_total_frames {camframe_total_frames}')
    number_of_full_camframes_needed = hook_total_frames // camframe_total_frames
    logger.info(f'number_of_full_camframes_needed {number_of_full_camframes_needed}')
    is_partial_camframe_needed = (hook_total_frames % camframe_total_frames) != 0
    logger.info(f'is_partial_camframe_needed {is_partial_camframe_needed}')

    clips_info = []
    track_index = get_track_index(track, project_handler, TRACK_TYPE_VIDEO)
    for _ in range(number_of_full_camframes_needed):
        clip_info = {
            'mediaPoolItem': camframe_clip,
            'trackIndex': track_index,
            # 'mediaType': ONLY_VIDEO_MEDIA_TYPE,
            'startFrame' : 0,
            'endFrame' : camframe_total_frames - NOT_OVERLAPPING_FRAME }
        clips_info.append(clip_info)
    if is_partial_camframe_needed:
        partial_frames_needed = hook_total_frames \
            - camframe_total_frames*number_of_full_camframes_needed
        logger.info(f'partial_frames_needed {partial_frames_needed}')
        clip_info = {
            'mediaPoolItem': camframe_clip,
            'trackIndex': track_index,
            # 'mediaType': ONLY_VIDEO_MEDIA_TYPE,
            'startFrame' : 0,
            'endFrame' : partial_frames_needed - NOT_OVERLAPPING_FRAME }
        clips_info.append(clip_info)
    return clips_info


def add_gameplay_to_hook(highlights_times, video_items, project_handler, media_pool_handler):
    """
    Agrega los clips de gameplay iniciales para el gancho del video.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    gameplay_asset = get_asset_by_name(ASSET_VIDEO_NAME_GAMEPLAY, video_items)
    gameplay_clips_info = generate_clip_info_list_from_highlights(
        gameplay_asset, highlights_times, HOOK_TRACK_GAMEPLAY, project_handler, track_type=TRACK_TYPE_VIDEO)
    logger.info(f'gameplay_clips_info {gameplay_clips_info}')
    media_pool_handler.AppendToTimeline(gameplay_clips_info)


def add_camera_to_hook(highlights_times, video_items, project_handler, media_pool_handler):
    """
    Agrega los clips de cámara iniciales para el gancho del video y los rezisea de forma
    adecuada para gameplay.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    camera_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMERA, video_items)
    camera_clips_info = generate_clip_info_list_from_highlights(
        camera_asset, highlights_times, HOOK_TRACK_CAMERA, project_handler, track_type=TRACK_TYPE_VIDEO)
    logger.info(f'camera_clips_info {camera_clips_info}')
    camera_items = media_pool_handler.AppendToTimeline(camera_clips_info)
    for timeline_item in camera_items:
        for property in CAMERA_PROPERTIES:
            timeline_item.SetProperty(*property)


def add_camframe_to_hook(highlights_times, video_items, project_handler, media_pool_handler):
    """
    Agrega el marco de la cámara para el gancho del video.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    camframe_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMFRAME, video_items)
    camframe_clips_info = generate_camframe_clip_info(
        camframe_asset, highlights_times, HOOK_TRACK_CAMFRAME, project_handler)
    logger.info(f'camframe_clips_info {camframe_clips_info}')
    media_pool_handler.AppendToTimeline(camframe_clips_info)


def add_micro_to_hook(highlights_times, audio_items, project_handler, media_pool_handler):
    """
    Agrega el audio del micrófono para stustituir el de la videograbación de la cámara
    en el gancho del video.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    micro_asset = get_asset_by_name(ASSET_AUDIO_NAME_MICRO, audio_items)
    micro_clips_info = generate_clip_info_list_from_highlights(
        micro_asset, highlights_times, HOOK_TRACK_MIC, project_handler, track_type=TRACK_TYPE_AUDIO)
    logger.info(f'micro_clips_info {micro_clips_info}')
    media_pool_handler.AppendToTimeline(micro_clips_info)


def insert_text(text, project_handler, resolve_handler):
    """
    Agrega un texto en el track actual de la línea de tiempo actual.
    Args:
        text (str): Texto por agregar
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        resolve_handler (obj): Objeto para controlar la instancia de davinci resolve.
    """
    timeline = project_handler.GetCurrentTimeline()
    timeline.InsertFusionTitleIntoTimeline("Text+")
    switch_to_page(PAGE_FUSION_NAME)
    fusion = resolve_handler.Fusion()
    comp = fusion.GetCurrentComp()
    template = comp.FindTool("Template")
    comp.SetActiveTool(template)
    template.SetInput("StyledText", text, 0)
    resolve_handler.OpenPage("edit")


def insert_title_in_hook():
    """
    TODO: Agregar texto para el gancho del video haciendo uso de la función insert_text.
    """
    pass


def create_hook(highlights_times, video_items, audio_items,
                project_handler, media_pool_handler, resolve_handler,
                automate_actions):
    """
    Crear el gancho inicial del video a partir de una lista de rangos de tiempo,
    cada elemento de la lista, a su vez es otra lista que solo pueden tener
    2 valores cadena en formato hh:mm:ss, el inicio y el fin del rango del tiempo.
    El inicio es el primer elemento de la lista y el fin es el segungo elemento de
    la lista.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        audio_items (list): Lista de assets de audio del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
        resolve_handler (obj): Objeto para controlar la instancia de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_HOOK, project_handler)
    logger.info(f'Hook Hightlights Timeranges: {highlights_times}')
    add_gameplay_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    add_camera_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    add_camframe_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    add_micro_to_hook(highlights_times, audio_items, project_handler, media_pool_handler)
    if automate_actions:
        process_manual_actions(MANUAL_ACTIONS_FOR_HOOK)
    else:
        wait_for_user_input()


def generate_clip_info(clip, track, project_handler,
                       media_type=None, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene información del media clip en cuestión de forma entendible por DaVinci Resolve.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_type (int): Valor opcional entero para usar constantes media type del api de davinci resolve.
        track_type (str): Valor opcional cadena para usar constantes track type del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    track_index = get_track_index(track, project_handler, track_type)
    clip_properties = clip.GetClipProperty()
    clip_info = {
        'mediaPoolItem': clip,
        'trackIndex': track_index,
        'startFrame' : START_FRAME,
        'endFrame' : clip_properties['End'] }
    logger.info(f'preparing {clip.GetName()} clip to add to {track} track')
    return clip_info


def add_intro(video_items, project_handler, media_pool_handler):
    """
    Agrega el clip del intro en la línea de tiempo actual.
    Args:
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    intro_asset = get_asset_by_name(ASSET_VIDEO_NAME_INTRO, video_items)
    intro_clip_info = generate_clip_info(
        intro_asset, INTRO_TRACK, project_handler, track_type=TRACK_TYPE_VIDEO)
    logger.info(f'intro_clip_info {intro_clip_info}')
    media_pool_handler.AppendToTimeline([intro_clip_info])


def create_intro(video_items, project_handler, media_pool_handler):
    """
    Importa el video de intro en su respectiva línea del tiempo.
    Args:
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_INTRO, project_handler)
    add_intro(video_items, project_handler, media_pool_handler)
    reset_playhead_position(project_handler)


def add_gameplay_to_subject(gameplay_times, video_items, project_handler, media_pool_handler):
    """
    Agrega los clips de gameplay iniciales para el subject del video.
    Args:
        gameplay_times (list): Rangos de tiempo de las partes deseadas del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    gameplay_asset = get_asset_by_name(ASSET_VIDEO_NAME_GAMEPLAY, video_items)
    gameplay_clips_info = generate_clip_info_list_from_highlights(
        gameplay_asset, gameplay_times, SUBJECT_TRACK_GAMEPLAY, project_handler,
        track_type=TRACK_TYPE_VIDEO)
    logger.info(f'gameplay_clips_info {gameplay_clips_info}')
    media_pool_handler.AppendToTimeline(gameplay_clips_info)


def add_camera_to_subject(gameplay_times, video_items, project_handler, media_pool_handler):
    """
    Agrega los clips de cámara iniciales para el subject del video y los rezisea de forma
    adecuada para gameplay.
    Args:
        gameplay_times (list): Rangos de tiempo de las partes deseadas del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    camera_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMERA, video_items)
    camera_clips_info = generate_clip_info_list_from_highlights(
        camera_asset, gameplay_times, SUBJECT_TRACK_CAMERA, project_handler,
        track_type=TRACK_TYPE_VIDEO)
    logger.info(f'camera_clips_info {camera_clips_info}')
    camera_items = media_pool_handler.AppendToTimeline(camera_clips_info)
    for timeline_item in camera_items:
        for property in CAMERA_PROPERTIES:
            timeline_item.SetProperty(*property)


def add_camframe_to_subject(gameplay_times, video_items, project_handler, media_pool_handler):
    """
    Agrega el marco de la cámara para el gancho del video.
    Args:
        gameplay_times (list): Rangos de tiempo de las partes deseadas del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    camframe_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMFRAME, video_items)
    camframe_clips_info = generate_camframe_clip_info(
        camframe_asset, gameplay_times, SUBJECT_TRACK_CAMFRAME, project_handler)
    logger.info(f'camframe_clips_info {camframe_clips_info}')
    media_pool_handler.AppendToTimeline(camframe_clips_info)


def add_micro_to_subject(highlights_times, audio_items, project_handler, media_pool_handler):
    """
    Agrega el audio del micrófono para stustituir el de la videograbación de la cámara
    en el gancho del video.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    micro_asset = get_asset_by_name(ASSET_AUDIO_NAME_MICRO, audio_items)
    micro_clips_info = generate_clip_info_list_from_highlights(
        micro_asset, highlights_times, SUBJECT_TRACK_MIC, project_handler, track_type=TRACK_TYPE_AUDIO)
    logger.info(f'micro_clips_info {micro_clips_info}')
    media_pool_handler.AppendToTimeline(micro_clips_info)


def create_subject(gameplay_times, video_items, audio_items,
                   project_handler, media_pool_handler):
    """
    Crear el subject del video a partir de una lista de rangos de tiempo, cada elemento
    de la lista, a su vez es otra lista que solo pueden tener 2 valores cadena en formato
    hh:mm:ss, el inicio y el fin del rango del tiempo.
    El inicio es el primer elemento de la lista y el fin es el segundo elemento de
    la lista.
    Si se desea incluir el video completo, basta con proporcionar un solo rango equivalente
    a la duración del mismo. Es poco probable que suceda, ya que primero se suele entrar
    en escena y al final terminar la grabación (dichas acciones no formarán parte del video
    final).
    Args:
        gameplay_times (list): Rangos específicos del tiempo de gameplay por incluir.
        video_items (list): Lista de assets de video del media pool.
        audio_items (list): Lista de assets de audio del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_SUBJECT, project_handler)
    logger.info(f'Gameplay Timeranges: {gameplay_times}')
    add_gameplay_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    add_camera_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    add_camframe_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    add_micro_to_hook(gameplay_times, audio_items, project_handler, media_pool_handler)
    reset_playhead_position(project_handler)


def get_H169FHD_media_pool_dir_items(media_pool_handler):
    """
    Importa toda la media compatible dentro de una lista de rutas del disco duro, a un
    directorio determinado del media pool.
    Args:
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
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
    media_pool_handler.SetCurrentFolder(horizontal_video_dir)
    items = horizontal_video_dir.GetClipList()
    return items


def add_timeline(timeline, track, H169FHD_items, project_handler, media_pool_handler):
    """
    Agrega una línea del tiempo del media pool en la línea de tiempo actual.
    Args:
        timeline (str): Nombre de la línea del tiempo que se desea agregar.
        track (str): Nombre del track donde se desea agregar la línea del tiempo.
        H169FHD_items (list): Lista de media pool itemas correspondientes al directorio H16.9FHD.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    timeline_asset = get_asset_by_name(timeline, H169FHD_items)
    intro_clip_info = generate_clip_info(
        timeline_asset, track, project_handler, track_type=TRACK_TYPE_VIDEO)
    logger.info(f'intro_clip_info {intro_clip_info}')
    media_pool_handler.AppendToTimeline([intro_clip_info])


def create_content(project_handler, media_pool_handler):
    """
    Crea el contenido del video, vinculando hook, intro y content.
    Args:
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_CONTENT, project_handler)
    H169FHD_items = get_H169FHD_media_pool_dir_items(media_pool_handler)
    add_timeline(TIMELINE_NAME_HOOK, CONTENT_TRACK_GAMEPLAY, H169FHD_items,
                 project_handler, media_pool_handler)
    add_timeline(TIMELINE_NAME_INTRO, CONTENT_TRACK_GAMEPLAY, H169FHD_items,
                 project_handler, media_pool_handler)
    add_timeline(TIMELINE_NAME_SUBJECT, CONTENT_TRACK_GAMEPLAY, H169FHD_items,
                 project_handler, media_pool_handler)
    reset_playhead_position(project_handler)


def add_outro(video_items, project_handler, media_pool_handler):
    """
    Agrega el clip del outro en la línea de tiempo actual.
    Args:
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    intro_asset = get_asset_by_name(ASSET_VIDEO_NAME_OUTRO, video_items)
    intro_clip_info = generate_clip_info(
        intro_asset, OUTRO_TRACK, project_handler, track_type=TRACK_TYPE_VIDEO)
    logger.info(f'intro_clip_info {intro_clip_info}')
    media_pool_handler.AppendToTimeline([intro_clip_info])


def create_canvas(video_items, project_handler, media_pool_handler):
    """
    Importa el video de outro en la línea del tiempo que servirá de lienzo o fondo.
    Args:
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_CANVAS, project_handler)
    add_outro(video_items, project_handler, media_pool_handler)
    reset_playhead_position(project_handler)


def generate_clip_info_for_timecode(clip, track, start_timecode,
                                    project_handler, media_type=None, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene información del media clip en cuestión de forma entendible por DaVinci Resolve.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_type (int): Valor opcional entero para usar constantes media type del api de davinci resolve.
        track_type (str): Valor opcional cadena para usar constantes track type del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    track_index = get_track_index(track, project_handler, track_type)
    clip_properties = clip.GetClipProperty()
    clip_info = {
        'mediaPoolItem': clip,
        'trackIndex': track_index,
        'startFrame' : START_FRAME,
        'endFrame' : clip_properties['End'] }
    logger.info(f'preparing {clip.GetName()} clip to add to {track} track')
    return clip_info


def add_timeline_in_timecode(timeline, track, start_timecode, H169FHD_items,
                             project_handler, media_pool_handler):
    """
    Agrega una línea del tiempo del media pool en la línea de tiempo actual.
    Args:
        timeline (str): Nombre de la línea del tiempo que se desea agregar.
        track (str): Nombre del track donde se desea agregar la línea del tiempo.
        start_timecode (str): Timecode de inicio.
        H169FHD_items (list): Lista de media pool itemas correspondientes al directorio H16.9FHD.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    timeline_asset = get_asset_by_name(timeline, H169FHD_items)
    intro_clip_info = generate_clip_info_for_timecode(
        timeline_asset, track, start_timecode, project_handler,
        track_type=TRACK_TYPE_VIDEO)
    logger.info(f'intro_clip_info {intro_clip_info}')
    media_pool_handler.AppendToTimeline([intro_clip_info])


def create_main(project_handler, media_pool_handler):
    """
    Crea el contenido del video, vinculando hook, intro y content.
    Args:
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_MAIN, project_handler)
    H169FHD_items = get_H169FHD_media_pool_dir_items(media_pool_handler)
    add_timeline(TIMELINE_NAME_CONTENT, MAIN_CONTENT_TRACK, H169FHD_items,
                 project_handler, media_pool_handler)
    add_timeline(TIMELINE_NAME_CANVAS, MAIN_CANVAS_TRACK, H169FHD_items,
                 project_handler, media_pool_handler)
    reset_playhead_position(project_handler)


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
    subject_timeranges = params['gameplay_details']['subject']
    automate_actions = params['gameplay_details']['enable_automated_manual_actions']
    create_hook(hook_timeranges, video_items, audio_items, project, media_pool, resolve, automate_actions)
    #create_intro(video_items, project, media_pool)
    #create_subject(subject_timeranges, video_items, audio_items, project, media_pool)
    #   create_content(project, media_pool)
    #create_canvas(video_items, project, media_pool)
    #   create_main(project, media_pool)

    # guardar cambios
    project_manager.SaveProject()
    if params['autoclose']:
        wait_for(SECONDS_TO_WAIT_FOR_PROJECT_SAVING, INFO_MESSAGE_SAVING_PROJECT)
        project_manager.CloseProject(project)
        wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
        resolve.Quit()


if __name__ == '__main__':
    main()
