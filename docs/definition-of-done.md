# Definition of Done — MiMedidor

Acordado por el equipo (José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún Moreira) el 2026-08-12, los tres presentes. Registro completo de la ceremonia en
[`docs/scrum/sprint-1.md`](scrum/sprint-1.md).

> **Ajuste del Sprint 2:** desde el Sprint 2 las tareas son Issues de GitHub en vez de tarjetas de
> Trello. Los siete puntos no cambian; solo cambia cómo se llama la unidad de trabajo, y se agrega
> el `Closes #N` al punto 2, que es lo que hace que el Issue se cierre solo. El acuerdo original
> y su fecha se mantienen.

Un **Issue** se considera **Hecho** cuando cumple todo lo siguiente:

1. **El Issue está asignado** a quien lo trabaja, y el código está en una rama `feature/` o `bugfix/`, nunca escrito directo en `main`.
2. Se abrió un Pull Request hacia `main`, con `Closes #N` en la descripción, y **se pidió la revisión a los otros dos integrantes** desde el panel *Reviewers*.
3. Al menos otro integrante del equipo revisó y aprobó el PR.
4. Los checks del pipeline de integración continua (compilación, pruebas unitarias, análisis estático) pasaron en verde.
5. El PR fue mergeado a `main`.
6. La documentación asociada (README, diagramas, comentarios de arquitectura) quedó actualizada si el cambio lo amerita.
7. Los criterios de aceptación específicos del Issue se cumplen y fueron verificados por quien lo ejecutó.

> **Sobre pedir la revisión.** Un PR sin revisores pedidos **no le notifica a nadie**: queda
> esperando a que alguien entre a mirar por su cuenta. Pasó de verdad — tres PR seguidos se
> quedaron horas sin revisión, con los checks en verde, solo porque nadie sabía que existían.
> Abrir el PR y no pedir la revisión es dejar el trabajo terminado en un cajón.
>
> Se piden **los dos** que no son el autor, no uno solo: alcanza con que apruebe cualquiera, y
> elegir a quién agrega una decisión que no hace falta tomar.

> **Sobre asignar el Issue.** Un Issue sin responsable no dice quién hizo el trabajo. Importa por
> dos motivos concretos: el profesor de ISW2 evalúa el flujo de trabajo y mira si las tarjetas
> tienen dueño, y la Defensa Técnica Individual pregunta por partes específicas del sistema — el
> tablero es el registro de quién tocó qué. También pasó de verdad: T-39 se trabajó entera y se
> abrió su PR con el Issue sin asignar a nadie.
>
> Va en el punto 1 porque se hace **antes** de abrir el PR, no después: quien toma la tarjeta se
> asigna al empezar, que es cuando la información sirve para que nadie más la agarre en paralelo.

## Excepciones

Los Issues de tipo `doc` o `campo` que no producen código directamente solo requieren los puntos 6 y 7.

## Quién revisa los Pull Requests

Decisión del equipo (2026-08-12): **no hay rotación fija.** Aprueba quien esté disponible en ese
momento, priorizando que el PR se apruebe rápido y no se acumule trabajo bloqueado.

**Riesgo aceptado a propósito, no un descuido:** sin rotación forzada, nada garantiza que los tres
terminen revisando código de las tres áreas (cliente, servidor, base de datos). Eso importa porque
la Defensa Técnica Individual de Sistemas Operativos puede preguntarle a cualquiera de los tres
sobre cualquier parte del sistema, no solo la que programó. Si en algún momento del sprint alguien
nota que solo está revisando (o que nadie está revisando) su propia área, es una señal para
ajustar esto — no hace falta esperar a la retrospectiva.
