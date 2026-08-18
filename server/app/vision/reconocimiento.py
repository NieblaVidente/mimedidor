"""Reconocimiento de dígitos sobre la ventana del odómetro (T-11).

`reconocer_digitos` (T-02b) ya probó que Tesseract lee dígitos de una imagen cualquiera. Esta
tarjeta parte de ahí y agrega el paso que faltaba: preparar el recorte real que entrega T-10
(`segmentacion.segmentar_ventana_odometro`) para que Tesseract tenga una chance razonable de
leerlo, y exponer una función que devuelva la lectura como número.

El recorte de T-10 no es solo la fila de dígitos: por diseño (ver `segmentacion.py`, franja de
búsqueda `FRACCION_Y`) puede incluir también la línea de texto de certificación/modelo que está
justo debajo en la carátula (confirmado visualmente sobre las 2 fotos reales disponibles:
`dataset-fotos/Medidor2_captura*.png`). Pasarle eso a Tesseract con `--psm 7` (una sola línea)
mezcla ambas líneas y arruina la lectura. Por eso este módulo hace su propio refinamiento antes
de llamar a Tesseract, sin tocar `segmentacion.py` (T-10 ya está cerrada y en `main`):

1. Aislar la fila de dígitos. Mismo tipo de filtro que usa T-10 (Sobel en X + Otsu + cierre
   morfológico) pero aplicado para encontrar bandas horizontales densas en vez de un cuadro
   completo. La ventana de T-10 típicamente trae dos bandas separadas por un hueco (dígitos
   arriba, texto de certificación abajo); nos quedamos con la primera banda porque en las fotos
   disponibles el odómetro siempre queda arriba en la franja de búsqueda de T-10.
2. Recortar el ícono inicial. Muchos odómetros traen un pequeño ícono/logo pegado a la izquierda
   de la fila de dígitos, separado de estos por un hueco real en blanco (columnas sin ningún
   borde). Se detecta ese primer hueco ancho y se descarta todo lo que quede a su izquierda —
   evita que Tesseract intente leer el ícono como si fuera un dígito.
3. Escalar y binarizar. Tesseract rinde mejor con texto grande y alto contraste; se escala 4x y
   se aplica Otsu.

Esto es una mejora razonable, no una promesa de exactitud alta — la tarjeta T-11 es explícita en
que el objetivo es medir y documentar qué tan bien funciona, no maquillar el número. Ver
`docs/exactitud-reconocimiento.md` para el resultado real medido sobre el dataset disponible y
por qué falla en los casos que falla (spoiler: las líneas divisorias entre casillas de dígitos se
confunden con el dígito "1" — un problema conocido de aplicar OCR genérico, pensado para
tipografía impresa, sobre un display de rodillos mecánico).
"""

from __future__ import annotations

import cv2
import numpy as np
import pytesseract
from PIL import Image

_CONFIGURACION_SOLO_DIGITOS = "--psm 7 -c tessedit_char_whitelist=0123456789"

# --- Constantes del refinamiento de T-11 (todas como fracción del tamaño de la imagen de
# entrada, para no depender de una resolución fija — mismo criterio que preprocesamiento.py y
# segmentacion.py). Calibradas visualmente sobre las 2 fotos reales disponibles (Medidor2).
_ESCALA_OCR = 4  # cuánto agrandar antes de binarizar y pasarle la imagen a Tesseract
_UMBRAL_RELATIVO_FILA = 0.3  # fracción del pico de densidad de bordes para considerar "fila densa"
_MARGEN_FILA_REL = 0.05  # margen adicional alrededor de la fila de dígitos detectada
_HUECO_MINIMO_REL = 0.005  # ancho mínimo (fracción del ancho) de un hueco para separar el ícono
_LARGO_MINIMO_LECTURA = 5  # una ventana de odómetro real trae varios dígitos, no uno o dos sueltos
_LARGO_MAXIMO_LECTURA = 8


def reconocer_digitos(imagen: Image.Image) -> str:
    """Aplica OCR sobre una imagen y devuelve el texto crudo detectado.

    Esta es la prueba mínima de T-02b: confirma que la librería elegida (Tesseract, vía
    pytesseract) lee dígitos de una imagen cualquiera. Medir la exactitud real sobre fotos
    de campo de hidrómetros es el alcance de T-11, no de esta función.
    """
    texto = pytesseract.image_to_string(imagen, config=_CONFIGURACION_SOLO_DIGITOS)
    return texto.strip()


