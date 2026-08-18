"""Pruebas unitarias de POST /api/lecturas/reconocer (T-15b).

No corre el pipeline de visión real de punta a punta con fotos de campo — eso ya lo mide
docs/exactitud-reconocimiento.md (T-11), con el resultado real (0%) sobre el dataset disponible.
Acá se verifica el cableado del endpoint: qué hace con cada resultado posible de la cadena
T-09 → T-10 → T-11, mockeando esas tres funciones en el punto donde este módulo las importa.
"""

from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.vision.preprocesamiento import CaratulaNoDetectada

client = TestClient(app)


def _bytes_imagen_valida() -> bytes:
    imagen = np.zeros((20, 20, 3), dtype=np.uint8)
    ok, codificada = cv2.imencode(".png", imagen)
    assert ok
    return codificada.tobytes()


def _peticion(contenido: bytes):
    return client.post(
        "/api/lecturas/reconocer",
        files={"foto": ("foto.png", contenido, "image/png")},
        data={"medidor_id": str(uuid4())},
    )


def test_reconocer_foto_archivo_no_es_imagen():
    respuesta = _peticion(b"esto no es una imagen")

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "IMAGEN_ILEGIBLE"


def test_reconocer_foto_caratula_no_detectada():
    with patch(
        "app.api.lecturas.preprocesar_caratula",
        side_effect=CaratulaNoDetectada("sin círculo"),
    ):
        respuesta = _peticion(_bytes_imagen_valida())

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "IMAGEN_ILEGIBLE"


def test_reconocer_foto_lectura_no_confiable():
    resultado_falso = SimpleNamespace(imagen=np.zeros((10, 10, 3), dtype=np.uint8))
    with (
        patch("app.api.lecturas.preprocesar_caratula", return_value=resultado_falso),
        patch("app.api.lecturas.segmentar_ventana_odometro", return_value=resultado_falso),
        patch("app.api.lecturas.reconocer_lectura", return_value=None),
    ):
        respuesta = _peticion(_bytes_imagen_valida())

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "IMAGEN_ILEGIBLE"


def test_reconocer_foto_exitoso():
    resultado_falso = SimpleNamespace(imagen=np.zeros((10, 10, 3), dtype=np.uint8))
    with (
        patch("app.api.lecturas.preprocesar_caratula", return_value=resultado_falso),
        patch("app.api.lecturas.segmentar_ventana_odometro", return_value=resultado_falso),
        patch("app.api.lecturas.reconocer_lectura", return_value=1284.0),
    ):
        respuesta = _peticion(_bytes_imagen_valida())

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["lectura_reconocida"] == 1284.0
    assert cuerpo["confianza"] is None
