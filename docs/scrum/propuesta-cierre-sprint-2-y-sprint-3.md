# Propuesta para el cierre del Sprint 2 y el Planning del Sprint 3

> ## ⚠️ Esto NO es un acta
>
> Las ceremonias **todavía no ocurrieron**. Están convocadas para el **7 de setiembre de 2026**.
> Este documento es **material preparado de antemano** para que los tres lleguen con los datos ya
> revisados en vez de buscarlos en la reunión.
>
> **El acta se escribe después, con lo que de verdad se decida**, en `sprint-2.md` (Review y
> Retrospectiva) y en `sprint-3.md` (Planning). Si en la reunión se decide algo distinto a lo que
> propone este archivo, **manda la reunión**.
>
> **Qué se espera de Isaac y Yariel en este Pull Request:** léanlo, comenten lo que no compartan y
> respondan las preguntas de la sección 7. Aprobarlo significa «estos datos son correctos y estas
> propuestas se pueden llevar a la reunión», no «esto ya está decidido».

**Autor de la propuesta:** José Pablo Ramírez Sánchez (Scrum Master)
**Fecha:** 2026-09-06

---

## 1. Los datos del Sprint 2

Todos salen del tablero de Issues y del historial de Pull Requests. **Ninguno es de memoria.**
Cualquiera se puede recalcular con los comandos que están al final de cada tabla.

### 1.1 El compromiso se cumplió entero

| Issue | Tarea | Puntos | Estado |
|---|---|---|---|
| #31 | T-21 · Conectar cliente y servidor | 3 | ✅ |
| #32 | T-22 · Prueba end-to-end con Cypress | 5 | ✅ |
| #33 | T-23 · Manual de usuario | 3 | ✅ |
| #34 | T-24 · Manual técnico | 3 | ✅ |
| #35 | T-25 · Casos de uso | 2 | ✅ |
| #36 | T-26 · Evidencia de pruebas | 2 | ✅ |
| #37 | T-27 · Retroalimentación del profesor | 3 | ✅ |
| #39 | T-29 · Respaldo y recuperación | 3 | ✅ |
| #40 | T-30 · Registro de ceremonias | 2 | ✅ |
| | **Total** | **26** | **26 de 26** |

**El matiz que ya estaba escrito en el acta del Planning se mantiene:** T-21 (3 puntos) ya estaba
terminado el día del Planning. **El trabajo nuevo del compromiso fueron 23 puntos, no 26.**

### 1.2 Se cerró bastante más de lo comprometido

| Issue | Tarea | Puntos | Nota |
|---|---|---|---|
| #29 | T-07 · Fotografías de campo | 5 | ⚠️ **Alcance reducido, no cumplida** |
| #30 | T-08 · Decidir alcance por marca | 3 | Decidida sobre 3 medidores |
| #41 | T-31 · PWA instalable | 3 | |
| #42 | T-32 · Reconocimiento | 5 | Diagnóstico entregado, arreglo diferido |
| #43 | T-33 · Errores del cliente | 1 | |
| #44 | T-34 · `modelo-datos.md` vs. scripts | 3 | |
| #52 | T-35 · Fecha de la lectura | 3 | |
| | **Total** | **23** | |

**T-07 no se puede contar como completada.** Sus criterios —6 tomas por medidor, 3 en condiciones
adversas, zonas repartidas— no se lograron. Se cerró en 3 de 8 medidores porque el equipo decidió
seguir adelante, no porque estuviera hecha.

Si esos 5 puntos se suman a la velocity, **la velocity queda inflada y la próxima planificación
sale mal**. Propongo contarlos aparte.

### 1.3 Seis tarjetas se cerraron sin ningún punto asignado

| Issue | Tarea | Puntos |
|---|---|---|
| #55 | T-36 · Dos datos mal en el documento de la encuesta | *ninguno* |
| #57 | T-37 · `CLAUDE.md` desactualizado | *ninguno* |
| #59 | T-38 · Tres commits de registro recuperados | *ninguno* |
| #65 | T-39 · La lectura se guardaba inflada ×10 o ×100 | *ninguno* |
| #72 | T-40 · El job de despliegue dejaba `main` en rojo | *ninguno* |
| #75 | T-41 · Verificar las cifras del proyecto | *ninguno* |

**Ninguna de las seis tiene etiqueta `puntos:`.** Aparecieron durante el sprint y se cerraron sin
estimar.

