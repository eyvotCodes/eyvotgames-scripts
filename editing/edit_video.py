#!/usr/bin/python3
import datetime
import json
import logging
import os
import psutil
import time
import re
import subprocess
import DaVinciResolveScript as davinci_resolve_script

from dotenv import load_dotenv
from pynput.mouse import Button, Controller
from tqdm import tqdm


# parámetros iniciales
load_dotenv()
PARAMS_JSON_FILE_PATH = \
    os.environ.get('EYVOT_GAMES_EDIT_VIDEO_PARAMS', '') # params.json
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
COMPOSITE_MODE_DIFF = 3
DEFAULT_IMAGE_CLIP_DURATION_IN_SECONDS = 5

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
TIMELINE_NAME_VERTICAL = 'V16.9FHD'
VIDEO_VALID_EXTENSIONS = ['mp4', 'mov']
IMAGE_VALID_EXTENSIONS = ['png', 'jpg', 'jpeg']
AUDIO_VALID_EXTENSIONS = ['mp3', 'wav']
MEDIA_POOL_ITEM_TYPE_VIDEO = 'video'
MEDIA_POOL_ITEM_TYPE_IMAGE = 'image'
MEDIA_POOL_ITEM_TYPE_AUDIO = 'audio'
MEDIA_POOL_ITEM_TYPE_TIMELINE = 'timeline'
ASSET_AUDIO_NAME_MIC = 'mic'
ASSET_IMAGE_NAME_WATERMARK = 'watermark'
ASSET_VIDEO_NAME_CAMERA = 'camera'
ASSET_VIDEO_NAME_CAMFRAME = 'camframe'
ASSET_VIDEO_NAME_GAMEPLAY = 'gameplay'
ASSET_VIDEO_NAME_INTRO = 'intro'
ASSET_VIDEO_NAME_OUTRO = 'outro'
ASSET_SHORT_OVERLAY = 'short_overlay'
ASSET_SHORT_BACKGROUND = 'short_background'
HOOK_TRACK_GAMEPLAY = 'gameplay'
HOOK_TRACK_CAMERA = 'camera'
HOOK_TRACK_CAMFRAME = 'camframe'
HOOK_TRACK_MIC = 'mic'
HOOK_TRACK_TITLE = 'title'
SHORT_TRACK_BACKGROUND = 'background'
SHORT_TRACK_OVERLAY = 'overlay'
HOOK_TITLE = 'Más adelante en este video...'
INTRO_TRACK = 'intro'
SUBJECT_TRACK_GAMEPLAY = 'gameplay'
SUBJECT_TRACK_CAMERA = 'camera'
SUBJECT_TRACK_CAMFRAME = 'camframe'
SUBJECT_TRACK_MIC = 'mic'
CONTENT_TRACK_GAMEPLAY = 'gameplay'
OUTRO_TRACK = 'outro'
MAIN_CANVAS_TRACK = 'canvas'
MAIN_CONTENT_TRACK = 'content'
H169HD_MAIN_TRACK = 'main'
H169HD_WATERMARK_TRACK = 'watermark'
VIDEO_TYPE_GAMEPLAY = 'gameplay'
VIDEO_TYPE_CLIP = 'clip'
VIDEO_TYPE_CLIPS = 'clips'
VIDEO_TYPE_SHORTS = 'shorts'
START_TIMECODE = '01:00:00:00'
SHORT_MAX_DURATION_IN_SECONDS = 59
START_FRAME = 0
SECONDS_OF_OUTRO_TRANSITION = 1
OUTRO_TRANSFORM_SIZE = 0.325
OUTRO_TRANSFORM_CENTER_X = 0.185
OUTRO_TRANSFORM_CENTER_Y = 0.288
CAMERA_PROPERTIES = [
    ('ZoomX', 0.285),
    ('ZoomY', 0.285),
    ('CropLeft', 420),
    ('CropRight', 420),
    ('AnchorPointX', 1082)]
WATERMARK_PROPERTIES = [
    ('CompositeMode', COMPOSITE_MODE_DIFF)]
HOOK_TITLE_PROPERTIES = [
    ('ZoomX', 0.450),
    ('ZoomY', 0.450),
    ('AnchorPointX', 0),
    ('AnchorPointY', 850),
    ('Opacity', 50)]
SHORT_GAMEPLAY_PROPERTIES = [
    ('ZoomX', 2.080),
    ('ZoomY', 2.080),
    ('AnchorPointY', 90)]
SHORT_CAMERA_PROPERTIES = [
    ('ZoomX', 2.080),
    ('ZoomY', 2.080),
    ('AnchorPointX', 650.00),
    ('AnchorPointY', -591.00),
    ('CropLeft', 885.00),
    ('CropRight', 15.00),
    ('CropTop', 214.00),
    ('CropBottom', 200.00)]

