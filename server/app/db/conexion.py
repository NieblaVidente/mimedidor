from collections.abc import Generator

import psycopg


def obtener_conexion() -> Generator[psycopg.Connection, None, None]:
    """Dependencia de FastAPI: una conexión por petición, cerrada al terminar.

    Lee la configuración de las variables de entorno estándar de libpq (PGHOST, PGPORT,
    PGDATABASE, PGUSER, PGPASSWORD) — mismas variables que ya usa el job `database` del CI y
    `database/README.md` para correr los scripts. No hace falta parsear nada a mano.
    """
    conexion = psycopg.connect(autocommit=True)
    try:
        yield conexion
    finally:
        conexion.close()
