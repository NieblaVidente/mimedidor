# Sprint 2 — Propuesta de planificación

> **Esto es una propuesta, no una decisión.** La escribe el Scrum Master para llevarla al Sprint
> Planning de la semana 8; lo que se comprometa de verdad lo define el equipo en esa ceremonia,
> después del Sprint Review y la Retrospectiva. Los puntos y las prioridades de acá son un punto
> de partida para discutir, no un plan cerrado.

---

## 1. Calendario

| Semana | Fechas | Qué pasa |
|---|---|---|
| 7 | 17–21 ago | Sprint 1 terminado. La entrega se aplazó: la semana fue virtual |
| **8** | **24–28 ago** | **Presencial.** Entrega del avance + retroalimentación del profesor · Sprint Review · Retrospectiva · Sprint Planning |
| 9 | 31 ago – 4 sep | Desarrollo |
| **10** | **7–11 sep** | **Segundo avance de la solución** (entregable de la guía) |

**El Sprint 2 dura efectivamente dos semanas**, no tres: arranca cuando termine el Planning de la
semana 8 y cierra antes de la entrega del 7 de setiembre. Conviene tenerlo presente al
comprometer alcance.

---

## 2. Qué pide la semana 10

De la Guía de Entregables (§3.3), textualmente:

- MVP con más funcionalidades **completas y estables**.
- Documentación ampliada: **manual funcional, casos de uso principales y evidencia de pruebas
  realizadas**.
- **Evidencia de que se incorporó la retroalimentación recibida en la semana 7.**

Y una recomendación de la misma guía (§6) que aplica directo a nuestro caso:

> "Prioricen que algo funcione de principio a fin, aunque sea sencillo, antes de agregar más
> funcionalidades."

---

## 3. Insumos para el Sprint Review y la Retrospectiva

Datos verificados contra el tablero y el repositorio, para no discutir de memoria en la ceremonia.

### 3.1 Velocity real

| | Puntos |
|---|---|
| Completados (21 tarjetas en Hecho) | **52** |
| No completados (T-07 y T-08, siguen en curso) | 8 |
| **Total en el tablero** | **60** |

**52 de 60 = 87 %.** Con un matiz honesto: T-15b (3 puntos) se creó **durante** el sprint, al
descubrir que T-15 mezclaba dos rutas distintas del contrato. O sea que el compromiso original
era menor que 60 y creció a mitad de camino. No hay registro del Sprint Planning para
confirmar la cifra exacta — eso mismo es un hallazgo para la Retrospectiva.

### 3.2 Qué se entregó

Hilo funcional completo: 5 rutas de API, 3 pantallas, 6 tablas normalizadas a 3FN, 2 roles de
mínimo privilegio, 1 procedimiento transaccional, 46 pruebas automatizadas y un pipeline de 3
jobs sobre `main` protegida.

### 3.3 Qué NO se logró

- **El reconocimiento automático acierta 0 de 2** (documentado y analizado en
  `docs/exactitud-reconocimiento.md`).
- **El dataset va en 2 de 12 medidores**, frenado por lluvia.
- **Cliente y servidor nunca se han ejecutado juntos.**
- No hay PWA ni entrega continua.

### 3.4 Material para la Retrospectiva

No son conclusiones — son hechos observados que valen la pena poner sobre la mesa:

1. **Tres tarjetas de frontend descubrieron que su backend no existía.** T-15/T-15b, T-17 y T-18
   asumían rutas que nadie había construido. Se resolvió sobre la marcha cada vez, pero es un
   patrón, no mala suerte.
2. **Tres ramas independientes chocaron entre sí al mergear.** T-16, T-17 y T-18 salieron de
   `main` en paralelo y crearon los mismos archivos. Fue una decisión consciente (evitar apilar
   PRs sin revisar), y el costo fue real.
3. **La documentación afirmaba cosas falsas.** Al dibujar el diagrama de arquitectura aparecieron
   cuatro afirmaciones incorrectas en `CLAUDE.md` y el `README.md`, y una regla de protección de
   `main` más floja de lo documentado.
4. **Solo se registró 1 ceremonia de todo el sprint.** El Definition of Done del 12 de agosto. No
   hay registro de Planning ni de Dailies, y el profesor de ISW2 evalúa esa evidencia.

---

## 4. Objetivo propuesto para el Sprint 2

> **Que el hilo funcione de verdad de punta a punta, se pueda demostrar en vivo, y esté
> documentado como pide la semana 10.**

La razón de poner la integración por encima de mejorar el reconocimiento: hoy las 46 pruebas
pasan y el sistema completo no se ha ejecutado nunca. Un 0 % de exactitud es un problema conocido
y explicado; un hilo sin integrar es un problema de tamaño desconocido. Y la guía pide
explícitamente priorizar que algo funcione de principio a fin.

---

## 5. Recomendación previa al Planning

**Cerrar la integración antes de la presencial de la semana 8, no después.**

El arreglo es chico: agregar `server.proxy` en `client/vite.config.ts` y correr el hilo completo
una vez contra el backend real. Hacerlo antes del lunes cambia la conversación con el profesor:
en vez de explicarle que cada capa está probada por separado, se le demuestra el sistema
funcionando. Y la retroalimentación que dé será sobre un producto que funciona, que es la que
sirve para la semana 10.

