import { useEffect, useRef, useState } from 'react'
import { abrirCamara, capturarFotograma, detenerCamara } from './camara'
import { guardarLectura, reconocerFoto, type LecturaGuardada } from './api/lecturas'
import { ErrorApi } from './api/errores'

type Estado = 'inicio' | 'camara' | 'reconociendo' | 'revisando' | 'guardando' | 'guardado'

function fechaHoyISO(): string {
  // OJO: `new Date().toISOString()` da la fecha en UTC, no la fecha local — en Costa Rica
  // (UTC-6), entre las 18:00 y la medianoche, UTC ya está en el día siguiente. Con esa fecha
  // "de mañana" el servidor la rechazaba con FECHA_INVALIDA (T-35) siendo todavía hoy acá.
  // Se arma a mano con los componentes locales para evitar la conversión a UTC.
  const hoy = new Date()
  const año = hoy.getFullYear()
  const mes = String(hoy.getMonth() + 1).padStart(2, '0')
  const dia = String(hoy.getDate()).padStart(2, '0')
  return `${año}-${mes}-${dia}`
}

function PantallaCaptura() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const [medidorId, setMedidorId] = useState('')
  const [estado, setEstado] = useState<Estado>('inicio')
  const [valorTexto, setValorTexto] = useState('')
  // Hoy por defecto, pero editable (T-35): antes se guardaba siempre con la fecha de hoy, sin
  // contemplar que el abonado normalmente toma la foto en el patio y registra la lectura después.
  const [fecha, setFecha] = useState(fechaHoyISO())
  const [origen, setOrigen] = useState<'reconocimiento' | 'manual'>('manual')
  const [mensajeError, setMensajeError] = useState<string | null>(null)
  const [lecturaGuardada, setLecturaGuardada] = useState<LecturaGuardada | null>(null)

  // El stream se asigna al <video> acá, no en manejarAbrirCamara: el elemento solo existe en el
  // DOM cuando estado === 'camara', y ese cambio de estado todavía no se renderizó en el momento
  // en que manejarAbrirCamara termina de correr.
  useEffect(() => {
    if (estado === 'camara' && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current
      videoRef.current.play().catch(() => {
        // Reproducción rechazada por el navegador (autoplay, permisos) — no rompe el flujo,
        // el usuario igual puede intentar tomar la foto.
      })
    }
  }, [estado])

  useEffect(() => {
    return () => {
      if (streamRef.current) detenerCamara(streamRef.current)
    }
  }, [])

  async function manejarAbrirCamara() {
    setMensajeError(null)
    try {
      streamRef.current = await abrirCamara()
      setEstado('camara')
    } catch {
      setMensajeError('No se pudo acceder a la cámara. Revisá los permisos del navegador.')
    }
  }

  async function manejarTomarFoto() {
    if (!videoRef.current) return
    try {
      const foto = await capturarFotograma(videoRef.current)
      if (streamRef.current) {
        detenerCamara(streamRef.current)
        streamRef.current = null
      }
      setEstado('reconociendo')
      await reconocer(foto)
    } catch {
      setMensajeError('No se pudo capturar la foto. Probá de nuevo.')
    }
  }

  async function reconocer(foto: Blob) {
    try {
      const resultado = await reconocerFoto(foto, medidorId)
      setValorTexto(String(resultado.lectura_reconocida))
      setOrigen('reconocimiento')
      setMensajeError(null)
    } catch (error) {
      setValorTexto('')
      setOrigen('manual')
      setMensajeError(
        error instanceof ErrorApi
          ? 'No se pudo leer la lectura automáticamente. Escribila a mano.'
          : 'Ocurrió un error inesperado al reconocer la foto. Podés escribir la lectura a mano.',
      )
    } finally {
      setEstado('revisando')
    }
  }

  function manejarCambioValor(nuevoValor: string) {
    setValorTexto(nuevoValor)
    setOrigen('manual')
  }

  async function manejarConfirmar() {
    const valorNumerico = Number(valorTexto)
    if (!medidorId || valorTexto.trim() === '' || Number.isNaN(valorNumerico)) {
      setMensajeError('Ingresá una lectura numérica válida antes de confirmar.')
      return
    }
    setEstado('guardando')
    setMensajeError(null)
    try {
      const lectura = await guardarLectura({
        medidor_id: medidorId,
        valor: valorNumerico,
        fecha,
        origen,
      })
      setLecturaGuardada(lectura)
      setEstado('guardado')
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi ? error.message : 'No se pudo guardar la lectura.',
      )
      setEstado('revisando')
    }
  }

  function manejarRegistrarOtra() {
    setEstado('inicio')
    setValorTexto('')
    setFecha(fechaHoyISO())
    setMensajeError(null)
    setLecturaGuardada(null)
  }

  return (
    <div>
      {estado === 'inicio' && (
        <section>
          <label htmlFor="medidor-id">Medidor</label>
          <input
            id="medidor-id"
            value={medidorId}
            onChange={(evento) => setMedidorId(evento.target.value)}
            placeholder="ID del medidor"
          />
          <button type="button" onClick={manejarAbrirCamara} disabled={!medidorId}>
            Abrir cámara
          </button>
        </section>
      )}

      {estado === 'camara' && (
        <section>
          <div className="visor-camara">
            <video ref={videoRef} autoPlay playsInline muted />
            <div aria-hidden="true" className="guia-encuadre" />
          </div>
          <p>Encuadrá la carátula del hidrómetro dentro de la guía.</p>
          <button type="button" onClick={manejarTomarFoto}>
            Tomar foto
          </button>
        </section>
      )}

      {estado === 'reconociendo' && <p>Reconociendo la lectura…</p>}

      {(estado === 'revisando' || estado === 'guardando') && (
        <section>
          <label htmlFor="valor-lectura">Lectura (m³)</label>
          <input
            id="valor-lectura"
            value={valorTexto}
            onChange={(evento) => manejarCambioValor(evento.target.value)}
            inputMode="decimal"
          />
          <p>
            {origen === 'reconocimiento'
              ? 'Lectura reconocida automáticamente — revisala antes de confirmar.'
              : 'Ingresada manualmente.'}
          </p>
          <label htmlFor="fecha-lectura">Fecha de la lectura</label>
          <input
            id="fecha-lectura"
            type="date"
            value={fecha}
            max={fechaHoyISO()}
            onChange={(evento) => setFecha(evento.target.value)}
          />
          <button type="button" onClick={manejarConfirmar} disabled={estado === 'guardando'}>
            {estado === 'guardando' ? 'Guardando…' : 'Confirmar lectura'}
          </button>
        </section>
      )}

      {estado === 'guardado' && lecturaGuardada && (
        <section>
          <p>Lectura guardada: {lecturaGuardada.valor} m³</p>
          {lecturaGuardada.consumo_desde_anterior_m3 != null && (
            <p>
              Consumo desde la lectura anterior: {lecturaGuardada.consumo_desde_anterior_m3} m³ en{' '}
              {lecturaGuardada.dias_desde_anterior} días.
            </p>
          )}
          <button type="button" onClick={manejarRegistrarOtra}>
            Registrar otra lectura
          </button>
        </section>
      )}

      {mensajeError && <p role="alert">{mensajeError}</p>}
    </div>
  )
}

export default PantallaCaptura
