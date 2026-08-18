import PantallaCaptura from './PantallaCaptura'
import PantallaHistorial from './PantallaHistorial'

function App() {
  return (
    <main>
      <h1>MiMedidor</h1>
      <p>Lectura automática de hidrómetros por fotografía.</p>
      <PantallaCaptura />
      <PantallaHistorial />
    </main>
  )
}

export default App
