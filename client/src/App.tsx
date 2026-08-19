import PantallaCaptura from './PantallaCaptura'
import PantallaHistorial from './PantallaHistorial'
import PantallaFactura from './PantallaFactura'

function App() {
  return (
    <main>
      <h1>MiMedidor</h1>
      <p>Lectura automática de hidrómetros por fotografía.</p>
      <PantallaCaptura />
      <PantallaHistorial />
      <PantallaFactura />
    </main>
  )
}

export default App