# mouse manual actions
# el delay se usa para evitar conflictos con el
# autosaving de DaVinci Resolve
MANUAL_ACTIONS_SECONDS_OF_DELAY = 4
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
MANUAL_ACTIONS_FOR_SUBJECT = """
L Click {"x":1228, "y":41}
L Click {"x":1254, "y":43}
L Click {"x":805, "y":858}
R Click {"x":817, "y":858}
L Click {"x":846, "y":867}
L Click {"x":810, "y":644}
R Click {"x":826, "y":642}
L Click {"x":850, "y":656}
L Click {"x":805, "y":677}
R Click {"x":821, "y":679}
L Click {"x":842, "y":690}
L Click {"x":725, "y":799}
L Click {"x":1334, "y":42}
"""

# info messages
INFO_MESSAGE_LOADING_DAVINCI_RESOLVE = 'Abriendo DaVinci Resolve'
INFO_MESSAGE_EXITING_DAVINCI_RESOLVE = 'Cerrando DaVinci Resolve'
INFO_MESSAGE_SAVING_PROJECT  = 'Guardando cambios'
INFO_MESSAGE_REPOSITIONING_PLAYHEAD  = 'Reposicionando PlayHead'
INFO_MESSAGE_PROCESSING_MANUAL_ACTIONS = 'Procesando Acciones Manuales Simuladas'
INFO_MESSAGE_WAIT_FOR_USER_INPUT = 'Presione cualquier tecla para continuar...'
INFO_MESSAGE_BAD_RANGE = 'Rango mal formado:'

# error messages
ERROR_MESSAGE_JSON_FILE_NOT_FOUND = 'No se pudo encontrar el archivo JSON.'
ERROR_MESSAGE_JSON_SYNTAX = 'Error de sintaxis en archivo JSON.'
ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND = 'No se encontró el proyecto base en DaVinci Resolve.'
ERROR_MESSAGE_MEDIA_DIR_NOT_FOUND = 'No se encontró el directorio en el Media Pool.'
ERROR_MESSAGE_TIMELINE_NOT_FOUND = 'No se encontró el timeline en el proyecto.'
ERROR_MESSAGE_ASSET_NOT_FOUND = 'No se encontró el asset en la lista dada.'
ERROR_MESSAGE_INCORREC_TIMESTRIG_FORMAT = 'Formato de timestring hh:mm:ss incorrecto.'
ERROR_MESSAGE_INVALID_VIDEO_TYPE = 'El tipo de video indicado no es válido.'
ERROR_MESSAGE_INVALID_SHORT_DURATION = 'La duración del short no es válida.'
ERROR_MESSAGE_INVALID_TIMERANGE = 'El rango de tiempo no es válido.'
ERROR_MESSAGE_INVALID_ASSET_TYPE = 'El tipo de asset no es válido.'

# guide messages
GUIDE_MESSAGE_ADD_OUTRO_KEYFRAMES = 'Agrega los KeyFrames a\nCenter X Y  ◇ → ◆\nSize        ◇ → ◆'
GUIDE_MESSAGE_ADD_OUTRO_TRANSFORM_NODE =\
    'Coloca el nodo de transformación entre los nodos de entrada y salida'
GUIDE_MESSAGE_ALIGN_CONTENT_WITH_CANVAS =\
    'Alínea el final del Track Canvas con el final del Track Content'
GUIDE_MESSAGE_ALIGN_INTRO_WITH_HOOK_AND_SUBJECT =\
    'Mueve el intro al Track de arriba y sobreponlo 14 FPS sobre el Hook y el Subject'

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
    """
    Simula acciones de click izquierdo y derecho. Para ello se pasa una cadena de
    acciones, donde cada línea es una instrucción diferente de click. El formato
    es el siguiente:
    L Click {"x":10, "y":20}
    R Click {"x":30, "y":40}
    Las líneas que inician con L serán click izquierdo y las que inician con R
    serán click derecho, para ambos casos se proporciona después de un espacio
    un objeto JSON con las coordenadas donde se simulará el click.
    Args:
        actions (str): Cadena de acciones.
    """
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
        json_start_index = 7
        coords = eval(click[json_start_index:])
        mouse.position = (coords['x'], coords['y'])
        mouse.click(button, 1)


def wait_for_user_input():
    """
    Pausa la ejecución del programa hasta que el usuario presione la
    tecla "enter".
    Ideal para realizar acciones manuales intermedias durante el proceso
    automatizado de edición.
    """
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


