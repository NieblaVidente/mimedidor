/**
 * Acceso a la cámara y captura de fotogramas. Aislado del componente de UI (PantallaCaptura)
 * a propósito: jsdom (el entorno de las pruebas) no tiene cámara ni implementa canvas de
 * verdad, así que estas tres funciones son el punto donde las pruebas sustituyen el
 * comportamiento real — igual que el servidor mockea la conexión a base de datos.
 */

export async function abrirCamara(): Promise<MediaStream> {
  return navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
}

export function detenerCamara(stream: MediaStream): void {
  stream.getTracks().forEach((track) => track.stop())
}

/** Milisegundos que se espera a que la cámara entregue su primer fotograma. */
const ESPERA_MAXIMA_FOTOGRAMA_MS = 5000

/**
 * Espera a que el video tenga un fotograma que se pueda dibujar.
 *
 * Hace falta porque entre que el `<video>` recibe el stream y entrega su primer fotograma pasa
 * un momento, y durante ese rato `videoWidth` y `videoHeight` valen 0. Si se captura ahí, el
 * canvas queda de 0×0, `toBlob` devuelve null y el usuario ve "No se pudo capturar la foto" sin
 * haber hecho nada mal — basta con tocar el botón apenas aparece, algo probable en un teléfono
 * lento. Lo detectó la prueba end-to-end de T-22.
 */
function esperarFotograma(video: HTMLVideoElement): Promise<void> {
  // readyState >= 2 (HAVE_CURRENT_DATA) significa que ya hay datos del fotograma actual.
  if (video.readyState >= 2 && video.videoWidth > 0) return Promise.resolve()

  return new Promise((resolve, reject) => {
    const limpiar = () => {
      clearTimeout(temporizador)
      video.removeEventListener('loadeddata', alCargar)
    }
    const alCargar = () => {
      limpiar()
      resolve()
    }
    const temporizador = setTimeout(() => {
      limpiar()
      reject(new Error('La cámara no entregó ningún fotograma a tiempo'))
    }, ESPERA_MAXIMA_FOTOGRAMA_MS)

    video.addEventListener('loadeddata', alCargar)
  })
}

export async function capturarFotograma(video: HTMLVideoElement): Promise<Blob> {
  await esperarFotograma(video)

  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const contexto = canvas.getContext('2d')
    if (!contexto) {
      reject(new Error('No se pudo crear el contexto de canvas'))
      return
    }
    contexto.drawImage(video, 0, 0, canvas.width, canvas.height)
    canvas.toBlob(
      (blob) => {
        if (blob) resolve(blob)
        else reject(new Error('No se pudo capturar la foto'))
      },
      'image/jpeg',
      0.9,
    )
  })
}
