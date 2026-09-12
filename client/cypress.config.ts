import { defineConfig } from 'cypress'
import { usarCamaraFalsa } from './cypress/camara-falsa'

/**
 * Prueba end-to-end contra el **servidor de desarrollo** (T-22).
 *
 * Es la que corre en cada PR sobre el código fuente. La otra configuración,
 * `cypress.preview.config.ts`, corre el mismo hilo contra el build con el trabajador de servicio
 * activo (T-50); el porqué de tener dos está en `docs/pruebas-end-to-end.md`.
 */
export default defineConfig({
  e2e: {
    // El servidor de desarrollo de Vite, que es el que tiene el proxy a la API (T-21).
    // Apuntar directo al 8000 no serviría: probaríamos la API sin el cliente.
    baseUrl: 'http://localhost:5173',

    // Solo el hilo funcional. Las pruebas de `cypress/e2e-pwa/` necesitan el trabajador de
    // servicio, que en desarrollo está desactivado a propósito (`devOptions.enabled: false` en
    // vite.config.ts): acá fallarían por el entorno, no por el código.
    specPattern: 'cypress/e2e/**/*.cy.ts',

    setupNodeEvents(on) {
      usarCamaraFalsa(on)
    },

    supportFile: false,
    video: false,
    // El hilo completo toca cámara, visión por computadora y base de datos: más lento que una
    // prueba de interfaz normal.
    defaultCommandTimeout: 15000,
  },
})
