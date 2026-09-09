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

| Integrante | Issues | Puntos |
|---|---|---|
| Yariel | #33 Manual de usuario (3) · #34 Manual técnico (3) | 6 |
| Isaac | #35 Casos de uso (2) · #36 Evidencia de pruebas (2) · #39 Respaldo y recuperación (3) | 7 |
| José Pablo | #32 Cypress end-to-end (5) · #37 Retroalimentación (3) · #40 Registro de ceremonias (2) | 10 |

#37 está asignado **para triaje, no para ejecutar**: el trabajo todavía no se conoce porque
depende de la retroalimentación del profesor. Cuando llegue se reparte entre los tres.

#31 (T-21, 3 puntos) no aparece en el reparto porque ya estaba cerrado el día del Planning.

**Cómo se repartió, y por qué así.** En el Sprint 1 los tres trabajaron en silos bastante
marcados: Yariel solo tocó visión por computadora, Isaac solo base de datos, y José Pablo el
resto — infraestructura, API y cliente. Eso contradice lo que advierte `CLAUDE.md` §2 y es un
riesgo directo para la Defensa Técnica Individual, donde a cualquiera le pueden preguntar por
cualquier parte del sistema.

La acción 5 de la retrospectiva pedía cruzar áreas. Este sprint lo hace fácil: **ocho de las
nueve tareas comprometidas son documentación**, porque es lo que exige el entregable de la
semana 10. Y escribir documentación es la mejor excusa para tener que entender algo — el manual
técnico obliga a recorrer instalación, base de datos y API; los casos de uso obligan a recorrer
el cliente. Se cruza sin frenar trabajo técnico.

Por eso Yariel, que venía solo de visión, toma los dos manuales; e Isaac, que venía solo de base
de datos, toma casos de uso y evidencia de pruebas además del respaldo, que sí es su área.

**La otra mitad de la acción 5 es quién revisa.** Cada Pull Request lo revisa quien sí conoce el
área que documenta: la parte de base de datos del manual técnico la revisa Isaac, la del cliente
la revisa José Pablo. Ahí es donde se transfiere el conocimiento de verdad, y no cuesta tiempo
extra.

**Sobre el reparto de carga.** En el Sprint 1 José Pablo hizo 22 puntos contra 13 de Yariel y 10
de Isaac — el doble. Este reparto (6 / 7 / 10) sigue cargándolo más, pero mucho menos, y los 3
puntos de #37 son de triaje, no de trabajo cierto. Queda anotado para vigilarlo en la próxima
retrospectiva.

#### Reasignación a mitad de sprint — 2026-08-29

Al cerrar la entrega de la semana 7, siete de las nueve tareas comprometidas estaban hechas. Se
repartió lo que quedaba vivo, más dos tarjetas que no venían del compromiso.

| Issue | Tarea | Puntos | Quién | Área |
|---|---|---|---|---|
| #29 | T-07 · Recolectar fotografías de campo | 5 | los tres | campo |
| #52 | T-35 · Fecha de la lectura | 3 | Isaac | cliente + servidor |
| #43 | T-33 · Unificar el manejo de errores del cliente | 1 | Yariel | cliente |
| #34 | T-24 · Manual técnico del repositorio | 3 | Yariel | documentación |
| #33 | T-23 · Manual de usuario | 3 | José Pablo ⚠️ | documentación |
| #40 | T-30 · Registrar las ceremonias | 2 | José Pablo | documentación |

**T-35 va a Isaac** y no a quien ya conoce el cliente. Es la única tarjeta del backlog que toca
cliente y servidor a la vez, que son sus dos áreas en blanco: contando los commits de `main`,
Isaac nunca había tocado `client/` ni `server/`, y Yariel nunca `client/` ni `database/`. La parte
de validación en la tabla cae en su terreno conocido, así que no arranca de cero. Por la misma
razón Yariel toma T-33, que es cliente puro y de 1 punto.

