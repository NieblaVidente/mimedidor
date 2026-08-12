from PIL import Image, ImageDraw, ImageFont

from app.vision.reconocimiento import reconocer_digitos


def _imagen_con_digitos(texto: str) -> Image.Image:
    """Genera una imagen sintética con dígitos, sin depender de un archivo externo."""
    imagen = Image.new("L", (400, 150), color=255)
    dibujo = ImageDraw.Draw(imagen)
    fuente = ImageFont.load_default(size=90)
    dibujo.text((20, 20), texto, fill=0, font=fuente)
    return imagen


def test_reconocer_digitos_lee_una_imagen_cualquiera():
    imagen = _imagen_con_digitos("1234")

    resultado = reconocer_digitos(imagen)

    assert "1234" in resultado
