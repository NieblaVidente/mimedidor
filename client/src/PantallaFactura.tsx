import { useState, type FormEvent } from 'react'
import { guardarFactura, obtenerComparacion, type Comparacion } from './api/facturas'
import { ErrorApi } from './api/errores'

type Estado = 'formulario' | 'procesando' | 'listo'

function textoDiferencia(comparacion: Comparacion): string {
  if (comparacion.consumo_medido_m3 == null || comparacion.diferencia_m3 == null) {
    return 'No hay suficientes lecturas propias en este período para comparar todavía.'
  }
  const direccion = comparacion.diferencia_m3 > 0 ? 'más' : 'menos'
  return (
    `El operador facturó ${Math.abs(comparacion.diferencia_m3)} m³ ${direccion} de lo que ` +
    `midieron tus propias lecturas (${comparacion.diferencia_porcentual}% de diferencia).`
  )
}

function PantallaFactura() {
  const [medidorId, setMedidorId] = useState('')
  const [periodoInicio, setPeriodoInicio] = useState('')
  const [periodoFin, setPeriodoFin] = useState('')
  const [consumoFacturado, setConsumoFacturado] = useState('')
  const [monto, setMonto] = useState('')

  const [estado, setEstado] = useState<Estado>('formulario')
  const [comparacion, setComparacion] = useState<Comparacion | null>(null)
  const [mensajeError, setMensajeError] = useState<string | null>(null)

  const formularioValido =
    medidorId.trim() !== '' &&
    periodoInicio !== '' &&
    periodoFin !== '' &&
    consumoFacturado.trim() !== '' &&
    monto.trim() !== '' &&
    !Number.isNaN(Number(consumoFacturado)) &&
    !Number.isNaN(Number(monto))

  async function manejarEnviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!formularioValido) {
      setMensajeError('Completá todos los campos con valores válidos antes de registrar la factura.')
      return
    }
    setEstado('procesando')
    setMensajeError(null)
    try {
      const factura = await guardarFactura({
        medidor_id: medidorId,
        periodo_inicio: periodoInicio,
        periodo_fin: periodoFin,
        consumo_facturado_m3: Number(consumoFacturado),
        monto: Number(monto),
      })
      const resultado = await obtenerComparacion(factura.id)
      setComparacion(resultado)
      setEstado('listo')
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi ? error.message : 'No se pudo registrar la factura.',
      )
      setEstado('formulario')
    }
  }

  function manejarNuevaFactura() {
    setEstado('formulario')
    setComparacion(null)
    setMensajeError(null)
  }

  if (estado === 'listo' && comparacion) {
    return (
      <section>
        <h2>Comparación de tu factura</h2>
        <p>Consumo facturado: {comparacion.consumo_facturado_m3} m³</p>
        <p>
          Consumo medido por tus lecturas:{' '}
          {comparacion.consumo_medido_m3 == null ? '—' : `${comparacion.consumo_medido_m3} m³`}
        </p>
        <p>{textoDiferencia(comparacion)}</p>
        {comparacion.supera_umbral && (
          <p role="alert">La diferencia supera el umbral esperado — vale la pena revisarla.</p>
        )}
        <button type="button" onClick={manejarNuevaFactura}>
          Registrar otra factura
        </button>
      </section>
    )
  }

  return (
    <section>
      <h2>Registrar factura</h2>
      <form onSubmit={manejarEnviar}>
        <label htmlFor="factura-medidor">Medidor</label>
        <input
          id="factura-medidor"
          value={medidorId}
          onChange={(evento) => setMedidorId(evento.target.value)}
          placeholder="ID del medidor"
        />

        <label htmlFor="factura-inicio">Inicio del período</label>
        <input
          id="factura-inicio"
          type="date"
          value={periodoInicio}
          onChange={(evento) => setPeriodoInicio(evento.target.value)}
        />

        <label htmlFor="factura-fin">Fin del período</label>
        <input
          id="factura-fin"
          type="date"
          value={periodoFin}
          onChange={(evento) => setPeriodoFin(evento.target.value)}
        />

        <label htmlFor="factura-consumo">Consumo facturado (m³)</label>
        <input
          id="factura-consumo"
          inputMode="decimal"
          value={consumoFacturado}
          onChange={(evento) => setConsumoFacturado(evento.target.value)}
        />

        <label htmlFor="factura-monto">Monto (₡)</label>
        <input
          id="factura-monto"
          inputMode="decimal"
          value={monto}
          onChange={(evento) => setMonto(evento.target.value)}
        />

        <button type="submit" disabled={estado === 'procesando'}>
          {estado === 'procesando' ? 'Procesando…' : 'Registrar y comparar'}
        </button>
      </form>

      {mensajeError && <p role="alert">{mensajeError}</p>}
    </section>
  )
}

export default PantallaFactura
