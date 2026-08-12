# Definition of Done — MiMedidor

Acordado por el equipo (José Pablo Ramírez Sánchez, Yariel Andrey Elizondo Jiménez, Isaac Felipe Morún Moreira) el [fecha].

Una tarjeta del tablero se considera **Hecha** cuando cumple todo lo siguiente:

1. El código está en una rama `feature/` o `bugfix/`, nunca escrito directo en `main`.
2. Se abrió un Pull Request hacia `main`.
3. Al menos otro integrante del equipo revisó y aprobó el PR.
4. Los checks del pipeline de integración continua (compilación, pruebas unitarias, análisis estático) pasaron en verde.
5. El PR fue mergeado a `main`.
6. La documentación asociada (README, diagramas, comentarios de arquitectura) quedó actualizada si el cambio lo amerita.
7. Los criterios de aceptación específicos de la tarjeta se cumplen y fueron verificados por quien la ejecutó.

## Excepciones

Las tarjetas de tipo `spike`, `campo` o `doc` que no producen código directamente solo requieren los puntos 6 y 7.

## Revisión cruzada de Pull Requests

Para evitar que cada integrante solo revise su propia área, las aprobaciones de PR rotan entre quienes no escribieron ese componente. El objetivo es que los tres puedan explicar y defender cualquier parte del sistema, no solo la que programaron — esto es evaluado individualmente en la Defensa Técnica de Sistemas Operativos y puede ser consultado por el profesor de Ingeniería de Software II.
