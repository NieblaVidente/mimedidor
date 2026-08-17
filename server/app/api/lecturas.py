from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import lecturas as db_lecturas
from app.db.conexion import obtener_conexion
from app.errores import ErrorAPI

router = APIRouter(prefix="/api/lecturas", tags=["lecturas"])


class LecturaEntrada(BaseModel):
    medidor_id: UUID
    valor: float = Field(ge=0)
    fecha: date
    origen: Literal["reconocimiento", "manual"]
    foto_url: str | None = None


class LecturaSalida(BaseModel):
    id: UUID
    medidor_id: UUID
    valor: float
    fecha: date
    origen: str
    consumo_desde_anterior_m3: float | None
    dias_desde_anterior: int | None


@router.post("", status_code=201, response_model=LecturaSalida)
def crear_lectura(entrada: LecturaEntrada, conexion=Depends(obtener_conexion)) -> LecturaSalida:
    """Guarda una lectura ya confirmada o corregida por el usuario (contrato de la API §3).

    No hace reconocimiento de imagen — eso es POST /api/lecturas/reconocer, que depende de
    T-09/T-10 y todavía no existe (ver la nota de alcance en la tarjeta T-15 de Trello).
    """
    if not db_lecturas.medidor_existe(conexion, entrada.medidor_id):
        raise ErrorAPI(
            "MEDIDOR_NO_ENCONTRADO",
            f"No existe un medidor con id {entrada.medidor_id}",
            404,
        )

    try:
        lectura_id = db_lecturas.llamar_registrar_lectura(
            conexion,
            entrada.medidor_id,
            entrada.valor,
            entrada.fecha,
            entrada.origen,
            entrada.foto_url,
        )
    except Exception as error:
        mensaje = str(error)
        if "LECTURA_INVALIDA" in mensaje:
            detalle = mensaje.split("LECTURA_INVALIDA:", 1)[-1].strip()
            raise ErrorAPI("LECTURA_INVALIDA", detalle, 422) from error
        raise

    anterior = db_lecturas.obtener_lectura_anterior(conexion, entrada.medidor_id, lectura_id)
    if anterior is None:
        consumo_desde_anterior_m3, dias_desde_anterior = None, None
    else:
        valor_anterior, fecha_anterior = anterior
        consumo_desde_anterior_m3 = float(entrada.valor) - float(valor_anterior)
        dias_desde_anterior = (entrada.fecha - fecha_anterior).days

    return LecturaSalida(
        id=lectura_id,
        medidor_id=entrada.medidor_id,
        valor=entrada.valor,
        fecha=entrada.fecha,
        origen=entrada.origen,
        consumo_desde_anterior_m3=consumo_desde_anterior_m3,
        dias_desde_anterior=dias_desde_anterior,
    )
