import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('muestra el nombre del proyecto', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: 'MiMedidor' })).toBeInTheDocument()
  })

  it('muestra en el pie qué versión del build se está viendo', () => {
    // Con un trabajador de servicio de por medio, la versión que hay en pantalla no tiene por qué
    // ser la última publicada (T-50). El pie es lo que lo dice.
    //
    // Vitest no corre `vite build`, así que `VITE_VERSION_BUILD` no está definida y se espera el
    // valor de reemplazo. Lo que esta prueba fija es que el elemento exista y tenga el
    // identificador que la prueba end-to-end busca.
    render(<App />)

    const version = document.querySelector('#version-build')
    expect(version, 'el pie tiene que traer #version-build').not.toBeNull()
    expect(version).toHaveTextContent('desarrollo')
  })
})
