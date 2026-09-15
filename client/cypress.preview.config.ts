import { defineConfig } from 'cypress'
import { usarCamaraFalsa } from './cypress/camara-falsa'

/**
 * Prueba end-to-end contra el **build servido por `vite preview`** (T-50).
 *
 * Diferencia con `cypress.config.ts`: acá el trabajador de servicio **está activo**, porque se
 * sirve el resultado de `npm run build` y no el código fuente. Ese es el único camino que el
 * abonado usa en producción y el único que hasta T-50 no se ejercitaba nunca (`CLAUDE.md` §13.4).
 *
 * El porqué de dos configuraciones y dos jobs, en vez de uno solo, está en
 * `docs/pruebas-end-to-end.md`.
 */
export default defineConfig({
  e2e: {
    // El puerto por defecto de `vite preview`. El proxy a `/api` para este servidor está en la
    // sección `preview` de vite.config.ts — `server.proxy` no aplica acá.
    baseUrl: 'http://localhost:4173',

    // Las dos carpetas: el hilo funcional completo tal cual (no se duplica, se reejecuta bajo el
    // trabajador de servicio) y lo que solo tiene sentido con él activo.
    //
    // Cada carpeta se corre en su propio `cypress run` desde el job de CI, para que el orden sea
    // explícito y un fallo diga cuál de las dos cosas se rompió.
    specPattern: ['cypress/e2e/**/*.cy.ts', 'cypress/e2e-pwa/**/*.cy.ts'],

    setupNodeEvents(on) {
      usarCamaraFalsa(on)
    },

    supportFile: false,
    video: false,
    defaultCommandTimeout: 15000,
  },
})
