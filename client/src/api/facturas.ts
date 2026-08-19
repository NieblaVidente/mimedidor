/**
 * Cliente de las rutas de facturas del contrato de la API (docs/architecture/contrato-api.md
 * §5 y §6). Rutas relativas: mismo origen que el servidor en este sprint.
 *
 * DEUDA TÉCNICA: esta rama nació de `main` sin los PR de T-16/T-17 (todavía sin mergear), así
 * que no puede importar `ErrorApiLecturas` de `./lecturas` — ese archivo no existe acá. Se
 * duplica la clase en vez de encadenar una dependencia entre ramas que se van a reconciliar por
 * separado. Cuando las tres ramas ya estén en `main`, vale la pena unificar el manejo de error
 * en un solo módulo (`api/errores.ts`) del que `lecturas.ts` y `facturas.ts` importen.
 */

export class ErrorApiFacturas extends Error {
  codigo: string

  constructor(codigo: string, mensaje: string) {
    super(mensaje)
    this.name = 'ErrorApiFacturas'
    this.codigo = codigo
  }
}

interface CuerpoError {
  error: { codigo: string; mensaje: string }
}

async function lanzarError(respuesta: Response): Promise<never> {
  const cuerpo = (await respuesta.json().catch(() => null)) as CuerpoError | null
  const error = cuerpo?.error ?? { codigo: 'ERROR_INTERNO', mensaje: 'Ocurrió un error inesperado' }
  throw new ErrorApiFacturas(error.codigo, error.mensaje)
}

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