def get_valid_extensions_for_asset_type(asset_type):
    """
    Obtiene la lista de extensiones válidas para un tipo de asset (video, imágen o audio).
    Args:
        asset_type (str): Tipo de asset por obtener sus extensiones válidas.
    Returns:
        list: Lista de extensiones válidas para el tipo de asset.
    Raises:
        Exception: Si el tipo de asset no es válido.
    """
    if asset_type == MEDIA_POOL_ITEM_TYPE_VIDEO\
            or asset_type == MEDIA_POOL_ITEM_TYPE_TIMELINE:
        return VIDEO_VALID_EXTENSIONS
    elif asset_type == MEDIA_POOL_ITEM_TYPE_IMAGE:
        return IMAGE_VALID_EXTENSIONS
    elif asset_type == MEDIA_POOL_ITEM_TYPE_AUDIO:
        return AUDIO_VALID_EXTENSIONS
    else:
        raise Exception(ERROR_MESSAGE_INVALID_ASSET_TYPE + '\n' + asset_type)


def get_asset_by_name(name, media_pool_items, asset_type):
    """
    Obtiene un media pool item buscándolo por su nombre.
    Args:
        name (str): Nombre del asset a obtener.
        media_pool_items (list): Lista de assets donde se realizará la búsqueda.
        asset_type (str): Tipo de asset por obtener (video, imágen o audio).
    Returns:
        obj: Media Pool Item del asset buscado.
    Raises:
        Exception: Si el asset no ha sido encontrado.
    """
    valid_extensions = get_valid_extensions_for_asset_type(asset_type)
    are_files_with_extension = asset_type != MEDIA_POOL_ITEM_TYPE_TIMELINE
    number_of_items = len(media_pool_items)
    for item_index in range(number_of_items):
        current_asset = media_pool_items[item_index]
        for extension in valid_extensions:
            media_pool_item_name = name
            if are_files_with_extension:
                media_pool_item_name = media_pool_item_name + '.' + extension
            if current_asset.GetName() == media_pool_item_name:
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
    Args:
        track_name (str): Nombre del track del cual se obtendrá su índice.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        track_type (str): Valor opcional cadena para usar constantes track type del api de davinci resolve.
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


def get_clip_duration_in_frames(clip):
    """
    Obtiene la cantidad de frames de un clip.
    Args:
        clip (obj): Objeto clip del api de dacinci resolve.
    """
    long_timestring = clip.GetClipProperty("duration")
    timestring = ':'.join(long_timestring.split(':')[:-1])
    total_seconds = timestring_to_second(timestring)
    total_frames = total_seconds * FPS
    return total_frames


def get_default_image_clip_duration_in_frames():
    """
    Obtiene la cantidad de frames que DaVinci Resolve asigna por defecto
    a los clips de imagen.
    """
    return DEFAULT_IMAGE_CLIP_DURATION_IN_SECONDS * FPS


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
        if end_second <= start_second:
            logger.info(f'{INFO_MESSAGE_BAD_RANGE} ["{start_timestring}", "{end_timestring}"]')
        hook_total_seconds += end_second - start_second
    
    hook_total_frames = hook_total_seconds * FPS
    logger.info(f'hook_total_frames {hook_total_frames}')
    camframe_total_frames = get_clip_duration_in_frames(camframe_clip)
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
    gameplay_asset = get_asset_by_name(ASSET_VIDEO_NAME_GAMEPLAY, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    camera_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMERA, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    camframe_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMFRAME, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    micro_asset = get_asset_by_name(ASSET_AUDIO_NAME_MIC, audio_items, MEDIA_POOL_ITEM_TYPE_AUDIO)
    micro_clips_info = generate_clip_info_list_from_highlights(
        micro_asset, highlights_times, HOOK_TRACK_MIC, project_handler, track_type=TRACK_TYPE_AUDIO)
    logger.info(f'micro_clips_info {micro_clips_info}')
    media_pool_handler.AppendToTimeline(micro_clips_info)


def add_title_to_hook(project_handler, resolve_handler):
    """
    Agrega el texto de título del hook.
    Args:
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        resolve_handler (obj): Objeto para controlar la instancia de davinci resolve.
    """
    timeline = project_handler.GetCurrentTimeline()
    title = timeline.InsertFusionTitleIntoTimeline('Text+')
    for prop in HOOK_TITLE_PROPERTIES:
        title.SetProperty(*prop)
    switch_to_page(PAGE_FUSION_NAME, resolve_handler)
    fusion = resolve_handler.Fusion()
    comp = fusion.GetCurrentComp()
    template = comp.FindTool('Template')
    comp.SetActiveTool(template)
    template.SetInput('StyledText', HOOK_TITLE, 0)
    resolve_handler.OpenPage(PAGE_EDIT_NAME, resolve_handler)


def create_hook_for_gameplay(highlights_times, video_items, audio_items,
                project_handler, media_pool_handler, resolve_handler,
                automate_actions, use_mic_audio):
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
        use_mic_audio (bool): Indica si se usará el audio del micrófono (si no, se usará el del video).
    """
    switch_to_timeline(TIMELINE_NAME_HOOK, project_handler)
    logger.info(f'Hook Hightlights Timeranges: {highlights_times}')
    add_title_to_hook(project_handler, resolve_handler)
    wait_for_user_input()
    add_gameplay_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    add_camera_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    add_camframe_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    if use_mic_audio:
        add_micro_to_hook(highlights_times, audio_items, project_handler, media_pool_handler)
    if automate_actions:
        process_manual_actions(MANUAL_ACTIONS_FOR_HOOK)
    else:
        wait_for_user_input()


def create_hook_for_clip(highlights_times, video_items, project_handler, media_pool_handler, resolve_handler):
    """
    Crear el gancho inicial del video a partir de una lista de rangos de tiempo,
    cada elemento de la lista, a su vez es otra lista que solo pueden tener
    2 valores cadena en formato hh:mm:ss, el inicio y el fin del rango del tiempo.
    El inicio es el primer elemento de la lista y el fin es el segungo elemento de
    la lista.
    Args:
        highlights_times (list): Rangos de tiempo de las partes más emocionantes del video.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
        resolve_handler (obj): Objeto para controlar la instancia de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_HOOK, project_handler)
    logger.info(f'Hook Hightlights Timeranges: {highlights_times}')
    add_title_to_hook(project_handler, resolve_handler)
    wait_for_user_input()
    add_gameplay_to_hook(highlights_times, video_items, project_handler, media_pool_handler)
    wait_for_user_input()


