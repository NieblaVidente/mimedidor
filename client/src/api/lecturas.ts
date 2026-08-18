/**
 * Cliente de las dos rutas de lecturas del contrato de la API
 * (docs/architecture/contrato-api.md §2 y §3). Rutas relativas: el cliente y el servidor se
 * sirven desde el mismo origen en este sprint, no hay configuración de host aparte.
 */

export class ErrorApiLecturas extends Error {
  codigo: string

  constructor(codigo: string, mensaje: string) {
    super(mensaje)
    this.name = 'ErrorApiLecturas'
    this.codigo = codigo
  }
}

interface CuerpoError {
  error: { codigo: string; mensaje: string }
}

async function lanzarError(respuesta: Response): Promise<never> {
  const cuerpo = (await respuesta.json().catch(() => null)) as CuerpoError | null
  const error = cuerpo?.error ?? { codigo: 'ERROR_INTERNO', mensaje: 'Ocurrió un error inesperado' }
  throw new ErrorApiLecturas(error.codigo, error.mensaje)
}

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
