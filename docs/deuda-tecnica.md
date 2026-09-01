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
a medida que crezca el dataset de T-07 (meta vigente: **8 medidores**, revisada en el Sprint
Planning del Sprint 2 desde los 12 originales), y si aparecen medidores de otra
marca/modelo, confirmar que la franja de búsqueda sigue sirviendo o recalibrarla. Si el recorte de
respaldo llega a activarse en la práctica con fotos reales, es señal de que la franja necesita
ajustarse o de que hace falta un método menos dependiente de la posición (por ejemplo, detectar la
ventana por su propio contraste sin acotar antes por posición).

**Tarjeta de seguimiento.** Anotado para crear en el Sprint 2: *"Revalidar y, si hace falta,
generalizar la detección de la ventana del odómetro contra el dataset completo."*

---

## T-13 · La vista y la función del modelo de datos nunca se escribieron — CERRADA (T-34)

> ✅ **Cerrada el 2026-08-27.** Se eligió la opción 2 de las dos de abajo: corregir
> `modelo-datos.md` §3 para que describa la realidad (cálculo en Python), en vez de escribir la
> vista y la función. Justificación completa en `modelo-datos.md` §3 y en el PR de T-34
> ([#44](https://github.com/NieblaVidente/mimedidor/issues/44)). Se deja el resto de esta
> entrada tal cual quedó escrita originalmente, como registro de la decisión.

**Qué se hizo.** `docs/architecture/modelo-datos.md` §3 dice que los campos derivados del contrato
de la API se resolverían en la base de datos: `vista_historial_lecturas` (con `LAG()`, para el
consumo entre lecturas consecutivas) y `fn_comparacion_factura(factura_id)` (para el contraste
contra factura). **Ninguna de las dos llegó a escribirse en los scripts de T-13.** Cuando T-17 y
T-18 necesitaron esos cálculos, se resolvieron en Python dentro de los routers.

**Por qué es deuda.** No es un bug — los cálculos están probados y dan el resultado correcto — pero
hay una diferencia real entre el modelo documentado y el implementado, y el documento de modelo de
datos afirma algo que no existe en la base. Alguien que lea el modelo y después busque la vista en
`psql` no la va a encontrar. Además, el razonamiento original de §3 sigue siendo válido: hacerlo en
SQL evita repetir la misma lógica en dos routers distintos.

**Qué haría falta para cerrarla.** Una de dos, y hay que decidir cuál:

1. **Escribir la vista y la función** en un script nuevo de `database/scripts/`, y cambiar los
   routers para que las consulten. Es lo que dice el modelo, y suma evidencia para la rúbrica de
   Base de Datos.
2. **Corregir `modelo-datos.md` §3** para que describa lo que de verdad se hizo, si el equipo
   decide que calcularlo en Python es mejor.

Lo que no se puede dejar es la contradicción actual entre los dos.

**Tarjeta de seguimiento.** Anotado para crear en el Sprint 2: *"Cerrar la diferencia entre
`modelo-datos.md` §3 y los scripts: escribir `vista_historial_lecturas` y `fn_comparacion_factura`,
o corregir el documento."*

---

## ✅ CERRADO — T-16 / T-17 / T-18 · Clase de error duplicada en el cliente

**Qué se hizo (cuando se registró la deuda).** `client/src/api/lecturas.ts` y
`client/src/api/facturas.ts` declaraban cada uno su propia clase de error (`ErrorApiLecturas` y
`ErrorApiFacturas`) y su propia función `lanzarError`, idénticas salvo el nombre.

**Por qué pasó.** Las ramas de T-16, T-17 y T-18 salieron de `main` por separado, antes de que
ninguna de las anteriores estuviera mergeada, porque los compañeros todavía no habían revisado
nada. Se prefirió duplicar unas pocas líneas antes que encadenar los Pull Requests entre sí, que
habría hecho que aprobar uno arrastrara código no revisado de los otros.

**Por qué era deuda.** Dos clases que hacen lo mismo se desincronizan: si mañana el contrato agrega
un campo al cuerpo de error, hay que acordarse de tocar los dos archivos.

**Cómo se cerró.** T-33 (#43): se extrajo una única clase `ErrorApi` y `lanzarError` a
`client/src/api/errores.ts`. `lecturas.ts` y `facturas.ts` la importan desde ahí en vez de
declararla cada uno, y `PantallaCaptura.tsx`, `PantallaHistorial.tsx` y `PantallaFactura.tsx`
(con sus pruebas) importan `ErrorApi` directo de `./api/errores` en lugar de los dos nombres
duplicados que exportaban antes `lecturas.ts`/`facturas.ts`. Las pruebas del cliente (`npm run
test`), el linter (`npm run lint`) y el build (`npm run build`) siguen en verde.
