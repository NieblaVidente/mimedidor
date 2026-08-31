from datetime import date
from typing import Literal
from uuid import UUID

import cv2
import numpy as np
from fastapi import APIRouter, Depends, Form, UploadFile
from pydantic import BaseModel, Field

from app.db import lecturas as db_lecturas
from app.db.conexion import obtener_conexion
from app.errores import ErrorAPI
from app.vision.preprocesamiento import CaratulaNoDetectada, preprocesar_caratula
from app.vision.reconocimiento import reconocer_lectura
from app.vision.segmentacion import segmentar_ventana_odometro

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


class ReconocimientoSalida(BaseModel):
    lectura_reconocida: float
    confianza: float | None


@router.post("/reconocer", status_code=200, response_model=ReconocimientoSalida)
async def reconocer_foto(
    foto: UploadFile,
    medidor_id: UUID = Form(...),
    # medidor_id se recibe porque el contrato lo pide, pero no se usa acá: esta ruta no persiste
    # nada (POST /api/lecturas sí valida el medidor cuando se guarda de verdad), y no consultar
    # la base acá evita darle una dependencia de conexión a un endpoint puramente de visión.
) -> ReconocimientoSalida:
    """Corre la cadena T-09 → T-10 → T-11 sobre una foto y devuelve la lectura reconocida
    **sin guardarla** (contrato de la API §2). Guardarla es POST /api/lecturas (T-15).

    `confianza` siempre viaja en `null`: `reconocer_lectura` (T-11) no expone una medida de
    confianza — Tesseract no la da directo, y el contrato ya contempla ese caso.
    """
    contenido = await foto.read()
    arreglo = np.frombuffer(contenido, dtype=np.uint8)
    imagen_bgr = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)
    if imagen_bgr is None:
        raise ErrorAPI("IMAGEN_ILEGIBLE", "El archivo recibido no es una imagen válida", 422)

    try:
        caratula = preprocesar_caratula(imagen_bgr)
    except CaratulaNoDetectada as error:
        raise ErrorAPI(
            "IMAGEN_ILEGIBLE", "No se pudo detectar la carátula del hidrómetro en la foto", 422
        ) from error

    ventana = segmentar_ventana_odometro(caratula.imagen)
    lectura = reconocer_lectura(ventana.imagen)

    if lectura is None:
        raise ErrorAPI(
            "IMAGEN_ILEGIBLE", "No se pudo leer la lectura del odómetro en la foto", 422
        )

    return ReconocimientoSalida(lectura_reconocida=lectura, confianza=None)


class LecturaHistorial(BaseModel):
    id: UUID
    valor: float
    fecha: date
    origen: str
    consumo_desde_anterior_m3: float | None
    dias_desde_anterior: int | None


class HistorialSalida(BaseModel):
    lecturas: list[LecturaHistorial]


@router.get("", response_model=HistorialSalida)
def listar_historial(medidor_id: UUID, conexion=Depends(obtener_conexion)) -> HistorialSalida:
    """Historial de lecturas de un medidor, de la más vieja a la más nueva, con el consumo
    calculado entre lecturas consecutivas (contrato de la API §4, tarjeta T-17).
    """
    if not db_lecturas.medidor_existe(conexion, medidor_id):
        raise ErrorAPI(
            "MEDIDOR_NO_ENCONTRADO",
            f"No existe un medidor con id {medidor_id}",
            404,
        )

    filas = db_lecturas.listar_lecturas(conexion, medidor_id)

    lecturas: list[LecturaHistorial] = []
    valor_anterior: float | None = None
    fecha_anterior: date | None = None
    for id_lectura, valor, fecha, origen in filas:
        if valor_anterior is None:
            consumo_desde_anterior_m3, dias_desde_anterior = None, None
        else:
            consumo_desde_anterior_m3 = float(valor) - float(valor_anterior)
            dias_desde_anterior = (fecha - fecha_anterior).days
        lecturas.append(
            LecturaHistorial(
                id=id_lectura,
                valor=valor,
                fecha=fecha,
                origen=origen,
                consumo_desde_anterior_m3=consumo_desde_anterior_m3,
                dias_desde_anterior=dias_desde_anterior,
            )
        )
        valor_anterior, fecha_anterior = valor, fecha

    return HistorialSalida(lecturas=lecturas)


@router.post("", status_code=201, response_model=LecturaSalida)
def crear_lectura(entrada: LecturaEntrada, conexion=Depends(obtener_conexion)) -> LecturaSalida:
    """Guarda una lectura ya confirmada o corregida por el usuario (contrato de la API §3).

    No hace reconocimiento de imagen — eso es POST /api/lecturas/reconocer (arriba).
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
            # Solo la primera línea. psycopg adjunta al mensaje el bloque CONTEXT de PostgreSQL,
            # que trae el nombre del procedimiento PL/pgSQL, su firma completa y el número de
            # línea donde se lanzó — detalles del motor que no pueden salir hacia el cliente
            # (CLAUDE.md §11). El detalle completo igual queda en el log del servidor.
            detalle = mensaje.split("LECTURA_INVALIDA:", 1)[-1].splitlines()[0].strip()
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
