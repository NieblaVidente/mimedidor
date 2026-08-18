import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('./api/facturas', async () => {
  const real = await vi.importActual<typeof import('./api/facturas')>('./api/facturas')
  return { ...real, guardarFactura: vi.fn(), obtenerComparacion: vi.fn() }
})

import { ErrorApiFacturas, guardarFactura, obtenerComparacion } from './api/facturas'
import PantallaFactura from './PantallaFactura'

beforeEach(() => {
  vi.clearAllMocks()
})

async function completarFormulario(usuario: ReturnType<typeof userEvent.setup>) {
  render(<PantallaFactura />)
  await usuario.type(screen.getByLabelText('Medidor'), 'medidor-1')
  await usuario.type(screen.getByLabelText('Inicio del período'), '2026-07-01')
  await usuario.type(screen.getByLabelText('Fin del período'), '2026-08-01')
  await usuario.type(screen.getByLabelText('Consumo facturado (m³)'), '14')
  await usuario.type(screen.getByLabelText('Monto (₡)'), '8250')
  await usuario.click(screen.getByRole('button', { name: 'Registrar y comparar' }))
}

describe('PantallaFactura', () => {
  it('registra la factura y muestra la comparación cuando hay lecturas suficientes', async () => {
    const usuario = userEvent.setup()
    vi.mocked(guardarFactura).mockResolvedValue({
      id: 'factura-1',
      medidor_id: 'medidor-1',
      periodo_inicio: '2026-07-01',
      periodo_fin: '2026-08-01',
      consumo_facturado_m3: 14,
      monto: 8250,
    })
    vi.mocked(obtenerComparacion).mockResolvedValue({
      factura_id: 'factura-1',
      consumo_medido_m3: 12,
      consumo_facturado_m3: 14,
      diferencia_m3: 2,
      diferencia_porcentual: 14.3,
      supera_umbral: false,
    })

    await completarFormulario(usuario)

    await screen.findByText('Comparación de tu factura')
    expect(screen.getByText('Consumo facturado: 14 m³')).toBeInTheDocument()
    expect(screen.getByText(/Consumo medido por tus lecturas:/)).toHaveTextContent('12 m³')
    expect(
      screen.getByText(/El operador facturó 2 m³ más de lo que midieron tus propias lecturas/),
    ).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('avisa cuando la diferencia supera el umbral', async () => {
    const usuario = userEvent.setup()
    vi.mocked(guardarFactura).mockResolvedValue({
      id: 'factura-2',
      medidor_id: 'medidor-1',
      periodo_inicio: '2026-07-01',
      periodo_fin: '2026-08-01',
      consumo_facturado_m3: 10,
      monto: 5000,
    })
    vi.mocked(obtenerComparacion).mockResolvedValue({
      factura_id: 'factura-2',
      consumo_medido_m3: 5,
      consumo_facturado_m3: 10,
      diferencia_m3: 5,
      diferencia_porcentual: 50,
      supera_umbral: true,
    })

    await completarFormulario(usuario)

    await screen.findByText('La diferencia supera el umbral esperado — vale la pena revisarla.')
  })

  it('muestra un aviso claro cuando no hay lecturas suficientes para comparar', async () => {
    const usuario = userEvent.setup()
    vi.mocked(guardarFactura).mockResolvedValue({
      id: 'factura-3',
      medidor_id: 'medidor-1',
      periodo_inicio: '2026-07-01',
      periodo_fin: '2026-08-01',
      consumo_facturado_m3: 14,
      monto: 8250,
    })
    vi.mocked(obtenerComparacion).mockResolvedValue({
      factura_id: 'factura-3',
      consumo_medido_m3: null,
      consumo_facturado_m3: 14,
      diferencia_m3: null,
      diferencia_porcentual: null,
      supera_umbral: false,
    })

    await completarFormulario(usuario)

    await screen.findByText(
      'No hay suficientes lecturas propias en este período para comparar todavía.',
    )
  })

  it('muestra el error del servidor si falla el registro', async () => {
    const usuario = userEvent.setup()
    vi.mocked(guardarFactura).mockRejectedValue(
      new ErrorApiFacturas('MEDIDOR_NO_ENCONTRADO', 'No existe ese medidor'),
    )

    await completarFormulario(usuario)

    await screen.findByText('No existe ese medidor')
  })

  it('no envía el formulario si falta algún campo', async () => {
    const usuario = userEvent.setup()
    render(<PantallaFactura />)

    await usuario.click(screen.getByRole('button', { name: 'Registrar y comparar' }))

    await screen.findByText(
      'Completá todos los campos con valores válidos antes de registrar la factura.',
    )
    expect(guardarFactura).not.toHaveBeenCalled()
  })
})
