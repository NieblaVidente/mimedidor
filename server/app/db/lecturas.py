"""Acceso a datos de lecturas. Cada función abre su propio cursor sobre la conexión recibida
— la conexión la maneja el dependency de FastAPI (app/db/conexion.py), no este módulo.
"""

from datetime import date
from uuid import UUID


def medidor_existe(conexion, medidor_id: UUID) -> bool:
    with conexion.cursor() as cur:
        cur.execute("SELECT 1 FROM mimedidor.medidor WHERE id = %s", (str(medidor_id),))
        return cur.fetchone() is not None


def llamar_registrar_lectura(
    conexion,
    medidor_id: UUID,
    valor: float,
    fecha: date,
    origen: str,
    foto_url: str | None,
) -> str:
    """Llama al procedimiento de T-14. Si la lectura es menor que la anterior, el procedimiento
    lanza una excepción con el prefijo 'LECTURA_INVALIDA:' (ver database/scripts/
    04_procedimiento_registrar_lectura.sql) — el llamador la traduce al código del contrato.
    """
    with conexion.cursor() as cur:
        cur.execute(
            "CALL mimedidor.registrar_lectura(%s, %s, %s, %s, %s, NULL)",
            (str(medidor_id), valor, fecha, origen, foto_url),
        )
        fila = cur.fetchone()
        return str(fila[0])


def obtener_lectura_anterior(
    conexion, medidor_id: UUID, lectura_id_actual: str
) -> tuple[float, date] | None:
    """La lectura inmediatamente anterior a la que se acaba de guardar, para calcular el
    consumo del período. Misma regla de orden que usa el procedimiento de T-14: por fecha y,
    en empate, por el momento en que se creó la fila.
    """
    with conexion.cursor() as cur:
        cur.execute(
            """
            SELECT valor, fecha
            FROM mimedidor.lectura
            WHERE medidor_id = %s AND id != %s
            ORDER BY fecha DESC, creado_en DESC
            LIMIT 1
            """,
            (str(medidor_id), lectura_id_actual),
        )
        return cur.fetchone()


def listar_lecturas(
    conexion, medidor_id: UUID
) -> list[tuple[str, float, date, str]]:
    """Todas las lecturas de un medidor, de la más vieja a la más nueva (T-17). El consumo y
    los días entre lecturas se calculan en Python sobre esta lista (ver app/api/lecturas.py),
    no acá: la vista `vista_historial_lecturas` que T-12 documentó nunca se implementó en T-13
    (mismo hueco que ya resolvimos así en T-15, ver docs/architecture/modelo-datos.md §3).
    """
    with conexion.cursor() as cur:
        cur.execute(
            """
            SELECT id, valor, fecha, origen
            FROM mimedidor.lectura
            WHERE medidor_id = %s
            ORDER BY fecha ASC, creado_en ASC
            """,
            (str(medidor_id),),
        )
        return cur.fetchall()
