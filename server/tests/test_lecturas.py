"""Pruebas unitarias de POST /api/lecturas (T-15).

No usan una base de datos real: la dependencia de conexión se sustituye por un cursor falso
que simula las tres consultas del endpoint en orden (existencia del medidor, llamada al
procedimiento de T-14, lectura anterior). El job `server` del CI no levanta Postgres a
propósito — eso ya lo cubre el job `database` para los scripts SQL en sí.
"""

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.conexion import obtener_conexion
from app.main import app


class CursorFalso:
    def __init__(self, respuestas, excepcion_en_llamada=None):
        self._respuestas = list(respuestas)
        self._excepcion_en_llamada = excepcion_en_llamada or {}
        self._llamada = 0

    def __enter__(self):
        return self

    def __exit__(self, *_excepcion):
        return False

    def execute(self, _consulta, _parametros=None):
        self._llamada += 1
        if self._llamada in self._excepcion_en_llamada:
            raise self._excepcion_en_llamada[self._llamada]

    def fetchone(self):
        return self._respuestas.pop(0) if self._respuestas else None


class ConexionFalsa:
    def __init__(self, respuestas, excepcion_en_llamada=None):
        self._cursor = CursorFalso(respuestas, excepcion_en_llamada)

    def cursor(self):
        return self._cursor


def _sobreescribir_conexion(respuestas, excepcion_en_llamada=None):
    app.dependency_overrides[obtener_conexion] = lambda: ConexionFalsa(
        respuestas, excepcion_en_llamada
    )


def teardown_function():
    app.dependency_overrides.clear()


client = TestClient(app)

CUERPO_BASE = {
    "medidor_id": str(uuid4()),
    "valor": 100.0,
    "fecha": "2026-08-17",
    "origen": "manual",
    "foto_url": None,
}


def test_crear_lectura_medidor_no_encontrado():
    _sobreescribir_conexion(respuestas=[None])

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "MEDIDOR_NO_ENCONTRADO"


def test_crear_lectura_primera_del_medidor():
    lectura_id = str(uuid4())
    _sobreescribir_conexion(respuestas=[(True,), (lectura_id,), None])

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] == lectura_id
    assert cuerpo["consumo_desde_anterior_m3"] is None
    assert cuerpo["dias_desde_anterior"] is None


def test_crear_lectura_con_consumo_calculado():
    lectura_id = str(uuid4())
    _sobreescribir_conexion(
        respuestas=[(True,), (lectura_id,), (88.0, date(2026, 7, 18))]
    )

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["consumo_desde_anterior_m3"] == 12.0
    assert cuerpo["dias_desde_anterior"] == 30


def test_crear_lectura_invalida():
    _sobreescribir_conexion(
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
    _sobreescribir_conexion(respuestas=[])

    respuesta = client.post("/api/lecturas", json={"medidor_id": "no-es-un-uuid"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"
