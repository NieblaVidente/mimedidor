"""Acceso a datos de facturas y de la comparación contra el consumo medido (T-18). Mismo
patrón que app/db/lecturas.py: cada función abre su propio cursor sobre la conexión recibida.
"""

from datetime import date
from uuid import UUID


def crear_factura(
    conexion,
    medidor_id: UUID,
    periodo_inicio: date,
    periodo_fin: date,
    consumo_facturado_m3: float,
    monto: float,
) -> str:
    with conexion.cursor() as cur:
        cur.execute(
            """
            INSERT INTO mimedidor.factura
                (medidor_id, periodo_inicio, periodo_fin, consumo_facturado_m3, monto)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (str(medidor_id), periodo_inicio, periodo_fin, consumo_facturado_m3, monto),
        )
        fila = cur.fetchone()
        return str(fila[0])


def obtener_factura(
    conexion, factura_id: UUID
) -> tuple[str, date, date, float] | None:
    """(medidor_id, periodo_inicio, periodo_fin, consumo_facturado_m3), o None si no existe."""
    with conexion.cursor() as cur:
        cur.execute(
            """
            SELECT medidor_id, periodo_inicio, periodo_fin, consumo_facturado_m3
            FROM mimedidor.factura
            WHERE id = %s
            """,
            (str(factura_id),),
        )
        return cur.fetchone()


def lectura_mas_reciente_hasta(
    conexion, medidor_id: UUID, fecha_limite: date
) -> tuple[float, date] | None:
    """(valor, fecha) de la última lectura del medidor con fecha <= fecha_limite, o None si no
    hay ninguna. Es el mismo concepto que usan las utilities de verdad para facturar: el valor
    del medidor al cierre de cada extremo del período.
    """
    with conexion.cursor() as cur:
        cur.execute(
            """
            SELECT valor, fecha
            FROM mimedidor.lectura
            WHERE medidor_id = %s AND fecha <= %s
            ORDER BY fecha DESC, creado_en DESC
            LIMIT 1
            """,
            (str(medidor_id), fecha_limite),
        )
        return cur.fetchone()