Es lo único que se propone hacer antes del Planning. Todo lo demás espera a la ceremonia.

---

## 6. Backlog propuesto

Puntos con la misma escala del Sprint 1.

### Arrastre del Sprint 1 (8 pts)

| Tarjeta | Puntos | Nota |
|---|---|---|
| T-07 · Recolectar fotografías de campo | 5 | 2/12. Depende del clima, no del equipo |
| T-08 · Consolidar dataset y decidir alcance por marca | 3 | Bloqueada de verdad hasta tener muestra |

### Bloque A — Que el hilo funcione (8 pts)

| Tarjeta | Puntos | Por qué |
|---|---|---|
| T-21 · Conectar cliente y servidor y ejecutar el hilo completo | 3 | Riesgo #1 de la semana 7. **Antes de la presencial** |
| T-22 · Prueba end-to-end con Cypress del hilo completo | 5 | Cubre el pendiente P-08 de ISW2 **y** la "evidencia de pruebas" de la semana 10 |

### Bloque B — Entregable de la semana 10 (13 pts)

| Tarjeta | Puntos |
|---|---|
| T-23 · Manual de usuario | 3 |
| T-24 · Manual técnico: instalación, configuración y tecnologías | 3 |
| T-25 · Casos de uso principales documentados | 2 |
| T-26 · Consolidar la evidencia de pruebas | 2 |
| T-27 · Incorporar la retroalimentación del profesor | 3 |

**T-27 va en blanco a propósito.** Se llena en la semana 8, cuando exista la retroalimentación.
Es un requisito explícito del entregable, así que reservarle espacio ahora evita que se atienda a
última hora.

### Bloque C — Rúbricas que hoy tienen huecos (13 pts)

| Tarjeta | Puntos | Qué rúbrica |
|---|---|---|
| T-28 · Pipeline de entrega continua | 5 | ISW2 la pide y no existe (2.5 % del curso) |
| T-29 · Implementar la estrategia de respaldo y recuperación | 3 | Base de Datos, 25 % × 4. **Ya se le presentó el modelo al profesor como "planificado"** — conviene cumplirlo |
| T-30 · Registrar las ceremonias y sostener el registro | 2 | ISW2, Scrum (2.0 %). Hoy hay 1 ceremonia documentada de un sprint entero |
| T-31 · PWA real: manifest y service worker | 3 | Cierra el riesgo #5 y hace honesto el nombre del producto |

### Bloque D — Reconocimiento (5 pts, condicionado)

| Tarjeta | Puntos | Nota |
|---|---|---|
| T-32 · Atacar las líneas divisorias del odómetro | 5 | **Solo tiene sentido si T-07 avanza.** Con 2 fotos casi idénticas no se puede calibrar nada |

### Bloque E — Deuda técnica registrada (4 pts)

| Tarjeta | Puntos |
|---|---|
| T-33 · Unificar el manejo de errores del cliente en `api/errores.ts` | 1 |
| T-34 · Cerrar la diferencia entre `modelo-datos.md` §3 y los scripts | 3 |

---

## 7. Cómo se compara con la capacidad

| | Puntos |
|---|---|
| Todo lo propuesto | 51 |
| Velocity del Sprint 1 | 52 |

Los números se parecen, pero **el Sprint 1 duró dos semanas completas y el Sprint 2 arranca a
mitad de la semana 8**. Comprometer 51 puntos sería asumir que rendimos igual en menos tiempo.

Propuesta de recorte para discutir en el Planning:

- **Comprometer** los bloques A y B (21 pts) más T-29 y T-30 del bloque C (5 pts) = **26 puntos**.
  Es lo que la semana 10 exige o lo que ya le prometimos a un profesor.
- **Dejar como "si alcanza"** T-28 (CD), T-31 (PWA) y el bloque E.
- **Condicionar** el bloque D a que el dataset avance.
- **Mantener el arrastre** de T-07/T-08 fuera del compromiso, porque depende del clima.

---

## 8. Riesgos que siguen abiertos

Los cinco de la semana 7 (ver `docs/documento-tecnico-semana-7.md` §7) siguen vigentes. El orden
cambia si se hace T-21 antes de la presencial: el riesgo #1 pasaría de ser el más grave a estar
cerrado, y **el dataset quedaría como el riesgo principal del proyecto**.

Ese es el que no se resuelve programando: depende de salir a la calle con buen clima. Vale la
pena hablarlo en el Planning y repartir zonas con fechas concretas, no dejarlo como "cuando se
pueda".

---

## 9. Qué falta decidir en el Planning

1. Cuánto se compromete de verdad (§7).
2. Quién toma cada tarjeta, y si se cambia la regla de revisión de PRs sin rotación fija —
   ver el riesgo que ya se anotó en `docs/definition-of-done.md` sobre la Defensa Técnica
   Individual.
3. Fechas concretas para las salidas de campo de T-07.
4. Qué se hace con la retroalimentación del profesor una vez que exista (T-27).
