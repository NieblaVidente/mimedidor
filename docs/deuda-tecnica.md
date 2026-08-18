# Deuda técnica

Registro vivo de atajos tomados a propósito para cumplir el alcance del sprint, con la
justificación y qué haría falta para resolverlos. No es una lista de bugs — es una lista de
decisiones conscientes que alguien debería revisar más adelante.

---

## T-10 · Posición fija de respaldo para la ventana del odómetro

**Qué se hizo.** `server/app/vision/segmentacion.py` intenta localizar la ventana de dígitos del
odómetro por bordes (Sobel + Otsu + cierre morfológico, acotado a una franja de la carátula). Si
ningún contorno pasa el filtro de relación de aspecto, cae a un recorte de **posición fija**
(`FRACCION_RESPALDO_X` / `FRACCION_RESPALDO_Y`), en vez de fallar. La tarjeta T-10 permite
explícitamente este atajo si la detección automática no alcanza a completarse a tiempo.

**Estado real.** Con las 2 fotos reales disponibles al cerrar la tarjeta (Medidor2, carátula
frontal y ángulo natural — ver `docs/dataset-campo/registro-medidores.md`), la detección
automática funcionó en las dos; el recorte de respaldo nunca se activó en la práctica. Queda en
el código como red de seguridad, no como el camino verificado.

**Por qué es deuda de todos modos.**

1. Las franjas de búsqueda (`FRACCION_X`, `FRACCION_Y`) y el recorte de respaldo están calibrados
   con fotos de **un solo medidor** (modelo `MJ-SDC`, marca ASADA Tronadora). No hay evidencia de
   que la posición relativa de la ventana se mantenga igual en otras marcas/modelos — T-08 todavía
   no cerró qué marca predomina en la muestra.
2. El criterio de aceptación ("70% de las salidas exitosas de T-09") se validó sobre una muestra
   de 2 fotos casi idénticas del mismo medidor, no sobre variedad real de ángulos/iluminación.

**Qué haría falta para cerrarla.** Volver a correr `test_segmentar_ventana_funciona_sobre_salidas_reales_de_t09`
a medida que crezca el dataset de T-07 (meta: 12 medidores), y si aparecen medidores de otra
marca/modelo, confirmar que la franja de búsqueda sigue sirviendo o recalibrarla. Si el recorte de
respaldo llega a activarse en la práctica con fotos reales, es señal de que la franja necesita
ajustarse o de que hace falta un método menos dependiente de la posición (por ejemplo, detectar la
ventana por su propio contraste sin acotar antes por posición).

**Tarjeta de seguimiento.** Anotado para crear en el Sprint 2: *"Revalidar y, si hace falta,
generalizar la detección de la ventana del odómetro contra el dataset completo de 12 medidores."*
