#!/usr/bin/python3

import argparse
import datetime
import screeninfo
import sys
import time

from pynput import keyboard, mouse


OS_MAC_NAME = "darwin"
TEN_MILLISECONDS = 0.01
AUDACITY_SOFTWARE_NAME = "audacity" # macbook air m1
AUDACITY_START_X = 1270
AUDACITY_START_Y = 35
AUDACITY_STOP_X = 1150
AUDACITY_STOP_Y = 35
OBS_STUDIO_SOFTWARE_NAME = "obs-studio" # macbook air m1
OBS_STUDIO_START_X = 950
OBS_STUDIO_START_Y = 1000
OBS_STUDIO_STOP_X = 950
OBS_STUDIO_STOP_Y = 1000
OBS_WIN_SOFTWARE_NAME = "obs-win" # xps13
OBS_WIN_START_X = 3650
OBS_WIN_START_Y = 1450
OBS_WIN_STOP_X = 3650
OBS_WIN_STOP_Y = 1450
HELP_TEXT = "Este script permite generar una lista de automatizaciones de clicks para los programas deseados.\n\
Si indica hora ya transcurrida en el día para su ejecución, el script se ejecutará de inmediato.\n\n\
    Los parámetros disponibles son:\n\
    --action: accion deseada a realizar con clicks start/stop\n\
    --in-apps : lista de nombres de cada software separada por espacios\n\
    --at : hora de la ejecución del script en formato hh:mm de las 24 horas\n\
    --help : muestra esta ayuda\n"


def click_on_monitor(is_primary_monitor, x, y):
    monitors = screeninfo.get_monitors()
    target_monitor = monitors[0] if is_primary_monitor else monitors[-1]
    target_x = target_monitor.x + x
    target_y = target_monitor.y + y
    mouse_controller = mouse.Controller()
    mouse_controller.position = (target_x, target_y)
    time.sleep(TEN_MILLISECONDS)
    mouse_controller.click(mouse.Button.left, 1)


def automate_clicks(input_data, action):
    if action == "start":
        coordinates = "start_coordinates"
    elif action == "stop":
        coordinates = "stop_coordinates"
    else:
        raise ValueError("La acción debe ser start o stop")

    for click_data in input_data["clicks"]:
        x = click_data[coordinates]["x"]
        y = click_data[coordinates]["y"]
        click_on_monitor(input_data["is_primary_monitor"], x, y)


def print_animation(message, duration):
    for i in range(duration):
        print(message[i % len(message)], end="\r", flush=True)
        time.sleep(0.1)


def wait_until_execution_time(input_data):
    execution_hour = int(input_data["execution_time"].split(":")[0])
    execution_minute = int(input_data["execution_time"].split(":")[1])
    now = datetime.datetime.now()
    execution_time = now.replace(hour=execution_hour, minute=execution_minute, second=0, microsecond=0)
    seconds_remaining = (execution_time - now).total_seconds()

    for i in range(int(seconds_remaining)):
        print("{:.0f} segundos  ".format(seconds_remaining - i), end="\r", flush=True)
        time.sleep(1)


def create_clicks(input_data, software_names):
    clicks = []
    for software_name in software_names.split():
        if software_name == AUDACITY_SOFTWARE_NAME:
            clicks.append({
                "software_name": AUDACITY_SOFTWARE_NAME,
                "start_coordinates": {"x": AUDACITY_START_X, "y": AUDACITY_START_Y},
                "stop_coordinates": {"x": AUDACITY_STOP_X, "y": AUDACITY_STOP_Y}})
        elif software_name == OBS_STUDIO_SOFTWARE_NAME:
            clicks.append({"software_name": OBS_STUDIO_SOFTWARE_NAME,
                "start_coordinates": {"x": OBS_STUDIO_START_X, "y": OBS_STUDIO_START_Y},
                "stop_coordinates": {"x": OBS_STUDIO_STOP_X, "y": OBS_STUDIO_STOP_Y}})
        elif software_name == OBS_WIN_SOFTWARE_NAME:
            clicks.append({"software_name": OBS_WIN_SOFTWARE_NAME,
                "start_coordinates": {"x": OBS_WIN_START_X, "y": OBS_WIN_START_Y},
                "stop_coordinates": {"x": OBS_WIN_STOP_X, "y": OBS_WIN_STOP_Y}})
    input_data["clicks"] = clicks


def parse_arguments():
    parser = argparse.ArgumentParser(description="Script para automatizar clicks.",
        epilog=HELP_TEXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-x', '--action', required=True, type=str,
        choices=["start", "stop"], help='Acción a realizar start/stop')
    parser.add_argument('-i', '--in-apps', required=True, type=str,
        help='Lista de software names separados por espacios')
    parser.add_argument('-a', '--at', required=True, type=str,
        help='Hora programada en formato hh:mm')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print(args)

    input_data = {
        "is_primary_monitor": True,
        "clicks": [],
        "execution_time": args.at
    }

    create_clicks(input_data, args.in_apps)

    if sys.platform == OS_MAC_NAME:
        keyboard_controller = keyboard.Controller()
        keyboard_controller.press(keyboard.Key.cmd)

    wait_until_execution_time(input_data)
    automate_clicks(input_data, args.action)

    if sys.platform == OS_MAC_NAME:
        keyboard_controller.release(keyboard.Key.cmd)
