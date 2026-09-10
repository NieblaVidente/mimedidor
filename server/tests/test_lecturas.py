"""Pruebas unitarias de POST /api/lecturas (T-15).

La conexión falsa (ConexionFalsa/CursorFalso) vive en conftest.py — la comparte con
test_historial.py (T-17) desde ahí en vez de duplicarla.
"""

from datetime import date, timedelta
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
    # Primera respuesta: los digitos rojos del medidor (T-39). `(0,)` = sin decimales, o sea
    # que el valor mostrado y el volumen coinciden.
    sobreescribir_conexion(respuestas=[(0,), (lectura_id,), None])

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] == lectura_id
    assert cuerpo["consumo_desde_anterior_m3"] is None
    assert cuerpo["dias_desde_anterior"] is None


def test_crear_lectura_con_consumo_calculado():
    lectura_id = str(uuid4())
    sobreescribir_conexion(
        respuestas=[(0,), (lectura_id,), (88.0, date(2026, 7, 18))]
    )

    respuesta = client.post("/api/lecturas", json=CUERPO_BASE)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["consumo_desde_anterior_m3"] == 12.0
    assert cuerpo["dias_desde_anterior"] == 30


def test_crear_lectura_convierte_los_digitos_rojos_a_metros_cubicos():
    """T-39: el abonado escribe lo que ve en el odometro; se guarda el volumen real."""
    lectura_id = str(uuid4())
    # Dos digitos rojos, como el MJ-SDC y el ACTARIS del dataset de campo.
    sobreescribir_conexion(respuestas=[(2,), (lectura_id,), None])

    respuesta = client.post(
        "/api/lecturas", json={**CUERPO_BASE, "valor": 452991.0}
    )

    assert respuesta.status_code == 201
    # 452991 mostrado con 2 rojos son 4529.91 m3, no 452991.
    assert respuesta.json()["valor"] == 4529.91


def test_crear_lectura_escala_distinta_por_medidor():
    """La escala es del medidor, no una constante: el ARAD del dataset marca 1 solo rojo."""
    lectura_id = str(uuid4())
    sobreescribir_conexion(respuestas=[(1,), (lectura_id,), None])

    respuesta = client.post("/api/lecturas", json={**CUERPO_BASE, "valor": 25888.0})

    assert respuesta.status_code == 201
    assert respuesta.json()["valor"] == 2588.8


def test_crear_lectura_consumo_en_metros_cubicos_reales():
    """El consumo sale en la misma unidad que la factura, que es lo que rompia antes de T-39."""
    lectura_id = str(uuid4())
    sobreescribir_conexion(
        respuestas=[(2,), (lectura_id,), (510.69, date(2026, 8, 12))]
    )

    respuesta = client.post("/api/lecturas", json={**CUERPO_BASE, "valor": 51085.0})

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["valor"] == 510.85
    # 0.16 m3, no 16: antes de T-39 esta resta daba 16 y se comparaba contra una factura en m3.
    assert cuerpo["consumo_desde_anterior_m3"] == 0.16


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


def test_crear_lectura_fecha_futura():
    # Se rechaza antes de tocar la base (T-35): ni siquiera se llega a llamar al procedimiento.
    sobreescribir_conexion(respuestas=[])

    manana = (date.today() + timedelta(days=1)).isoformat()
    respuesta = client.post("/api/lecturas", json={**CUERPO_BASE, "fecha": manana})

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "FECHA_INVALIDA"


def test_crear_lectura_fecha_hoy_se_acepta():
    # Hoy es el límite, no un caso rechazado — T-35 solo prohíbe fechas *futuras*.
    lectura_id = str(uuid4())
    sobreescribir_conexion(respuestas=[(True,), (lectura_id,), None])

    hoy = date.today().isoformat()
    respuesta = client.post("/api/lecturas", json={**CUERPO_BASE, "fecha": hoy})

    assert respuesta.status_code == 201
    assert respuesta.json()["fecha"] == hoy


def test_crear_lectura_validacion_falla():
    # FastAPI resuelve las dependencias (incluida la conexión) antes de evaluar si el cuerpo
    # es inválido, así que igual hay que reemplazarla aunque nunca se llegue a usar.
    sobreescribir_conexion(respuestas=[])

    respuesta = client.post("/api/lecturas", json={"medidor_id": "no-es-un-uuid"})

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"
