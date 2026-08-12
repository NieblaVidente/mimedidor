import pytesseract
from PIL import Image

_CONFIGURACION_SOLO_DIGITOS = "--psm 7 -c tessedit_char_whitelist=0123456789"


def reconocer_digitos(imagen: Image.Image) -> str:
    """Aplica OCR sobre una imagen y devuelve el texto crudo detectado.

    Esta es la prueba mínima de T-02b: confirma que la librería elegida (Tesseract, vía
    pytesseract) lee dígitos de una imagen cualquiera. Medir la exactitud real sobre fotos
    de campo de hidrómetros es el alcance de T-11, no de esta función.
    """
    texto = pytesseract.image_to_string(imagen, config=_CONFIGURACION_SOLO_DIGITOS)
    return texto.strip()
