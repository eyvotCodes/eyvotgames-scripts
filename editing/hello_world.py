#!/usr/bin/python3
import DaVinciResolveScript as davinci_resolve_script

# project setup
PROJECT_NAME = "00-test"
TIMELINE_NAME = "My Automated Timeline"
TEXT_TITLE = "Hola Mundo! DaVinci Resolve"

# davinci resolve api values
DVR_SCRIPT_APP = "Resolve"


# create project
resolve = davinci_resolve_script.scriptapp(DVR_SCRIPT_APP)
project_manager = resolve.GetProjectManager()
current_project = project_manager.GetCurrentProject()
project_manager.CloseProject(current_project)
project_manager.DeleteProject(PROJECT_NAME)
project = project_manager.CreateProject(PROJECT_NAME)

# timeline
media_pool = project.GetMediaPool()
timeline = media_pool.CreateEmptyTimeline(TIMELINE_NAME)
project.SetCurrentTimeline(timeline)

# título
title = timeline.InsertFusionTitleIntoTimeline("Text+")
resolve.OpenPage("fusion")
fusion = resolve.Fusion()
comp = fusion.GetCurrentComp()
print("comp:", dir(comp))
print("tools:", comp.GetToolList())
template = comp.FindTool("Template")
print("template:", dir(template))
comp.SetActiveTool(template)
template.SetInput("StyledText", TEXT_TITLE, 0)
resolve.OpenPage("edit")

# save changes
project_manager.SaveProject(project)

# cerrar proyecto y programa
# project_manager.CloseProject(project)
# resolve.Quit()
