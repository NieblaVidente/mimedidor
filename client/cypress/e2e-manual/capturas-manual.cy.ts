/**
 * TEMPORAL — genera las capturas del manual de usuario (T-23). No es una prueba: no afirma
 * nada. Vive fuera de cypress/e2e/ para que el job de CI no la levante.
 *
 * Uso, con la API en 8000, el cliente en 5173 y la base sembrada:
 *   npx cypress run --browser edge --config specPattern=cypress/e2e-manual/*.cy.ts
 *
 * Deja los PNG en cypress/screenshots/ (ya ignorada por git). De ahi se copian a
 * docs/manual-usuario/ los que el manual usa, renombrados.
 *
 * Hay que correrla en un navegador Chromium, igual que la prueba end-to-end.
 */

const MEDIDOR = '33333333-3333-3333-3333-333333333333'
const MOSTRADA = 52669

function fechaISO(diasAtras: number): string {
  const f = new Date()
  f.setDate(f.getDate() - diasAtras)
  return `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, '0')}-${String(f.getDate()).padStart(2, '0')}`
}

describe('Capturas del manual', () => {
  beforeEach(() => cy.viewport(390, 844))

  it('genera las capturas', () => {
    // Cámara dibujada. Dos motivos: la cámara falsa de Chromium entrega cuadros negros, que en
    // una captura de manual no muestran nada; y una foto real de un hidrómetro es dato personal
    // de un abonado y no puede quedar versionada en el repositorio
    // (ver docs/dataset-campo/registro-medidores.md). El código de la aplicación corre igual:
    // lo único sustituido es de dónde salen los píxeles.
    cy.visit('/', {
      onBeforeLoad(ventana) {
        const lienzo = ventana.document.createElement('canvas')
        lienzo.width = 640
        lienzo.height = 480
        const c = lienzo.getContext('2d')!
        const dibujar = () => {
          c.fillStyle = '#6b6f63'
          c.fillRect(0, 0, 640, 480)
          c.fillStyle = '#3c3f38'
          c.fillRect(0, 0, 640, 60)
          c.fillRect(0, 420, 640, 60)
          c.beginPath()
          c.arc(320, 240, 175, 0, Math.PI * 2)
          c.fillStyle = '#d8d4c8'
          c.fill()
          c.lineWidth = 10
          c.strokeStyle = '#2f322c'
          c.stroke()
          c.fillStyle = '#15161a'
          c.fillRect(180, 195, 280, 70)
          const digitos = '0052669'
          for (let i = 0; i < digitos.length; i++) {
            // Los dos últimos van en rojo: son fracción de m³ en este medidor (T-39).
            c.fillStyle = i >= 5 ? '#8c1d1d' : '#f2f2f0'
            c.fillRect(188 + i * 39, 202, 34, 56)
            c.fillStyle = i >= 5 ? '#ffffff' : '#111111'
            c.font = 'bold 40px monospace'
            c.textAlign = 'center'
            c.fillText(digitos[i], 205 + i * 39, 245)
          }
          c.fillStyle = '#2f322c'
          c.font = 'bold 22px sans-serif'
          c.fillText('m³', 320, 300)
          ventana.requestAnimationFrame(dibujar)
        }
        dibujar()
        const flujo = lienzo.captureStream(30)
        ventana.navigator.mediaDevices.getUserMedia = async () => flujo
      },
    })

    // 1 — pantalla inicial
    cy.get('#medidor-id').should('be.visible')
    cy.screenshot('01-inicio', { overwrite: true })

    // 2 — cámara con la guía de encuadre
    cy.get('#medidor-id').type(MEDIDOR)
    cy.contains('button', 'Abrir cámara').click()
    cy.contains('button', 'Tomar foto').should('be.visible')
    cy.wait(1000)
    cy.screenshot('02-camara', { overwrite: true })

    // 3 — revisión de la lectura, que es donde el abonado corrige
    cy.contains('button', 'Tomar foto').click()
    cy.get('#valor-lectura').should('be.visible')
    cy.screenshot('03-revision-vacia', { overwrite: true })

    cy.get('#valor-lectura').clear()
    cy.get('#valor-lectura').type(String(MOSTRADA))
    cy.screenshot('04-revision-escrita', { overwrite: true })

    // 4 — confirmada
    cy.contains('button', 'Confirmar lectura').click()
    cy.contains('Lectura guardada').should('be.visible')
    cy.screenshot('05-guardada', { overwrite: true })

    // 5 — historial
    cy.get('#medidor-historial').type(MEDIDOR)
    cy.contains('button', 'Ver historial').click()
    cy.get('table').should('be.visible')
    cy.screenshot('06-historial', { overwrite: true })

    // 6 — factura y comparación
    //
    // El inicio del período se toma de la PRIMERA fila del historial, no de "hace 5 días": la
    // comparación necesita una lectura con fecha <= inicio del período, y si el inicio cae un
    // día antes de la primera lectura no hay con qué comparar. Leerla de la tabla hace que
    // esto funcione aunque la base y el navegador no coincidan en qué día es hoy.
    cy.get('table tbody tr').first().find('td').first().invoke('text').then((primeraFecha) => {
      cy.get('#factura-medidor').type(MEDIDOR)
      cy.get('#factura-inicio').type(primeraFecha.trim())
      cy.get('#factura-fin').type(fechaISO(0))
    })
    cy.get('#factura-consumo').type('20')
    cy.get('#factura-monto').type('9500')
    cy.screenshot('07-factura-formulario', { overwrite: true })

    cy.contains('button', 'Registrar y comparar').click()
    cy.contains('Comparación de tu factura').should('be.visible')
    cy.screenshot('08-comparacion', { overwrite: true })
  })
})
