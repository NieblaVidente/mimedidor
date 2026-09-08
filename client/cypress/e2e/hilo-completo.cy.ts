/**
 * Prueba end-to-end del hilo funcional completo (T-22).
 *
 * Recorre lo que hace un abonado de verdad, contra el sistema entero corriendo: navegador →
 * cliente → proxy de Vite → FastAPI → PostgreSQL. Nada está sustituido por un objeto falso.
 *
 * Existe por lo que pasó en T-21: había 46 pruebas unitarias en verde mientras
 * `POST /api/lecturas` devolvía error 500 contra cualquier base real. Todas sustituían la
 * conexión a la base, así que ninguna podía ver el problema. Esta prueba es la que sí lo habría
 * visto.
 *
 * Requisitos para correrla (ver docs/como-empezar.md):
 *   1. PostgreSQL con el esquema y `datos_de_prueba.sql` aplicados
 *   2. La API en el puerto 8000
 *   3. El cliente en el puerto 5173
 */

const MEDIDOR = '33333333-3333-3333-3333-333333333333'

// El medidor sembrado tiene 2 dígitos rojos en el odómetro (T-39): lo que el abonado escribe
// son los dígitos tal como los ve, y lo que el sistema guarda y muestra es el volumen en m³.
// Distinguir las dos cosas es justamente lo que esta prueba tiene que ejercitar.

/** Lo que se teclea, tal como se lee en la carátula. */
const MOSTRADA_NUEVA = 52669

/** Lo que el sistema guarda y muestra: los mismos dígitos con el punto en su lugar. */
const VOLUMEN_SEMBRADO = 510.69   // sembrado por `datos_de_prueba.sql`, de hace 5 días
const VOLUMEN_NUEVO = 526.69

/** 16 m³ **de verdad**. Antes de T-39 esta resta daba 16 «unidades del odómetro», que se
 *  comparaban contra una factura en m³ como si fueran lo mismo. */
const CONSUMO_ESPERADO = Number((VOLUMEN_NUEVO - VOLUMEN_SEMBRADO).toFixed(2)) // 16 m³

/** Hoy según el navegador — el mismo reloj con el que `PantallaCaptura` fecha la lectura. */
function hoyISO(): string {
  // Componentes locales, no `toISOString()` (UTC) — mismo bug que se corrigió en
  // PantallaCaptura.tsx (T-35): en huso horario negativo, UTC ya puede estar en el día
  // siguiente aunque acá todavía sea "hoy".
  const hoy = new Date()
  const año = hoy.getFullYear()
  const mes = String(hoy.getMonth() + 1).padStart(2, '0')
  const dia = String(hoy.getDate()).padStart(2, '0')
  return `${año}-${mes}-${dia}`
}

/** Días entre dos fechas `AAAA-MM-DD`, contadas como fechas y no como instantes. */
function diasEntre(desdeISO: string, hastaISO: string): number {
  const [a1, m1, d1] = desdeISO.split('-').map(Number)
  const [a2, m2, d2] = hastaISO.split('-').map(Number)
  return Math.round((Date.UTC(a2, m2 - 1, d2) - Date.UTC(a1, m1 - 1, d1)) / 86_400_000)
}

/**
 * La fecha de la lectura que sembró `datos_de_prueba.sql`, **leída del sistema** en vez de
 * recalculada acá (T-43).
 *
 * Por qué no se calcula: la siembra usa `CURRENT_DATE - 5`, que es la fecha en la zona horaria
 * del **servidor de PostgreSQL**, mientras que la lectura nueva la fecha el **navegador** con su
 * hora local. Cuando esas dos zonas no coinciden —el caso reportado tenía la base en GMT y la
 * máquina en Costa Rica— la diferencia entre ambas lecturas no es de 5 días, y la prueba fallaba
 * de noche con el código intacto.
 *
 * Leerla del historial hace que la prueba verifique la aritmética del sistema sin depender de que
 * los dos relojes coincidan. El consumo en m³ se sigue afirmando exacto: eso no depende de la
 * zona horaria de nadie.
 */
function fechaSembrada(): Cypress.Chainable<string> {
  return cy
    .request(`/api/lecturas?medidor_id=${MEDIDOR}`)
    .then(({ body }) => {
      expect(body.lecturas, 'datos_de_prueba.sql tiene que haber sembrado una lectura').to.have.length
        .of.at.least(1)
      return body.lecturas[0].fecha as string
    })
}

