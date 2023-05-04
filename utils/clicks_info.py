#!/usr/bin/python3
from pynput import mouse, keyboard

def on_click(x, y, button, pressed):
    if pressed:
        if button == mouse.Button.left:
            print(f'L Click {{x:{int(x)}, y:{int(y)}}}')
        elif button == mouse.Button.right:
            print(f'R Click {{x:{int(x)}, y:{int(y)}}}')

def on_press(key):
    if key == keyboard.Key.enter:
        return False  # Sale del programa

# Inicia los listeners del mouse y del teclado
with mouse.Listener(on_click=on_click) as click_listener, \
    keyboard.Listener(on_press=on_press) as keys_listener:
    keys_listener.join()  # Espera a que se presione enter

print('\nExecution finished!')
