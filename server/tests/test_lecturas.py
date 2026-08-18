"""Pruebas unitarias de POST /api/lecturas (T-15).

La conexión falsa (ConexionFalsa/CursorFalso) vive en conftest.py — la comparte con
test_historial.py (T-17) desde ahí en vez de duplicarla.
"""

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import sobreescribir_conexion

client = TestClient(app)

CUERPO_BASE = {
    "medidor_id": str(uuid4()),
    "valor": 100.0,
    "fecha": "2026-08-17",
    "origen": "manual",
    "foto_url": None,
}


def test_crear_lectura_medidor_no_encontrado():
    sobreescribir_conexion(respuestas=[None])

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "MEDIDOR_NO_ENCONTRADO"


def test_crear_lectura_primera_del_medidor():
    lectura_id = str(uuid4())
    sobreescribir_conexion(respuestas=[(True,), (lectura_id,), None])

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] == lectura_id
    assert cuerpo["consumo_desde_anterior_m3"] is None
    assert cuerpo["dias_desde_anterior"] is None


def test_crear_lectura_con_consumo_calculado():
    lectura_id = str(uuid4())
    sobreescribir_conexion(
        respuestas=[(True,), (lectura_id,), (88.0, date(2026, 7, 18))]
    )

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["consumo_desde_anterior_m3"] == 12.0
    assert cuerpo["dias_desde_anterior"] == 30


def test_crear_lectura_invalida():
    sobreescribir_conexion(
        respuestas=[(True,)],
        excepcion_en_llamada={
            2: Exception(
                "No se pudo registrar la lectura: LECTURA_INVALIDA: el valor 100.00 "
                "es menor que la última lectura registrada (150.00)"
            )
        },
    )

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "LECTURA_INVALIDA"


def test_crear_lectura_validacion_falla():
    # FastAPI resuelve las dependencias (incluida la conexión) antes de evaluar si el cuerpo
    # es inválido, así que igual hay que reemplazarla aunque nunca se llegue a usar.
    sobreescribir_conexion(respuestas=[])

    respuesta = client.post("/api/lecturas", json={"medidor_id": "no-es-un-uuid"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"
