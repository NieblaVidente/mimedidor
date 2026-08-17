import math
from pathlib import Path

import cv2
import numpy as np
import pytest

from app.vision.preprocesamiento import (
    TAMANO_SALIDA,
    CaratulaNoDetectada,
    preprocesar_caratula,
)

# No versionada (.gitignore: /dataset-fotos/) — cada integrante la baja de la carpeta
# compartida de OneDrive. Ver docs/dataset-campo/registro-medidores.md.
CARPETA_DATASET = Path(__file__).resolve().parents[2] / "dataset-fotos"


def _imagen_sintetica_con_perspectiva() -> np.ndarray:
    """Genera una carátula circular sintética con una inclinación de perspectiva conocida,
    sin depender de una foto real. Sirve para probar el pipeline de forma determinística,
    igual que test_reconocimiento.py hace con dígitos sintéticos para T-02b."""
    lado = 500
    imagen = np.full((lado, lado, 3), 40, dtype=np.uint8)  # fondo oscuro (caja de concreto)
    cv2.circle(imagen, (lado // 2, lado // 2), 180, (200, 200, 200), thickness=-1)
    cv2.circle(imagen, (lado // 2, lado // 2), 180, (60, 60, 60), thickness=4)

    # Empuja las esquinas superiores hacia adentro, simulando una foto tomada desde abajo
    # (caso típico: medidor a ras de suelo, cámara apuntando hacia arriba).
    origen = np.float32([[0, 0], [lado, 0], [lado, lado], [0, lado]])
    destino = np.float32([[60, 0], [lado - 60, 0], [lado, lado], [0, lado]])
    homografia = cv2.getPerspectiveTransform(origen, destino)
    return cv2.warpPerspective(imagen, homografia, (lado, lado), borderValue=(40, 40, 40))


def test_preprocesar_caratula_detecta_circulo_sintetico():
    imagen = _imagen_sintetica_con_perspectiva()

    resultado = preprocesar_caratula(imagen)

    assert resultado.imagen.shape == (TAMANO_SALIDA, TAMANO_SALIDA, 3)
    assert resultado.radio_original > 0


def test_preprocesar_caratula_lanza_excepcion_sin_circulo():
    imagen_sin_caratula = np.full((300, 300, 3), 30, dtype=np.uint8)  # negro liso, sin bordes

    with pytest.raises(CaratulaNoDetectada):
        preprocesar_caratula(imagen_sin_caratula)


def _fotos_reales_disponibles() -> list[Path]:
    if not CARPETA_DATASET.exists():
        return []
    extensiones = {".jpg", ".jpeg", ".png"}
    return sorted(p for p in CARPETA_DATASET.iterdir() if p.suffix.lower() in extensiones)


@pytest.mark.skipif(
    len(_fotos_reales_disponibles()) < 2,
    reason=(
        "Requiere al menos 2 fotos reales en dataset-fotos/ en la raíz del repo (no "
        "versionada; se baja de la carpeta compartida de OneDrive — ver "
        "docs/dataset-campo/registro-medidores.md). No corre en CI a propósito: las fotos "
        "son datos personales de los abonados y no se suben al repositorio."
    ),
)
def test_preprocesar_caratula_funciona_sobre_dataset_real():
    """Corre el pipeline sobre las fotos reales disponibles localmente y verifica el criterio
    de aceptación de T-09: al menos 70% de las fotos frontales/de ángulo natural deben
    procesarse sin lanzar CaratulaNoDetectada. Con 2 fotos disponibles, 70% exige que las 2
    funcionen (ceil(0.7 * 2) == 2)."""
    fotos = _fotos_reales_disponibles()

    exitosas = 0
    for ruta in fotos:
        imagen = cv2.imread(str(ruta))
        assert imagen is not None, f"No se pudo leer {ruta.name}"
        try:
            resultado = preprocesar_caratula(imagen)
            assert resultado.imagen.shape == (TAMANO_SALIDA, TAMANO_SALIDA, 3)
            exitosas += 1
        except CaratulaNoDetectada:
            pass

    minimo_requerido = math.ceil(0.7 * len(fotos))
    assert exitosas >= minimo_requerido, (
        f"Solo {exitosas}/{len(fotos)} fotos se procesaron correctamente "
        f"(mínimo requerido para el 70%: {minimo_requerido})"
    )
