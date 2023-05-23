#!/usr/bin/python3

"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Diccionario de parámetros de texto por defecto
DEFAULT_TEXT_PARAMS = {
    "font_size": 40,
    "font_family": "Arial Unicode",
    "bold": False,
    "italic": False,
    "underline": False,
    "strike": False,
    "fill": ["#ffffff"],
    "border": {
        "thickness": 0,
        "color": "#000000"
    },
    "gradient_angle": None
}

# Función para obtener la fuente con los parámetros indicados
def get_font(text_params):
    font_size = text_params.get("font_size", DEFAULT_TEXT_PARAMS["font_size"])
    font_family = text_params.get("font_family", DEFAULT_TEXT_PARAMS["font_family"])
    bold = text_params.get("bold", DEFAULT_TEXT_PARAMS["bold"])
    italic = text_params.get("italic", DEFAULT_TEXT_PARAMS["italic"])
    underline = text_params.get("underline", DEFAULT_TEXT_PARAMS["underline"])
    strike = text_params.get("strike", DEFAULT_TEXT_PARAMS["strike"])
    font = ImageFont.truetype(font_family, font_size)
    if bold:
        font = ImageFont.truetype(font_family, font_size, bold=bold)
    if italic:
        font = ImageFont.truetype(font_family, font_size, italic=italic)
    if underline:
        font = ImageFont.truetype(font_family, font_size, underline=underline)
    if strike:
        font = ImageFont.truetype(font_family, font_size, strike=strike)
    return font

# Función para obtener el color de relleno con los parámetros indicados
def get_fill_color(text_params):
    fill = text_params.get("fill", DEFAULT_TEXT_PARAMS["fill"])
    if isinstance(fill, list) and len(fill) == 1:
        return fill[0]
    else:
        return tuple(map(int, fill))

# Función para obtener el gradiente de relleno con los parámetros indicados
def get_fill_gradient(text_params, width, height):
    fill = text_params.get("fill", DEFAULT_TEXT_PARAMS["fill"])
    if isinstance(fill, list) and len(fill) > 1:
        gradient_angle = text_params.get("gradient_angle", DEFAULT_TEXT_PARAMS["gradient_angle"])
        if gradient_angle is not None:
            angle = gradient_angle
        else:
            angle = 0
        gradient = Image.new("RGB", (width, height), 0)
        step_size = 1.0 / (len(fill) - 1)
        for i in range(len(fill) - 1):
            start = int(i * step_size * width)
            end = int((i + 1) * step_size * width)
            fill_color1 = tuple(map(int, fill[i]))
            fill_color2 = tuple(map(int, fill[i+1]))
            for x in range(start, end):
                color = tuple(map(int, [fill_color1[c] * (end - x) / (end - start) + fill_color2[c] * (x - start) / (end - start) for c in range(3)]))
                for y in range(height):
                    gradient.putpixel((x, y), color)
        gradient = gradient.rotate(angle)
        return gradient
    else:
        return get_fill_color(text_params)

# Función para obtener el borde con los parámetros indicados
def get_border(text_params):
    border_thickness = text_params.get("border_thickness", 0)
    if border_thickness == 0:
        return None

    border_color = text_params.get("border_color", "#000000")
    return (border_color, border_thickness)


class TextoEstilizado:
    def __init__(self, texto, params):
        self.texto = texto
        self.params = params
        
    def __add__(self, other):
        return TextoEstilizado(self.texto + other.texto, {**self.params, **other.params})
    
    def render(self):
        text_params = {**DEFAULT_TEXT_PARAMS, **self.params}
        font = get_font(text_params)
        fill = get_fill_gradient(text_params, font.getsize(self.texto)[0], font.getsize(self.texto)[1])
        border = get_border(text_params)

        size = font.getsize(self.texto)
        image = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), self.texto, font=font, fill=fill, stroke_width=border[1] if border else 0, stroke_fill=border[0] if border else None)

        directory = os.path.expanduser('~/Desktop/image-texts')
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = 'text.png'
        filepath = os.path.join(directory, filename)

        image.save(filepath)
        return filepath
    
def estilizar(texto, params=None):
    if params is None:
        params = {}

    return TextoEstilizado(texto, params)

# texto = estilizar('Hola') + estilizar(' mundo 😃👍')
# texto.render()

"""

# -----------------------------------------------------

"""
import io
import requests

# Define el emoji a convertir
emoji = '🥶'

# Define la URL de la imagen PNG de ese emoji
url = f'https://twemoji.maxcdn.com/v/latest/72x72/{ord(emoji):x}.png'

# Descarga la imagen de la URL y la guarda en un objeto BytesIO
response = requests.get(url)
image_bytes = io.BytesIO(response.content)

# Guarda los bytes de la imagen en un archivo PNG
with open('emoji.png', 'wb') as f:
    f.write(image_bytes.getbuffer())
"""

# -----------------------------------------------------

from PIL import Image, ImageDraw, ImageFont
import emoji

def text_to_image(text):
    # Create image with transparent background
    img = Image.new('RGBA', (500, 500), (255, 255, 255, 0))
    
    # Load Apple Color Emoji font
    font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 64)
    
    # Draw text using emoji font
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), text, font=font, fill=(0, 0, 0, 255))
    
    # Add a small value to each channel to prevent Pillow from converting to grayscale
    r, g, b, a = img.split()
    r = r.point(lambda i: i + 1)
    g = g.point(lambda i: i + 1)
    b = b.point(lambda i: i + 1)
    img = Image.merge('RGBA', (r, g, b, a))
    
    # Save image
    img.save('test.png')

text_to_image('🥶')
