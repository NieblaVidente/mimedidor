from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from app.vision.preprocesamiento import CaratulaNoDetectada, preprocesar_caratula
from app.vision.reconocimiento import leer_lectura, reconocer_digitos, reconocer_lectura
from app.vision.segmentacion import segmentar_ventana_odometro

# Misma carpeta no versionada que usan test_preprocesamiento.py y test_segmentacion.py.
CARPETA_DATASET = Path(__file__).resolve().parents[2] / "dataset-fotos"

# Lectura real registrada a mano para cada foto — ver docs/dataset-campo/registro-medidores.md.
# Las dos fotos son de Medidor2 (carátula frontal / ángulo natural, casi idénticas).
LECTURA_REAL_POR_FOTO = {
    "Medidor2_captura1.png": "0051069",
    "Medidor2_captura2.png": "0051069",
}


def _imagen_con_digitos(texto: str) -> Image.Image:
    """Genera una imagen sintética con dígitos, sin depender de un archivo externo."""
    imagen = Image.new("L", (400, 150), color=255)
    dibujo = ImageDraw.Draw(imagen)
    fuente = ImageFont.load_default(size=90)
    dibujo.text((20, 20), texto, fill=0, font=fuente)
    return imagen


def test_reconocer_digitos_lee_una_imagen_cualquiera():
    imagen = _imagen_con_digitos("1234")

    resultado = reconocer_digitos(imagen)

    assert "1234" in resultado


def _ventana_sintetica_de_odometro(texto_digitos: str, texto_ruido: str) -> np.ndarray:
    """Ventana de odómetro sintética que imita la estructura real que entrega T-10: un ícono
    (círculo relleno) pegado a la izquierda de la fila de dígitos, y una segunda línea de texto
    más chico debajo (simulando el texto de certificación/modelo que a veces cae dentro del
    recorte de T-10 — ver docstring del módulo). No depende de fotos reales; sirve para probar
    de forma determinística que `leer_lectura` aísla la fila correcta y descarta el ícono. Para
    la exactitud real de campo está `test_reconocer_lectura_mide_exactitud_sobre_dataset_real`.
    """
    ancho, alto = 500, 200
    imagen = np.full((alto, ancho, 3), 255, dtype=np.uint8)
    cv2.circle(imagen, (35, 45), 20, (30, 30, 30), thickness=-1)  # ícono a la izquierda
    imagen_pil = Image.fromarray(imagen)
    dibujo = ImageDraw.Draw(imagen_pil)
    fuente_grande = ImageFont.load_default(size=70)
    fuente_chica = ImageFont.load_default(size=30)
    dibujo.text((80, 5), texto_digitos, fill=(0, 0, 0), font=fuente_grande)
    dibujo.text((10, 130), texto_ruido, fill=(0, 0, 0), font=fuente_chica)
    return cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)


def test_leer_lectura_aisla_fila_de_digitos_y_descarta_icono_y_texto_debajo():
    ventana = _ventana_sintetica_de_odometro("51069", "CERT M241383")

    texto = leer_lectura(ventana)

    assert "51069" in texto


def test_reconocer_lectura_devuelve_none_si_no_hay_suficientes_digitos():
    ventana_lisa = np.full((120, 400, 3), 255, dtype=np.uint8)  # blanco liso, sin dígitos

    assert reconocer_lectura(ventana_lisa) is None


def _fotos_reales_disponibles() -> list[Path]:
    if not CARPETA_DATASET.exists():
        return []
    extensiones = {".jpg", ".jpeg", ".png"}
    return sorted(
        p
        for p in CARPETA_DATASET.iterdir()
        if p.suffix.lower() in extensiones and p.name in LECTURA_REAL_POR_FOTO
    )


@pytest.mark.skipif(
    len(_fotos_reales_disponibles()) < 2,
    reason=(
        "Requiere al menos 2 fotos reales en dataset-fotos/ en la raíz del repo (no "
        "versionada; se baja de la carpeta compartida de OneDrive — ver "
        "docs/dataset-campo/registro-medidores.md). No corre en CI a propósito: las fotos "
        "son datos personales de los abonados y no se suben al repositorio."
    ),
)
def test_reconocer_lectura_mide_exactitud_sobre_dataset_real():
    """Corre el pipeline completo T-09 -> T-10 -> T-11 sobre TODAS las fotos reales disponibles
    y compara contra la lectura real registrada a mano (criterio de aceptación de T-11: medir
    exactitud sobre el dataset completo, sin excluir fotos difíciles ni maquillar el resultado).

    Esta prueba fija (pin) el resultado medido en el momento de cerrar T-11: 0 de 2 lecturas
    coinciden exactamente con la real. Si cambia el algoritmo de reconocimiento y este número
    mejora o empeora, esta prueba va a fallar — es intencional, como recordatorio de actualizar
    `docs/exactitud-reconocimiento.md` con el nuevo resultado en vez de dejar la documentación
    desactualizada."""
    fotos = _fotos_reales_disponibles()

    aciertos = 0
    for ruta in fotos:
        imagen = cv2.imread(str(ruta))
        assert imagen is not None, f"No se pudo leer {ruta.name}"

        try:
            caratula = preprocesar_caratula(imagen).imagen
        except CaratulaNoDetectada:
            continue  # T-09 no detectó la carátula; no hay ventana que reconocer

        ventana = segmentar_ventana_odometro(caratula).imagen
        lectura = reconocer_lectura(ventana)
        real = float(int(LECTURA_REAL_POR_FOTO[ruta.name]))

        if lectura == real:
            aciertos += 1

    assert aciertos == 0, (
        f"La exactitud medida cambió ({aciertos}/{len(fotos)} correctas) — actualizar "
        "docs/exactitud-reconocimiento.md con el nuevo resultado y ajustar este número."
    )