def _aislar_fila_digitos(ventana_bgr: np.ndarray) -> np.ndarray:
    """Recorta la banda horizontal más densa en bordes verticales dentro de la ventana de T-10.

    Es el mismo filtro que `segmentacion._candidato_por_bordes` (Sobel-X + Otsu + cierre
    morfológico) pero mirando la densidad por fila en vez de buscar un solo contorno rectangular:
    la ventana de T-10 puede traer más de una línea de contenido, y esto se queda con la de más
    arriba (el odómetro), descartando cualquier línea de texto que haya quedado debajo.
    """
    alto, ancho = ventana_bgr.shape[:2]
    gris = cv2.cvtColor(ventana_bgr, cv2.COLOR_BGR2GRAY)
    gradiente = cv2.convertScaleAbs(cv2.Sobel(gris, cv2.CV_32F, 1, 0, ksize=3))
    _, binaria = cv2.threshold(gradiente, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, ancho // 20) | 1, 3))
    cerrada = cv2.morphologyEx(binaria, cv2.MORPH_CLOSE, nucleo)

    perfil = cerrada.sum(axis=1).astype(float)
    if perfil.max() == 0:
        return ventana_bgr  # sin bordes detectables: devolver la ventana tal cual llegó

    umbral = perfil.max() * _UMBRAL_RELATIVO_FILA
    denso = perfil > umbral

    bandas: list[tuple[int, int]] = []
    inicio = None
    for i, es_denso in enumerate(denso):
        if es_denso and inicio is None:
            inicio = i
        elif not es_denso and inicio is not None:
            bandas.append((inicio, i))
            inicio = None
    if inicio is not None:
        bandas.append((inicio, len(denso)))
    if not bandas:
        return ventana_bgr

    y0, y1 = bandas[0]  # la fila de dígitos queda más arriba que cualquier texto debajo
    margen = max(2, int(alto * _MARGEN_FILA_REL))
    y0 = max(0, y0 - margen)
    y1 = min(alto, y1 + margen)
    return ventana_bgr[y0:y1, :]


def _indice_fin_icono(binaria_invertida: np.ndarray) -> int:
    """Busca el primer hueco ancho de columnas en blanco después de algo de contenido, y
    devuelve el índice donde termina (el punto donde probablemente empiezan los dígitos, después
    de un ícono/logo pegado a la izquierda). Si no encuentra un hueco así, devuelve 0 (no recorta
    nada) — más vale no recortar que recortar mal."""
    perfil = binaria_invertida.sum(axis=0) / 255.0
    ancho = len(perfil)
    hueco_minimo = max(4, int(ancho * _HUECO_MINIMO_REL))
    visto_contenido = False
    i = 0
    while i < ancho:
        if perfil[i] > 1.0:
            visto_contenido = True
            i += 1
            continue
        if visto_contenido:
            j = i
            while j < ancho and perfil[j] <= 1.0:
                j += 1
            if j - i >= hueco_minimo:
                return j
            i = j
        else:
            i += 1
    return 0


def leer_lectura(ventana_bgr: np.ndarray) -> str:
    """Recibe el recorte de la ventana del odómetro (salida de T-10,
    `segmentacion.segmentar_ventana_odometro(...).imagen`) y devuelve la cadena de dígitos que
    Tesseract detectó, tal cual — sin corregir ni completar dígitos a mano. Puede devolver una
    cadena vacía o con menos/más dígitos de los reales; ese es justamente el dato que T-11 tiene
    que medir y documentar, no ocultar."""
    fila = _aislar_fila_digitos(ventana_bgr)
    grande = cv2.resize(fila, None, fx=_ESCALA_OCR, fy=_ESCALA_OCR, interpolation=cv2.INTER_CUBIC)
    gris = cv2.cvtColor(grande, cv2.COLOR_BGR2GRAY)

    _, invertida = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    x0 = _indice_fin_icono(invertida)

    _, binaria = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    recorte = binaria[:, x0:]

    imagen_pil = Image.fromarray(recorte)
    texto = pytesseract.image_to_string(imagen_pil, config=_CONFIGURACION_SOLO_DIGITOS)
    return texto.strip()


def reconocer_lectura(ventana_bgr: np.ndarray) -> float | None:
    """Envuelve `leer_lectura` para el criterio de aceptación de T-11: recibe el recorte de T-10
    y devuelve la lectura como número.

    Devuelve `None` (en vez de inventar un número) cuando el texto detectado no tiene una
    cantidad de dígitos razonable para una ventana de odómetro real (entre
    `_LARGO_MINIMO_LECTURA` y `_LARGO_MAXIMO_LECTURA`) — por ejemplo si Tesseract no detectó nada,
    o si detectó tan pocos o tantos caracteres que claramente no es una lectura válida.

    Nota de alcance: esta función interpreta la cadena de dígitos como un entero tal cual se ve
    en el odómetro (p. ej. "0051069" -> 51069.0), igual que se registra en
    `docs/dataset-campo/registro-medidores.md`. Algunos odómetros marcan en rojo los últimos
    dígitos para indicar una fracción de m³; decidir esa convención de punto decimal no es parte
    del alcance de T-11 (no hay todavía evidencia suficiente de campo para fijarla) y queda para
    una tarjeta futura una vez que el dataset de T-07/T-08 crezca."""
    texto = leer_lectura(ventana_bgr)
    if not texto.isdigit():
        return None
    if not (_LARGO_MINIMO_LECTURA <= len(texto) <= _LARGO_MAXIMO_LECTURA):
        return None
    return float(int(texto))
