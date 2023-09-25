#!/usr/bin/python3
from PIL import Image, ImageDraw, ImageFont, ImageFilter


EMOJIS_TO_COMBINE = ["paths", "to", "emoji images"]
CONFIG = {
    'text': {
        'font': 'Arial.ttf',
        'fill': 'white',
        'size': 48,
        'stroke': {
            'width': 2,
            'color': 'black'
        },
        'bold': False
    },
    'image': {
        'output_path': 'output.png',
        'show_outline': False,
        'outline_size': 2,
        'margin_size': 10,
        'shadow': {
            'blur_radius': 5,
            'color': 'black',
            'alpha': 0.5
        }
    }
}


def unir_imagenes_horizontalmente(imagenes, tamano_salida=160):
    """
    Combina una serie de imágenes de forma horizontal, de izquierda a derecha. Y las
    escala de forma proporcional para producir un tamaño deseado pixeles de anchura.
    Args:
        imagenes (list): Paths de imágenes a combinar.
        tamano_salida (int): Ancho deseado de la imagen combinada.
    """
    # abrir todas las imágenes y obtener sus tamaños
    imagenes_abiertas = [Image.open(img_path).convert("RGBA") for img_path in imagenes]
    anchos = [img.width for img in imagenes_abiertas]
    alturas = [img.height for img in imagenes_abiertas]

    # calcular imagen resultante
    ancho_salida = sum(anchos)
    altura_salida = max(alturas)
    imagen_salida = Image.new("RGBA", (ancho_salida, altura_salida), (0, 0, 0, 0))
    posicion_x = 0
    for img in imagenes_abiertas:
        imagen_salida.paste(img, (posicion_x, 0))
        posicion_x += img.width
    proporcion = tamano_salida / altura_salida
    tamano_redimensionado = (int(ancho_salida * proporcion), tamano_salida)
    imagen_salida = imagen_salida.resize(tamano_redimensionado)

    # guardar imagen
    imagen_salida.save("output.png", format="PNG")


def t2i(text):
    """
    Convierte texto a imagen agregando el formato de texto especificado por CONFIG['text']
    y guarda la imagen producida con la configuración especificada en CONFIG['image'].
    Args:
        text (str): Texto por convertir en imagen.
    """
    font = ImageFont.truetype(
        font=CONFIG['text']['font'],
        size=CONFIG['text']['size'])
    text_width, text_height = font.getsize(text)
    shadow_size = CONFIG['image']['shadow']['blur_radius'] * 2

    image_width = text_width + CONFIG['image']['outline_size'] * CONFIG['image']['margin_size']
    image_height = text_height + CONFIG['image']['outline_size'] * CONFIG['image']['margin_size']
    canvas_width = image_width + shadow_size
    canvas_height = image_height + shadow_size
    shadow_offset_x = (canvas_width - image_width) // 2
    shadow_offset_y = (canvas_height - image_height) // 2
    image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    text_x = (canvas_width - image_width) // (2 * CONFIG['image']['outline_size']) + shadow_offset_x
    text_y = (canvas_height - image_height) // (2 * CONFIG['image']['outline_size']) + shadow_offset_y
    stroke_width = CONFIG['text']['stroke']['width']
    if stroke_width > 0:
        stroke_color = CONFIG['text']['stroke']['color']
        draw.text((text_x-stroke_width, text_y), text, font=font, fill=stroke_color)
        draw.text((text_x+stroke_width, text_y), text, font=font, fill=stroke_color)
        draw.text((text_x, text_y-stroke_width), text, font=font, fill=stroke_color)
        draw.text((text_x, text_y+stroke_width), text, font=font, fill=stroke_color)

    text_fill_color = CONFIG['text']['fill']
    draw.text((text_x, text_y), text, font=font, fill=text_fill_color, stroke_width=stroke_width)
    if CONFIG['text']['bold']:
        draw.text((text_x+1, text_y), text, font=font, fill=text_fill_color)
    if CONFIG['image']['show_outline']:
        outline_color = "magenta"
        outline_rect = [(0, 0), (image_width - 1, image_height - 1)]
        draw.rectangle(outline_rect, width=CONFIG['image']['outline_size'], outline=outline_color)

    shadow_image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.text((text_x, text_y), text, font=font, fill=CONFIG['image']['shadow']['color'])
    shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(CONFIG['image']['shadow']['blur_radius']))
    final_image = Image.alpha_composite(image.convert("RGBA"), shadow_image)
    final_image.save(CONFIG['image']['output_path'], "PNG")


# ejemplo de uso
t2i("Hola, mundo!")
