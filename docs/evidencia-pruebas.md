# Consolidación de la evidencia de pruebas

**Issue:** [#36](https://github.com/NieblaVidente/mimedidor/issues/36) (T-26) · Exigido
explícitamente por la Guía de Entregables §3.3 y §5.

Este documento junta en un solo lugar qué se prueba, en qué nivel, cuántas pruebas hay y qué
**no** está cubierto. No es una lista de números para presumir — el punto central de este
documento es contar honestamente que las pruebas unitarias solas no bastaron, y por qué.

---

## La historia que explica por qué existe este documento

Al cerrar T-15/T-16/T-17/T-18 (Sprint 1), había **46 pruebas unitarias en verde** — 31 del
servidor y 15 del cliente — y el CI las corría en cada Pull Request sin que nada fallara nunca.

Cuando en T-21 (Sprint 2) se conectó el cliente y el servidor de verdad por primera vez y se
ejecutó el hilo completo contra una base de datos real, **aparecieron dos errores que ninguna de
esas 46 pruebas podía ver**:

1. `POST /api/lecturas` devolvía `500` siempre. `psycopg` manda los `float` de Python como
   `double precision`; el procedimiento `registrar_lectura` declara sus parámetros `numeric`, y
   en PostgreSQL ese cast es de asignación, no implícito — para resolver a qué procedimiento
   llamar solo se consideran los casts implícitos. La llamada fallaba con "no existe el
   procedimiento" aunque el procedimiento existiera.
2. El error de `LECTURA_INVALIDA` filtraba al cliente el bloque `CONTEXT` de PostgreSQL completo
   — nombre del procedimiento, firma y número de línea —, algo que `CLAUDE.md` §11 prohíbe
   explícitamente.

**Por qué las 46 pruebas no lo vieron:** todas, sin excepción, sustituían la conexión a la base
de datos por un objeto falso (`conftest.py` en el servidor, módulos de API sustituidos en el
cliente). Un objeto falso no puede fallar por un cast de tipos de PostgreSQL. Este no es un
detalle anecdótico — es la razón de ser de dos capas enteras de prueba que no existían antes de
T-21: las pruebas de integración contra base real (`server/tests/test_integracion_db.py`) y la
prueba end-to-end (`client/cypress/e2e/hilo-completo.cy.ts`, T-22), que corre contra el sistema
completo levantado — sin nada sustituido — precisamente para que un error de este tipo no vuelva
a pasar inadvertido.

---

## Inventario por nivel

| Nivel | Dónde vive | Cuántas | Qué sustituye / qué no |
|---|---|---|---|
| Unitarias del servidor | `server/tests/*.py` (excepto `test_integracion_db.py`) | **31** (28 corren en cada PR, 3 solo con el dataset de campo local — ver nota abajo) | La conexión a PostgreSQL está sustituida por un objeto falso — prueban lógica de negocio y de visión aisladas, rápido y sin infraestructura |
| Unitarias del cliente | `client/src/*.test.tsx` | **15** | El módulo de API (`fetch`) está sustituido — prueban la lógica de cada pantalla en aislamiento |
| Integración contra base real | `server/tests/test_integracion_db.py` | **4** | Nada sustituido: corre contra PostgreSQL 16 real. Se saltan solas en el job `server` (no tiene Postgres) y corren de verdad en el job `database`. Existen por el bug del cast de T-21 — ver arriba |
| Transaccional en SQL | `database/scripts/verificar_registrar_lectura.sql` | 1 escenario, 2 casos | Registra una lectura válida y fuerza una inválida a propósito; confirma que la transacción de dos escrituras (`lectura` + `lectura_evento`) no dejó nada a medias (T-14) |
| Respaldo y restauración | `database/scripts/verificar_restauracion.sh` | 1 escenario de punta a punta | Inserta un dato, respalda, restaura en una base aparte y confirma que el dato sobrevivió con el mismo valor — no solo que los comandos no fallaron (T-29) |
| End-to-end | `client/cypress/e2e/hilo-completo.cy.ts` | **2** | Nada sustituido: navegador real → cliente → proxy de Vite → FastAPI → PostgreSQL. Cubre el hilo feliz completo (foto → lectura → historial → factura → comparación con alerta de umbral) y el rechazo de una lectura inválida sin fuga de detalles internos (T-22) |
| Exactitud del reconocimiento | `docs/exactitud-reconocimiento.md` | 2 fotos medidas | **0 de 2 (0%)** coinciden exactamente con la lectura real — medido, no maquillado (T-11). **No corre en CI**: el dataset de fotos no se versiona (`CLAUDE.md`, política de no subir fotos crudas), así que es una medición manual puntual, fijada como número de referencia — ver nota abajo |

**Total de pruebas automatizadas que corren de verdad en cada Pull Request: 28 + 15 + 4 + 2 = 49.**
Las 3 pruebas restantes del servidor (sobre `dataset-fotos/`, no versionado) están escritas y
pasan cuando alguien las corre con el dataset local, pero **se saltan en CI** — ver la nota sobre
la exactitud del reconocimiento más abajo. Aparte quedan las verificaciones de base de datos
(T-14/T-29), que también corren en CI pero se cuentan aparte por no ser aserciones de
`pytest`/Vitest/Cypress en el sentido estricto.

Los cuatro jobs de `.github/workflows/ci.yml` (`client`, `server`, `database`, `e2e`) corren en
paralelo en cada Pull Request y bloquean el merge si alguno falla. Confirmado corriendo la suite
completa en este entorno: `server` da **32 passed, 3 skipped** en total (35 con integración
incluida), idéntico a lo que muestra la corrida real de CI de abajo.

---

## Evidencia del CI en verde

**Nota sobre el formato de esta evidencia.** El resto de este documento se armó con acceso
directo a este entorno de trabajo; una captura de pantalla real de GitHub Actions, en cambio,
requiere un navegador con acceso a `github.com`, que esta sesión tiene bloqueado por política.
En su lugar, la evidencia de abajo es la salida real de `gh run view` sobre la corrida en `main`
después de mergear T-22 (Cypress) — verificable en el enlace, e igual de real que una captura,
aunque no sea una imagen. Si el equipo prefiere tener además el PNG (mismo formato que
`docs/evidencia/ci-bloquea-merge.png` y `proteccion-main.png`), alguien con navegador sin esa
restricción puede agregarlo desde el enlace de abajo.

**Corrida:** [`#33037200695`](https://github.com/NieblaVidente/mimedidor/actions/runs/33037200695)
(disparada por el merge de T-22, 2026-08-27).

```
$ gh run view 33037200695
conclusion: success
event: push
headSha: 4acacd3d4e8afd01c1e2cf248cc85f46eabe055a

jobs:
  Servidor (lint, tests)              success   03:43:11 → 03:43:48
  Cliente (lint, build, tests)        success   03:43:11 → 03:43:37
  Base de datos (esquema, tablas...)  success   03:43:11 → 03:43:40
  End-to-end (Cypress)                success   03:43:11 → 03:44:26
```

Los cuatro jobs completos y en verde en 75 segundos, sobre el mismo commit.

---

## Qué NO está cubierto

Dicho explícitamente, como pide el criterio de aceptación:

- **La exactitud del reconocimiento no está "cubierta" en el sentido de que pase.** Está medida y
  documentada (0 de 2), y esa medición está fijada con una prueba unitaria
  (`test_reconocer_lectura_mide_exactitud_sobre_dataset_real`) que fallaría si alguien cambiara
  el resultado sin actualizar el documento — pero el número en sí no es un éxito, es la línea
  base honesta de partida.
- **Esa prueba no corre en CI.** El dataset de fotos vive en almacenamiento compartido, no en el
  repositorio (política explícita de `CLAUDE.md` de no versionar fotos crudas), así que en el
  runner de GitHub Actions esta prueba y otras dos que dependen del mismo dataset
  (`test_preprocesar_caratula_funciona_sobre_dataset_real`,
  `test_segmentar_ventana_funciona_sobre_salidas_reales_de_t09`) **se saltan siempre** —
  confirmado en la corrida real del CI: `28 passed, 7 skipped`. La medición del 0 % es manual,
  hecha una vez por quien tenía el dataset local, y quedó pinneada en el documento. Si el
  reconocimiento cambia y nadie vuelve a correr esa prueba con el dataset a mano, el documento
  puede quedar desactualizado sin que el pipeline lo detecte.
- **`vista_historial_lecturas` y `fn_comparacion_factura` no existen en la base de datos.**
  `docs/architecture/modelo-datos.md` §3 dice que ahí se resolverían los campos calculados; en la
  práctica se calcularon en Python dentro de los routers (`server/app/api/lecturas.py`,
  `facturas.py`), y estos sí están probados — pero no hay ninguna prueba SQL de esas dos vistas
  porque no se llegaron a escribir. Es deuda técnica reconocida en
  `docs/deuda-tecnica.md` (T-13) y tiene su propio Issue de seguimiento
  ([#44](https://github.com/NieblaVidente/mimedidor/issues/44), T-34).
- **No hay pruebas de carga ni de concurrencia.** Ni el procedimiento transaccional de T-14 ni la
  API se probaron bajo escritura simultánea sobre el mismo medidor.
- **No hay pruebas de seguridad más allá de los permisos por rol.** `database/README.md`
  documenta y prueba que `mimedidor_app` no puede borrar ni hacer DDL, pero no hay pruebas de
  inyección SQL, límites de tamaño de archivo en la subida de fotos, ni límites de tasa
  (rate limiting) sobre los endpoints.
- **No hay pruebas de accesibilidad** (lectores de pantalla, navegación por teclado) sobre las
  pantallas del cliente.
- **La segmentación de la ventana del odómetro (T-10) está probada solo sobre un medidor.** Las
  franjas de búsqueda y el recorte de respaldo están calibrados con fotos de un solo modelo —
  detalle completo en `docs/deuda-tecnica.md` (T-10).
- **No hay pruebas del manejo de errores duplicado del cliente.** `ErrorApiLecturas` y
  `ErrorApiFacturas` son casi idénticas (deuda técnica, `docs/deuda-tecnica.md`,
  [#43](https://github.com/NieblaVidente/mimedidor/issues/43) T-33); cada una tiene su propia
  cobertura de pruebas por separado, no una compartida.