Esto no es un detalle administrativo: **T-39 fue el hallazgo más importante del sprint** —el
sistema guardaba la lectura multiplicada por 10 o por 100, y rompía justo la comparación contra la
factura— y en el registro de velocity vale cero.

### 1.4 El número honesto

| | Puntos |
|---|---|
| Comprometido y cumplido | **26** |
| Cerrado fuera del compromiso | **23** |
| — de los cuales, cerrados sin cumplir sus criterios (T-07) | −5 |
| **Trabajo estimado y realmente completado** | **44** |
| Tarjetas cerradas sin estimar | **6 tarjetas, 0 puntos registrados** |
| Abierto al cierre | **5** (#38 T-28) |

Comparado con el Sprint 1 (52 de 60), el Sprint 2 cerró **más trabajo del que comprometió**. Pero
esa comparación **no es confiable** mientras seis tarjetas valgan cero.

> **Comandos para recalcular**
> ```bash
> gh issue list --state all --limit 100 --json number,title,state,labels
> gh pr list --state merged --limit 60 --json number,author,mergedAt,reviews,files
> ```

---

## 2. Seguimiento de las cinco acciones de la retrospectiva del Sprint 1

Esta sección es la que más importa. **Las acciones de una retrospectiva que nadie revisa después
son decoración.**

### Acción 1 — Cada Issue de frontend nombra los endpoints que consume

**Sin evidencia concluyente, y poco aplicable este sprint.**

Solo hubo dos Issues de cliente. #52 (T-35) sí nombra `POST /api/lecturas` con un ejemplo de
petición. #43 (T-33) es una refactorización interna que no consume ningún endpoint nuevo.

No hay con qué juzgarla. **Propongo no darla por cumplida ni por incumplida**, y ver si aplica en
el Sprint 3.

### Acción 2 — Toda funcionalidad que toque base de datos o HTTP lleva una prueba contra la cosa real

**Cumplida.**

- `server/tests/test_integracion_db.py` corre contra PostgreSQL de verdad.
- `client/cypress/e2e/hilo-completo.cy.ts` corre el hilo completo en cada Pull Request.
- El job `e2e` es uno de los cuatro obligatorios para mergear.

Es la única de las cinco que se sostuvo sola, y la razón es que **quedó dentro del pipeline**: no
depende de que alguien se acuerde.

### Acción 3 — Nunca tres ramas en vuelo

**Incumplida, y no por poco.**

Hubo **11 momentos distintos con 3 o más Pull Requests abiertos a la vez**, con un pico de
**cinco**:

| Cuándo | PRs abiertos a la vez | De quién |
|---|---|---|
| 2026-09-01 | #64, #66, #67, #68 | mezclados |
| 2026-09-01 | #68, #69, #70 | los tres de Isaac |
| 2026-09-02 | #76, #77, #78, #79, **#80** | **los cinco de José Pablo** |

**El pico de cinco es mío.** Escribí la acción, soy el Scrum Master, y soy quien más la incumplió.
Queda escrito así.

### Acción 4 — Daily asíncrono y registro semanal

**Incumplida las dos semanas. Y el criterio de fracaso que el equipo escribió por adelantado se
activó.**

El acta del Sprint 2 dice, textual, sobre la semana del 25 al 31 de agosto:

> **No se hizo ningún Daily Scrum esta semana.** Ni presencial ni asíncrono, ningún día.

Y a continuación el equipo cambió el formato a **daily presencial**, dejando escrito por adelantado
qué significaría fallar otra vez:

> Si al cerrar la semana del 1 al 7 de setiembre tampoco hay registro, el problema no es el formato
> sino que el equipo no está haciendo dailies, y eso entra a la retrospectiva del Sprint 2 como
> **hallazgo** — no como una acción más que se vuelve a escribir igual.

**No hay registro de la semana del 1 al 7 de setiembre.** El criterio se cumplió.

Esto es lo importante: **el equipo predijo su propio fallo y acertó.** Se probó «nadie era dueño»
(Sprint 1) y se probó «el formato no encaja» (Sprint 2). Ninguna de las dos explicaciones alcanzó.

**Propongo dejar de escribir la misma acción por tercera vez** — ver la sección 4.

### Acción 5 — Rotación de revisión de Pull Requests por área

**Incumplida.** Es la más medible de las cinco, y los números son claros:

| Integrante | Pull Requests que escribió | Pull Requests que aprobó |
|---|---|---|
| José Pablo (NieblaVidente) | **24** | 9 |
| Isaac (PipeDevGit) | 7 | **23** |
| Yariel (yariel3199-gif) | **2** | **0** |

**Yariel no aprobó ningún Pull Request en todo el sprint.** No es un reproche: es el dato, y explica
por qué la transferencia de conocimiento que buscaba la acción 5 no ocurrió.

Y la acción pedía que **cada uno** revisara al menos uno de cliente, uno de servidor y uno de base
de datos. **Ninguno de los tres cumplió las tres áreas.**

> **Por qué esto pesa más que las otras cuatro.** Hay una **Defensa Técnica Individual** en
> Sistemas Operativos: a cualquiera de los tres le pueden preguntar por cualquier parte del
> sistema. Revisar el código de otro es la forma más barata de conocerlo. Con 0 y 2 revisiones,
> esa preparación no está pasando.

---

## 3. Hallazgos que propongo llevar a la retrospectiva

Propuestas para discutir, no conclusiones.

### 3.1 El reparto de trabajo empeoró, no mejoró

En el Sprint 1 la brecha fue 22 / 13 / 10 puntos. El acta del Sprint 2 dice que se repartió
6 / 7 / 10 «para vigilarlo en la próxima retrospectiva». **Esta es esa retrospectiva**, y el
resultado en Pull Requests es **24 / 7 / 2**.

Vale la pena preguntarse qué pasó: si fue disponibilidad, si las tarjetas quedaron mal repartidas,
o si el reparto del Planning nunca se sostuvo en la práctica.

### 3.2 Estimar sigue siendo el punto flojo

Seis tarjetas cerradas sin puntos, y del Sprint 1 no se conservó la estimación tarjeta por tarjeta
al migrar de Trello. **Hoy el equipo no puede planificar por velocity porque no tiene una serie
confiable.**

Esto ya costó algo concreto: en la presentación de release planning varias tarjetas del Sprint 1
tuvieron que ir marcadas como *«sin registro»*.

### 3.3 Tres defectos aparecieron solo al mirar el producto con ojos de usuario

Al escribir el manual de usuario (T-23) aparecieron **tres defectos que ninguna prueba veía**:

| | Qué |
|---|---|
| [#84](https://github.com/NieblaVidente/mimedidor/issues/84) | **La aplicación corre sin hojas de estilo.** Nadie importa `App.css`. La guía de encuadre que la pantalla te dice que uses **no existe** |
| [#85](https://github.com/NieblaVidente/mimedidor/issues/85) | **La prueba end-to-end falla por zona horaria.** En CI pasa (todo en UTC); en una máquina en Costa Rica después de las 18:00, falla |
| [#86](https://github.com/NieblaVidente/mimedidor/issues/86) | El rótulo «Lectura (m³)» nombra mal lo que hay que escribir |

Los tres estaban en `main`, con los cuatro checks en verde.

**#84 es el que más incomoda:** la guía de encuadre existía para mejorar la foto de entrada y
reducirle trabajo al reconocimiento. **Nunca funcionó.** Ninguna de las fotos de campo se tomó con
ella, y el reconocimiento se midió sobre fotos tomadas sin la ayuda que se suponía que existía.

### 3.4 Lo que sí funcionó, y conviene no perderlo

- **El compromiso se cumplió entero**, algo que no pasó en el Sprint 1.
- **Cerrar tarjetas sin maquillarlas.** T-07 cerró como alcance reducido, T-32 entregó diagnóstico
  sin arreglo, el reconocimiento se reporta como 0 de 5. Nada se marcó como hecho sin estarlo.
- **La acción 2 se sostuvo porque vive en el pipeline.** Es el patrón a copiar: las acciones que
  dependen de la memoria se caen; las que quedan dentro de una herramienta, no.

---

## 4. Acciones que propongo para el Sprint 3

**Tres, no cinco.** De las cinco del Sprint 1, tres se incumplieron. Escribir más no mejora nada.

El criterio: **una acción solo entra si se puede verificar sin depender de que alguien se acuerde.**

| # | Acción propuesta | Cómo se verifica | Responsable |
|---|---|---|---|
| **A** | **Ningún Issue se cierra sin etiqueta `puntos:`.** Si aparece a mitad del sprint, se estima entre los tres antes de empezarla | `gh issue list --state closed` y contar cuántas quedaron sin etiqueta. Verificable en 10 segundos | Los tres |
| **B** | **Cada integrante aprueba al menos 3 Pull Requests, y al menos uno tiene que ser de código** (no de documentación) | `gh pr list --json reviews`. Los números de este documento se recalculan igual | Los tres |
| **C** | **Se elimina el Daily Scrum como ceremonia con registro escrito.** Se reemplaza por un repaso del tablero de 10 minutos **al inicio de cada clase presencial en que coincidan los tres**, anotado en una sola línea en el acta del sprint | Que el acta del Sprint 3 tenga esas líneas con fecha | José Pablo |

### Por qué la acción C, y no «esta vez sí hacemos dailies»

Se intentó dos veces con dos formatos distintos y se cayó las dos. **Insistir por tercera vez es la
definición de no aprender de la retrospectiva.**

Lo que el profesor evalúa es **el registro fechado de las ceremonias**, no que se llamen «Daily
Scrum» ni que sean diarias. Un repaso corto anclado a algo que ya ocurre —la clase presencial— tiene
posibilidad real de sostenerse. Un daily diario para tres personas que se ven en clase, ya se
demostró dos veces que no.

**Esto hay que discutirlo.** Es un cambio a una ceremonia de Scrum y no lo debería decidir una
persona sola.

---

## 5. Lo urgente: la entrega de la semana 10 es mañana

⚠️ **Antes de planificar el Sprint 3 hay que resolver esto.**

El hito «Semana 10 — Segundo avance» vence el **7 de setiembre**, o sea mañana.

**El contenido está en el repositorio:**

| Qué pide | Dónde está |
|---|---|
| MVP con más funciones estables | `main`, con el hilo completo funcionando y 4 checks en verde |
| Manual de usuario | `docs/manual-usuario.md` ✅ mergeado hoy |
| Casos de uso | `docs/casos-de-uso.md` ✅ |
| Evidencia de pruebas | `docs/evidencia-pruebas.md` ✅ |
| Manual técnico | `docs/manual-tecnico-instalacion.md` ✅ |

**Lo que no está claro es el formato de entrega.** En `entregas/` solo hay documentos del **27 de
agosto** (semana 7): los dos PDF en formato IEEE. No hay nada armado para la semana 10.

**Pregunta abierta, y es la más urgente de todo este documento:** ¿la semana 10 se entrega como la
semana 7 —documentos IEEE en PDF— o alcanza con el repositorio? Nadie lo tiene anotado.

Además, si hay que regenerar documentos: **los de la semana 7 tienen cifras que después se
corrigieron** en T-41 (el agua no contabilizada se atribuía a ARESEP siendo de la Contraloría, y el
precio del hardware decía 150–430 dólares en vez de 269–624). Regenerarlos sin corregir eso sería
entregar dos veces un dato que ya sabemos que está mal.

---

## 6. Propuesta de Sprint 3

**Del 8 al 21 de setiembre. Termina el día de la feria.** Es el último sprint: lo que no entre acá,
no existe.

### 6.1 Objetivo propuesto

> **Que el proyecto se pueda demostrar en vivo el día de la feria sin depender de que arranque la
> laptop de alguien, y que cada integrante pueda defender cualquier parte del sistema.**

No agrega funcionalidad nueva a propósito. **Las dos cosas que faltan no son código:** un ambiente
donde correrlo, y tres personas preparadas para que las pregunten.

### 6.2 Tarjetas que ya existen

| Issue | Tarea | Puntos | Estado |
|---|---|---|---|
| [#38](https://github.com/NieblaVidente/mimedidor/issues/38) | T-28 · Pipeline de entrega continua | 5 | Reabierta. Falta servidor, secretos y reversión |
| [#84](https://github.com/NieblaVidente/mimedidor/issues/84) | T-42 · La aplicación corre sin hojas de estilo | 2 | Nueva |
| [#85](https://github.com/NieblaVidente/mimedidor/issues/85) | T-43 · La prueba e2e falla por zona horaria | 2 | Nueva |
| [#86](https://github.com/NieblaVidente/mimedidor/issues/86) | T-44 · El rótulo «Lectura (m³)» nombra mal | 1 | Nueva |
| | **Subtotal** | **10** | |

### 6.3 Tarjetas que hay que crear

> **⚠️ Los puntos de esta tabla son una propuesta mía, no una estimación del equipo.** Ninguno está
> registrado. **Se estiman entre los tres en el Planning**, y ahí pueden cambiar.
>
> Lo digo explícito porque el problema 3.2 de este mismo documento es justamente que estimamos mal
> y tarde. No quiero repetirlo poniendo números míos como si fueran del equipo.

| Propuesta | Qué es | Puntos sugeridos |
|---|---|---|
| **T-45** | **Preparar y ensayar la demostración de la feria.** Qué se muestra, en qué orden, quién habla. Ensayarla completa al menos una vez, cronometrada | 5 |
| **T-46** | **Decidir y escribir el guion frente al 0 de 5.** El reconocimiento no acierta. Hay que decidir si se muestra fallando y se explica, o si se muestra el flujo con corrección manual. Esconderlo no es opción: el profesor pregunta | 2 |
| **T-47** | **Material de presentación para la feria** (afiche, diapositivas o lo que el profesor indique) | 3 |
| **T-48** | **Preparar la Defensa Técnica Individual.** Que cada uno pueda explicar las tres capas. Concretamente: que Yariel explique base de datos, Isaac el cliente, José Pablo visión por computadora — cada uno el área que menos tocó | 3 |
| **T-49** | **Registrar el Sprint Review y la Retrospectiva del Sprint 2** | 2 |
| **T-50** | **Cubrir el camino con trabajador de servicio en la prueba end-to-end.** Riesgo 13.4 de `CLAUDE.md`: hoy no tiene cobertura automatizada | 3 |
| **T-51** | **Corregir el formulario de la encuesta.** La pregunta filtro no corta el cuestionario, y por eso hubo que descartar el 51,5 % de las respuestas | 1 |
| | **Subtotal** | **19** |

### 6.4 El problema de capacidad, dicho de frente

| | Puntos |
|---|---|
| Tarjetas existentes | 10 |
| Tarjetas nuevas propuestas | 19 |
| **Total** | **29** |

La velocity observada está entre 23 y 30 puntos por sprint de dos semanas. **29 cabe justo en el
límite superior, y eso es exactamente cómo se sobrecompromete un equipo.**

Además hay dos cosas que este número no incluye:

1. **Los 4 proyectos de C++ de Sistemas Operativos** siguen corriendo en paralelo.
2. **Si la semana 10 exige documentos IEEE** (sección 5), eso es trabajo adicional que todavía no
   está estimado.

**Mi recomendación:** comprometer las de la sección 6.2 más T-45, T-46, T-49 y T-48 —lo que
sostiene la feria y la defensa— y dejar T-47, T-50 y T-51 fuera del compromiso, para tomarlas si
sobra capacidad.

### 6.5 Riesgos del Sprint 3

| Riesgo | Por qué |
|---|---|
| **El servidor no se contrata a tiempo** | T-28 no cierra sin él, y la demostración de la feria depende de que exista. Es la cadena más larga y la que no depende de programar |
| **La rúbrica de Señales y Sistemas sigue sin publicar** | Riesgo 13.1, abierto desde el Sprint 1 |
| **La Defensa Técnica Individual llega sin preparación** | Con 0 y 2 revisiones de Pull Requests en el sprint, hoy no está pasando la transferencia de conocimiento |
| **La fecha es dura** | 21 de setiembre. No hay sprint siguiente donde arrastrar nada |

---

## 7. Lo que necesito que me respondan

Contesten acá en el Pull Request, aunque sea en una línea. Si algo no lo comparten, mejor discutirlo
antes de la reunión que en la reunión.

1. **¿Los datos de la sección 1 y 2 les cuadran?** Si algún número está mal, díganlo — están
   sacados del tablero, pero pude interpretar algo torcido.

2. **Sección 5, la más urgente: ¿cómo se entrega la semana 10?** ¿Documentos IEEE en PDF como la
   semana 7, o alcanza con el repositorio? ¿Alguno tiene el enunciado a mano?

3. **¿Están de acuerdo con eliminar el Daily Scrum como ceremonia diaria** y reemplazarlo por el
   repaso de tablero de la acción C? Es un cambio de ceremonia y necesita los tres.

4. **Yariel: ¿qué haría falta para que puedas revisar Pull Requests?** No es reclamo. Si el
   problema es tiempo, herramienta o que no sabés por dónde empezar a revisar código de otro,
   decilo y lo acomodamos — la acción B depende de eso.

5. **¿Quién contrata el servidor, y cuándo?** Sin eso T-28 no cierra y la demostración de la feria
   depende de una laptop.

6. **Del objetivo del Sprint 3 (sección 6.1): ¿lo comparten?** Propone no agregar funcionalidad
   nueva y dedicar el último sprint a poder demostrar y defender lo que ya existe.

7. **¿Alguna tarjeta que falte en la sección 6.3?** Es la última oportunidad de que algo entre al
   proyecto.