> ⚠️ **T-23 pasó de Yariel a José Pablo, y esa decisión se revirtió.** Se había tomado sin ver el
> razonamiento del Planning que está más arriba, porque vivía en una rama sin mergear. Allí los dos
> manuales se le daban a Yariel **a propósito**, con revisores asignados por área para que la
> transferencia de conocimiento ocurriera en la revisión y no solo en la escritura. Ese mecanismo
> es mejor que el criterio de «que toque código» con el que se reasignó, porque cruza áreas sin
> frenar trabajo técnico.
>
> **Resuelto el 2026-08-31: T-23 (#33) vuelve a Yariel**, restituyendo el reparto del Planning. Para
> entonces Yariel ya había cerrado T-24 (#62) y T-33 (#61), así que tenía capacidad libre y el
> manual de usuario es continuación natural del manual técnico que acababa de escribir. La revisión
> la hace José Pablo, que es quien conoce el cliente — que es la mitad de la acción 5 que la
> reasignación se había saltado.

**Sobre el alcance.** El reparto agrega 9 puntos sobre el compromiso de 26: T-07 (5) y T-33 (1)
estaban en «Fuera del compromiso», y T-35 (3) es posterior al Planning —salió al escribir la
prueba end-to-end de T-22—. Del compromiso original quedaban 8 puntos vivos, así que el trabajo
pendiente real son 17 puntos. Si algo tiene que caerse, el orden es **T-33 primero** (1 punto,
deuda técnica que no bloquea nada) y **T-24 después**, que ya viene reducido. T-07 no se cae: es
el cuello de botella del proyecto entero.

### Salidas de campo (T-07)

**Meta revisada: 6 medidores nuevos, 2 por integrante.** Sumados a los 2 ya registrados, el
dataset quedaría en 8.

Se bajó desde los 12 originales a propósito. Esa cifra se fijó cuando había dos semanas por
delante y no había llovido; el Sprint 1 cerró con 2. Comprometer una meta que se pueda cumplir
vale más que fallar la misma meta dos sprints seguidos, y 8 medidores ya permiten aplicar el
criterio de alcance por marca de T-08 con algo de sentido.

**Zonas: cada integrante sale en su propia provincia.** Los tres viven en provincias distintas,
así que no hay riesgo de pisarse ni de duplicar medidores.

Esto además mejora la muestra más de lo que parece. El protocolo de captura pedía repartir zonas
"para no sesgar la muestra hacia un solo barrio": tres provincias distintas dan variedad real de
marcas de hidrómetro, de antigüedad de instalación y de condiciones de la caja — que es
justamente lo que necesita la decisión de T-08 para no acotar el MVP sobre una muestra
engañosa.

**Fechas: sin fecha fija.** Cada quien sale entre semana cuando pueda.

> ⚠️ **Riesgo aceptado explícitamente.** La retrospectiva de este mismo día concluyó que el 2 de
> 12 del Sprint 1 no se explica solo por la lluvia: la tarea nunca tuvo fecha ni dueño por zona,
> y "cuando se pueda" no genera urgencia. El equipo decidió igualmente no fijar fechas, por la
> carga de los 4 proyectos de C++ en paralelo. Queda anotado igual que el riesgo de la revisión
> de PRs sin rotación fija en `docs/definition-of-done.md`: si se nota que no avanza, se revisa.
>
> **Mitigación acordada sin costo extra:** el daily asíncrono de la acción 4 sirve como señal
> temprana. Si pasan varios días sin que nadie reporte una salida, se detecta a mitad de sprint
> y no al cerrarlo.

**Recordatorio operativo:** lo que hace útil una foto es la lectura real transcrita a mano en el
momento de tomarla. Sin ese dato la foto no sirve para medir exactitud, que es el propósito
completo de la tarea.

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

---

## Daily Scrum — registro semanal

La acción 4 de la retrospectiva del Sprint 1 comprometió un «daily asíncrono de tres líneas
(ayer / hoy / bloqueos) y registro semanal en `docs/scrum/`», con el Scrum Master como responsable
y frecuencia diaria.

### Semana del 25 al 31 de agosto

**No se hizo ningún Daily Scrum esta semana.** Ni presencial ni asíncrono, ningún día. El equipo
estuvo en clases presenciales y la ceremonia simplemente no se convocó.

Queda escrito así, sin adornarlo. Un registro inventado no sirve para la Defensa Técnica Individual
y el profesor lo nota; un incumplimiento anotado con su fecha sí es evidencia de que el equipo se
audita.

#### Qué sí avanzó, según el historial del repositorio

Que no hubiera ceremonia no significa que no hubiera trabajo. Esto no es un daily reconstruido a
posteriori —nadie reportó nada en su momento— sino lo que `git` y los Issues registran por su
cuenta:

| Integrante | PR mergeados | Qué cerró |
|---|---|---|
| José Pablo | 9 | T-21 integración, T-22 Cypress, migración a Issues, registro de ceremonias del Sprint 1 y del Planning, T-27, T-36, T-37, T-38 |
| Isaac | 4 | T-29 respaldo y recuperación, T-25 casos de uso, T-26 evidencia de pruebas, encuesta de viabilidad |
| Yariel | 2 | T-33 errores del cliente, T-24 manual técnico de instalación |

Once Issues cerrados en la ventana. El sprint avanzó **a pesar** de no tener daily, no gracias a él.

#### Lectura honesta

El daily no se cayó por falta de trabajo ni por desorganización: se cayó porque **el formato
elegido no encaja con cómo trabaja este equipo**. Se acordó un daily asíncrono por chat para un
grupo que se ve en persona varias veces por semana en clase. Escribir tres líneas por chat a
alguien que uno va a ver esa misma mañana no tiene sentido práctico, y por eso no ocurrió ni una
vez.

La retrospectiva del Sprint 1 concluyó que el registro de ceremonias se había caído porque **nadie
era dueño de la tarea**. Se nombró dueño y aun así se cayó. La causa, entonces, no era solo la
falta de dueño: era también el formato. Repetir la acción 4 sin cambiarla la haría fallar otra vez.

#### Decisión: se cambia el formato, no el compromiso

| | Antes (acción 4) | Desde ahora |
|---|---|---|
| Cuándo | Diario, asíncrono por chat | Presencial, al inicio de la clase en que coincidan los tres |
| Qué | Ayer / hoy / bloqueos, por escrito | Ayer / hoy / bloqueos, hablado |
| Registro | Semanal en `docs/scrum/` | Igual: semanal acá, y es lo único que se versiona |
| Responsable | Scrum Master | Scrum Master (José Pablo), sin cambio |

Se conserva lo que el profesor evalúa —el registro fechado y semanal— y se cambia el ritual que lo
alimenta, para que sea uno que el equipo vaya a sostener de verdad.

> **Criterio de fracaso, escrito por adelantado.** Si al cerrar la semana del 1 al 7 de setiembre
> tampoco hay registro, el problema no es el formato sino que el equipo no está haciendo dailies, y
> eso entra a la retrospectiva del Sprint 2 como hallazgo — no como una acción más que se vuelve a
> escribir igual.

#### Estado del sprint al 31 de agosto

Quedan **7 días** (cierra el 7 de setiembre) y estas tarjetas vivas:

| Issue | Tarea | Puntos | Quién |
|---|---|---|---|
| #29 | T-07 · Recolectar fotografías de campo | 5 | los tres |
| #52 | T-35 · Fecha de la lectura | 3 | Isaac |
| #33 | T-23 · Manual de usuario | 3 | Yariel |
| #40 | T-30 · Registrar las ceremonias | 2 | José Pablo — se cierra con este registro |

**El bloqueo real del sprint es T-07.** Va en 2 medidores de los 8 de la meta revisada, y detrás de
él están parados T-08 (#30) y T-32 (#42). Es lo único de esta lista que no se resuelve programando,
y la mitigación que se había acordado para vigilarlo era justamente el daily que no ocurrió.


---

## Decisión de alcance — 2026-09-06

**Acordada por los tres**, un día antes del cierre del sprint.

### Se cierra la recolección de fotografías de campo en 3 medidores

La meta fue 12 en el Sprint 1, con 2 cumplidos. Se revisó a 8 en el Sprint 2, con 3 cumplidos.
**Dos metas distintas y el mismo resultado**, así que el problema no era el número.

En vez de arrastrar T-07 a un tercer sprint con la feria encima, el equipo decide quedarse con
las 3 unidades y seguir adelante.

### Qué se cierra y cómo

| Tarjeta | Cómo se cierra |
|---|---|
| **T-07** (#29) | **Alcance reducido**, no cumplida. 3 de 8, con el número real a la vista |
| **T-08** (#30) | **Decidida sobre la muestra que existe**: el MVP no se acota por marca |
| **T-32** (#42) | **Diagnóstico entregado**, arreglo diferido con su justificación |

Ninguna se marca como cumplida si no lo está. T-07 tenía criterios —6 tomas por medidor, 3 en
condiciones adversas, zonas repartidas— que no se lograron, y eso queda escrito.

### Lo que el equipo asume al decidir esto

- **El reconocimiento se queda en 0 de 5** hasta la feria. La demostración va a mostrar el flujo
  con corrección manual, y hay que decirlo en vez de esquivarlo.
- **El MVP no queda acotado a ninguna marca**, porque la muestra no permite aplicar el criterio.
- **El riesgo de fragmentación del parque** (`CLAUDE.md` §13.2) pasa de hipótesis a observación:
  tres unidades, tres situaciones de marca distintas.

### Por qué se registra así

Cerrar T-07 como «Hecho» habría dado un tablero más limpio y un registro falso. El número real
—3 de 8, con dos metas fallidas— es el dato que la retrospectiva necesita para entender por qué
esta tarea no avanzó en dos sprints, y esa conversación vale más que la tarjeta.


---

# Sprint Review — 2026-09-08

**Modalidad:** videollamada.
**Asistentes:** José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún
Moreira. Los tres presentes.

Se hizo **antes** de la Retrospectiva, en el orden que fija `CLAUDE.md` §10.

> **Nota sobre la fecha.** El sprint cerraba el 7 de setiembre y las ceremonias se hicieron el 8,
> un día después. Queda anotado en vez de corregido hacia atrás.

## El incremento que se revisó

Lo que estaba en `main` al cierre del sprint:

| Qué | Estado |
|---|---|
| Hilo completo foto → lectura → historial → factura → comparación | Funcionando, con los cuatro verificadores del CI en verde |
| Conversión de la lectura a volumen real (T-39) | Corregida. Antes se guardaba la cadena del odómetro como si fuera m³ |
| Fecha de la lectura editable y validada (T-35) | Hecha |
| PWA instalable en un teléfono real | Comprobada, con evidencia en `docs/evidencia/pwa-instalable-t31.md` |
| Manual de usuario | `docs/manual-usuario.md`, con capturas de las tres pantallas |
| Manual técnico, casos de uso, evidencia de pruebas | Entregados |
| Respaldo y recuperación | `database/scripts/respaldar.sh` y `restaurar.sh`, documentados |

## Lo que se dijo que NO está

Queda registrado acá porque es lo que el equipo va a tener que decir en la feria:

- **El reconocimiento automático acierta 0 de 5** sobre el dataset de campo. No cambió durante el
  sprint y no va a cambiar antes de la feria.
- **No hay entrega continua.** El pipeline valida pero no despliega, porque no hay servidor
  contratado (#38 quedó abierta).
- **El dataset de campo se cerró en 3 medidores** de los 8 de la meta revisada.

---

# Sprint Retrospective — 2026-09-08

**Modalidad:** videollamada, a continuación del Review.
**Asistentes:** los tres.

El material se preparó de antemano en
[`propuesta-cierre-sprint-2-y-sprint-3.md`](propuesta-cierre-sprint-2-y-sprint-3.md) y se revisó
en el Pull Request #87, que **los tres aprobaron**.

## Los números del sprint

| | Puntos |
|---|---|
| Comprometido y cumplido | **26 de 26** |
| Cerrado fuera del compromiso | 23 |
| — descontando T-07, cerrada como alcance reducido y no cumplida | −5 |
| **Trabajo estimado y realmente completado** | **44** |
| Tarjetas cerradas **sin ninguna estimación** | **6 tarjetas, 0 puntos registrados** |
| Abierto al cierre | 5 (#38, T-28) |

**El compromiso se cumplió entero**, cosa que no pasó en el Sprint 1 (52 de 60).

Dos matices que el equipo acordó dejar escritos:

1. **T-21 (3 pts) ya estaba terminado el día del Planning.** El trabajo nuevo del compromiso fueron
   23 puntos.
2. **T-07 no se cuenta como completada.** Cerró en 3 de 8 medidores porque el equipo decidió seguir
   adelante, no porque estuviera hecha. Sumar sus 5 puntos a la velocity la inflaría.

## Seguimiento de las cinco acciones del Sprint 1

| # | Acción | Resultado |
|---|---|---|
| 1 | Los Issues de frontend nombran los endpoints que consumen | **Sin evidencia concluyente.** Solo hubo dos Issues de cliente: #52 sí los nombra, #43 no los necesitaba |
| 2 | Prueba contra la cosa real en todo lo que toque base de datos o HTTP | ✅ **Cumplida** |
| 3 | Nunca tres ramas en vuelo | ❌ **Incumplida** |
| 4 | Daily asíncrono con registro semanal | ❌ **Incumplida las dos semanas** |
| 5 | Rotación de revisión de Pull Requests por área | ❌ **Incumplida** |

### Por qué la acción 2 sobrevivió y las otras no

Es la conclusión central de esta retrospectiva. La acción 2 **quedó dentro del pipeline**: el job
`e2e` es obligatorio para mergear, así que no depende de que nadie se acuerde. Las otras cuatro
dependían de memoria y disciplina, y se cayeron.

### Acción 3 — el detalle, porque señala al Scrum Master

Hubo **11 momentos distintos con 3 o más Pull Requests abiertos a la vez**, con un pico de **cinco**
el 2026-09-02: #76, #77, #78, #79 y #80.

**Los cinco eran de José Pablo**, que es quien escribió la acción y quien facilita las ceremonias.
Queda escrito así.

### Acción 4 — el criterio de fracaso escrito por adelantado se activó

En el registro de la semana del 25 al 31 de agosto el equipo dejó por escrito, *antes* de que
ocurriera:

> Si al cerrar la semana del 1 al 7 de setiembre tampoco hay registro, el problema no es el formato
> sino que el equipo no está haciendo dailies, y eso entra a la retrospectiva del Sprint 2 como
> **hallazgo** — no como una acción más que se vuelve a escribir igual.

**No hubo registro de esa semana.** El equipo predijo su propio fallo y acertó.

Se probaron dos explicaciones y ninguna alcanzó: en el Sprint 1 se concluyó que «nadie era dueño» y
se nombró dueño; en el Sprint 2 se concluyó que «el formato no encaja» y se cambió el formato. Falló
las dos veces.

### Acción 5 — la que más pesa

| Integrante | Pull Requests que escribió | Pull Requests que aprobó |
|---|---|---|
| José Pablo | **24** | 9 |
| Isaac | 7 | **23** |
| Yariel | **2** | **0** |

**Ninguno de los tres cubrió las tres áreas.** Yariel no aprobó ningún Pull Request en todo el
sprint.

Pesa más que las otras cuatro porque hay una **Defensa Técnica Individual** en Sistemas Operativos
(8 %): a cualquiera le pueden preguntar por cualquier parte del sistema. Revisar el código de otro
es la forma más barata de conocerlo, y con 0 y 2 revisiones esa preparación no está pasando.

## Hallazgos

1. **El reparto de trabajo empeoró.** Sprint 1: 22 / 13 / 10 puntos. Sprint 2 en Pull Requests:
   **24 / 7 / 2**. El acta del Planning decía «queda anotado para vigilarlo en la próxima
   retrospectiva» — esta es esa retrospectiva, y la brecha creció.
2. **Estimar sigue siendo el punto flojo.** Seis tarjetas cerradas sin puntos, entre ellas T-39, que
   fue el hallazgo más importante del sprint y en el registro de velocity **vale cero**. El equipo
   hoy no puede planificar por velocity porque no tiene una serie confiable.
3. **Tres defectos aparecieron solo al mirar el producto con ojos de usuario**, al escribir el
   manual (#84, #85, #86). Los tres estaban en `main` con los cuatro verificadores en verde. El más
   incómodo es #84: la guía de encuadre que la pantalla dice que uses **nunca funcionó**, y el
   reconocimiento se midió sobre fotos tomadas sin la ayuda que se suponía que existía.
4. **Lo que funcionó y no hay que perder:** el compromiso se cumplió entero, y **ninguna tarjeta se
   marcó como hecha sin estarlo** — T-07 cerró como alcance reducido, T-32 entregó diagnóstico sin
   arreglo, y el reconocimiento se reporta como 0 de 5.

## Acciones acordadas para el Sprint 3

**Tres, no cinco.** De las cinco anteriores, tres se incumplieron; escribir más no mejora nada.

El criterio que el equipo adoptó: **una acción solo entra si se puede verificar sin depender de que
alguien se acuerde** — que es la lección de por qué la acción 2 sobrevivió.

**Las tres se aprobaron tal cual, sin cambios.**

| # | Acción | Cómo se verifica | Responsable |
|---|---|---|---|
| **A** | Ningún Issue se cierra sin etiqueta `puntos:`. Si aparece a mitad del sprint, se estima entre los tres antes de empezarla | `gh issue list --state closed` y contar los que quedaron sin etiqueta | Los tres |
| **B** | Cada integrante aprueba al menos 3 Pull Requests, y al menos uno tiene que ser de código, no de documentación | `gh pr list --json reviews` | Los tres |
| **C** | **Se elimina el Daily Scrum como ceremonia con registro escrito.** Se reemplaza por un repaso del tablero de 10 minutos al inicio de cada clase presencial en que coincidan los tres, anotado en una línea en el acta del sprint | Que el acta del Sprint 3 tenga esas líneas con fecha | José Pablo |

### Sobre la acción C

Es un cambio a una ceremonia de Scrum y por eso se decidió entre los tres, no por el Scrum Master
solo.

La razón: se intentó dos veces con dos formatos distintos y se cayó las dos. **Insistir por tercera
vez sería no aprender de la retrospectiva.** Lo que el profesor de ISW2 evalúa es el registro fechado
de las ceremonias, no que se llamen «Daily Scrum» ni que sean diarias. Un repaso corto anclado a algo
que ya ocurre —la clase presencial— tiene posibilidad real de sostenerse.

**`CLAUDE.md` §10 queda desactualizado por esta decisión** y se corrige en el mismo Pull Request que
este registro.
