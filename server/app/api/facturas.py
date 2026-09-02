from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.db import facturas as db_facturas
from app.db import lecturas as db_lecturas
from app.db.conexion import obtener_conexion
from app.errores import ErrorAPI

router = APIRouter(prefix="/api/facturas", tags=["facturas"])

# Umbral fijo para este sprint (contrato de la API §6: "un valor fijo razonable" hasta que se
# implemente T-18). Hacerlo configurable por el usuario es alcance de Sprint 2.
UMBRAL_DIFERENCIA_PORCENTUAL = 15.0


class FacturaEntrada(BaseModel):
    medidor_id: UUID
    periodo_inicio: date
    periodo_fin: date
    consumo_facturado_m3: float = Field(ge=0)
    monto: float = Field(ge=0)


class FacturaSalida(BaseModel):
    id: UUID
    medidor_id: UUID
    periodo_inicio: date
    periodo_fin: date
    consumo_facturado_m3: float
    monto: float


@router.post("", status_code=201, response_model=FacturaSalida)
def crear_factura(entrada: FacturaEntrada, conexion=Depends(obtener_conexion)) -> FacturaSalida:
    """Registra una factura ingresada manualmente por el usuario (contrato de la API §5)."""
    if entrada.periodo_fin <= entrada.periodo_inicio:
        # Mismo criterio que el CHECK de 02_tablas.sql — se valida acá primero para devolver
        # un 400 VALIDACION claro en vez de dejar que la base rechace el INSERT.
        raise ErrorAPI("VALIDACION", "periodo_fin debe ser posterior a periodo_inicio", 400)

    if not db_lecturas.medidor_existe(conexion, entrada.medidor_id):
        raise ErrorAPI(
            "MEDIDOR_NO_ENCONTRADO",
            f"No existe un medidor con id {entrada.medidor_id}",
            404,
        )

    factura_id = db_facturas.crear_factura(
        conexion,
        entrada.medidor_id,
        entrada.periodo_inicio,
        entrada.periodo_fin,
        entrada.consumo_facturado_m3,
        entrada.monto,
    )

    return FacturaSalida(id=factura_id, **entrada.model_dump())


class ComparacionSalida(BaseModel):
    factura_id: UUID
    consumo_medido_m3: float | None
    consumo_facturado_m3: float
    diferencia_m3: float | None
    diferencia_porcentual: float | None
    supera_umbral: bool


@router.get("/{factura_id}/comparacion", response_model=ComparacionSalida)
def comparar_factura(
    factura_id: UUID, conexion=Depends(obtener_conexion)
) -> ComparacionSalida:
    """Cierra el hilo funcional del sprint (contrato de la API §6): consumo medido por las
    lecturas propias contra el consumo facturado, en el mismo período de la factura.

    El consumo medido se calcula igual que lo haría el operador real: la lectura del medidor
    más reciente hasta el inicio del período, contra la más reciente hasta el fin del período.
    Si falta cualquiera de las dos, no hay forma honesta de calcular un consumo — se devuelve
    `None` en vez de inventar un número (mismo criterio de T-11: no maquillar).
    """
    factura = db_facturas.obtener_factura(conexion, factura_id)
    if factura is None:
        raise ErrorAPI(
            "FACTURA_NO_ENCONTRADA", f"No existe una factura con id {factura_id}", 404
        )

    medidor_id, periodo_inicio, periodo_fin, consumo_facturado_m3 = factura

    lectura_inicio = db_facturas.lectura_mas_reciente_hasta(conexion, medidor_id, periodo_inicio)
    lectura_fin = db_facturas.lectura_mas_reciente_hasta(conexion, medidor_id, periodo_fin)

    consumo_medido_m3: float | None = None
    if lectura_inicio is not None and lectura_fin is not None:
        valor_inicio, fecha_inicio = lectura_inicio
        valor_fin, fecha_fin = lectura_fin
        if fecha_fin > fecha_inicio:
            # Redondeado a 3, que es la escala de `lectura.valor`. Restar dos flotantes deja
            # restos: 526.69 - 510.69 da 16.000000000000057, y ese numero llegaba tal cual a la
            # pantalla del abonado. Antes de T-39 no se notaba porque las lecturas eran enteras.
            consumo_medido_m3 = round(float(valor_fin) - float(valor_inicio), 3)

    diferencia_m3: float | None = None
    diferencia_porcentual: float | None = None
    supera_umbral = False
    if consumo_medido_m3 is not None and consumo_facturado_m3:
        diferencia_m3 = round(float(consumo_facturado_m3) - consumo_medido_m3, 3)
        diferencia_porcentual = round(diferencia_m3 / float(consumo_facturado_m3) * 100, 1)
        supera_umbral = abs(diferencia_porcentual) > UMBRAL_DIFERENCIA_PORCENTUAL

    return ComparacionSalida(
        factura_id=factura_id,
        consumo_medido_m3=consumo_medido_m3,
        consumo_facturado_m3=consumo_facturado_m3,
        diferencia_m3=diferencia_m3,
        diferencia_porcentual=diferencia_porcentual,
        supera_umbral=supera_umbral,
    )
