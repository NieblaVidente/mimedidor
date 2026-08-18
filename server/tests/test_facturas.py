"""Pruebas unitarias de POST /api/facturas y GET /api/facturas/{id}/comparacion (T-18).

Conexión falsa compartida en conftest.py, mismo patrón que test_lecturas.py y
test_historial.py.
"""

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import sobreescribir_conexion

client = TestClient(app)

CUERPO_FACTURA = {
    "medidor_id": str(uuid4()),
    "periodo_inicio": "2026-07-01",
    "periodo_fin": "2026-08-01",
    "consumo_facturado_m3": 14.0,
    "monto": 8250.0,
}


def test_crear_factura_periodo_invalido():
    cuerpo = {**CUERPO_FACTURA, "periodo_fin": "2026-06-01"}  # antes de periodo_inicio
    sobreescribir_conexion(respuestas=[])

    respuesta = client.post("/api/facturas", json=cuerpo)

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"


def test_crear_factura_medidor_no_encontrado():
    sobreescribir_conexion(respuestas=[None])

    respuesta = client.post("/api/facturas", json=CUERPO_FACTURA)

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "MEDIDOR_NO_ENCONTRADO"


def test_crear_factura_exitosa():
    factura_id = str(uuid4())
    sobreescribir_conexion(respuestas=[(True,), (factura_id,)])

    respuesta = client.post("/api/facturas", json=CUERPO_FACTURA)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] == factura_id
    assert cuerpo["consumo_facturado_m3"] == 14.0
    assert cuerpo["monto"] == 8250.0


def test_comparacion_factura_no_encontrada():
    sobreescribir_conexion(respuestas=[None])

    respuesta = client.get(f"/api/facturas/{uuid4()}/comparacion")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "FACTURA_NO_ENCONTRADA"


def test_comparacion_factura_dentro_del_umbral():
    medidor_id = str(uuid4())
    sobreescribir_conexion(
        respuestas=[
            (medidor_id, date(2026, 7, 1), date(2026, 8, 1), 14.0),  # factura
            (100.0, date(2026, 6, 20)),  # última lectura hasta periodo_inicio
            (112.0, date(2026, 7, 28)),  # última lectura hasta periodo_fin
        ]
    )

    respuesta = client.get(f"/api/facturas/{uuid4()}/comparacion")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["consumo_medido_m3"] == 12.0
    assert cuerpo["consumo_facturado_m3"] == 14.0
    assert cuerpo["diferencia_m3"] == 2.0
    assert cuerpo["diferencia_porcentual"] == 14.3
    assert cuerpo["supera_umbral"] is False


def test_comparacion_factura_supera_umbral():
    medidor_id = str(uuid4())
    sobreescribir_conexion(
        respuestas=[
            (medidor_id, date(2026, 7, 1), date(2026, 8, 1), 10.0),
            (100.0, date(2026, 6, 20)),
            (105.0, date(2026, 7, 28)),  # consumo medido 5 vs facturado 10 -> 50% de diferencia
        ]
    )

    respuesta = client.get(f"/api/facturas/{uuid4()}/comparacion")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["consumo_medido_m3"] == 5.0
    assert cuerpo["diferencia_porcentual"] == 50.0
    assert cuerpo["supera_umbral"] is True


def test_comparacion_factura_sin_lecturas_suficientes():
    medidor_id = str(uuid4())
    sobreescribir_conexion(
        respuestas=[
            (medidor_id, date(2026, 7, 1), date(2026, 8, 1), 14.0),
            None,  # no hay ninguna lectura antes del inicio del período
            (112.0, date(2026, 7, 28)),
        ]
    )

    respuesta = client.get(f"/api/facturas/{uuid4()}/comparacion")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["consumo_medido_m3"] is None
    assert cuerpo["diferencia_m3"] is None
    assert cuerpo["diferencia_porcentual"] is None
    assert cuerpo["supera_umbral"] is False
