/**
 * Cámara sintética para los navegadores Chromium.
 *
 * El hilo arranca en la cámara y no hay forma de registrar una lectura sin pasar por ella, así que
 * la prueba necesita una. `use-fake-device-for-media-stream` entrega un video sintético y
 * `use-fake-ui-for-media-stream` acepta el permiso sin mostrar el diálogo, que en modo automatizado
 * nadie podría aceptar.
 *
 * ⚠️ **Tiene que ser un navegador Chromium** — Electron, Chrome o Edge. En Firefox estos flags no
 * existen: no habría cámara, no se podría tomar la foto, y la prueba fallaría por el navegador y no
 * por el código.
 *
 * Vive aparte porque lo comparten las dos configuraciones de Cypress: la que corre contra el
 * servidor de desarrollo (`cypress.config.ts`) y la que corre contra el build con el trabajador de
 * servicio activo (`cypress.preview.config.ts`, T-50).
 */
export function usarCamaraFalsa(on: Cypress.PluginEvents): void {
  on('before:browser:launch', (navegador, opciones) => {
    if (navegador.family === 'chromium') {
      opciones.args.push('--use-fake-device-for-media-stream')
      opciones.args.push('--use-fake-ui-for-media-stream')
    }
    return opciones
  })
}
