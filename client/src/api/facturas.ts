/**
 * Cliente de las rutas de facturas del contrato de la API (docs/architecture/contrato-api.md
 * §5 y §6). Rutas relativas: mismo origen que el servidor en este sprint.
 *
 * El manejo de errores vive en `./errores` (T-33) — antes este módulo declaraba su propia clase
 * duplicada, ver `docs/deuda-tecnica.md`.
 */

import { lanzarError } from './errores'

export interface FacturaNueva {
  medidor_id: string
  periodo_inicio: string
  periodo_fin: string
  consumo_facturado_m3: number
  monto: number
}

export interface FacturaGuardada extends FacturaNueva {
  id: string
}

export async function guardarFactura(datos: FacturaNueva): Promise<FacturaGuardada> {
  const respuesta = await fetch('/api/facturas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  if (!respuesta.ok) return lanzarError(respuesta)
  return (await respuesta.json()) as FacturaGuardada
}

export interface Comparacion {
  factura_id: string
  consumo_medido_m3: number | null
  consumo_facturado_m3: number
  diferencia_m3: number | null
  diferencia_porcentual: number | null
  supera_umbral: boolean
}

export async function obtenerComparacion(facturaId: string): Promise<Comparacion> {
  const respuesta = await fetch(`/api/facturas/${encodeURIComponent(facturaId)}/comparacion`)
  if (!respuesta.ok) return lanzarError(respuesta)
  return (await respuesta.json()) as Comparacion
}
