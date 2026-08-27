import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    // El servidor de desarrollo de Vite, que es el que tiene el proxy a la API (T-21).
    // Apuntar directo al 8000 no serviría: probaríamos la API sin el cliente.
    baseUrl: 'http://localhost:5173',

    // El hilo arranca en la cámara y no hay forma de registrar una lectura sin pasar por ella,
    // así que la prueba necesita una. Los navegadores basados en Chromium pueden simular una:
    // `use-fake-device-for-media-stream` entrega un video sintético, y
    // `use-fake-ui-for-media-stream` acepta el permiso de cámara sin mostrar el diálogo, que en
    // modo automatizado nadie podría aceptar.
    //
    // ⚠️ **Hay que correrla en un navegador Chromium** — Electron (el que trae Cypress y el que
    // se usa por defecto), Chrome o Edge. En Firefox estos flags no existen: no habría cámara,
    // no se podría tomar la foto, y la prueba fallaría por el navegador y no por el código.
    setupNodeEvents(on) {
      on('before:browser:launch', (navegador, opciones) => {
        if (navegador.family === 'chromium') {
          opciones.args.push('--use-fake-device-for-media-stream')
          opciones.args.push('--use-fake-ui-for-media-stream')
        }
        return opciones
      })
    },

    supportFile: false,
    video: false,
    // El hilo completo toca cámara, visión por computadora y base de datos: más lento que una
    // prueba de interfaz normal.
    defaultCommandTimeout: 15000,
  },
})
