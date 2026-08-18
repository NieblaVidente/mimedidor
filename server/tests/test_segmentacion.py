import math
from pathlib import Path

import cv2
import numpy as np
import pytest

from app.vision.preprocesamiento import CaratulaNoDetectada, preprocesar_caratula
from app.vision.segmentacion import (
    FRACCION_RESPALDO_X,
    FRACCION_RESPALDO_Y,
    FRACCION_X,
    FRACCION_Y,
    segmentar_ventana_odometro,
)

# Misma carpeta no versionada que usa test_preprocesamiento.py.
CARPETA_DATASET = Path(__file__).resolve().parents[2] / "dataset-fotos"
LADO_CARATULA_SINTETICA = 400


def _caratula_sintetica_con_ventana() -> np.ndarray:
    """Carátula sintética: fondo claro con una franja de trazos verticales densos (imitan el
    patrón de bordes de una fila de dígitos: muchos bordes verticales seguidos, separados por
    pocos píxeles) ubicada dentro de la franja de búsqueda (FRACCION_X/FRACCION_Y). No dibuja
    dígitos reales — solo el patrón de bordes que el cierre morfológico necesita fundir en un
    único bloque, igual que test_reconocimiento.py genera dígitos sintéticos sin ser un OCR
    real. Sirve para probar el mecanismo de detección de forma determinística."""
    lado = LADO_CARATULA_SINTETICA
    imagen = np.full((lado, lado, 3), 235, dtype=np.uint8)  # carátula clara

    y0 = int(lado * (FRACCION_Y[0] + FRACCION_Y[1]) / 2) - 15
    x0 = int(lado * FRACCION_X[0]) + 20
    for i in range(30):
        x = x0 + i * 7
        cv2.line(imagen, (x, y0), (x, y0 + 30), (20, 20, 20), thickness=3)

    return imagen


def test_segmentar_ventana_detecta_fila_de_digitos_sintetica():
    caratula = _caratula_sintetica_con_ventana()

    resultado = segmentar_ventana_odometro(caratula)

    assert resultado.deteccion_automatica is True
    x, y, ancho, alto = resultado.caja
    assert ancho > alto  # la ventana es una fila, mucho más ancha que alta
    assert resultado.imagen.shape[0] > 0
    assert resultado.imagen.shape[1] > 0


def test_segmentar_ventana_cae_a_posicion_fija_sin_bordes():
    caratula_lisa = np.full((LADO_CARATULA_SINTETICA, LADO_CARATULA_SINTETICA, 3), 200, np.uint8)

    resultado = segmentar_ventana_odometro(caratula_lisa)

    assert resultado.deteccion_automatica is False
    alto, ancho = LADO_CARATULA_SINTETICA, LADO_CARATULA_SINTETICA
    ancho_esperado = int(ancho * FRACCION_RESPALDO_X[1]) - int(ancho * FRACCION_RESPALDO_X[0])
    alto_esperado = int(alto * FRACCION_RESPALDO_Y[1]) - int(alto * FRACCION_RESPALDO_Y[0])
    # +/- el margen que agrega segmentar_ventana_odometro al recortar
    assert abs(resultado.caja[2] - ancho_esperado) <= 20
    assert abs(resultado.caja[3] - alto_esperado) <= 20


def _fotos_reales_disponibles() -> list[Path]:
    if not CARPETA_DATASET.exists():
        return []
    extensiones = {".jpg", ".jpeg", ".png"}
    return sorted(p for p in CARPETA_DATASET.iterdir() if p.suffix.lower() in extensiones)


@pytest.mark.skipif(
    len(_fotos_reales_disponibles()) < 2,
    reason=(
        "Requiere al menos 2 fotos reales en dataset-fotos/ en la raíz del repo (no "
        "versionada; ver docs/dataset-campo/registro-medidores.md)."
    ),
)
def test_segmentar_ventana_funciona_sobre_salidas_reales_de_t09():
    """Corre el pipeline completo T-09 -> T-10 sobre las fotos reales disponibles y verifica
    el criterio de aceptación: al menos 70% de las carátulas que T-09 sí pudo procesar deben
    segmentarse por detección automática (no por el recorte de respaldo)."""
    fotos = _fotos_reales_disponibles()

    caratulas_ok = []
    for ruta in fotos:
        imagen = cv2.imread(str(ruta))
        assert imagen is not None, f"No se pudo leer {ruta.name}"
        try:
            caratulas_ok.append(preprocesar_caratula(imagen).imagen)
        except CaratulaNoDetectada:
            pass

    assert caratulas_ok, "T-09 no procesó ninguna foto real — revisar dataset-fotos/"

    exitosas = 0
    for caratula in caratulas_ok:
        resultado = segmentar_ventana_odometro(caratula)
        assert resultado.imagen.size > 0
        if resultado.deteccion_automatica:
            exitosas += 1

    minimo_requerido = math.ceil(0.7 * len(caratulas_ok))
    assert exitosas >= minimo_requerido, (
        f"Solo {exitosas}/{len(caratulas_ok)} carátulas se segmentaron por detección "
        f"automática (mínimo requerido para el 70%: {minimo_requerido})"
    )
