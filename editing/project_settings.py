#!/usr/bin/python3
import DaVinciResolveScript as davinci_resolve_script

"""
INSTRUCCIONES:
1. Hacer Copy + Paste de forma manual del proyecto 00-base
2. Ejecutar el script

Nota: No existe forma de duplicar un proyecto a través de DRScript, podría
intentarse de forma manual con un script de bash, pero se podría corromper
la consistencia de los datos (DR guarda los proyectos en una base de datos
de PostgreSQL), así que es más seguro utilizar la propia API del programa
para realizar dicha acción.
A futuro podría considerarse investigar cómo se estructuran de forma interna
los proyectos en PostgreSQL haciendo Reverse Engineering o simplemente
esperar si en próximas versiones del API se introduce esa capacidad.
De momento es mejor opción hacerlo de forma manual, ya que no consume mucho
tiempo dicha tarea, y es una solución viable.
"""

# project setup
PROJECT_NAME = "00-base (Copy)"
PROJECT_NAME_NEW = "00-today_video"
TIMELINE_NAME = "My Automated Timeline"

# davinci resolve api values
DVR_SCRIPT_APP = "Resolve"


# create project
resolve = davinci_resolve_script.scriptapp(DVR_SCRIPT_APP)
project_manager = resolve.GetProjectManager()
current_project = project_manager.GetCurrentProject()
project_manager.CloseProject(current_project)
project = project_manager.LoadProject(PROJECT_NAME)

# project settings
project.SetName(PROJECT_NAME_NEW)

# timeline
media_pool = project.GetMediaPool()
timeline = media_pool.CreateEmptyTimeline(TIMELINE_NAME)
project.SetCurrentTimeline(timeline)

# save changes
project_manager.SaveProject()

# cerrar proyecto y programa
# project_manager.CloseProject(project)
# resolve.Quit()
