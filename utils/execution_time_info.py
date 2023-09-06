#!/usr/bin/python3
from pynput import keyboard
import time

timestamps = []
start_time = time.time()


def get_formatted_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

def on_key_release(key):
    try:
        if key == keyboard.Key.shift_r:
            elapsed_time = time.time() - start_time
            timestamps.append(get_formatted_time(elapsed_time))
            print(f"execution time - {get_formatted_time(elapsed_time)}")
        elif key == keyboard.Key.backspace:
            print("exiting...\n")
            return False  # Detiene el listener de teclado
    except AttributeError:
        pass

with keyboard.Listener(on_release=on_key_release) as listener:
    listener.join()

print("Lista de tiempos de ejecución:")
for idx, timestamp in enumerate(timestamps, start=1):
    print(f"{idx}. {timestamp}")
