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

export function capturarFotograma(video: HTMLVideoElement): Promise<Blob> {
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
