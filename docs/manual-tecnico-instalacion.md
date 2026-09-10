# Manual técnico — instalación, configuración y ejecución

Documento para quien clona este repositorio y necesita levantarlo, sin conocer el proyecto de
antemano. Complementa, sin repetir, el manual técnico entregado al profesor en la semana 7
(`MiMedidor_Manual_Tecnico.pdf`, formato IEEE) — ese documento explica **arquitectura, modelo de
datos, contrato de la API y limitaciones**; este documento explica **cómo levantar el sistema**.

**Convención de esta guía:** cuando el contenido ya vive en otro documento del repositorio, se
enlaza en vez de repetirse — copiarlo en dos lugares es exactamente el tipo de duplicación que
`docs/deuda-tecnica.md` ya registró como problema una vez (ver la entrada de T-16/T-17/T-18).

---

## 1. Qué ya está resuelto en otro documento (no repetido acá)

| Tema | Dónde está |
|---|---|
| Qué es MiMedidor y por qué existe | [`CLAUDE.md`](../CLAUDE.md) §1 |
| Stack completo, con la justificación de cada decisión (por qué Python, por qué sin ORM, por qué Tesseract y no otro OCR) | [`CLAUDE.md`](../CLAUDE.md) §3, y el manual entregado (Tabla I) |
| Diagrama de arquitectura y responsabilidad de cada módulo | [`docs/architecture/arquitectura.md`](architecture/arquitectura.md) — nota: fechado en T-19 (Sprint 1); si contradice `CLAUDE.md` en algo, manda `CLAUDE.md` |
| Modelo entidad-relación y justificación de 3FN | [`docs/architecture/modelo-datos.md`](architecture/modelo-datos.md) |
| Contrato de la API (rutas, formato de error, ejemplos) | [`docs/architecture/contrato-api.md`](architecture/contrato-api.md) |
| Roles de base de datos y por qué esos privilegios y no más | [`database/README.md`](../database/README.md) §"Roles", y el manual entregado (Tabla IV) |
| Equivalencias T-SQL ↔ PostgreSQL que pide la rúbrica | [`database/README.md`](../database/README.md) §"Equivalencia de mecanismos" |
| Por qué hace falta el proxy de Vite | [`CLAUDE.md`](../CLAUDE.md) §13.6, y [`docs/como-empezar.md`](como-empezar.md) §4b |
| Flujo de trabajo del equipo (ramas, PR, `Closes #N`, Definition of Done) | [`docs/como-empezar.md`](como-empezar.md) §6-8 |
| Resumen de entrega del Sprint 1, alcance, y el resultado real (no maquillado) del reconocimiento automático | [`docs/documento-tecnico-semana-7.md`](documento-tecnico-semana-7.md) — es la fuente del manual entregado en PDF (`MiMedidor_Manual_Tecnico.pdf`); es una foto fija de la semana 7, así que algunos detalles (por ejemplo, dice que Cypress está "planificado para el Sprint 2") ya quedaron atrás — para lo vigente, siempre `CLAUDE.md` |

---

## 2. Requisitos — versiones exactas

No rangos: son las versiones que corren en CI (`.github/workflows/ci.yml`) y las que deberían
correr en cualquier máquina del equipo.

| Herramienta | Versión exacta | Fijada en |
|---|---|---|
| Python | **3.12** | `server/.python-version` |
| Node.js | **24** | `client/.nvmrc` |
| PostgreSQL | **16** | `database/README.md`, job `database` de CI |
| Tesseract OCR | La que instale el gestor de paquetes del sistema (sin pin de versión — CI usa `apt-get install tesseract-ocr` sobre el runner `ubuntu-latest` de GitHub Actions) | — |

