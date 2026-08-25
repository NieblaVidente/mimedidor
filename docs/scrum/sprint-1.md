# Registro de ceremonias — Sprint 1

## Definition of Done — 2026-08-12

**Asistentes:** José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún
Moreira. Los tres presentes en persona (tarjeta T-06).

**Acuerdos:**

1. Se adopta el Definition of Done propuesto en el scaffold inicial del repositorio
   ([`docs/definition-of-done.md`](../definition-of-done.md)), con los 7 puntos completos:
   rama `feature/`/`bugfix/`, PR hacia `main`, al menos 1 aprobación, CI en verde, PR mergeado,
   documentación actualizada si aplica, y criterios de aceptación de la tarjeta verificados por
   quien la ejecutó.
2. Los puntos 6 y 7 (documentación y criterios verificados) van más allá de lo que exige
   explícitamente el profesor de Ingeniería de Software II — él solo pide el mecanismo de PR
   (puntos 1 a 4). El equipo decide sumarlos porque ya se venían aplicando de hecho en todas las
   tarjetas cerradas hasta ahora del sprint (T-01 a T-04b) y dan algo concreto que responder si el
   profesor pregunta qué significa que una tarjeta esté "Hecha".
3. **Revisión de PRs sin rotación fija:** aprueba quien esté disponible, para no bloquear el
   avance. Riesgo aceptado explícitamente: no garantiza que los tres revisen las tres áreas del
   sistema, lo cual importa para la Defensa Técnica Individual de Sistemas Operativos. Queda
   anotado como algo a revisar si se nota desbalance durante el sprint.
4. Tarjetas de tipo `spike`, `campo` o `doc` (que no producen código) solo se evalúan contra los
   puntos 6 y 7 del DoD, no contra el flujo de PR/CI completo.

**Resultado:** DoD versionado en `docs/definition-of-done.md`, con fecha real y firma de los tres.
Cierra T-06.

---

## Sprint Review — 2026-08-25

**Asistentes:** José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún
Moreira. Los tres presentes, sesión presencial.

**Por qué en esta fecha y no el jueves de la semana 7.** La semana 7 fue virtual y el profesor
aplazó la entrega a la semana presencial para poder dar la retroalimentación en persona. El
equipo movió el Review y la Retrospectiva a la misma fecha, para que la conversación fuera
completa en vez de partida.

### Qué se demostró

**El hilo funcional completo, corriendo en el navegador y de punta a punta**: la aplicación
cliente hablando con la API, y la API contra PostgreSQL real. **Funcionó sin incidentes.**

Lo demostrado se apoya sobre el incremento del sprint: 5 rutas de API, 3 pantallas, 6 tablas
normalizadas a 3FN, 2 roles de mínimo privilegio, 1 procedimiento transaccional, 46 pruebas
automatizadas y un pipeline de 3 jobs sobre `main` protegida.

**Vale la pena dejar constancia de que esta demostración no era posible el día anterior.** T-21 se
cerró esa misma mañana: hasta entonces cliente y servidor nunca se habían ejecutado juntos, porque
las pantallas llaman rutas relativas que asumen mismo origen y el servidor de desarrollo no tenía
el proxy configurado. Cada capa estaba probada por separado, pero el sistema integrado no se había
corrido nunca.

Al conectarlo aparecieron dos errores que ninguna de las 46 pruebas podía detectar — uno de ellos
dejaba `POST /api/lecturas`, la ruta central del producto, devolviendo error 500 contra cualquier
base real. Los dos se corrigieron antes del Review. Ese episodio es el origen del hallazgo
principal de la retrospectiva de más abajo.

### Revisión del Definition of Done, tarea por tarea

Se revisaron las 21 tareas cerradas contra los 7 puntos del DoD. **Apareció un incumplimiento
real:** T-12 estaba en Hecho, pero la tabla de aprobación del propio `modelo-datos.md` marcaba la
revisión de Yariel como pendiente — o sea que fallaba el punto 6, documentación actualizada.

Yariel revisó el documento en la misma sesión y quedó aprobado por los tres. Con eso las 21 tareas
cumplen el DoD.

### Trabajo no completado

T-07 (recolectar fotografías de campo) y T-08 (consolidar dataset y decidir alcance por marca)
quedaron abiertas: 2 de 12 medidores. Se arrastran al Sprint 2.

### Retroalimentación

