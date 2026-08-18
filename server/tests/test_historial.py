"""Pruebas unitarias de GET /api/lecturas (T-17).

Conexión falsa compartida en conftest.py. El consumo entre lecturas consecutivas se calcula en
Python (app/api/lecturas.py), no en SQL — ver la nota en app/db/lecturas.py sobre por qué
(vista_historial_lecturas nunca se implementó en T-13).
"""

from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import sobreescribir_conexion

client = TestClient(app)


def test_listar_historial_medidor_no_encontrado():
    sobreescribir_conexion(respuestas=[None])

    respuesta = client.get(f"/api/lecturas?medidor_id={uuid4()}")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "MEDIDOR_NO_ENCONTRADO"


def test_listar_historial_sin_lecturas():
    sobreescribir_conexion(respuestas=[(True,)])

    respuesta = client.get(f"/api/lecturas?medidor_id={uuid4()}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"lecturas": []}


def test_listar_historial_calcula_consumo_entre_lecturas_consecutivas():
    id1, id2, id3 = str(uuid4()), str(uuid4()), str(uuid4())
    sobreescribir_conexion(
        respuestas=[
            (True,),  # existencia del medidor
            (id1, 100.0, date(2026, 6, 1), "manual"),
            (id2, 112.0, date(2026, 7, 1), "manual"),
            (id3, 130.0, date(2026, 8, 1), "reconocimiento"),
        ]
    )

    respuesta = client.get(f"/api/lecturas?medidor_id={uuid4()}")

    assert respuesta.status_code == 200
    lecturas = respuesta.json()["lecturas"]
    assert [lectura["id"] for lectura in lecturas] == [id1, id2, id3]

    assert lecturas[0]["consumo_desde_anterior_m3"] is None
    assert lecturas[0]["dias_desde_anterior"] is None

    assert lecturas[1]["consumo_desde_anterior_m3"] == 12.0
    assert lecturas[1]["dias_desde_anterior"] == 30  # junio tiene 30 días

    assert lecturas[2]["consumo_desde_anterior_m3"] == 18.0
    assert lecturas[2]["dias_desde_anterior"] == 31  # julio tiene 31 días


def test_listar_historial_valida_medidor_id_como_uuid():
    # FastAPI resuelve la conexión antes de validar los parámetros de la petición (mismo
    # detalle que en test_lecturas.py::test_crear_lectura_validacion_falla).
    sobreescribir_conexion(respuestas=[])

    respuesta = client.get("/api/lecturas?medidor_id=no-es-un-uuid")

    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["codigo"] == "VALIDACION"
