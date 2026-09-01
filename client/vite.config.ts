/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      // `autoUpdate`: el trabajador de servicio nuevo reemplaza al viejo sin preguntarle nada
      // al abonado. Preguntar exigiría una interfaz de "hay una versión nueva" que no está en
      // el alcance de T-31, y dejar una versión vieja pegada sería peor.
      registerType: 'autoUpdate',

      // Los iconos son PNG y no SVG a propósito: los navegadores no aceptan SVG para el icono
      // de instalación, y un manifest con el formato equivocado pasa el build sin quejarse
      // pero nunca ofrece instalar.
      includeAssets: ['icono.svg', 'icono-192.png'],

      manifest: {
        name: 'MiMedidor — lectura de hidrómetro',
        short_name: 'MiMedidor',
        description:
          'Fotografíe su hidrómetro, lleve su propio historial de consumo y contrástelo ' +
          'contra la factura de su operador.',
        lang: 'es-CR',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        background_color: '#FFFFFF',
        theme_color: '#1B4E80',
        icons: [
          { src: 'icono-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icono-512.png', sizes: '512x512', type: 'image/png' },
          // `maskable` deja que Android recorte el icono a su forma sin comerse el contenido:
          // el dibujo vive dentro del 80 % central por eso mismo.
          { src: 'icono-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },

      workbox: {
        // El trabajador de servicio se queda con los archivos del build. `/api` NO se cachea:
        // una lectura o un historial servidos desde caché serían datos viejos presentados como
        // actuales, que es justo lo que este producto no puede hacer.
        globPatterns: ['**/*.{js,css,html,svg,png,ico,webmanifest}'],
        navigateFallbackDenylist: [/^\/api/],
      },

      // En desarrollo no se registra: un trabajador de servicio cacheando durante `vite dev`
      // esconde los cambios que uno acaba de hacer.
      devOptions: { enabled: false },
    }),
  ],

  server: {
    // El cliente llama rutas relativas (`/api/…`, ver client/src/api/*.ts) porque en producción
    // el build de Vite y la API se sirven desde el mismo origen. En desarrollo no es así: Vite
    // escucha en el 5173 y Uvicorn en el 8000, así que sin este proxy `fetch('/api/lecturas')`
    // le pega al servidor de Vite y devuelve el index.html en vez de la respuesta de la API.
    //
    // Esto es lo que faltaba para que cliente y servidor se ejecutaran juntos (riesgo #1 del
    // documento de la semana 7, tarjeta T-21).
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    pool: 'threads',
    globals: true,
  },
})
