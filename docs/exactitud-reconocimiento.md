# Exactitud del reconocimiento de dígitos (T-11)

Este documento mide, sin maquillar el número, qué tan bien funciona el reconocimiento de la
lectura del odómetro sobre el dataset real disponible hoy. Es el criterio de aceptación central
de T-11: la tarjeta no pide acertar el 100% de las fotos, pide medir y documentar qué tan bien
funciona — incluyendo los casos que fallan y por qué.

## Qué se midió

Pipeline completo sobre cada foto real disponible:

`preprocesar_caratula` (T-09) → `segmentar_ventana_odometro` (T-10) → `reconocer_lectura` (T-11)

El resultado de `reconocer_lectura` se compara contra la lectura real anotada a mano en
`docs/dataset-campo/registro-medidores.md` al momento de tomar la foto. Coincidencia exacta
(número igual dígito por dígito), no aproximada.

## Dataset usado

Al cerrar esta tarjeta, `dataset-fotos/` tiene 2 fotos utilizables para el pipeline completo (la
carpeta no se versiona — ver `docs/dataset-campo/registro-medidores.md`):

| Foto | Medidor | Lectura real |
|---|---|---|
| `Medidor2_captura1.png` | Medidor2 (carátula frontal) | `0051069` m³ |
| `Medidor2_captura2.png` | Medidor2 (ángulo natural, casi idéntica a la anterior) | `0051069` m³ |

**Nota de transparencia sobre exclusión de fotos.** El registro también anota una foto de
Medidor1 ("primer plano del odómetro"), pero esa foto no es un recorte de carátula completa
— T-09 necesita ver la carátula redonda entera para detectar el círculo, y esta toma no la
tiene. Además, esa foto no estaba disponible en `dataset-fotos/` (ni local ni en la carpeta
compartida sincronizada) al momento de esta medición, así que no se pudo incluir ni siquiera
probándola por fuera del pipeline T-09→T-10. No se excluyó a propósito por ser "difícil": no
estaba disponible. Queda anotado para volver a medir cuando esa foto (u otras nuevas de T-07/T-08)
estén accesibles.

Con solo 2 fotos, y casi idénticas entre sí, esta medición **no es representativa** de cómo va a
funcionar el reconocimiento sobre otros medidores, ángulos o condiciones de luz. Es el punto de
partida, no una conclusión general — igual que ya advierte `docs/deuda-tecnica.md` sobre T-10.

## Resultado medido

**0 de 2 lecturas (0%) coinciden exactamente con la lectura real.**

| Foto | Texto crudo de Tesseract | Lectura interpretada | Lectura real | ¿Correcta? |
|---|---|---|---|---|
| `Medidor2_captura1.png` | `0051401691` (10 caracteres) | `None` (descartada: fuera del rango de largo válido) | `0051069` | No — y lo marca como no confiable en vez de inventar un número |
| `Medidor2_captura2.png` | `0015110` (7 caracteres) | `15110.0` | `51069.0` | No — y no hay forma de saber que está mal solo con este dato |

Este resultado está fijado (pin) en
`server/tests/test_reconocimiento.py::test_reconocer_lectura_mide_exactitud_sobre_dataset_real`:
si alguien mejora el algoritmo y la exactitud cambia, esa prueba va a fallar como recordatorio de
actualizar este documento en vez de dejarlo desactualizado.

## Por qué falla — análisis de los dos casos

Ambas fotos comparten la misma causa raíz de fondo, pero fallan de dos maneras distintas y vale
la pena distinguirlas:

**Caso 1 — falla "seguro" (se detecta a sí mismo como no confiable).** El texto crudo trae 10
caracteres en vez de 7. Revisando el recorte que le llega a Tesseract, el problema son las
líneas divisorias verticales entre casillas de dígitos del odómetro: Tesseract las interpreta
como si fueran el dígito "1" suelto entre cada par de números reales. Esto es un problema
conocido de aplicarle OCR genérico — entrenado sobre tipografía impresa continua — a un display
de rodillos mecánico con separadores físicos entre casillas. Como el resultado tiene una
cantidad de dígitos claramente fuera de lo esperado, `reconocer_lectura` lo descarta y devuelve
`None` en vez de forzar un número. Es el comportamiento deseable: falla de forma visible.

