/**
 * Pruebas del camino con **trabajador de servicio activo** (T-50).
 *
 * Cierran el riesgo §13.4 de `CLAUDE.md`: hasta ahora Cypress corría solo contra `npm run dev`, y
 * T-31 dejó el trabajador de servicio desactivado en desarrollo a propósito. En producción sí está
 * activo, así que **el único camino que el abonado usa era el único que no se probaba nunca**.
 *
 * Estas pruebas corren contra `vite preview`, que sirve el build. Ver `cypress.preview.config.ts`.
 *
 * Requisitos para correrlas (ver docs/pruebas-end-to-end.md):
 *   1. `npm run build` hecho
 *   2. `npm run preview` en el puerto 4173
 *   3. La API en el puerto 8000 (el proxy vive en la sección `preview` de vite.config.ts)
 */

/** El valor con el que se reconstruye a mitad de la prueba, para ver si la caché lo deja pasar. */
const VERSION_NUEVA = 'prueba-t50-version-nueva'

/**
 * Deja el navegador sin nada guardado de una corrida anterior.
 *
 * Sin esto la prueba mentiría en las dos direcciones: un trabajador de servicio viejo podría
 * servir un build que ya no existe, y una caché ya poblada haría pasar por bueno un registro que
 * en realidad no ocurrió. En CI cada corrida arranca con una máquina nueva, pero en la máquina de
 * un integrante no.
 */
function limpiarTrabajadoresYCaches(): void {
  cy.window({ log: false }).then(async (win) => {
    const registros = await win.navigator.serviceWorker.getRegistrations()
    await Promise.all(registros.map((registro) => registro.unregister()))

    const nombres = await win.caches.keys()
    await Promise.all(nombres.map((nombre) => win.caches.delete(nombre)))
  })
}

/** Espera a que haya un trabajador de servicio activo y que sea él quien sirva la página. */
function esperarQueControleLaPagina(): void {
  cy.window({ log: false }).then((win) => win.navigator.serviceWorker.ready)

  // `ready` solo garantiza que hay uno **activo**. Que además **controle** esta pestaña es otra
  // cosa: en la primera visita la página se cargó antes de que existiera. Una recarga lo asegura
  // sin depender de que `clientsClaim` esté configurado.
  cy.reload()
  cy.window({ log: false }).its('navigator.serviceWorker.controller').should('not.be.null')
}

describe('La aplicación con el trabajador de servicio activo', () => {
  it('queda controlada por el trabajador de servicio y no guarda /api en caché', () => {
    cy.visit('/')
    limpiarTrabajadoresYCaches()

    // Después de limpiar, esta visita es la instalación real que se quiere probar.
    cy.visit('/')
    esperarQueControleLaPagina()

    // La aplicación sigue siendo usable: no es un cascarón servido desde caché.
    cy.contains('h1', 'MiMedidor').should('be.visible')

    // Y una petición a la API hecha **desde el navegador** —o sea, pasando por el trabajador de
    // servicio— llega hasta el servidor y trae datos. Se hace desde la interfaz y no con
    // `cy.request()` a propósito: `cy.request()` sale de Node y nunca toca el trabajador de
    // servicio, así que no probaría nada de lo que esta prueba existe para probar.
    cy.get('#medidor-historial').type('33333333-3333-3333-3333-333333333333')
    cy.contains('button', 'Ver historial').click()
    cy.get('table tbody tr').should('have.length.of.at.least', 1)

    // Lo que el trabajador de servicio **no** debe guardar: nada de `/api`. Una lectura o un
    // historial servidos desde caché serían datos viejos presentados como actuales, que es
    // exactamente lo que este producto no puede hacer (CLAUDE.md §13.5).
    //
    // Hoy no hay `runtimeCaching` configurado, así que esto pasa solo. La prueba existe para que
    // deje de pasar el día que alguien agregue uno "para que cargue más rápido".
    cy.window({ log: false })
      .then(async (win) => {
        const nombres = await win.caches.keys()
        const guardadas: string[] = []
        for (const nombre of nombres) {
          const cache = await win.caches.open(nombre)
          for (const peticion of await cache.keys()) {
            guardadas.push(new URL(peticion.url).pathname)
          }
        }
        return guardadas
      })
      .then((rutas) => {
        expect(rutas, 'el trabajador de servicio precargó algo').to.have.length.of.at.least(1)
        // `.to.have.length(0)` y no `.to.be.empty`: la segunda es una propiedad de Chai, no una
        // llamada, y ESLint la marca como expresión sin efecto.
        expect(
          rutas.filter((ruta) => ruta.startsWith('/api')),
          'rutas de /api guardadas en caché',
        ).to.have.length(0)
      })
  })

  it('no sigue sirviendo una versión vieja cuando se publica una nueva', () => {
    // Ésta es la prueba que le da sentido al job: un trabajador de servicio que se queda pegado en
    // el build anterior es un fallo silencioso —la aplicación abre, funciona y muestra otra cosa—
    // y el peor día para descubrirlo es el de la feria.

    cy.visit('/')
    limpiarTrabajadoresYCaches()

    cy.visit('/')
    esperarQueControleLaPagina()

    cy.get('#version-build')
      .invoke('text')
      .then((versionVieja) => {
        expect(
          versionVieja,
          'la prueba tiene que reconstruir con un valor distinto al actual',
        ).to.not.equal(VERSION_NUEVA)

        // Se publica una versión nueva mientras el navegador tiene la anterior en caché. `vite
        // preview` lee el disco en cada petición, así que reconstruir alcanza: no hace falta
        // reiniciarlo.
        cy.exec('npm run build', {
          env: { VITE_VERSION_BUILD: VERSION_NUEVA },
          timeout: 300_000,
        })

        // Con `registerType: 'autoUpdate'` el reemplazo tarda dos recargas: en la primera el
        // navegador descubre el trabajador de servicio nuevo y lo instala, y recién en la
        // siguiente es él quien responde. Se reintenta con margen en vez de fijar una espera.
        recargarHasta(VERSION_NUEVA, 6)
      })
  })
})

/** Recarga hasta que el pie muestre la versión esperada, o falla diciendo cuál quedó pegada. */
function recargarHasta(versionEsperada: string, intentosRestantes: number): void {
  cy.reload()

  cy.get('#version-build').then(($version) => {
    const actual = $version.text()
    if (actual === versionEsperada) return

    if (intentosRestantes <= 0) {
      throw new Error(
        `El trabajador de servicio siguió sirviendo la versión «${actual}» después de varias ` +
          `recargas; se publicó «${versionEsperada}». La aplicación se quedó pegada en un build ` +
          `viejo, que es justo lo que esta prueba existe para detectar.`,
      )
    }

    cy.wait(1000)
    recargarHasta(versionEsperada, intentosRestantes - 1)
  })
}
