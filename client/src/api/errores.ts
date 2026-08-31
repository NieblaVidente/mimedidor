/**
 * Manejo de errores compartido por los módulos de `client/src/api/*` (T-33).
 *
 * Antes de esta tarjeta, `lecturas.ts` y `facturas.ts` declaraban cada uno su propia clase
 * (`ErrorApiLecturas` / `ErrorApiFacturas`) y su propia función `lanzarError`, idénticas salvo
 * el nombre. Pasó porque las ramas de T-16, T-17 y T-18 salieron de `main` en paralelo, antes de
 * que ninguna estuviera mergeada, y se prefirió duplicar unas líneas antes que encadenar los PR
 * entre sí (ver `docs/deuda-tecnica.md`, sección "T-16 / T-17 / T-18"). Ahora que las tres ramas
 * ya están en `main`, este módulo es el único lugar donde vive esa lógica.
 */

export class ErrorApi extends Error {
  codigo: string

  constructor(codigo: string, mensaje: string) {
    super(mensaje)
    this.name = 'ErrorApi'
    this.codigo = codigo
  }
}

interface CuerpoError {
  error: { codigo: string; mensaje: string }
}

export async function lanzarError(respuesta: Response): Promise<never> {
  const cuerpo = (await respuesta.json().catch(() => null)) as CuerpoError | null
  const error = cuerpo?.error ?? { codigo: 'ERROR_INTERNO', mensaje: 'Ocurrió un error inesperado' }
  throw new ErrorApi(error.codigo, error.mensaje)
}