**Caso 2 — falla "silenciosa" (devuelve un número con confianza, pero está mal).** Acá el texto
crudo sí tiene 7 caracteres — la cantidad correcta — pero salieron mal: `0015110` en vez de
`0051069`. Es la misma confusión de líneas divisorias, pero esta vez el conteo de caracteres
"cuadra" por coincidencia, así que `reconocer_lectura` no tiene forma de detectar que el
resultado es incorrecto. Esta es la falla que más importa documentar: el sistema puede devolver
un número que parece válido y no lo es, sin ninguna señal de alerta. Es exactamente el motivo
por el que la corrección manual (criterio de aceptación #4, ver abajo) no es un detalle menor
sino la red de seguridad real mientras el reconocimiento automático esté en este nivel.

**Mejora que sí se aplicó en esta tarjeta.** Antes de este análisis, el recorte que entrega T-10
(`segmentacion.segmentar_ventana_odometro`) incluía no solo la fila de dígitos sino también la
línea de texto de certificación/modelo justo debajo (visible en la carátula). Eso hacía que
Tesseract mezclara ambas líneas y devolviera números del serial o del código de modelo en vez de
la lectura. `reconocimiento.py` ahora aísla la fila de dígitos por su propia cuenta (ver su
docstring) antes de llamar a Tesseract — sin modificar `segmentacion.py`, que ya está cerrado y
en `main` (T-10). Esto mejoró la calidad de lo que le llega a Tesseract, pero no alcanzó para
resolver el problema de las líneas divisorias, que es la causa raíz que queda pendiente.

## Qué haría falta para mejorar esto (fuera de alcance de T-11)

- **Más dataset.** Con 2 fotos casi idénticas de un solo medidor no se puede saber si el problema
  de las líneas divisorias se repite igual en otros modelos, ni calibrar nada con confianza.
  Bloqueado por T-07/T-08 (meta vigente: 8 medidores, revisada en el Sprint Planning del
  Sprint 2 desde los 12 originales).
- **Manejar las líneas divisorias explícitamente** — por ejemplo, detectarlas y borrarlas antes
  de pasarle la imagen a Tesseract, o segmentar cada casilla de dígito por separado y reconocerla
  individualmente en vez de pedirle a Tesseract que lea la fila completa de una sola vez.
- **Un método distinto a OCR genérico** para este tipo de display (comparación contra plantillas
  de dígitos, o un modelo entrenado específicamente para este tipo de odómetro). CLAUDE.md marca
  explícitamente que entrenar un modelo propio **no es alcance de este sprint** — queda anotado
  para evaluar más adelante, cuando haya dataset suficiente para hacerlo con criterio.

Se anota como tarjeta de seguimiento para Sprint 2, en la misma línea que la de T-10 en
`docs/deuda-tecnica.md`.

## Criterio de aceptación #4 — corrección manual de la lectura

T-11 pide asegurar que la app permita corregir manualmente la lectura cuando el reconocimiento
se equivoca. Dado el resultado de arriba, esto no es opcional.

Esto ya está cubierto por trabajo existente, sin necesidad de construir nada nuevo en esta
tarjeta: `POST /api/lecturas` (T-15, ya implementado — ver `server/app/api/lecturas.py`) recibe
un campo `origen: "manual" | "reconocimiento"` en `LecturaEntrada`. Cualquier lectura entra por
ese mismo endpoint sea cual sea su origen, así que una lectura reconocida automáticamente y
resultó incorrecta se corrige simplemente registrando una nueva lectura con `origen: "manual"` y
el valor correcto — el mismo campo es, según el contrato de API
(`docs/architecture/contrato-api.md`), "el que permite calcular la exactitud real en T-11
(cuántas lecturas necesitaron corrección manual)".

Lo que **no** existe todavía, y no es parte del alcance de T-11, es el endpoint
`POST /api/lecturas/reconocer` descrito en el contrato de API, que encadenaría T-09 → T-10 → T-11
sobre una foto subida y devolvería `{lectura_reconocida, confianza}` sin persistir nada. Construir
ese endpoint es el paso natural de integración una vez que las tres tarjetas de visión (T-09,
T-10, T-11) están cerradas — queda como siguiente tarjeta, no como parte de esta.


---

# Segunda medición — 5 fotos, 3 medidores, 3 marcas (2026-09-02)

La primera medición se hizo sobre **2 fotos casi idénticas de un solo medidor**. Con el dataset
en 3 medidores y 3 marcas se repitió, sin modificar código, para ver si el diagnóstico original
se sostenía.

**No se sostiene.** El resultado sigue siendo cero, pero por **tres causas distintas**, y la que
describe T-32 es la última de la cadena, no la primera.

## Resultado

| Foto | Real | Crudo de Tesseract | Devuelto | ¿Perspectiva corregida? |
|---|---|---|---|---|
| `Medidor1_captura1` | `025888` | `''` | `None` | **no** |
| `Medidor2_captura1` | `0051069` | `'005140691'` | `None` | sí |
| `Medidor2_captura2` | `0051069` | `'00151106'` | `151106.0` ⚠️ | sí |
| `Medidor3_captura1` | `452991` | `''` | `None` | **no** |
| `Medidor3_captura2` | `452991` | `''` | `None` | **no** |

**Exactitud: 0 de 5.** La correlación es exacta: cuando la perspectiva se corrige, Tesseract lee
algo; cuando no, no lee nada.

## La cadena de fallos, eslabón por eslabón

### 1. La esfera de Medidor1 nunca llega a ser candidata

`_detectar_circulo_caratula` fija `radio_min = 15 %` del lado corto de la imagen. En esa foto la
esfera del ARAD es más chica que ese umbral, así que **Hough no la propone**. Los dos candidatos
que sí propone son la boca de la caja, en dos posiciones distintas — se verificó recortando ambos.

La regla actual elige «el más centrado», y ahí lo centrado es la caja.

> **Esto es en parte un problema de captura, no de código.** El registro del dataset anota esa
> foto como «primer plano del odómetro» y no lo es: se ve la caja completa con la esfera pequeña
> arriba. El protocolo pide «bien de cerca, dígitos grandes y nítidos». Se corrigió la anotación.

### 2. En Medidor3 el círculo es correcto, pero la corrección de perspectiva falla igual

Acá el círculo elegido **sí es la esfera**: es el más centrado *y* el más claro de los candidatos.

| Candidato | Radio | Brillo interior | Distancia al centro |
|---|---|---|---|
| **elegido** | 794 | **158,7** | 0,063 |
| otro | 1011 | 47,2 | 0,434 |

Aun así `perspectiva_corregida` es `False` y el recorte incluye bastante bisel negro alrededor de
la esfera. Como la franja de búsqueda de la segmentación se define en **fracciones de una carátula
ya enderezada**, sobre un recorte mal normalizado apunta al lugar equivocado: devuelve la carátula
entera en vez de la ventana del odómetro.

### 3. Recién acá aparecen las líneas divisorias, que es lo que describe T-32

En las dos fotos de Medidor2 la ventana **sí** queda bien recortada, y ahí el diagnóstico original
se confirma: `005140691` son 9 caracteres donde van 7, y `00151106` son 8. Las líneas entre
casillas se leen como dígitos.

`Medidor2_captura2` sigue siendo **la falla peligrosa**: devuelve `151106.0`, con cantidad de
dígitos plausible y sin ninguna señal de alerta.

## Un dato que sí quedó medido y sirve

El brillo interior separa la esfera del resto de los círculos con margen amplio en 4 de las 5
fotos:

| Foto | Brillo del círculo correcto | Brillo del mejor competidor |
|---|---|---|
| Medidor2_captura1 | 206,2 | 79,1 |
| Medidor2_captura2 | 197,6 | 61,6 |
| Medidor3_captura1 | 126,1 | 54,0 |
| Medidor3_captura2 | 158,7 | 47,2 |
| Medidor1_captura1 | *(la esfera no es candidata)* | — |

Es un criterio con fundamento de dominio —la esfera es una cara clara bajo vidrio, la caja y el
bisel son oscuros— y no un ajuste a estas fotos. Queda anotado como la vía más prometedora.

## Por qué no se escribió el arreglo todavía

**Escribirlo ahora repetiría el error que esta misma medición acaba de destapar.**

La regla que falla en Medidor3 está documentada en `segmentacion.py:82` como «confirmado con las
2 fotos reales», y la de la carátula se eligió con el mismo criterio. Calibrar el reemplazo sobre
**5 fotos, de las cuales 1 no cumple el protocolo de captura**, produciría otra heurística que
funciona en la muestra y falla en el próximo medidor.

Lo que hace falta antes:

- **Más dataset** (T-07, hoy en 3 de 8), y sobre todo **más de una foto útil por medidor**: hoy
  Medidor1 aporta una sola y no sirve.
- **Repetir la toma de Medidor1** siguiendo el protocolo, con la esfera llenando el encuadre.
- Con eso, atacar en orden: detección de la carátula → segmentación de la ventana → líneas
  divisorias. T-32 describe el tercer eslabón; los dos primeros bloquean hoy el 60 % del dataset.
