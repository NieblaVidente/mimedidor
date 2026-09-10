import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('./api/lecturas', async () => {
  const real = await vi.importActual<typeof import('./api/lecturas')>('./api/lecturas')
  return { ...real, obtenerHistorial: vi.fn() }
})

import { obtenerHistorial } from './api/lecturas'
import { ErrorApi } from './api/errores'
import PantallaHistorial from './PantallaHistorial'

beforeEach(() => {
  vi.clearAllMocks()
})

async function cargarHistorial(usuario: ReturnType<typeof userEvent.setup>) {
  render(<PantallaHistorial />)
  await usuario.type(screen.getByLabelText('Medidor'), 'medidor-1')
  await usuario.click(screen.getByRole('button', { name: 'Ver historial' }))
}

describe('PantallaHistorial', () => {
  it('no deja cargar sin un medidor ingresado', () => {
    render(<PantallaHistorial />)

    expect(screen.getByRole('button', { name: 'Ver historial' })).toBeDisabled()
  })

  it('muestra un aviso cuando el medidor no tiene lecturas', async () => {
    const usuario = userEvent.setup()
    vi.mocked(obtenerHistorial).mockResolvedValue({ lecturas: [] })

    await cargarHistorial(usuario)

    await screen.findByText('Este medidor todavía no tiene lecturas registradas.')
  })

  it('lista las lecturas con el consumo calculado, y marca la primera lectura sin consumo', async () => {
    const usuario = userEvent.setup()
    vi.mocked(obtenerHistorial).mockResolvedValue({
      lecturas: [
        {
          id: 'l1',
          valor: 100,
          fecha: '2026-06-01',
          origen: 'manual',
          consumo_desde_anterior_m3: null,
          dias_desde_anterior: null,
        },
        {
          id: 'l2',
          valor: 112,
          fecha: '2026-07-01',
          origen: 'reconocimiento',
          consumo_desde_anterior_m3: 12,
          dias_desde_anterior: 30,
        },
      ],
    })

    await cargarHistorial(usuario)

    await screen.findByText('2026-06-01')
    expect(
      screen.getByText('Primera lectura registrada de este medidor — todavía no hay consumo que calcular.'),
    ).toBeInTheDocument()

    expect(screen.getByText('2026-07-01')).toBeInTheDocument()
    expect(screen.getByText('12 m³ en 30 días')).toBeInTheDocument()
    expect(screen.getByText('Reconocimiento automático')).toBeInTheDocument()
  })

  it('muestra el error del servidor si falla la carga', async () => {
    const usuario = userEvent.setup()
    vi.mocked(obtenerHistorial).mockRejectedValue(
      new ErrorApi('MEDIDOR_NO_ENCONTRADO', 'No existe ese medidor'),
    )

    await cargarHistorial(usuario)

    await screen.findByText('No existe ese medidor')
  })
})
