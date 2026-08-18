import { useState } from 'react'
import { ErrorApiLecturas, obtenerHistorial, type LecturaHistorialItem } from './api/lecturas'

type Estado = 'inicio' | 'cargando' | 'listo' | 'error'

function textoOrigen(origen: string): string {
  return origen === 'manual' ? 'Manual' : 'Reconocimiento automático'
}

function textoConsumo(lectura: LecturaHistorialItem): string {
  if (lectura.consumo_desde_anterior_m3 == null || lectura.dias_desde_anterior == null) {
    return 'Primera lectura registrada de este medidor — todavía no hay consumo que calcular.'
  }
  return `${lectura.consumo_desde_anterior_m3} m³ en ${lectura.dias_desde_anterior} días`
}

function PantallaHistorial() {
  const [medidorId, setMedidorId] = useState('')
  const [estado, setEstado] = useState<Estado>('inicio')
  const [lecturas, setLecturas] = useState<LecturaHistorialItem[]>([])
  const [mensajeError, setMensajeError] = useState<string | null>(null)

  async function manejarCargar() {
    setEstado('cargando')
    setMensajeError(null)
    try {
      const historial = await obtenerHistorial(medidorId)
      setLecturas(historial.lecturas)
      setEstado('listo')
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApiLecturas ? error.message : 'No se pudo cargar el historial.',
      )
      setEstado('error')
    }
  }

  return (
    <section>
      <h2>Historial de lecturas</h2>

      <label htmlFor="medidor-historial">Medidor</label>
      <input
        id="medidor-historial"
        value={medidorId}
        onChange={(evento) => setMedidorId(evento.target.value)}
        placeholder="ID del medidor"
      />
      <button type="button" onClick={manejarCargar} disabled={!medidorId || estado === 'cargando'}>
        {estado === 'cargando' ? 'Cargando…' : 'Ver historial'}
      </button>

      {mensajeError && <p role="alert">{mensajeError}</p>}

      {estado === 'listo' && lecturas.length === 0 && (
        <p>Este medidor todavía no tiene lecturas registradas.</p>
      )}

      {estado === 'listo' && lecturas.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Lectura (m³)</th>
              <th>Origen</th>
              <th>Consumo del período</th>
            </tr>
          </thead>
          <tbody>
            {lecturas.map((lectura) => (
              <tr key={lectura.id}>
                <td>{lectura.fecha}</td>
                <td>{lectura.valor}</td>
                <td>{textoOrigen(lectura.origen)}</td>
                <td>{textoConsumo(lectura)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

export default PantallaHistorial