**Del profesor: pendiente.** La entrega se aplazó a esta semana presencial y todavía no se ha
recibido. Queda anotada como entrada obligatoria del Sprint 2 — el entregable de la semana 10
exige evidencia de que se incorporó (Issue #37).

---

## Sprint Retrospective — 2026-08-25

**Asistentes:** los tres, sesión presencial.

### Velocity

**52 de 60 puntos completados (87 %).** Los 8 restantes son T-07 y T-08.

Matiz que el equipo decidió dejar escrito: T-15b (3 puntos) se creó **durante** el sprint, al
descubrir que T-15 mezclaba dos rutas distintas del contrato. El compromiso original era menor
que 60 y creció a mitad de camino. **No hay registro del Sprint Planning para confirmar la cifra
exacta** — y esa ausencia es en sí misma uno de los hallazgos de esta retrospectiva.

### Qué salió bien

1. **Congelar el contrato de la API temprano (T-04b).** Es lo que permitió construir tres
   pantallas en paralelo sin pisarse entre sí.
2. **La disciplina de no maquillar resultados aguantó bajo presión.** El 0 % de exactitud del
   reconocimiento se reportó tal cual, con el análisis de por qué falla. Es más defendible que un
   número inflado.
3. **La base de datos es la parte más sólida del proyecto**, y es la que más pesa en rúbrica.
4. **El pipeline atrapó problemas reales**, no solo formalidades: por ejemplo una dependencia
   usada pero no declarada, que en local no fallaba porque ya estaba instalada.
5. **Aislar el código de visión de FastAPI** hizo que el trabajo de Computación Gráfica sea
   probable y demostrable por separado.

### Qué salió mal

1. **Había 46 pruebas en verde sobre una ruta que estaba rota.** `POST /api/lecturas` —el centro
   del producto— devolvía 500 contra cualquier base real, y no se supo hasta ejecutarlo de verdad,
   ya cerrado el sprint.
2. **Tres tareas de frontend descubrieron que su backend no existía** (T-15, T-17, T-18). Se
   resolvió sobre la marcha cada vez; solo una quedó registrada como cambio de alcance.
3. **Tres ramas en vuelo a la vez** produjeron trabajo duplicado (`api/lecturas.ts` escrito dos
   veces, `conftest.py` dos veces) y tres resoluciones de conflicto.
4. **La documentación afirmaba cuatro cosas falsas**, y aparecieron de casualidad, porque a
   alguien le tocó dibujar el diagrama de arquitectura.
5. **Se registró una sola ceremonia de todo el sprint** — el acuerdo del DoD del 12 de agosto.
6. **El dataset quedó en 2 de 12 medidores**, bloqueando a la vez la medición del reconocimiento,
   la decisión de marca y la calibración de la segmentación.
7. **T-12 estaba en Hecho incumpliendo el DoD**, detectado en el Review de hoy.

### El patrón de fondo

El equipo identificó que los cuatro problemas más caros son la misma cosa:

> **Verificábamos contra lo que escribimos, no contra la realidad.**

- Las pruebas se verificaban contra objetos falsos, no contra la base real → ruta rota en verde.
- La documentación se verificaba contra nuestras intenciones, no contra el código → cuatro
  afirmaciones falsas.
- El Definition of Done se verificaba contra el tablero, no contra el artefacto → T-12 "hecho"
  sin estarlo.
- La protección de `main` se verificaba contra lo que creíamos haber configurado → el check de
  base de datos corría pero no bloqueaba el merge.

No se atribuye a descuido de nadie: en los cuatro casos el atajo daba una señal verde creíble.

### Acciones para el Sprint 2

| # | Acción | Responsable | Cuándo |
|---|---|---|---|
| 1 | Cada Issue de frontend nombra los endpoints que consume, y se verifica que existan durante el Planning | Quien facilite el Planning | Cada Planning |
| 2 | Toda funcionalidad que toque base de datos o HTTP lleva al menos una prueba contra la cosa real, no solo contra objetos falsos | Quien la implemente | Desde ya |
| 3 | Mergear la primera rama aprobada de inmediato; las demás traen `main`. Nunca tres en vuelo | Los tres | Desde ya |
| 4 | Daily asíncrono de tres líneas (ayer / hoy / bloqueos) y registro semanal en `docs/scrum/` | Scrum Master | Diario |
| 5 | Rotación de revisión de Pull Requests por área: cada integrante revisa al menos uno de cliente, uno de servidor y uno de base de datos durante el sprint | Los tres | Este sprint |

La acción 2 ya arrancó: `server/tests/test_integracion_db.py` (T-21) es el primer caso, y corre
contra PostgreSQL real en el job `Base de datos` del pipeline.

La acción 5 atiende un riesgo que ya estaba anotado en `docs/definition-of-done.md` desde el
12 de agosto y que no se había atendido: revisar sin rotación fija no garantiza que los tres
conozcan las tres áreas del sistema, lo cual importa para la Defensa Técnica Individual.