`pyproject.toml` declara `requires-python = ">=3.12"`, que es un **rango de compatibilidad**, no
un pin — no alcanza solo: `setup-python` puede agarrar una versión más nueva y romper la
instalación (pasó en T-02b: corrió en 3.14 y Pillow no compiló). Usar siempre `server/.python-version`
como fuente de verdad, no el rango de `pyproject.toml`.

Cómo instalar cada herramienta en Windows (con `winget`) está en
[`docs/como-empezar.md`](como-empezar.md) §1 — no se repite acá porque son los mismos comandos
para cualquier persona que arranque, sin importar en qué tarjeta esté trabajando.

---

## 3. Obtener el código

```bash
gh repo clone NieblaVidente/mimedidor
cd mimedidor
```

⚠️ Cloná en una ruta **sin espacios ni tildes** (ej. `C:\dev\mimedidor`, no
`C:\Users\vos\Documentos\Proyectos 2026\mimedidor`). Con espacios, las pruebas del cliente
(Vitest) se cuelgan sin terminar — ya nos pasó una vez, ver la tabla de la §8.

---

## 4. Configuración — variables de entorno

El servidor no tiene un archivo de configuración propio ni un `.env`: se conecta a PostgreSQL
leyendo las **variables de entorno estándar de `libpq`**, las mismas que usa cualquier cliente de
PostgreSQL (`psql` incluido). Están centralizadas en `server/app/db/conexion.py`, que llama
`psycopg.connect()` sin argumentos a propósito, para no tener que parsear nada a mano.

| Variable | Para qué | Valor típico en desarrollo local |
|---|---|---|
| `PGHOST` | Host de PostgreSQL | `localhost` |
| `PGPORT` | Puerto | `5432` (el default de PostgreSQL; no hace falta declararlo si es ese) |
| `PGDATABASE` | Nombre de la base | `mimedidor` |
| `PGUSER` | Rol con el que se conecta | `mimedidor_app` (el rol de lectura/escritura — ver `database/README.md`) |
| `PGPASSWORD` | Contraseña de ese rol | La que le hayas puesto al correr `03_roles_permisos.sql` (ver §5) |

Estas cinco variables son las que hay que exportar (o anteponer al comando, como en §6) antes de
levantar la API o de correr las pruebas de integración (§7) — son el requisito previo que nadie
adivina si nunca vio `conexion.py`.

---

## 5. Base de datos — creación y orden de los scripts

Con PostgreSQL 16 instalado y corriendo:

```bash
createdb mimedidor

cd database/scripts
psql -d mimedidor \
     -v password_app='elegí-una-clave-local' \
     -v password_lectura='elegí-una-clave-local' \
     -f ejecutar_todo.sql
```

`ejecutar_todo.sql` corre, en este orden exacto (encadenado por `\i` dentro del script, no hace
falta correrlos a mano uno por uno):

1. `01_esquema.sql` — crea el esquema `mimedidor` y revoca el acceso por defecto a `PUBLIC`
2. `02_tablas.sql` — crea las tablas, normalizadas a 3FN
3. `03_roles_permisos.sql` — crea `mimedidor_app` y `mimedidor_lectura` con las contraseñas que
   pasaste arriba, y les otorga solo los privilegios que necesita cada uno
4. `04_procedimiento_registrar_lectura.sql` — crea el procedimiento transaccional (T-14)

Detalle completo de cada paso, la nota sobre qué hacer si los roles ya existen de una corrida
anterior, y cómo respaldar/restaurar: [`database/README.md`](../database/README.md).

---

## 6. Preparar cliente y servidor, y levantar el sistema completo

Instalación de dependencias, y cómo correr lint/build/pruebas de cada pieza por separado:
[`docs/como-empezar.md`](como-empezar.md) §4.

Para levantarlo **completo y verificar que las tres piezas se hablan entre sí** (necesario porque
hasta T-21 nunca se habían ejecutado juntas — ver `CLAUDE.md` §13.6), en tres terminales:

