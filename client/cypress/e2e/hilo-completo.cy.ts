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

/** La lectura sembrada por `datos_de_prueba.sql`, de hace 5 días. */
const LECTURA_SEMBRADA = 51069
const LECTURA_NUEVA = 51085
const CONSUMO_ESPERADO = LECTURA_NUEVA - LECTURA_SEMBRADA // 16 m³

function fechaISO(diasAtras: number): string {
  const fecha = new Date()
  fecha.setDate(fecha.getDate() - diasAtras)
  return fecha.toISOString().slice(0, 10)
}

describe('Hilo completo: foto → lectura → historial → factura → comparación', () => {
  it('registra una lectura, la ve en el historial y la contrasta contra una factura', () => {
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
    cy.get('#valor-lectura').type(String(LECTURA_NUEVA))
    cy.contains('button', 'Confirmar lectura').click()

    cy.contains(`Lectura guardada: ${LECTURA_NUEVA} m³`).should('be.visible')

    // --- 2. Verla en el historial, con el consumo calculado ----------------------------------
    //
    // Que aparezca el consumo prueba que la lectura llegó de verdad a la base: el número sale de
    // compararla contra la lectura sembrada hace 5 días, no de nada que viva en el navegador.

    cy.get('#medidor-historial').type(MEDIDOR)
    cy.contains('button', 'Ver historial').click()

    cy.get('table').within(() => {
      cy.contains('td', String(LECTURA_SEMBRADA)).should('exist')
      cy.contains('td', String(LECTURA_NUEVA)).should('exist')
      cy.contains(`${CONSUMO_ESPERADO} m³ en 5 días`).should('exist')
    })

    // --- 3. Registrar una factura y contrastarla --------------------------------------------
    //
    // El período cubre las dos lecturas. Se factura un consumo mayor al medido a propósito, para
    // que la diferencia supere el umbral del 15 % y se vea la alerta — que es el caso que le
    // importa al abonado y la razón de ser del producto.

    const CONSUMO_FACTURADO = 20
    const DIFERENCIA_PORCENTUAL = ((CONSUMO_FACTURADO - CONSUMO_ESPERADO) / CONSUMO_FACTURADO) * 100

    cy.get('#factura-medidor').type(MEDIDOR)
    cy.get('#factura-inicio').type(fechaISO(5))
    cy.get('#factura-fin').type(fechaISO(0))
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
