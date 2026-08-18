"""Segmentación de la ventana del odómetro sobre la carátula ya enderezada (T-10).

Recibe la salida de `preprocesamiento.preprocesar_caratula` (T-09) y localiza el recorte
rectangular donde están los dígitos del odómetro, para que T-11 (reconocimiento) trabaje sobre
una imagen chica y ya acotada en vez de la carátula completa.

Filtros aplicados y por qué:

1. Franja de búsqueda acotada por posición relativa. La tarjeta señala que la ventana "está en
   una posición relativamente estable respecto al centro de la carátula", y así se confirmó con
   las 2 fotos reales disponibles (Medidor2): en ambas, la ventana cae dentro del mismo rango de
   fracciones de alto/ancho de la carátula ya enderezada. Acotar la búsqueda a esa franja antes
   de buscar bordes descarta de entrada a otros elementos de alto contraste que no son la
   ventana (el nombre de marca impreso arriba, el aro de la tapa, el visor de la esfera roja).
2. Gradiente de Sobel en X. Los dígitos del odómetro están en casillas separadas por líneas
   verticales; ese patrón produce muchos bordes verticales seguidos. Sobel en X mide justo ese
   tipo de borde, a diferencia de Canny (que mezcla bordes en todas direcciones y es más
   sensible al ruido de la foto de campo).
3. Umbral de Otsu. Binariza automáticamente sin fijar un valor de intensidad a mano — necesario
   porque el contraste real cambia foto a foto (luz, humedad, reflejos en el vidrio del medidor).
4. Cierre morfológico horizontal ancho. Funde los bordes de dígitos y separadores individuales
   en un solo bloque rectangular contiguo (la fila completa), en vez de detectar cada dígito por
   separado — así un solo contorno describe toda la ventana.
5. Filtro de relación de aspecto. La ventana es mucho más ancha que alta (siete dígitos en fila);
   se descartan contornos cuadrados o verticales que hayan sobrevivido al cierre morfológico.

Si ningún contorno pasa el filtro (foto con muy poco contraste, franja de búsqueda que no
aplica a un modelo de medidor distinto), se usa un recorte de posición fija en vez de fallar —
alcance explícitamente aceptado por la tarjeta T-10. Ver docs/deuda-tecnica.md.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# Franja de búsqueda, como fracción del tamaño de la carátula ya enderezada (TAMANO_SALIDA de
# preprocesamiento.py). Calibrada sobre las 2 fotos reales de Medidor2 con margen adicional.
FRACCION_Y = (0.20, 0.48)
FRACCION_X = (0.10, 0.90)
ASPECTO_MINIMO = 2.0  # ancho / alto — la ventana es una fila de dígitos, mucho más ancha que alta
MARGEN_RECORTE_PX = 8

# Recorte de respaldo (posición fija), como fracción de la carátula — ver DEUDA TÉCNICA arriba.
FRACCION_RESPALDO_X = (0.19, 0.84)
FRACCION_RESPALDO_Y = (0.29, 0.41)


@dataclass
class ResultadoSegmentacion:
    imagen: np.ndarray  # BGR, recorte de la ventana del odómetro
    caja: tuple[int, int, int, int]  # (x, y, ancho, alto) sobre la carátula de entrada
    deteccion_automatica: bool  # False si se usó el recorte de posición fija (deuda técnica)


def _candidato_por_bordes(caratula_bgr: np.ndarray) -> tuple[int, int, int, int] | None:
    alto, ancho = caratula_bgr.shape[:2]
    y0, y1 = int(alto * FRACCION_Y[0]), int(alto * FRACCION_Y[1])
    x0, x1 = int(ancho * FRACCION_X[0]), int(ancho * FRACCION_X[1])

    franja = caratula_bgr[y0:y1, x0:x1]
    gris = cv2.cvtColor(franja, cv2.COLOR_BGR2GRAY)
    gradiente = cv2.convertScaleAbs(cv2.Sobel(gris, cv2.CV_32F, 1, 0, ksize=3))
    _, binaria = cv2.threshold(gradiente, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    nucleo = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    cerrada = cv2.morphologyEx(binaria, cv2.MORPH_CLOSE, nucleo)

    contornos, _ = cv2.findContours(cerrada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidatos = []
    for contorno in contornos:
        x, y, cw, ch = cv2.boundingRect(contorno)
        if ch == 0 or cw / ch < ASPECTO_MINIMO:
            continue
        candidatos.append((x + x0, y + y0, cw, ch))

    if not candidatos:
        return None

    # El más grande domina claramente sobre cualquier otro borde suelto que haya sobrevivido
    # al filtro de aspecto (confirmado con las 2 fotos reales: 5x-8x más área que el siguiente).
    return max(candidatos, key=lambda c: c[2] * c[3])


def _caja_de_respaldo(alto: int, ancho: int) -> tuple[int, int, int, int]:
    x0 = int(ancho * FRACCION_RESPALDO_X[0])
    x1 = int(ancho * FRACCION_RESPALDO_X[1])
    y0 = int(alto * FRACCION_RESPALDO_Y[0])
    y1 = int(alto * FRACCION_RESPALDO_Y[1])
    return x0, y0, x1 - x0, y1 - y0


def segmentar_ventana_odometro(caratula_bgr: np.ndarray) -> ResultadoSegmentacion:
    """Recibe la carátula ya enderezada (salida de `preprocesar_caratula`, T-09) y devuelve el
    recorte de la ventana de dígitos del odómetro.

    Nunca lanza una excepción: si la detección por bordes no encuentra un candidato confiable,
    cae a un recorte de posición fija (deuda técnica documentada, permitida explícitamente por
    los criterios de aceptación de T-10)."""
    alto, ancho = caratula_bgr.shape[:2]

    caja = _candidato_por_bordes(caratula_bgr)
    deteccion_automatica = caja is not None
    if caja is None:
        caja = _caja_de_respaldo(alto, ancho)

    x, y, cw, ch = caja
    m = MARGEN_RECORTE_PX
    x0, y0 = max(0, x - m), max(0, y - m)
    x1, y1 = min(ancho, x + cw + m), min(alto, y + ch + m)

    return ResultadoSegmentacion(
        imagen=caratula_bgr[y0:y1, x0:x1],
        caja=(x0, y0, x1 - x0, y1 - y0),
        deteccion_automatica=deteccion_automatica,
    )
