# Registro de ceremonias — Sprint 3

**Del 8 al 21 de setiembre de 2026.** Es el último sprint y **cierra el día de la feria**: lo que
no entre acá, no existe.

---

## ⚠️ No hubo Sprint Planning

**El sprint arrancó sin ceremonia de Planning.** El reparto de tarjetas se acordó **por chat**, y el
trabajo empezó el 8 de setiembre.

Queda escrito así, sin adornarlo, por el mismo criterio que se aplicó a los dailies del Sprint 2:
un incumplimiento anotado con su fecha es evidencia de que el equipo se audita; un acta inventada
no sirve para nada y el profesor lo nota.

**Es un hallazgo para la retrospectiva del Sprint 3**, y tiene un agravante: se decidió el mismo día
en que se aprobaron tres acciones sobre rigor de proceso. La primera ceremonia posterior a esa
retrospectiva no se hizo.

### Qué sí se acordó, y dónde

El contenido que habría ido a un Planning estaba preparado en
[`propuesta-cierre-sprint-2-y-sprint-3.md`](propuesta-cierre-sprint-2-y-sprint-3.md), revisado y
aprobado por los tres en el Pull Request #87.

Lo que **no** ocurrió es la ceremonia: no hubo estimación conjunta, ni discusión de capacidad, ni
decisión explícita de qué entra al compromiso y qué queda fuera.

---

## Objetivo del sprint

Tomado de la propuesta aprobada en #87. **No fue ratificado en una ceremonia de Planning**, así que
conviene confirmarlo entre los tres antes de seguir:

> **Que el proyecto se pueda demostrar en vivo el día de la feria sin depender de que arranque la
> laptop de alguien, y que cada integrante pueda defender cualquier parte del sistema.**

No agrega funcionalidad nueva a propósito: las dos cosas que faltan no son código, sino un ambiente
donde correrlo y tres personas preparadas para que las pregunten.

---

## Backlog y reparto

Milestone *Semana 12 — Presentación final (Feria)*.

> **Los puntos son una estimación provisional del Scrum Master**, puesta para poder repartir. **No
> fueron estimados por los tres**, que es justamente lo que pide la acción A. Cada tarjeta lo dice
> en su encabezado.

| Issue | Tarea | Puntos | Quién |
|---|---|---|---|
| #38 | T-28 · Pipeline de entrega continua | 5 | José Pablo |
| #88 | T-45 · Preparar y ensayar la demostración de la feria | 5 | José Pablo |
| #92 | T-49 · Registrar el Sprint Review y la Retrospectiva | 2 | José Pablo |
| #84 | T-42 · La aplicación corre sin hojas de estilo | 2 | Yariel |
| #86 | T-44 · El rótulo «Lectura (m³)» nombra mal el campo | 1 | Yariel |
| #95 | T-52 · Pasada visual mínima para la feria | 2 | Yariel |
| #85 | T-43 · La prueba e2e falla por zona horaria | 2 | Isaac ✅ |
| #94 | T-51 · Corregir el formulario de la encuesta | 1 | Isaac ✅ |
| #89 | T-46 · Guion frente al 0 de 5 del reconocimiento | 2 | los tres |
| #91 | T-48 · Preparar la Defensa Técnica Individual | 3 | los tres |
| #90 | T-47 · Material de presentación para la feria | 3 | **sin asignar** |
| #93 | T-50 · Trabajador de servicio en la prueba e2e | 3 | **sin asignar** |

**#90 está sin asignar a propósito:** nadie confirmó qué formato pide el profesor, y diseñar antes
de saberlo es trabajo tirado.

---

## Trabajo ya cerrado en este sprint

| Cuándo | Qué |
|---|---|
| 2026-09-09 | **#85 (T-43)** · La prueba end-to-end deja de depender de que dos relojes coincidan — Isaac |
| 2026-09-09 | **#94 (T-51)** · La pregunta filtro corta el cuestionario — Isaac |

### Trabajo que entró a `main` sin tarjeta

El Pull Request **#96** —verificar en CI que las migraciones y los scripts de creación produzcan el
mismo esquema— se mergeó **sin cerrar ningún Issue**. Es una mejora útil y bienvenida, pero no está
en el tablero.

Queda anotado acá para que el registro del sprint refleje el trabajo real. **No se crea una tarjeta
retroactiva**, por el mismo criterio con que no se migraron a Issues las 21 tarjetas del Sprint 1:
una tarjeta creada y cerrada el mismo día, después del hecho, falsea la fecha del trabajo.

---

## Repaso del tablero (reemplaza al Daily Scrum)

Acción C de la retrospectiva del Sprint 2: 10 minutos al inicio de cada clase presencial en que
coincidan los tres, anotado acá en una línea con su fecha.

| Fecha | Qué se repasó |
|---|---|
| *(pendiente — el primero que ocurra se anota acá)* | |

---

## Riesgos del sprint

| Riesgo | Por qué |
|---|---|
| **El servidor no se contrata a tiempo** | #38 no cierra sin él, y #88 depende de que exista un ambiente. Es la cadena más larga y la única que no se destraba programando |
| **La Defensa Técnica Individual llega sin preparación** | Vale 8 % y se evalúa persona por persona. Con 0 y 2 revisiones de Pull Requests en el Sprint 2, la transferencia de conocimiento no está pasando |
| **La rúbrica de Señales y Sistemas sigue sin publicar** | Riesgo 13.1, abierto desde el Sprint 1 |
| **La fecha es dura** | 21 de setiembre. No hay sprint siguiente donde arrastrar nada |
| **El reparto arranca desbalanceado** | 13,7 puntos para José Pablo contra 6,7 y 1,7. Es el mismo patrón que la retrospectiva acaba de señalar como hallazgo 1 |
