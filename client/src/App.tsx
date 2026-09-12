import PantallaCaptura from './PantallaCaptura'
import PantallaHistorial from './PantallaHistorial'
import PantallaFactura from './PantallaFactura'

/**
 * Qué build está viendo el abonado.
 *
 * No es decoración. Esta aplicación es una PWA: el trabajador de servicio guarda los archivos del
 * build y los sirve desde caché, así que «recargá la página» no garantiza que alguien esté viendo
 * la versión última. Cuando un integrante reporte un problema, esto es lo que dice contra qué
 * versión reportarlo — y es lo que la prueba de T-50 mira para comprobar que una versión nueva
 * de verdad reemplaza a la cacheada.
 *
 * Vite lo reemplaza por su valor literal en tiempo de build. En desarrollo nadie la define.
 */
const VERSION_BUILD = import.meta.env.VITE_VERSION_BUILD ?? 'desarrollo'

function App() {
  return (
    <>
      <header>
        <h1>MiMedidor</h1>
        <p>Lectura automática de hidrómetros por fotografía.</p>
      </header>
      <main>
        <PantallaCaptura />
        <PantallaHistorial />
        <PantallaFactura />
      </main>
      <footer>
        <p>
          MiMedidor · versión <span id="version-build">{VERSION_BUILD}</span>
        </p>
      </footer>
    </>
  )
}

export default App
