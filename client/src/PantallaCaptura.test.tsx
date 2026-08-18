import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('./camara', () => ({
  abrirCamara: vi.fn(),
  detenerCamara: vi.fn(),
  capturarFotograma: vi.fn(),
}))

vi.mock('./api/lecturas', async () => {
  const real = await vi.importActual<typeof import('./api/lecturas')>('./api/lecturas')
  return {
    ...real,
    reconocerFoto: vi.fn(),
    guardarLectura: vi.fn(),
  }
})

import { abrirCamara, capturarFotograma } from './camara'
import { ErrorApiLecturas, guardarLectura, reconocerFoto } from './api/lecturas'
import PantallaCaptura from './PantallaCaptura'

const streamFalso = { getTracks: () => [{ stop: vi.fn() }] } as unknown as MediaStream

const LECTURA_GUARDADA_BASE = {
  id: 'lectura-1',
  medidor_id: 'medidor-1',
  fecha: '2026-08-19',
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(abrirCamara).mockResolvedValue(streamFalso)
  vi.mocked(capturarFotograma).mockResolvedValue(new Blob(['foto'], { type: 'image/jpeg' }))
  HTMLMediaElement.prototype.play = vi.fn().mockResolvedValue(undefined)
})

async function avanzarHastaCamara(usuario: ReturnType<typeof userEvent.setup>) {
  render(<PantallaCaptura />)
  await usuario.type(screen.getByLabelText('Medidor'), 'medidor-1')
  await usuario.click(screen.getByRole('button', { name: 'Abrir cámara' }))
  await screen.findByRole('button', { name: 'Tomar foto' })
}

describe('PantallaCaptura', () => {
  it('reconoce la lectura y permite confirmarla tal cual', async () => {
    const usuario = userEvent.setup()
    vi.mocked(reconocerFoto).mockResolvedValue({ lectura_reconocida: 1284, confianza: null })
    vi.mocked(guardarLectura).mockResolvedValue({
      ...LECTURA_GUARDADA_BASE,
      valor: 1284,
      origen: 'reconocimiento',
      consumo_desde_anterior_m3: 12,
      dias_desde_anterior: 30,
    })

    await avanzarHastaCamara(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Tomar foto' }))

    const campoValor = await screen.findByLabelText('Lectura (m³)')
    expect(campoValor).toHaveValue('1284')

    await usuario.click(screen.getByRole('button', { name: 'Confirmar lectura' }))

    await screen.findByText(/Lectura guardada: 1284/)
    expect(screen.getByText(/Consumo desde la lectura anterior: 12 m³ en 30 días/)).toBeInTheDocument()
    expect(guardarLectura).toHaveBeenCalledWith(
      expect.objectContaining({ origen: 'reconocimiento', valor: 1284, medidor_id: 'medidor-1' }),
    )
  })

  it('deja corregir la lectura a mano cuando el reconocimiento falla', async () => {
    const usuario = userEvent.setup()
    vi.mocked(reconocerFoto).mockRejectedValue(
      new ErrorApiLecturas('IMAGEN_ILEGIBLE', 'No se pudo leer'),
    )
    vi.mocked(guardarLectura).mockResolvedValue({
      ...LECTURA_GUARDADA_BASE,
      valor: 500,
      origen: 'manual',
      consumo_desde_anterior_m3: null,
      dias_desde_anterior: null,
    })

    await avanzarHastaCamara(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Tomar foto' }))

    const campoValor = await screen.findByLabelText('Lectura (m³)')
    expect(campoValor).toHaveValue('')
    await screen.findByText(/No se pudo leer la lectura automáticamente/)

    await usuario.type(campoValor, '500')
    await usuario.click(screen.getByRole('button', { name: 'Confirmar lectura' }))

    await screen.findByText(/Lectura guardada: 500/)
    expect(guardarLectura).toHaveBeenCalledWith(
      expect.objectContaining({ origen: 'manual', valor: 500 }),
    )
  })

  it('marca origen manual si el usuario edita una lectura reconocida', async () => {
    const usuario = userEvent.setup()
    vi.mocked(reconocerFoto).mockResolvedValue({ lectura_reconocida: 1000, confianza: null })
    vi.mocked(guardarLectura).mockResolvedValue({
      ...LECTURA_GUARDADA_BASE,
      valor: 1050,
      origen: 'manual',
      consumo_desde_anterior_m3: null,
      dias_desde_anterior: null,
    })

    await avanzarHastaCamara(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Tomar foto' }))

    const campoValor = await screen.findByLabelText('Lectura (m³)')
    await usuario.clear(campoValor)
    await usuario.type(campoValor, '1050')
    await usuario.click(screen.getByRole('button', { name: 'Confirmar lectura' }))

    await screen.findByText(/Lectura guardada: 1050/)
    expect(guardarLectura).toHaveBeenCalledWith(
      expect.objectContaining({ origen: 'manual', valor: 1050 }),
    )
  })

  it('muestra el error del servidor si falla el guardado, sin perder la lectura escrita', async () => {
    const usuario = userEvent.setup()
    vi.mocked(reconocerFoto).mockResolvedValue({ lectura_reconocida: 1284, confianza: null })
    vi.mocked(guardarLectura).mockRejectedValue(
      new ErrorApiLecturas('LECTURA_INVALIDA', 'El valor es menor que la última lectura'),
    )

    await avanzarHastaCamara(usuario)
    await usuario.click(screen.getByRole('button', { name: 'Tomar foto' }))
    const campoValor = await screen.findByLabelText('Lectura (m³)')

    await usuario.click(screen.getByRole('button', { name: 'Confirmar lectura' }))

    await screen.findByText('El valor es menor que la última lectura')
    expect(campoValor).toHaveValue('1284')
  })

  it('no deja abrir la cámara sin un medidor ingresado', async () => {
    render(<PantallaCaptura />)

    expect(screen.getByRole('button', { name: 'Abrir cámara' })).toBeDisabled()
  })
})
