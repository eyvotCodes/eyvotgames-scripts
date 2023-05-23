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

from PIL import Image

def unir_imagenes_horizontalmente(imagenes, tamano_salida=160):
    # Abrir todas las imágenes y obtener sus tamaños
    imagenes_abiertas = [Image.open(img_path).convert("RGBA") for img_path in imagenes]
    anchos = [img.width for img in imagenes_abiertas]
    alturas = [img.height for img in imagenes_abiertas]

    # Calcular las dimensiones de la imagen de salida
    ancho_salida = sum(anchos)
    altura_salida = max(alturas)

    # Crear una imagen de salida en blanco
    imagen_salida = Image.new("RGBA", (ancho_salida, altura_salida), (0, 0, 0, 0))

    # Copiar las imágenes de entrada a la imagen de salida
    posicion_x = 0
    for img in imagenes_abiertas:
        imagen_salida.paste(img, (posicion_x, 0))
        posicion_x += img.width

    # Redimensionar la imagen de salida al tamaño deseado
    proporcion = tamano_salida / altura_salida
    tamano_redimensionado = (int(ancho_salida * proporcion), tamano_salida)
    imagen_salida = imagen_salida.resize(tamano_redimensionado)

    # Guardar la imagen de salida en formato PNG sin fondo
    imagen_salida.save("output.png", format="PNG")

# Ejemplo de uso
imagenes_input = [
    "/Users/fleyva/Downloads/emojis/astonished-face_1f632.png",
    "/Users/fleyva/Downloads/emojis/exploding-head_1f92f.png",
    "/Users/fleyva/Downloads/emojis/cold-face_1f976.png",
]

unir_imagenes_horizontalmente(imagenes_input, tamano_salida=160)

# -----------------------------------------------------