def generate_clip_info(clip, track, project_handler, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene información del media clip en cuestión de forma entendible por DaVinci Resolve.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
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
    intro_asset = get_asset_by_name(ASSET_VIDEO_NAME_INTRO, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    gameplay_asset = get_asset_by_name(ASSET_VIDEO_NAME_GAMEPLAY, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    camera_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMERA, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    camframe_asset = get_asset_by_name(ASSET_VIDEO_NAME_CAMFRAME, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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
    micro_asset = get_asset_by_name(ASSET_AUDIO_NAME_MIC, audio_items, MEDIA_POOL_ITEM_TYPE_AUDIO)
    micro_clips_info = generate_clip_info_list_from_highlights(
        micro_asset, highlights_times, SUBJECT_TRACK_MIC, project_handler, track_type=TRACK_TYPE_AUDIO)
    logger.info(f'micro_clips_info {micro_clips_info}')
    media_pool_handler.AppendToTimeline(micro_clips_info)


def create_subject_for_gameplay(gameplay_times, video_items, audio_items, project_handler,
                                media_pool_handler, automate_actions, use_mic_audio):
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
        use_mic_audio (bool): Indica si se usará el audio del micrófono (si no, se usará el del video).
    """
    switch_to_timeline(TIMELINE_NAME_SUBJECT, project_handler)
    logger.info(f'Gameplay Timeranges: {gameplay_times}')
    add_gameplay_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    add_camera_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    add_camframe_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    if use_mic_audio:
        add_micro_to_hook(gameplay_times, audio_items, project_handler, media_pool_handler)
    if automate_actions:
        process_manual_actions(MANUAL_ACTIONS_FOR_SUBJECT)
    else:
        wait_for_user_input()


def create_subject_for_clip(gameplay_times, video_items, project_handler, media_pool_handler):
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
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_SUBJECT, project_handler)
    logger.info(f'Gameplay Timeranges: {gameplay_times}')
    add_gameplay_to_subject(gameplay_times, video_items, project_handler, media_pool_handler)
    wait_for_user_input()


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
    timeline_asset = get_asset_by_name(timeline, H169FHD_items, MEDIA_POOL_ITEM_TYPE_TIMELINE)
    intro_clip_info = generate_clip_info(
        timeline_asset, track, project_handler, track_type=TRACK_TYPE_VIDEO)
    logger.info(f'intro_clip_info {intro_clip_info}')
    items = media_pool_handler.AppendToTimeline([intro_clip_info])
    return items[0]


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
    print(GUIDE_MESSAGE_ALIGN_INTRO_WITH_HOOK_AND_SUBJECT)
    wait_for_user_input()


def add_outro(video_items, project_handler, media_pool_handler):
    """
    Agrega el clip del outro en la línea de tiempo actual.
    Args:
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    intro_asset = get_asset_by_name(ASSET_VIDEO_NAME_OUTRO, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
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


def generate_clip_info_for_timecode(clip, track, project_handler, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene información del media clip en cuestión de forma entendible por DaVinci Resolve.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
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
    timeline_asset = get_asset_by_name(timeline, H169FHD_items, MEDIA_POOL_ITEM_TYPE_TIMELINE)
    intro_clip_info = generate_clip_info_for_timecode(
        timeline_asset, track, start_timecode, project_handler,
        track_type=TRACK_TYPE_VIDEO)
    logger.info(f'intro_clip_info {intro_clip_info}')
    media_pool_handler.AppendToTimeline([intro_clip_info])


def animate_content_to_outro_transition(item_content, item_canvas, resolve_handler):
    """
    Crea la animación de transición del contenido al outro del video.
    Args:
        item_content (obj): timeline item del contenido
        item_canvas (obj): timeline item del canvas
        resolve_handler (obj): Objeto para controlar la instancia de davinci resolve.
    """
    switch_to_page(PAGE_FUSION_NAME, resolve_handler)
    fusion = resolve_handler.Fusion()
    comp = fusion.GetCurrentComp()
    animation_start_frame = item_content.GetDuration() - item_canvas.GetDuration()
    animation_end_frame = animation_start_frame + FPS*SECONDS_OF_OUTRO_TRANSITION
    logger.info(f'animation_start_frame: {animation_start_frame}')
    logger.info(f'animation_end_frame: {animation_end_frame}')
    transform = comp.AddTool("Transform")
    comp.SetActiveTool(transform)

    comp.CurrentTime = animation_start_frame
    print(GUIDE_MESSAGE_ADD_OUTRO_KEYFRAMES)
    wait_for_user_input()

    comp.CurrentTime = animation_end_frame
    print(GUIDE_MESSAGE_ADD_OUTRO_KEYFRAMES)
    wait_for_user_input()
    transform.SetInput("Size", OUTRO_TRANSFORM_SIZE, comp.CurrentTime)
    transform.SetInput("Center", [OUTRO_TRANSFORM_CENTER_X, OUTRO_TRANSFORM_CENTER_Y], comp.CurrentTime)
    print(GUIDE_MESSAGE_ADD_OUTRO_TRANSFORM_NODE)
    wait_for_user_input()


def create_main(project_handler, media_pool_handler, resolve_handler):
    """
    Crea el contenido del video, vinculando hook, intro y content.
    Args:
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
        resolve_handler (obj): Objeto para controlar la instancia de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME_MAIN, project_handler)
    H169FHD_items = get_H169FHD_media_pool_dir_items(media_pool_handler)
    item_content = add_timeline(TIMELINE_NAME_CONTENT, MAIN_CONTENT_TRACK, H169FHD_items,
                                project_handler, media_pool_handler)
    item_canvas = add_timeline(TIMELINE_NAME_CANVAS, MAIN_CANVAS_TRACK, H169FHD_items,
                               project_handler, media_pool_handler)    
    reset_playhead_position(project_handler)
    animate_content_to_outro_transition(item_content, item_canvas, resolve_handler)
    switch_to_page(PAGE_EDIT_NAME, resolve_handler)
    print(GUIDE_MESSAGE_ALIGN_CONTENT_WITH_CANVAS)
    wait_for_user_input()


def generate_watermark_clip_info(watermark_clip, track, project_handler):
    """
    Obtiene información del media clip de marca de agua de forma entendible por DaVinci Resolve.
    Args:
        watermark_clip (obj): Clip de la marca de agua.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    track_index = get_track_index(track, project_handler, TRACK_TYPE_VIDEO)
    clip_info = {
        'mediaPoolItem': watermark_clip,
        'trackIndex': track_index }
    return [clip_info]


def create_H169FHD(image_items, project_handler, media_pool_handler):
    """
    Crea el contenido del video, vinculando contenido main y la marca de agua del canal.
    Args:
        image_items (list): Lista de assets de imágen del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    switch_to_timeline(TIMELINE_NAME, project_handler)
    H169FHD_items = get_H169FHD_media_pool_dir_items(media_pool_handler)
    add_timeline(TIMELINE_NAME_MAIN, H169HD_MAIN_TRACK, H169FHD_items,
                 project_handler, media_pool_handler)
    watermark_asset = get_asset_by_name(ASSET_IMAGE_NAME_WATERMARK, image_items, MEDIA_POOL_ITEM_TYPE_IMAGE)
    watermark_info = generate_watermark_clip_info(
        watermark_asset, H169HD_WATERMARK_TRACK, project_handler)
    logger.info(f'watermark_info {watermark_info}')
    watermark_items = media_pool_handler.AppendToTimeline(watermark_info)
    for item in watermark_items:
        for property in WATERMARK_PROPERTIES:
            item.SetProperty(*property)


def calculate_short_duration(short_timeranges):
    """
    Cacula la duración en segundos de un short.
    Args:
        short_timeranges (list): Lista de rangos de tiempo del short.
    """
    short_duration = 0
    for timeranges in short_timeranges:
        start_time = list(map(int, timeranges[0].split(':')))
        end_time = list(map(int, timeranges[1].split(':')))
        short_duration += (end_time[0] - start_time[0]) * 3600\
            + (end_time[1] - start_time[1]) * 60 + (end_time[2] - start_time[2])
    return short_duration


def valid_shorts_duration_or_stop(shorts_timeranges):
    """
    Verifica que ningún short exceda la duración máxima que pueden tener.
    Args:
        shorts_timeranges (list): Listas de rangos de tiempo de todos los shorts.
    """
    for index, short_timeranges in enumerate(shorts_timeranges):
        short_number = str(index + 1).zfill(2)
        short_duration = calculate_short_duration(short_timeranges)
        logger.info(f'short-{short_number}_duration: {short_duration}s')
        if short_duration > SHORT_MAX_DURATION_IN_SECONDS:
            raise Exception(f'{ERROR_MESSAGE_INVALID_SHORT_DURATION}'\
                            + f'\nshort-{short_number}:{short_duration}s > {SHORT_MAX_DURATION_IN_SECONDS}s')


def validate_timeranges(timeranges):
    """
    Verifica que no haya incoherencias o malformaciones en una serie de rangos de tiempo.
    Args:
        timeranges (list): Lista de rangos de tiempo por evaluar.
    """
    for index, timerange in enumerate(timeranges):
        start_time = timerange[0]
        end_time = timerange[1]
        if start_time >= end_time:
            raise Exception(f'{ERROR_MESSAGE_INVALID_TIMERANGE}'\
                            + f'\nrango: {index + 1}')


def generate_clip_info_list_for_short_background(clip, duration, track, project_handler,
                                                 media_type=None, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene una lista de directorios con información del media clip entendible por
    DaVinci Resolve. Esta información detalla cuántos clips de background de short se
    necesitarán para cubrir la duración del short, incluso si solo se necesita un
    segmento del mismo.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        duration (int): Duración del short en segundos.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_type (int): Valor opcional entero para usar constantes media type del api de davinci resolve.
        track_type (str): Valor opcional cadena para usar constantes track type del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    clips_info = []
    start_frame = 0
    end_frame = duration*FPS - NOT_OVERLAPPING_FRAME
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


def generate_clip_info_list_for_short_camframe(clip, duration, track, project_handler,
                                               media_type=None, track_type=TRACK_TYPE_VIDEO):
    """
    Obtiene una lista de directorios con información del media clip entendible por
    DaVinci Resolve. Esta información detalla cuántos clips de camframe se necesitarán
    para cubrir la duración del short, incluso si solo se necesita un segmento del mismo.
    Args:
        clip (obj): Media pool item del api de davinci resolve.
        duration (int): Duración del short en segundos.
        track (str): Nombre del track del timeline donde se desea agregar el clip.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_type (int): Valor opcional entero para usar constantes media type del api de davinci resolve.
        track_type (str): Valor opcional cadena para usar constantes track type del api de davinci resolve.
    Returns:
        dict: Lista de directorios con información del clip a importar.
    """
    short_total_frames = duration*FPS
    overlay_total_frames = get_clip_duration_in_frames(clip)
    number_of_full_overlays_needed = short_total_frames // overlay_total_frames
    is_partial_overlay_needed = (short_total_frames % overlay_total_frames) != 0
    track_index = get_track_index(track, project_handler, track_type)
    clips_info = []

    for _ in range(number_of_full_overlays_needed):
        clip_info = {
            'mediaPoolItem': clip,
            'trackIndex': track_index,
            'mediaType': track_type,
            'startFrame' : 0,
            'endFrame' : overlay_total_frames - NOT_OVERLAPPING_FRAME }
        clips_info.append(clip_info)

    if is_partial_overlay_needed:
        partial_frames_needed = short_total_frames \
            - overlay_total_frames*number_of_full_overlays_needed
        clip_info = {
            'mediaPoolItem': clip,
            'trackIndex': track_index,
            'mediaType': media_type,
            'startFrame' : 0,
            'endFrame' : partial_frames_needed - NOT_OVERLAPPING_FRAME }
        clips_info.append(clip_info)

    return clips_info


def edit_gameplay(hook_timeranges, video_items, audio_items, project, media_pool, resolve,
                  automate_actions, subject_timeranges, image_items, use_mic_audio):
    """
    Desencadena el proceso de edición de gameplay con la configuración dada por los parámetros.
    Args:
        hook_timeranges (list): Rangos de tiempo del hook del video.
        video_items (list): Lista de assets de video del media pool.
        audio_items (list): Lista de assets de audio del media pool.
        project (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool (obj): Objeto para controlar el media pool del api de davinci resolve.
        resolve (obj): Objeto para controlar la instancia de davinci resolve.
        automate_actions (str): Intrucciones de clicks para simulación de acciones manuales.
        subject_timeranges (list): Rangos de tiempo del contenido del video.
        image_items (list): Lista de assets de imágen del media pool.
        use_mic_audio (bool): Indica si se usará el audio del micrófono (si no, se usará el del video).
    """
    create_hook_for_gameplay(hook_timeranges, video_items, audio_items, project, media_pool, resolve,
                             automate_actions, use_mic_audio)
    create_intro(video_items, project, media_pool)
    create_subject_for_gameplay(subject_timeranges, video_items, audio_items, project, media_pool,
                                automate_actions, use_mic_audio)
    create_content(project, media_pool)
    create_canvas(video_items, project, media_pool)
    create_main(project, media_pool, resolve)
    create_H169FHD(image_items, project, media_pool)


def edit_clip(hook_timeranges, video_items, project, media_pool, resolve, subject_timeranges, image_items):
    """
    Desencadena el proceso de edición de clip con la configuración dada por los parámetros.
    Se usa para extraer partes de un video de gameplay ya editado, manteniendo el formato usual
    de los videos.
    Args:
        hook_timeranges (list): Rangos de tiempo del hook del video.
        video_items (list): Lista de assets de video del media pool.
        project (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool (obj): Objeto para controlar el media pool del api de davinci resolve.
        resolve (obj): Objeto para controlar la instancia de davinci resolve.
        subject_timeranges (list): Rangos de tiempo del contenido del video.
        image_items (list): Lista de assets de imágen del media pool.
    """
    create_hook_for_clip(hook_timeranges, video_items, project, media_pool, resolve)
    create_intro(video_items, project, media_pool)
    create_subject_for_clip(subject_timeranges, video_items, project, media_pool)
    create_content(project, media_pool)
    create_canvas(video_items, project, media_pool)
    create_main(project, media_pool, resolve)
    create_H169FHD(image_items, project, media_pool)


def edit_shorts(shorts_timeranges, video_items, project_handler, media_pool_handler):
    """
    Desencadena el proceso de edición de shorts con la configuración dada por los parámetros.
    Se usa para extraer shorts de un video de gameplay ya editado, pero transformándolo al
    formato usual de los shorts.
    Args:
        shorts_timeranges (list): Rangos de tiempo de los shorts por extraer.
        video_items (list): Lista de assets de video del media pool.
        project_handler (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool_handler (obj): Objeto para controlar el media pool del api de davinci resolve.
    """
    valid_shorts_duration_or_stop(shorts_timeranges)
    for index, timeranges in enumerate(shorts_timeranges):
        short_number = str(index + 1).zfill(2)
        switch_to_timeline(TIMELINE_NAME_VERTICAL, project_handler)
        short_timeline = project_handler.GetCurrentTimeline()
        short_timeline = short_timeline.DuplicateTimeline(f'{TIMELINE_NAME_VERTICAL}_{short_number}')

        background_asset = get_asset_by_name(ASSET_SHORT_BACKGROUND, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
        short_duration = calculate_short_duration(timeranges)
        background_clips_info = generate_clip_info_list_for_short_background(
            background_asset, short_duration, SHORT_TRACK_BACKGROUND, project_handler)
        logger.info(f'short-{short_number}_clips_info {background_clips_info}')
        gameplay_items = media_pool_handler.AppendToTimeline(background_clips_info)

        gameplay_asset = get_asset_by_name(ASSET_VIDEO_NAME_GAMEPLAY, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
        gameplay_clips_info = generate_clip_info_list_from_highlights(
            gameplay_asset, timeranges, HOOK_TRACK_GAMEPLAY, project_handler)
        logger.info(f'short-{short_number}_clips_info {gameplay_clips_info}')
        gameplay_items = media_pool_handler.AppendToTimeline(gameplay_clips_info)
        for timeline_item in gameplay_items:
            for property in SHORT_GAMEPLAY_PROPERTIES:
                timeline_item.SetProperty(*property)
        
        camera_clips_info = generate_clip_info_list_from_highlights(
            gameplay_asset, timeranges, HOOK_TRACK_CAMERA, project_handler)
        logger.info(f'short-{short_number}_clips_info {camera_clips_info}')
        camera_items = media_pool_handler.AppendToTimeline(camera_clips_info)
        for timeline_item in camera_items:
            for property in SHORT_CAMERA_PROPERTIES:
                timeline_item.SetProperty(*property)

        overlay_asset = get_asset_by_name(ASSET_SHORT_OVERLAY, video_items, MEDIA_POOL_ITEM_TYPE_VIDEO)
        short_duration = calculate_short_duration(timeranges)
        gameplay_clips_info = generate_clip_info_list_for_short_camframe(
            overlay_asset, short_duration, SHORT_TRACK_OVERLAY, project_handler)
        logger.info(f'short-{short_number}_clips_info {gameplay_clips_info}')
        gameplay_items = media_pool_handler.AppendToTimeline(gameplay_clips_info)

        wait_for_user_input()


def edit_video(hook_timeranges, video_items, audio_items, project, media_pool, resolve,
               automate_actions, subject_timeranges, image_items, video_type,
               shorts_timeranges, use_mic_audio):
    """
    Elige que proceso de edición debe ser desencadenado, dependiendo del tipo de video
    que se desea producir.
    Args:
        hook_timeranges (list): Rangos de tiempo del hook del video.
        video_items (list): Lista de assets de video del media pool.
        audio_items (list): Lista de assets de audio del media pool.
        project (obj): Objeto para controlar el proyecto del api de davinci resolve.
        media_pool (obj): Objeto para controlar el media pool del api de davinci resolve.
        resolve (obj): Objeto para controlar la instancia de davinci resolve.
        automate_actions (str): Intrucciones de clicks para simulación de acciones manuales.
        subject_timeranges (list): Rangos de tiempo del contenido del video.
        image_items (list): Lista de assets de imágen del media pool.
        video_type (str): Tipo de video que se editará.
        shorts_timeranges (list): Rangos de tiempo de los shorts por extraer.
        use_mic_audio (bool): Indica si se usará el audio del micrófono (si no, se usará el del video).
    """
    validate_timeranges(hook_timeranges)
    validate_timeranges(subject_timeranges)

    if video_type == VIDEO_TYPE_GAMEPLAY:
        edit_gameplay(hook_timeranges, video_items, audio_items, project, media_pool, resolve,
                      automate_actions, subject_timeranges, image_items, use_mic_audio)
    elif video_type == VIDEO_TYPE_CLIP:
        edit_clip(hook_timeranges, video_items, project, media_pool, resolve,
                  subject_timeranges, image_items)
    elif video_type == VIDEO_TYPE_SHORTS:
        edit_shorts(shorts_timeranges, video_items, project, media_pool)
    elif video_type == VIDEO_TYPE_CLIPS:
        pass
    else:
        raise Exception(ERROR_MESSAGE_INVALID_VIDEO_TYPE + '\n' + video_type)


def main():
    """
    Entry point del script, inicializa la ejecución del script y parametriza las
    funciones que harán el trabajo de edición. El proceso consta de los siguientes
    pasos:
    1. Abrir DaVinci Resolve.
    2. Abrir o crear el archivo base para trabajar.
    3. Obtener parámetros para producir el video.
    4. Editar video.
    5. Guardar cambios en el proyecto de DaVinci Resolve.
    """
    # abrir davinci resolve
    open_davinci_resolve()

    # abrir o crear el archivo base para trabajar
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
    if project is None:
        if params['autoclose']:
            wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
            resolve.Quit()
        raise Exception(ERROR_MESSAGE_BASE_PROJECT_NOT_FOUND + '\n' + BASE_PROJECT_NAME)
    project.SetName(project_name)
    logger.info(f'Project Name: {project_name}')
    media_pool = project.GetMediaPool()
    assets_dirs = params['gameplay_details']['assets']
    video_type = params['video_type'] # gameplay, clip, shorts

    # obtener parámetros para producir el video
    switch_to_page(PAGE_EDIT_NAME, resolve)
    logger.info(f'Media Items to Load: {assets_dirs}')
    audio_items = import_to_media_pool_dir(assets_dirs['audio'], AUDIO_MEDIA_DIR, media_pool)
    image_items = import_to_media_pool_dir(assets_dirs['image'], IMAGE_MEDIA_DIR, media_pool)
    video_items = import_to_media_pool_dir(assets_dirs['video'], VIDEO_MEDIA_DIR, media_pool)
    logger.info(f'Media Pool Items Loaded: {audio_items}, {image_items}, {video_items}')
    hook_timeranges = params['gameplay_details']['hook']
    subject_timeranges = params['gameplay_details']['subject']
    shorts_timeranges = params['gameplay_details']['shorts']
    use_mic_audio = params['gameplay_details']['use_mic_audio']
    automate_actions = params['gameplay_details']['enable_automated_manual_actions']

    # editar video
    edit_video(hook_timeranges, video_items, audio_items, project, media_pool, resolve,
               automate_actions, subject_timeranges, image_items, video_type,
               shorts_timeranges, use_mic_audio)

    # guardar cambios en el proyecto de DaVinci Resolve
    project_manager.SaveProject()
    if params['autoclose']:
        wait_for(SECONDS_TO_WAIT_FOR_PROJECT_SAVING, INFO_MESSAGE_SAVING_PROJECT)
        project_manager.CloseProject(project)
        wait_for(SECONDS_TO_WAIT_FOR_DAVINCI_TO_QUIT, INFO_MESSAGE_EXITING_DAVINCI_RESOLVE)
        resolve.Quit()


if __name__ == '__main__':
    main()
