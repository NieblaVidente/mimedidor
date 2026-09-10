import PantallaCaptura from './PantallaCaptura'
import PantallaHistorial from './PantallaHistorial'
import PantallaFactura from './PantallaFactura'

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
    </>
  )
}

export default App
