/// <reference types="vite/client" />

// Variables de entorno propias. Vite solo expone al navegador las que empiezan con `VITE_`, y las
// reemplaza por su valor literal en tiempo de build: no se leen en tiempo de ejecución.
interface ImportMetaEnv {
  /**
   * Identificador de la versión construida, que la aplicación muestra en el pie.
   *
   * Lo pone quien hace el build (el pipeline de despliegue, o la prueba de T-50). Si no está
   * definida, `App.tsx` muestra «desarrollo».
   */
  readonly VITE_VERSION_BUILD?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
