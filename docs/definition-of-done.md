# Definition of Done — MiMedidor

Acordado por el equipo (José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún Moreira) el 2026-08-12, los tres presentes. Registro completo de la ceremonia en
[`docs/scrum/sprint-1.md`](scrum/sprint-1.md).

> **Ajuste del Sprint 2:** desde el Sprint 2 las tareas son Issues de GitHub en vez de tarjetas de
> Trello. Los siete puntos no cambian; solo cambia cómo se llama la unidad de trabajo, y se agrega
> el `Closes #N` al punto 2, que es lo que hace que el Issue se cierre solo. El acuerdo original
> y su fecha se mantienen.

Un **Issue** se considera **Hecho** cuando cumple todo lo siguiente:

1. El código está en una rama `feature/` o `bugfix/`, nunca escrito directo en `main`.
2. Se abrió un Pull Request hacia `main`, con `Closes #N` en la descripción.
3. Al menos otro integrante del equipo revisó y aprobó el PR.
4. Los checks del pipeline de integración continua (compilación, pruebas unitarias, análisis estático) pasaron en verde.
5. El PR fue mergeado a `main`.
6. La documentación asociada (README, diagramas, comentarios de arquitectura) quedó actualizada si el cambio lo amerita.
7. Los criterios de aceptación específicos del Issue se cumplen y fueron verificados por quien lo ejecutó.

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