describe('Hilo completo: foto → lectura → historial → factura → comparación', () => {
  it('registra una lectura, la ve en el historial y la contrasta contra una factura', () => {
    // Se lee del sistema antes de empezar, en vez de asumir "hace 5 días" (T-43).
    let sembradaISO = ''
    fechaSembrada().then((fecha) => {
      sembradaISO = fecha
    })

    cy.visit('/')

    // --- 1. Capturar y registrar una lectura -------------------------------------------------
    //
    // No hay forma de registrar una lectura sin pasar por la cámara, así que Chrome corre con
    // una cámara falsa (ver cypress.config.ts). El reconocimiento va a fallar sobre ese video
    // sintético — igual que falla hoy sobre fotos reales, ver docs/exactitud-reconocimiento.md —
    // y la pantalla deja el campo vacío para escribir la lectura a mano.
    //
    // Ese es el camino que de verdad usa el abonado hoy, no un caso de borde.

    cy.get('#medidor-id').type(MEDIDOR)
    cy.contains('button', 'Abrir cámara').click()
    cy.contains('button', 'Tomar foto').click()

    // La pantalla llega a "revisando" pase lo que pase con el reconocimiento.
    cy.get('#valor-lectura').should('be.visible')

    // Se limpia antes de escribir: si el reconocimiento llegara a devolver algo, el campo no
    // estaría vacío. La prueba es del hilo, no del acierto del OCR.
    cy.get('#valor-lectura').clear()
    cy.get('#valor-lectura').type(String(MOSTRADA_NUEVA))
    cy.contains('button', 'Confirmar lectura').click()

    // Se teclearon 52669 y se confirma 526.69 m³: la conversión es lo que se verifica acá.
    cy.contains(`Lectura guardada: ${VOLUMEN_NUEVO} m³`).should('be.visible')

    // --- 2. Verla en el historial, con el consumo calculado ----------------------------------
    //
    // Que aparezca el consumo prueba que la lectura llegó de verdad a la base: el número sale de
    // compararla contra la lectura sembrada, no de nada que viva en el navegador.

    cy.get('#medidor-historial').type(MEDIDOR)
    cy.contains('button', 'Ver historial').click()

    cy.get('table').within(() => {
      cy.contains('td', String(VOLUMEN_SEMBRADO)).should('exist')
      cy.contains('td', String(VOLUMEN_NUEVO)).should('exist')
      // El consumo en m³ se afirma exacto — no depende de ninguna zona horaria. Los días salen
      // de la fecha realmente sembrada, que sí depende del reloj de la base (T-43).
      cy.contains(`${CONSUMO_ESPERADO} m³ en ${diasEntre(sembradaISO, hoyISO())} días`).should(
        'exist',
      )
    })

    // --- 3. Registrar una factura y contrastarla --------------------------------------------
    //
    // El período cubre las dos lecturas. Se factura un consumo mayor al medido a propósito, para
    // que la diferencia supere el umbral del 15 % y se vea la alerta — que es el caso que le
    // importa al abonado y la razón de ser del producto.

    const CONSUMO_FACTURADO = 20
    const DIFERENCIA_PORCENTUAL = ((CONSUMO_FACTURADO - CONSUMO_ESPERADO) / CONSUMO_FACTURADO) * 100

    // El período arranca exactamente en la fecha sembrada, no en "hoy menos 5" (T-43): la
    // comparación necesita una lectura con `fecha <= periodo_inicio`, y si ese extremo cae antes
    // de lo sembrado no hay con qué comparar y la comparación devuelve nulo. Ese fallo parecía
    // un error de la lógica de comparación sin serlo.
    cy.get('#factura-medidor').type(MEDIDOR)
    // Dentro de `cy.then()` a propósito: los argumentos de un comando de Cypress se evalúan
    // cuando el comando se **encola**, no cuando se ejecuta. Fuera del `then`, `sembradaISO`
    // todavía vale "" y `cy.type()` falla con "cannot accept an empty string".
    cy.then(() => {
      cy.get('#factura-inicio').type(sembradaISO)
      cy.get('#factura-fin').type(hoyISO())
    })
    cy.get('#factura-consumo').type(String(CONSUMO_FACTURADO))
    cy.get('#factura-monto').type('9500')
    cy.contains('button', 'Registrar y comparar').click()

    cy.contains('Comparación de tu factura').should('be.visible')
    cy.contains(`Consumo facturado: ${CONSUMO_FACTURADO} m³`).should('be.visible')
    cy.contains('Consumo medido por tus lecturas:').should('contain', `${CONSUMO_ESPERADO} m³`)
    cy.contains(`${DIFERENCIA_PORCENTUAL}% de diferencia`).should('be.visible')

    // 20 % de diferencia supera el umbral fijo de 15 % del sprint.
    //
    // Se busca el aviso por su texto y no con `cy.get('[role="alert"]')` a secas porque las tres
    // pantallas están montadas a la vez y puede haber más de un aviso en la página.
    cy.contains('[role="alert"]', 'supera el umbral').should('be.visible')
  })

  it('rechaza una lectura menor que la anterior sin dejar nada a medias', () => {
    // El procedimiento de T-14 hace dos escrituras en una sola transacción. Esta prueba confirma
    // que la regla de negocio ("un hidrómetro no retrocede") llega hasta el usuario como un
    // mensaje entendible, y no como un error 500 ni como una traza de la base de datos.

    cy.visit('/')

    cy.get('#medidor-id').type(MEDIDOR)
    cy.contains('button', 'Abrir cámara').click()
    cy.contains('button', 'Tomar foto').click()

    cy.get('#valor-lectura').should('be.visible')
    cy.get('#valor-lectura').clear()
    cy.get('#valor-lectura').type('1')
    cy.contains('button', 'Confirmar lectura').click()

    cy.contains('[role="alert"]', 'menor que la última lectura registrada')
      .should('be.visible')
      // Y nada de las tripas de la base de datos se filtra al usuario (CLAUDE.md §11). Antes de
      // T-21 este mismo mensaje traía el nombre del procedimiento PL/pgSQL, su firma completa y
      // el número de línea donde se lanzó.
      .should('not.contain', 'CONTEXT')
      .and('not.contain', 'PL/pgSQL')
  })
})
