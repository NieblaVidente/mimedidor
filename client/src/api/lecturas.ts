/**
 * Cliente de las rutas de lecturas del contrato de la API (docs/architecture/contrato-api.md
 * §2, §3 y §4). Rutas relativas: el cliente y el servidor se sirven desde el mismo origen en
 * este sprint, no hay configuración de host aparte.
 *
 * El manejo de errores vive en `./errores` (T-33) — antes este módulo declaraba su propia clase
 * duplicada, ver `docs/deuda-tecnica.md`.
 */

import { lanzarError } from './errores'

export interface ResultadoReconocimiento {
  lectura_reconocida: number
  confianza: number | null
}

export async function reconocerFoto(
  foto: Blob,
  medidorId: string,
): Promise<ResultadoReconocimiento> {
  const formulario = new FormData()
  formulario.append('foto', foto, 'foto.jpg')
  formulario.append('medidor_id', medidorId)

  const respuesta = await fetch('/api/lecturas/reconocer', {
    method: 'POST',
    body: formulario,
  })
  if (!respuesta.ok) return lanzarError(respuesta)
  return (await respuesta.json()) as ResultadoReconocimiento
}

export interface LecturaNueva {
  medidor_id: string
  valor: number
  fecha: string
  origen: 'reconocimiento' | 'manual'
  foto_url?: string | null
}

export interface LecturaGuardada {
  id: string
  medidor_id: string
  valor: number
  fecha: string
  origen: string
  consumo_desde_anterior_m3: number | null
  dias_desde_anterior: number | null
}

export async function guardarLectura(datos: LecturaNueva): Promise<LecturaGuardada> {
  const respuesta = await fetch('/api/lecturas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  if (!respuesta.ok) return lanzarError(respuesta)
  return (await respuesta.json()) as LecturaGuardada
}

// --- Historial (T-17) ---

export interface LecturaHistorialItem {
  id: string
  valor: number
  fecha: string
  origen: string
  consumo_desde_anterior_m3: number | null
  dias_desde_anterior: number | null
}

export interface Historial {
  lecturas: LecturaHistorialItem[]
}

export async function obtenerHistorial(medidorId: string): Promise<Historial> {
  const respuesta = await fetch(`/api/lecturas?medidor_id=${encodeURIComponent(medidorId)}`)
  if (!respuesta.ok) return lanzarError(respuesta)
  return (await respuesta.json()) as Historial
}