| Terminal | Comando | Puerto |
|---|---|---|
| 1 — API | `cd server` y `PGHOST=localhost PGDATABASE=mimedidor PGUSER=mimedidor_app PGPASSWORD=<tu-clave> .venv/Scripts/uvicorn.exe app.main:app --reload` | `8000` |
| 2 — Cliente | `cd client` y `npm run dev` | `5173` |
| 3 — Verificación | `curl http://localhost:5173/api/salud` → debe responder `{"estado":"ok"}` | — |

El navegador se abre en el **5173** (el de Vite), no en el 8000: `client/vite.config.ts` tiene un
proxy que reenvía todo lo que empieza con `/api` al servidor. Sin ese proxy, el navegador le
pediría `/api/...` al propio servidor de Vite y recibiría `index.html` en vez de una respuesta de
la API — el bug concreto que cerró T-21.

Para probar el hilo completo hace falta un medidor ya existente en la base — el contrato de la
API no expone ninguna ruta para crear medidores. `database/scripts/datos_de_prueba.sql` siembra
uno (con una lectura de hace 5 días, para que haya un período real que medir):

```bash
cd database/scripts
psql -d mimedidor -v ON_ERROR_STOP=1 -f datos_de_prueba.sql
```

---

## 7. Correr las pruebas — con los requisitos que no se adivinan

| Suite | Comando | Requisito previo |
|---|---|---|
| Cliente (Vitest) | `cd client && npm run test` | Ninguno — todo sustituido |
| Servidor (pytest, unitarias) | `cd server && .venv\Scripts\python.exe -m pytest -v` | Ninguno — usan una conexión falsa (`conftest.py`); 3 pruebas de visión se saltan solas si falta `dataset-fotos/` (carpeta no versionada, ver `docs/dataset-campo/registro-medidores.md`) |
| Servidor (pytest, **integración**, T-21) | `cd server` y con las 5 variables de la §4 puestas: `pytest tests/test_integracion_db.py -v` | **PostgreSQL corriendo, con el esquema ya aplicado (§5), y las variables `PGHOST`/`PGDATABASE`/`PGUSER`/`PGPASSWORD` exportadas.** Si no hay base accesible se saltan solas — no rompen el trabajo de nadie, pero tampoco avisan si te olvidaste de levantar la base |
| End-to-end (Cypress) | `cd client && npm run e2e` (o `npm run e2e:abrir` para verla paso a paso) | **Los tres procesos de la §6 levantados**, más los datos de prueba sembrados (`datos_de_prueba.sql`, ver §6). Tiene que correr en un navegador Chromium (Chrome, Edge, o el Electron que trae Cypress) — la cámara falsa que usa la prueba no existe en Firefox |

Por qué existe la suite de integración además de las unitarias: las pruebas con conexión falsa no
detectan errores de tipos entre Python y SQL (un `float` de Python vs. un `numeric` de
PostgreSQL le rompió una llamada real a `registrar_lectura` mientras las 46 pruebas unitarias
seguían en verde). Detalle completo en el docstring de `server/tests/test_integracion_db.py`.

En CI las cuatro suites corren en jobs separados (`client`, `server`, `database`, `e2e`) en cada
Pull Request — `.github/workflows/ci.yml` es la referencia exacta y siempre actualizada de cómo se
preparan sus prerrequisitos (incluida la base de datos, que ahí se crea desde cero en cada corrida).

---

## 8. Si algo falla

Tabla de síntomas ya conocidos y su solución (rutas con espacios, Python equivocado, Tesseract
faltante, PATH no recargado, etc.): [`docs/como-empezar.md`](como-empezar.md) §10.

---

## 9. Verificación de este documento

Cumple el criterio de aceptación de la tarjeta: alguien que clona el repositorio y sigue las
secciones 2 a 7 en orden llega a tener las cuatro suites de prueba corriendo en verde, sin tener
que adivinar ninguna variable de entorno ni el orden de los scripts de base de datos.
