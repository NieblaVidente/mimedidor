"""Conexión falsa compartida entre las pruebas que mockean la base de datos (T-15, T-17, T-18).

No se conecta a Postgres real — el job `server` del CI no lo necesita, eso ya lo cubre el job
`database` para los scripts SQL en sí. `fetchone()` simula un `SELECT ... LIMIT 1` (una fila o
`None`); `fetchall()` simula un `SELECT` de varias filas, devolviendo todo lo que quede en la
cola de respuestas de una sola vez.
"""

import pytest

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

    def fetchall(self):
        restantes = self._respuestas
        self._respuestas = []
        return restantes


class ConexionFalsa:
    def __init__(self, respuestas, excepcion_en_llamada=None):
        self._cursor = CursorFalso(respuestas, excepcion_en_llamada)

    def cursor(self):
        return self._cursor


def sobreescribir_conexion(respuestas, excepcion_en_llamada=None):
    app.dependency_overrides[obtener_conexion] = lambda: ConexionFalsa(
        respuestas, excepcion_en_llamada
    )


@pytest.fixture(autouse=True)
def _limpiar_overrides_de_dependencias():
    yield
    app.dependency_overrides.clear()
