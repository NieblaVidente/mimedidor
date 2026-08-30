# Registro de ceremonias — Sprint 2

## Sprint Planning — 2026-08-25

**Asistentes:** José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún
Moreira. Los tres presentes, sesión presencial.

Se hizo después del Sprint Review y la Retrospectiva del Sprint 1 (registradas en
[`sprint-1.md`](sprint-1.md)), en ese orden, para que las conclusiones de la retrospectiva
entraran en la planificación y no quedaran como un documento aparte.

### Duración

Del 25 de agosto al 7 de setiembre: **dos semanas**, no tres. El Sprint 1 duró dos semanas
completas; este arranca a mitad de la semana 8 y cierra antes del segundo avance de la semana 10.
Se tuvo en cuenta al decidir cuánto comprometer.

### Objetivo del sprint

> **Que el hilo funcione de verdad de punta a punta, se pueda demostrar en vivo, y esté
> documentado como pide la semana 10.**

La integración se puso por encima de mejorar el reconocimiento a propósito. Un 0 % de exactitud es
un problema conocido, medido y explicado; un hilo sin integrar era de tamaño desconocido — y al
cerrarlo aparecieron dos errores que ninguna prueba veía. Además, la Guía de Entregables pide
explícitamente priorizar que algo funcione de principio a fin antes de agregar funcionalidades.

### Dónde vive el trabajo

Desde este sprint, las tareas son **Issues de este repositorio**, no tarjetas de Trello. El motivo
y qué pasó con el historial del Sprint 1 están en `CLAUDE.md` §9.

### Compromiso: 26 puntos

Etiquetados con `sprint 2: comprometido` y agrupados en el milestone
*Semana 10 — Segundo avance*.

| Issue | Tarea | Puntos |
|---|---|---|
| #31 | T-21 · Conectar cliente y servidor y ejecutar el hilo completo | 3 |
| #32 | T-22 · Prueba end-to-end del hilo completo con Cypress | 5 |
| #33 | T-23 · Manual de usuario | 3 |
| #34 | T-24 · Manual técnico | 3 |
| #35 | T-25 · Casos de uso principales | 2 |
| #36 | T-26 · Consolidar la evidencia de pruebas | 2 |
| #37 | T-27 · Incorporar la retroalimentación del profesor | 3 |
| #39 | T-29 · Implementar la estrategia de respaldo y recuperación | 3 |
| #40 | T-30 · Registrar las ceremonias y sostener el registro | 2 |
| | **Total** | **26** |

**Nota honesta sobre estos 26 puntos.** T-21 (#31) ya estaba terminado el día del Planning: se
cerró esa misma mañana, dentro de la ventana del sprint. O sea que de los 26 comprometidos, **3
venían hechos y el trabajo nuevo son 23**.

El equipo decidió contarlos igual y dejarlo escrito, en vez de agregar otra tarea para que el
número quedara redondo. La razón: acababan de comprometer un sprint más corto, y sumar puntos
para cuadrar una cifra es exactamente como se sobrecompromete un equipo. Al cerrar el sprint hay
que tener presente este matiz para que la velocity no quede inflada.

### Fuera del compromiso

No entran al compromiso, pero quedan en el milestone porque apuntan a la misma entrega. Se toman
solo si sobra capacidad.

| Issue | Tarea | Puntos | Por qué queda fuera |
|---|---|---|---|
| #29 | T-07 · Recolectar fotografías de campo | 5 | Depende del clima, no de la capacidad del equipo |
| #30 | T-08 · Consolidar dataset y decidir alcance por marca | 3 | Bloqueada hasta tener muestra suficiente |
| #38 | T-28 · Pipeline de entrega continua | 5 | Deseable para la rúbrica de ISW2, pero la semana 10 no lo exige |
| #41 | T-31 · PWA real | 3 | Ídem |
| #42 | T-32 · Atacar las líneas divisorias del odómetro | 5 | **Condicionada:** sin más dataset no se puede calibrar ni saber si una mejora generaliza |
| #43 | T-33 · Unificar el manejo de errores del cliente | 1 | Deuda técnica, no bloquea nada |
| #44 | T-34 · Cerrar la diferencia entre `modelo-datos.md` §3 y los scripts | 3 | Deuda técnica |
| | **Total** | **25** | |

### Acciones de la retrospectiva que aplican desde este sprint

Las cinco acciones acordadas están en [`sprint-1.md`](sprint-1.md). Dos entran en vigor de
inmediato en la forma de trabajar:

- Toda funcionalidad que toque base de datos o HTTP lleva al menos una prueba contra la cosa real.
- Se mergea la primera rama aprobada de inmediato; las demás traen `main`. Nunca tres en vuelo.

### Asignación de tareas

<!-- COMPLETAR: quién toma cada Issue.
     Recordar la acción 5 de la retrospectiva: asignar cruzando áreas a propósito, para que cada
     integrante toque cliente, servidor y base de datos durante el sprint. Si se asigna por
     comodidad, la acción queda escrita pero no hecha, y es la que atiende el riesgo de la
     Defensa Técnica Individual. -->

### Salidas de campo (T-07)

<!-- COMPLETAR: zonas, días y responsable de cada salida.
     La retrospectiva concluyó que el 2 de 12 del Sprint 1 no fue solo el clima: la tarea nunca
     tuvo fecha ni dueño por zona. Dejarlo otra vez como "cuando se pueda" repite el problema. -->

### Riesgo principal del sprint

Con la integración cerrada, **el dataset pasa a ser el riesgo principal del proyecto**: 2 de 12
medidores, y es el único que no se resuelve programando. Bloquea la medición del reconocimiento,
la decisión de alcance por marca y la calibración de la segmentación.

### Retroalimentación del profesor sobre el primer avance

**Recibida** en la sesión presencial de la semana 8. Registrada el 2026-08-29 por José Pablo
Ramírez Sánchez (Scrum Master), que fue quien la recibió.

**Qué dijo:** que el proyecto va bien como va. **No dio ninguna observación específica ni pidió
ningún cambio.**

> ⚠️ Este registro es una **paráfrasis**, no una cita textual. El Issue #37 pedía anotar la
> retroalimentación palabra por palabra; la evaluación fue verbal y no se transcribió en el
> momento, así que lo que queda es el resumen de quien la recibió. Se anota la limitación en vez
> de simular una cita que nadie tomó.

**Qué se atiende a raíz de esto:** nada, porque no hubo puntos concretos que atender. No se abren
tarjetas nuevas y no se recorta nada del sprint.

**Riesgo que esto deja abierto.** La Guía de Entregables §3.3 exige para la semana 10 «evidencia
de que se incorporó la retroalimentación recibida en la semana 7». Con una evaluación sin
observaciones, la única evidencia posible es este registro, y es delgada. Conviene **pedirle al
profesor al menos un punto concreto a mejorar** antes de la semana 10 — no para inventar trabajo,
sino porque el entregable exige mostrar algo incorporado y hoy no hay de dónde. Si aun así no hay
observaciones, este registro fechado es la respuesta y se presenta tal cual.

Con esto el Issue #37 queda cerrado. Si el profesor da observaciones más adelante, se abre una
tarjeta nueva enlazada a esta sección en vez de reabrirlo.
