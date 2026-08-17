"""Preprocesamiento de fotos del hidrómetro: detección de la carátula circular y
corrección de perspectiva (T-09).

Filtros aplicados y por qué (relevante para Señales y Sistemas — ver CLAUDE.md §7, la imagen
se trata como una señal 2D):

1. Escala de grises. La detección de bordes y círculos solo necesita intensidad, no color;
   reduce el volumen de datos a convolucionar sin perder la información geométrica que se
   busca (la forma de la carátula, no su color).
2. Suavizado gaussiano. Es una convolución 2D con un núcleo gaussiano que atenúa el ruido de
   alta frecuencia (grano del sensor, textura del concreto de la caja, salpicaduras) antes de
   derivar bordes. Sin este paso la transformada de Hough vota por círculos falsos sobre el
   ruido en vez de sobre el borde real de la carátula.
3. Transformada de Hough para círculos (`cv2.HOUGH_GRADIENT`). Vota en el espacio de
   parámetros (centro, radio) por los píxeles de borde consistentes con un círculo. Es el
   método estándar para localizar la carátula porque es circular por diseño — a diferencia del
   odómetro, que es rectangular (T-10) y no se busca con este método.
4. Detección de bordes (Canny) + ajuste de elipse (`cv2.fitEllipse`) sobre el recorte. La
   proyección de un círculo fotografiado en ángulo es una elipse: cuanto más inclinada la
   cámara, más aplanada la elipse. Ajustar una elipse al contorno real permite medir esa
   inclinación directamente de la imagen, sin conocer el ángulo de la cámara de antemano.
5. Transformación afín de rotar + escalar + rotar. Lleva la elipse ajustada a un círculo:
   rota la imagen para alinear el eje mayor de la elipse con un eje de coordenadas, escala
   ese eje corto para igualarlo al eje largo (deshaciendo el achatamiento por perspectiva), y
   rota de vuelta. Es una aproximación afín (no una homografía completa de 4 puntos, que
   necesitaría más referencias que las que da una sola elipse) pero alcanza para "enderezar"
   la carátula porque el objeto real que se corrige es circular y simétrico.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

TAMANO_SALIDA = 400  # lado del cuadrado de salida, en píxeles
MARGEN_RECORTE = 1.15  # margen extra alrededor del círculo detectado al recortar
AREA_MINIMA_CONTORNO = 0.15  # fracción del recorte que debe cubrir el contorno para confiar en él


class CaratulaNoDetectada(Exception):
    """La imagen no tiene un círculo lo bastante claro como para ser la carátula del medidor."""


@dataclass
class ResultadoPreprocesamiento:
    imagen: np.ndarray  # BGR, TAMANO_SALIDA x TAMANO_SALIDA
    centro_original: tuple[int, int]
    radio_original: int
    perspectiva_corregida: bool  # False si solo se pudo recortar y redimensionar


def _a_escala_de_grises_suavizada(imagen_bgr: np.ndarray) -> np.ndarray:
    gris = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gris, (9, 9), sigmaX=2)


def _detectar_circulo_caratula(gris_suavizado: np.ndarray) -> tuple[int, int, int]:
    """Ubica el círculo más probable de ser la carátula. Devuelve (x, y, radio) en píxeles."""
    alto, ancho = gris_suavizado.shape
    radio_min = int(min(alto, ancho) * 0.15)
    radio_max = int(min(alto, ancho) * 0.48)

    circulos = cv2.HoughCircles(
        gris_suavizado,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=radio_max,
        param1=100,
        param2=40,
        minRadius=radio_min,
        maxRadius=radio_max,
    )

    if circulos is None:
        raise CaratulaNoDetectada("No se detectó ningún círculo compatible con una carátula")

    candidatos = np.round(circulos[0]).astype(int)
    # Si hay varios candidatos, NO alcanza con tomar el círculo más grande: en las fotos reales
    # del dataset la tapa exterior de la caja (abierta, detrás) también es circular y suele ser
    # más grande que la carátula del medidor. El protocolo de captura (docs/dataset-campo) apunta
    # la cámara directo a la carátula, así que se prioriza el círculo más centrado en el encuadre;
    # el radio solo desempata entre candidatos igual de centrados.
    centro_imagen = np.array([ancho / 2, alto / 2])

    def _distancia_al_centro(circulo):
        x, y, _ = circulo
        return np.linalg.norm(np.array([x, y]) - centro_imagen)

    candidatos_ordenados = sorted(candidatos, key=lambda c: (_distancia_al_centro(c), -c[2]))
    x, y, r = candidatos_ordenados[0]
    return int(x), int(y), int(r)


def _recortar_con_margen(imagen_bgr: np.ndarray, x: int, y: int, r: int) -> np.ndarray:
    alto, ancho = imagen_bgr.shape[:2]
    radio_con_margen = int(r * MARGEN_RECORTE)

    x0 = max(0, x - radio_con_margen)
    y0 = max(0, y - radio_con_margen)
    x1 = min(ancho, x + radio_con_margen)
    y1 = min(alto, y + radio_con_margen)

    return imagen_bgr[y0:y1, x0:x1]


def _contorno_caratula(recorte_bgr: np.ndarray) -> np.ndarray | None:
    gris = cv2.cvtColor(recorte_bgr, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (5, 5), sigmaX=1.5)
    bordes = cv2.Canny(gris, 50, 150)
    bordes = cv2.dilate(bordes, None, iterations=1)
    contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    contornos_validos = [c for c in contornos if len(c) >= 5]
    if not contornos_validos:
        return None

    mayor = max(contornos_validos, key=cv2.contourArea)
    area_minima = AREA_MINIMA_CONTORNO * recorte_bgr.shape[0] * recorte_bgr.shape[1]
    if cv2.contourArea(mayor) < area_minima:
        return None
    return mayor


def _enderezar_por_elipse(recorte_bgr: np.ndarray) -> tuple[np.ndarray, bool]:
    """Corrige la perspectiva ajustando una elipse al borde de la carátula y llevándola a un
    círculo. Si no se logra un contorno confiable, devuelve el recorte solo redimensionado
    (perspectiva_corregida=False) en vez de fallar — un recorte sin enderezar sigue siendo
    útil para T-10/T-11."""
    contorno = _contorno_caratula(recorte_bgr)
    if contorno is None:
        return cv2.resize(recorte_bgr, (TAMANO_SALIDA, TAMANO_SALIDA)), False

    (cx, cy), (eje_a, eje_b), angulo = cv2.fitEllipse(contorno)
    eje_mayor, eje_menor = max(eje_a, eje_b), min(eje_a, eje_b)

    if eje_menor <= 1:  # elipse degenerada, no dividir por ~0 más abajo
        return cv2.resize(recorte_bgr, (TAMANO_SALIDA, TAMANO_SALIDA)), False

    # cv2 mide `angulo` como la rotación del eje que devuelve primero (eje_a) respecto al eje X.
    # Si el eje mayor real es eje_b, el eje mayor queda 90° rotado respecto a `angulo`.
    angulo_eje_mayor = angulo if eje_a >= eje_b else angulo + 90
    # Alinear un eje a 0° sirve igual rotando +angulo_eje_mayor que rotando eso menos 180° (una
    # elipse es simétrica ante una rotación de 180°) — pero visualmente NO da lo mismo: una de
    # las dos opciones puede dejar la carátula boca abajo. Se normaliza al ángulo equivalente
    # más chico en (-90°, 90°] para que solo se corrija la inclinación de perspectiva y la foto
    # mantenga su orientación original (arriba sigue siendo arriba).
    angulo_eje_mayor = ((angulo_eje_mayor + 90) % 180) - 90

    alto, ancho = recorte_bgr.shape[:2]
    # 1) Rotar para alinear el eje mayor de la elipse con el eje X.
    rotacion = cv2.getRotationMatrix2D((cx, cy), angulo_eje_mayor, 1.0)
    rotada = cv2.warpAffine(recorte_bgr, rotacion, (ancho, alto))

    # 2) Escalar el eje corto (Y, ya alineado) para igualar al eje largo — deshace el
    #    achatamiento que produce la perspectiva sobre un círculo real.
    factor_escala = eje_mayor / eje_menor
    escalado = cv2.resize(
        rotada,
        None,
        fx=1.0,
        fy=factor_escala,
        interpolation=cv2.INTER_LINEAR,
    )
    cy_escalado = cy * factor_escala

    # 3) Rotar de vuelta el mismo ángulo. Sin este paso la carátula queda circularizada pero
    #    girada a la orientación que le tocó al eje mayor (de lado o boca abajo según la foto) —
    #    rotar-escalar-rotar de vuelta es la forma estándar de corregir un achatamiento elíptico
    #    sin alterar la orientación original de la imagen.
    rotacion_vuelta = cv2.getRotationMatrix2D((cx, cy_escalado), -angulo_eje_mayor, 1.0)
    enderezado = cv2.warpAffine(escalado, rotacion_vuelta, (escalado.shape[1], escalado.shape[0]))

    # 4) Recortar un cuadrado centrado en la carátula ya circularizada y llevarlo al tamaño
    #    de salida estándar.
    radio_final = eje_mayor / 2 * MARGEN_RECORTE
    x0 = max(0, int(cx - radio_final))
    y0 = max(0, int(cy_escalado - radio_final))
    x1 = min(enderezado.shape[1], int(cx + radio_final))
    y1 = min(enderezado.shape[0], int(cy_escalado + radio_final))

    cuadrado = enderezado[y0:y1, x0:x1]
    if cuadrado.size == 0:
        return cv2.resize(recorte_bgr, (TAMANO_SALIDA, TAMANO_SALIDA)), False

    return cv2.resize(cuadrado, (TAMANO_SALIDA, TAMANO_SALIDA)), True


def preprocesar_caratula(imagen_bgr: np.ndarray) -> ResultadoPreprocesamiento:
    """Recibe una foto (array BGR, como lo entrega `cv2.imread`) y devuelve la carátula
    recortada y enderezada a un cuadrado de TAMANO_SALIDA x TAMANO_SALIDA.

    Lanza CaratulaNoDetectada si no se encuentra ningún círculo compatible con una carátula
    en la imagen completa (paso 1). La corrección de perspectiva (paso 2) es best-effort: si
    no se puede ajustar una elipse confiable, se devuelve el recorte sin enderezar en vez de
    fallar, porque igual es más útil que rechazar la foto entera.
    """
    gris_suavizado = _a_escala_de_grises_suavizada(imagen_bgr)
    x, y, r = _detectar_circulo_caratula(gris_suavizado)

    recorte = _recortar_con_margen(imagen_bgr, x, y, r)
    enderezada, perspectiva_corregida = _enderezar_por_elipse(recorte)

    return ResultadoPreprocesamiento(
        imagen=enderezada,
        centro_original=(x, y),
        radio_original=r,
        perspectiva_corregida=perspectiva_corregida,
    )
