#!/usr/bin/python3
import DaVinciResolveScript as davinci_resolve_script


# TODO: crear assets que se requerirán para desarrollar el script


"""
TODO: Inicializar proyecto
* Crear proyecto
  - Función main desde la cual se llamarán las demás funciones
  - Inicializar resolve y project manager en función main
  - Crear proyecto con timestamp YYMMDD en el nombre + "_" + clave nombre videojuego + "_" + "gameplay"
"""


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
