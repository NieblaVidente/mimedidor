/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

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
