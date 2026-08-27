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

### Pendiente de entrada externa

La **retroalimentación del profesor** sobre el avance de la semana 7 todavía no se ha recibido; la
entrega se aplazó a esta semana presencial. Es entrada obligatoria del Issue #37, porque el
entregable de la semana 10 exige evidencia de haberla atendido. Cuando llegue, tiene prioridad
máxima aunque obligue a recortar otra cosa.
