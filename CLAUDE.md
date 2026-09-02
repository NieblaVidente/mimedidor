# MiMedidor — Contexto del proyecto

> **Este archivo es la fuente de verdad del proyecto.** Claude Code lo carga automáticamente al
> abrir el repositorio. Si algo aquí contradice un Issue o una tarjeta vieja de Trello, **manda
> este archivo** — varias tarjetas del Sprint 1 se escribieron antes de que se cerraran
> decisiones técnicas y quedaron desactualizadas (ver §9).
>
> Se actualiza como cualquier otro archivo: rama, PR y aprobación. No lo edites directo en `main`.

---

## 1. Qué es el proyecto

**MiMedidor** es una aplicación web progresiva (PWA) que permite a un hogar costarricense
fotografiar su hidrómetro, obtener la lectura automáticamente por visión por computadora,
mantener un historial propio y contrastarlo contra el consumo y el monto que le factura su
operador (AyA, municipalidad o ASADA).

**Por qué existe.** La Contraloría encontró que en 2023 **más del 50 % del agua producida por el
AyA no se contabilizó ni facturó**, y un estudio de ARESEP sobre 419 hidrómetros del Gran Área
Metropolitana halló que **alrededor del 60 % no funcionaba apropiadamente** — dato de 2015, que
hay que citar con su año. El abonado, mientras tanto, no tiene forma práctica de verificar su
propia lectura. Los productos existentes (Flume 2, Phyn Plus, Moen Flo) son hardware de **269 a
624 dólares** que asume Wi-Fi y electricidad en el punto de medición — supuestos que no se cumplen
en la instalación típica costarricense, que es una caja de concreto a ras de suelo, húmeda y sin
electricidad.

> **Cada una de esas cifras tiene fuente, cita textual y fecha de consulta en
> [`docs/fuentes.md`](docs/fuentes.md).** Si alguna se usa en un entregable, se cita desde ahí. Dos
> de las tres estaban mal enunciadas antes de T-41 y se corrigieron: el agua no contabilizada se
> atribuía a ARESEP siendo de la Contraloría, y el precio del hardware decía 150–430 dólares
> cuando ningún producto oficial cae en ese rango.

**Diferenciador.** Ninguna alternativa existente combina lectura automática por foto + historial
propio del abonado + contraste contra factura, sobre el parque de medidores ya instalado y sin
hardware adicional.

**Alcance del Sprint 1.** Un hilo funcional completo de punta a punta:
foto → lectura → historial → factura → comparación.
**La exactitud del reconocimiento NO es objetivo de este sprint.** Ver §8.

---

## 2. Equipo

| Integrante | Rol Scrum |
|---|---|
| José Pablo Ramírez Sánchez | Scrum Master · Equipo de desarrollo |
| Yariel Andrey Elizondo Jiménez | Equipo de desarrollo |
| Isaac Felipe Morún Moreira | Product Owner · Equipo de desarrollo |

Universidad Invenio · TICE · III Trimestre 2026.

El curso integrador **es** el Invenio Fest: no es un curso aparte, es un evento donde varios
profesores evalúan este mismo proyecto desde la perspectiva de su materia (ver §7).

> **Defensa Técnica Individual.** El curso de Sistemas Operativos incluye una defensa individual:
> cualquiera de los tres puede ser preguntado sobre **cualquier** parte del sistema, no solo sobre
> lo que programó. No se especialicen en silos. Si trabajaste una semana sin tocar la base de
> datos, pedile a quien la hizo que te la explique.

---

## 3. Stack tecnológico — decidido, no reabrir sin razón nueva

| Capa | Tecnología | Notas |
|---|---|---|
| Cliente | **Vite + React + TypeScript** | Cámara vía `getUserMedia`. PWA armada en T-31: `vite-plugin-pwa` genera manifest y trabajador de servicio en el build |
| Backend | **Python + FastAPI + Uvicorn** | El procesamiento de imagen vive en el mismo proceso |
| Visión por computadora | **OpenCV** (`opencv-python-headless`) para preprocesamiento (T-09/T-10) | La variante `headless` no trae dependencias de interfaz gráfica: el servidor y el runner de CI procesan arreglos, no muestran ventanas |
| Reconocimiento de dígitos (OCR) | **Tesseract**, vía `pytesseract` | Decidido en T-02b — ver justificación abajo |
| Base de datos | **PostgreSQL** | Acceso con `psycopg` (v3), **SQL plano, sin ORM** |
| Pruebas unitarias | `pytest` (server) · Vitest (client) | |
| Pruebas end-to-end | Cypress | Implementadas en T-22. Corren el hilo completo contra el backend real en cada PR |
| Análisis estático | `ruff` (server) · ESLint (client) | |
| CI/CD | GitHub Actions | Cuatro jobs paralelos: `client`, `server`, `database` y `e2e`. Los cuatro son obligatorios para mergear. ⚠️ **Todavía no hay entrega continua** — ver §13.7 |

### Por qué estas decisiones

**Python en el backend.** El corazón del proyecto son las tarjetas T-09 → T-10 → T-11 (OpenCV +
OCR). Con Python eso es una función más del backend. Con Node haría falta un microservicio Python
aparte, o usar `opencv.js`/`tesseract.js`, que son versiones empobrecidas justo del componente que
evalúa Computación Gráfica. Un servicio extra no se paga solo en un sprint de 10 días.

**PWA y no app nativa.** Cypress funciona directo para las pruebas end-to-end que pide el profesor
de Ingeniería de Software II; con nativo habría que usar Appium o Detox y confirmarlo. El despliegue
continuo a un servidor es viable en el plazo del curso; a una tienda de aplicaciones no lo es.
Además es reversible a nativo si el proyecto continúa después del trimestre.

**PostgreSQL.** Confirmado con el profesor de Base de Datos como motor relacional válido. La
rúbrica usa vocabulario de T-SQL pero no exige SQL Server. Ver §6 para la tabla de equivalencias.

**Sin ORM, SQL plano.** No es preferencia de estilo. La rúbrica de Base de Datos vale 25 % × 4 y
exige procedimientos almacenados, roles con mínimo privilegio y control transaccional escritos por
nosotros. Un ORM esconde exactamente lo que hay que mostrarle al profesor.

**Tesseract (`pytesseract`) para OCR, sobre EasyOCR y el DNN de OpenCV (T-02b).** El criterio de
esta tarjeta no es exactitud sobre hidrómetros — eso es T-11 — sino que funcione hoy y se instale
en CI sin pelear media tarde:
- **EasyOCR** se descarta: depende de PyTorch (una descarga pesada) y baja modelos pre-entrenados
  de internet la primera vez que corre, lo que vuelve el pipeline de CI lento y dependiente de la
  red en cada corrida — justo lo que un test rápido y confiable no debería tener.
- **El OCR por DNN de OpenCV** se descarta para este sprint: requiere descargar y cablear modelos
  `.pb`/`.onnx` aparte, desproporcionado para una tarjeta de 1 punto cuyo único objetivo es probar
  que *alguna* librería funciona.
- **Tesseract** gana: el motor y sus datos de entrenamiento se instalan con un solo paquete del
  sistema (`apt-get install tesseract-ocr` en CI), no descarga nada en tiempo de ejecución, y
  `pytesseract` es solo una envoltura fina en Python. Es la opción más madura y con menos piezas
  móviles para un sprint de 10 días.

Función mínima en `server/app/vision/reconocimiento.py`, probada en
`server/tests/test_reconocimiento.py` con una imagen generada en el momento (sin depender de un
archivo externo ni de una foto real todavía).

### Versiones — fijar el primer día

Los tres tienen que correr las mismas versiones que el CI. Anotarlas aquí apenas se definan:

- Python: `3.12` — declarado en `server/.python-version` (pin exacto) y leído por el workflow de CI desde ahí. `pyproject.toml` declara `requires-python = ">=3.12"`, que es un rango de compatibilidad, no un pin — no alcanza solo, `setup-python` puede agarrar una versión más nueva y romper la instalación de dependencias sin wheels precompilados para esa versión (nos pasó en T-02b: corrió en 3.14 y Pillow falló al compilar)
- Node: `24` (LTS) — declarado en `client/.nvmrc` y leído por el workflow de CI desde ahí
- PostgreSQL: `16` — fijado en T-13. `database/README.md` documenta cómo correr los scripts

---

## 4. Estructura del repositorio

```
mimedidor/
├── CLAUDE.md            # Este archivo — contexto para el equipo y para Claude Code
├── README.md            # Presentación pública del proyecto
├── client/              # Aplicación web (Vite + React + TS)
│   └── src/             # Las pruebas viven junto al código: Pantalla.tsx y Pantalla.test.tsx
├── server/              # API FastAPI + procesamiento de imagen
│   ├── app/
│   │   ├── api/         # Routers / endpoints
│   │   ├── vision/      # T-09 preprocesamiento, T-10 segmentación, T-11 reconocimiento
│   │   └── db/          # Acceso a datos (psycopg), llamadas a procedimientos
│   └── tests/           # pytest
├── database/
│   ├── scripts/         # Creación de esquema, tablas, roles, permisos, procedimientos
│   └── migrations/      # Cambios incrementales, numerados y en orden
├── docs/
│   ├── architecture/    # Diagrama de arquitectura, modelo entidad-relación, contrato de la API
│   ├── dataset-campo/   # Registro de los medidores fotografiados (T-07/T-08)
│   ├── evidencia/       # Capturas que prueban configuración que no vive en el código
│   ├── scrum/           # Registro de ceremonias y respaldo del tablero del Sprint 1
│   └── deuda-tecnica.md # Atajos tomados a propósito, con qué haría falta para cerrarlos
└── .github/workflows/   # Pipelines de CI
```

**Regla:** el código de visión por computadora va en `server/app/vision/` y **no importa nada de
FastAPI**. Son funciones puras que reciben una imagen y devuelven un resultado. Así se pueden
probar con `pytest` sin levantar el servidor, y así el trabajo de Computación Gráfica queda
aislado y demostrable por separado.

---

## 5. Convenciones de código

### Idioma

- **Nombres del dominio en español**: tablas, columnas, modelos, rutas de la API, funciones de
  negocio. `lectura`, `medidor`, `factura`, `POST /api/lecturas`.
- **Comentarios y documentación en español.**
- **En inglés solo lo que impone el framework o el lenguaje**: `def get_reading()` no, pero
  `class Config`, `useState`, `if __name__ == "__main__"` obviamente sí.

La razón: el modelo entidad-relación, los scripts SQL y los documentos que entregamos están en
español y los leen los profesores. Mezclar `readings` en la base de datos con "lecturas" en el
diagrama de entrega es una inconsistencia gratuita que nos van a señalar.

### Estilo

- Python: `ruff` decide. No discutir formato, correr el linter.
- TypeScript: ESLint + el formateador configurado. Igual.
- Nada de código comentado "por si acaso". Para eso está el historial de git.

### Logs

Desde el primer endpoint, **logs estructurados a stdout**. El profesor de Ingeniería de Software II
pide logs centralizados como parte de la herramienta de troubleshooting (P-05), y agregarlos
después es mucho más caro que hacerlo ahora. Cada log de una petición lleva: momento, ruta, código
de respuesta, duración y un identificador de la petición.

**Nunca** loguear la imagen completa ni datos personales del abonado.

---

## 6. Base de datos

Motor: **PostgreSQL**. La rúbrica describe los mecanismos con vocabulario de T-SQL (SQL Server).
Equivalencias que usamos y que hay que documentar en la entrega:

| La rúbrica pide | En PostgreSQL |
|---|---|
| `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK` | Igual — es sintaxis estándar |
| `TRY...CATCH` | `BEGIN ... EXCEPTION WHEN ... THEN ... END` en PL/pgSQL |
| `THROW` | `RAISE EXCEPTION 'mensaje'` |
| `XACT_ABORT` | No existe y **no hace falta**: PostgreSQL aborta la transacción completa por defecto ante cualquier error no capturado |

**No escribas T-SQL.** Si una tarjeta vieja del Sprint 1 dice `XACT_ABORT`, está desactualizada
(ver §9).

Entidades mínimas del modelo (T-12): `usuario`, `vivienda`, `medidor`, `lectura`, `factura`.
Normalizado hasta 3FN, con la justificación escrita de por qué lo cumple.

Roles con mínimo privilegio (T-13): al menos un rol de aplicación con lectura y escritura sobre lo
que necesita, y un rol de solo lectura para consultas. En PostgreSQL el usuario es un rol con
`LOGIN`, no un objeto aparte.

---

## 7. Qué evalúa cada curso

Esto condiciona decisiones técnicas. Léelo antes de proponer arquitectura.

**Ingeniería de Software II** (10 % del curso, cuenta como examen parcial). El profesor dijo
explícitamente que **la idea del proyecto no le importa** — evalúa cómo se construye el software:
Scrum con ceremonias registradas, feature branch workflow con `main` protegida, pipeline de CI,
pipeline de entrega continua, pruebas end-to-end, y una herramienta de troubleshooting.
Rúbrica: CI/CD 2.5 % · troubleshooting 2.5 % · feature branch workflow 2.0 % · Scrum 2.0 % ·
documentación 1.0 %. **Revisa el trabajo en clase, grupo por grupo, antes del evento.**

**Base de Datos** (25 % × 4). Modelo normalizado a 3FN, usuarios/roles/esquemas con mínimo
privilegio, control transaccional con manejo de errores, y estrategia de respaldo y recuperación
documentada.

**Computación Gráfica y Procesamiento de Imágenes.** Preprocesamiento (corrección de perspectiva,
realce de contraste), segmentación de la ventana del odómetro, reconocimiento de dígitos.

**Sistemas Operativos.** El fest **no reemplaza** los 4 proyectos de C++ del curso. Aporta 10 % de
participación técnica + 8 % de Defensa Técnica Individual + 10 % de portafolio. Evalúa el sistema
desde la perspectiva de procesos, memoria, almacenamiento, seguridad y virtualización.

**Señales y Sistemas.** ⚠️ **Rúbrica sin publicar — riesgo abierto.** El encaje propuesto: tratar
la imagen como señal 2D (convolución, filtrado) y la serie histórica de lecturas como señal 1D
(caudal, tendencia, consumo anómalo). Documenten los filtros aplicados y por qué, en T-09; ese
texto se reutiliza cuando salga la rúbrica.

---

## 8. Cosas que NO hay que hacer

Lista corta pero importante. Varias vienen de ajustes verbales del profesor en clase que
contradicen documentos escritos que circulan.

- ❌ **Docker y Kubernetes.** Retirados del alcance verbalmente por el profesor de ISW2, aunque el
  enunciado escrito original los mencione.
- ❌ **Entorno de staging.** Solo desarrollo y producción. También ajuste verbal.
- ❌ **Despliegue Blue/Green.** Retirado igual que los anteriores.
- ❌ **ORM** (SQLAlchemy, Prisma, etc.). Ver §3.
- ❌ **Sintaxis T-SQL.** Ver §6.
- ❌ **Push directo a `main`.** Ver §10.
- ❌ **Inventar o maquillar el número de exactitud del reconocimiento.** El objetivo del Sprint 1
  es *medir* la exactitud real sobre fotos de campo, no que sea buena. Un número malo bien
  explicado vale más que un número ausente, y muchísimo más que uno inventado. Ese número es la
  línea base que justifica el trabajo del Sprint 2.
- ❌ **Entrenar un modelo propio de reconocimiento en el Sprint 1.** Se usa una librería existente y
  se mide qué tan mal funciona. Punto.

---

## 9. Dónde vive el trabajo: GitHub Issues

**Desde el Sprint 2, las tareas son Issues de este repositorio.** Trello quedó como archivo de
solo lectura del Sprint 1.

Por qué se cambió: tener las tareas en el mismo lugar que el código permite que un Pull Request
cierre su tarea sola (`Closes #31`), que cada tarea enlace a los commits que la resolvieron, y que
no haya que mantener dos tableros sincronizados a mano — algo que en el Sprint 1 costó varias
correcciones.

Cómo están organizados los Issues:

| Etiqueta | Para qué |
|---|---|
| `área: …` | Dónde vive el trabajo: cliente, servidor, base de datos, infraestructura, documentación |
| `rúbrica: …` | Qué curso lo evalúa. Sirve para mostrarle a cada profesor su parte |
| `tipo: …` | `feature`, `doc` o `campo` |
| `puntos: …` | Estimación, misma escala del Sprint 1 |

El **milestone** agrupa lo que entra en cada entrega (`Semana 10 — Segundo avance`).

### El historial del Sprint 1

No se migró a Issues **a propósito**: recrear a mano 21 tarjetas ya cerradas les habría puesto
fecha de hoy, y eso daría a entender que todo el Sprint 1 se hizo en un día. Un registro falso es
peor que no tenerlo, sobre todo con la Defensa Técnica Individual de por medio.

El historial vive en dos lugares, los dos válidos como evidencia:

- El tablero de Trello, congelado.
- [`docs/scrum/sprint-1-tarjetas.md`](docs/scrum/sprint-1-tarjetas.md), que es el respaldo
  versionado en git del contenido de esas tarjetas.

Ese archivo también documenta qué tarjetas del Sprint 1 quedaron desactualizadas frente a las
decisiones técnicas que se cerraron después (T-01, T-02, T-05, T-13, T-14, T-15/T-16). Si alguna
vez lo consultás: **cuando una tarjeta vieja y este archivo se contradigan, manda este archivo.**

---

## 10. Cómo se trabaja aquí

### Flujo de git

`main` está protegida: no se puede pushear directo, todo entra por Pull Request con al menos una
aprobación y con los checks de CI en verde.

```
feature/descripcion-corta    → funcionalidad nueva
bugfix/descripcion-corta     → corrección de errores
```

Una rama por Issue. Mencioná el código de la tarea en el título del PR:
`T-09 · Corrección de perspectiva de la carátula`.

**Escribí `Closes #N` en la descripción del PR**, con el número del Issue. Así el Issue se cierra
solo al mergear y queda enlazado al código que lo resolvió — que es medio punto de haberse pasado
a Issues.

PRs chicos. Un PR de 800 líneas no lo revisa nadie de verdad, y la aprobación se vuelve un trámite
que el profesor va a notar.

### Definition of Done

Un Issue está Hecho cuando:

1. El código está en una rama `feature/` o `bugfix/`.
2. Se abrió un Pull Request hacia `main`, con `Closes #N`, y **se pidió la revisión a los
   otros dos integrantes** desde el panel *Reviewers*.
3. Al menos otro integrante aprobó el PR.
4. Los checks de CI pasaron en verde.
5. El PR fue mergeado a `main`.
6. La documentación asociada quedó actualizada si aplica.
7. Los criterios de aceptación del Issue se cumplen y fueron verificados.

Para Issues de tipo `doc` o `campo` que no producen código, aplican solo 6 y 7.

### Ceremonias

| Ceremonia | Cuándo |
|---|---|
| Sprint Planning | Lunes semana 6, al inicio |
| Daily Scrum | Todos los días, 15 min |
| Sprint Review | Jueves semana 7, antes de entregar |
| Sprint Retrospective | Jueves semana 7, después del review |

**Registrá cada ceremonia en `docs/scrum/`** con fecha, asistentes y acuerdos. El profesor de ISW2
va a pedir evidencia de que ocurrieron. Una foto de la reunión no prueba nada; un registro fechado
versionado en git sí.

---

## 11. Contrato de la API

Definido en T-04b y congelado una vez que los tres lo aprueben — no se edita por cuenta propia
después de eso. El documento completo, con ejemplos de petición/respuesta y la lista de códigos
de error, vive en [`docs/architecture/contrato-api.md`](docs/architecture/contrato-api.md). Es lo
que permite que el cliente y el servidor avancen en paralelo: quien hace la pantalla trabaja
contra los ejemplos de ese documento sin esperar al backend.

Resumen de rutas — para el detalle completo, ver el documento:

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/api/lecturas/reconocer` | Recibe la imagen, devuelve la lectura reconocida **sin guardar** |
| `POST` | `/api/lecturas` | Guarda la lectura ya confirmada o corregida por el usuario |
| `GET` | `/api/lecturas` | Historial ordenado por fecha, con el consumo entre lecturas consecutivas |
| `POST` | `/api/facturas` | Registra una factura ingresada a mano |
| `GET` | `/api/facturas/{id}/comparacion` | Consumo medido vs. consumo facturado, y la diferencia |

Reconocer y guardar están separados a propósito: el usuario tiene que poder **corregir** la lectura
antes de confirmarla, porque sabemos que el reconocimiento va a fallar seguido en este sprint.

Nunca exponer trazas internas ni detalles del motor de base de datos en la respuesta. Eso va al
log, no al cliente.

---

## 12. Instrucciones para Claude Code

Si estás asistiendo a un integrante de este equipo:

1. **Leé el Issue antes de escribir código** (`gh issue view N`), y contrastalo con §3 y §8: las
   decisiones técnicas ya cerradas mandan sobre lo que diga el Issue.
2. **Respetá el stack de §3.** No propongas cambiar de framework, agregar un ORM, meter Docker ni
   introducir un servicio nuevo. Esas decisiones ya se tomaron y tienen razones anotadas.
3. **Nunca hagas commit ni push a `main`.** Creá una rama `feature/` o `bugfix/`.
4. **Escribí la prueba junto con el código**, no después. El pipeline de CI corre `pytest` y Vitest,
   y un PR sin pruebas no debería aprobarse.
5. **El código de visión no importa FastAPI.** Funciones puras en `server/app/vision/`.
6. **No inventes resultados.** Si un reconocimiento falla o una exactitud sale baja, reportala tal
   cual. Ver §8.
7. **Explicá lo que hacés en español y sin saltarte el porqué.** Hay una Defensa Técnica Individual:
   el integrante tiene que poder defender este código sin vos delante.
8. Si algo de este archivo quedó desactualizado por una decisión nueva, **decílo y proponé la
   edición** en lugar de trabajar contra información vieja.

---

## 13. Riesgos abiertos

> **Los riesgos cerrados no se borran ni se renumeran: se marcan.** Otras secciones de este archivo
> referencian riesgos por número (§13.5, §13.7); renumerar los rompe. Además, dejar el registro de
> qué se identificó y qué lo cerró es evidencia, y borrarlo la pierde.

1. **Rúbrica de Señales y Sistemas sin publicar.** Es el eslabón más débil hasta que se confirme.
2. **Fragmentación del parque de medidores.** El alcance del MVP depende de qué tan concentrada
   salga la muestra de marcas en el dataset de campo. Criterio ya definido: si una marca aparece en
   ≥ 60 % de la muestra, el MVP se acota a ella.
3. **Carga simultánea de infraestructura y funcionalidad** en un sprint de 10 días, con tres
   personas que además llevan 4 proyectos de C++ de Sistemas Operativos.
4. **La prueba end-to-end no cubre el camino con trabajador de servicio.** Cypress corre contra
   `npm run dev` (ver `client/cypress.config.ts`, que apunta al 5173), y T-31 dejó el trabajador
   de servicio **desactivado en desarrollo** a propósito: uno cacheando durante `vite dev` esconde
   los cambios que uno acaba de hacer. La consecuencia es que la combinación Cypress + PWA no está
   probada — **no se rompió, simplemente no se ejercita**. En producción el trabajador de servicio
   sí está activo, así que ese camino hoy no tiene cobertura automatizada. Cerrarlo implica correr
   Cypress contra `vite preview` en un job aparte, y eso no entró en el alcance de T-31.

Los tres siguientes salieron de dibujar el diagrama de arquitectura (T-19): son diferencias reales
entre lo que este archivo declaraba y lo que hay en el repositorio.

5. ✅ **CERRADO — La PWA todavía no está armada.** Cerrado en T-31 (#41). El build genera
   `manifest.webmanifest`, `sw.js` y los iconos PNG de 192 y 512 px; `registerSW.js` queda
   inyectado en el `index.html`. Con eso la justificación de la decisión T-01 —web sobre nativo,
   porque «se instala desde el navegador sin pasar por una tienda»— deja de estar a medias.

   **Lo que el trabajador de servicio hace y lo que no:** guarda los archivos del build para que
   la aplicación abra rápido y sobreviva a una conexión intermitente. **No cachea `/api`**, a
   propósito: una lectura o un historial servidos desde caché serían datos viejos presentados como
   actuales, que es exactamente lo que este producto no puede hacer. El funcionamiento sin
   conexión —guardar una lectura tomada sin señal y sincronizarla después— sigue sin existir.
6. ✅ **CERRADO — Cliente y servidor nunca se han ejecutado juntos.** Cerrado en T-21 (#31, PR #28,
   commit `575680a`, 2026-08-25). El proxy vive en `client/vite.config.ts:17` y reenvía `/api` a
   `http://localhost:8000`; desde T-22 (#32, PR #50) la prueba end-to-end corre el hilo completo
   contra el backend real en cada PR, así que el riesgo no puede volver en silencio.

   **Lo que dejó de lección:** al conectarlos aparecieron dos errores que ninguna prueba veía,
   porque cada capa se probaba contra una sustitución de la otra. De ahí salió la acción de la
   retrospectiva de que toda funcionalidad que toque base de datos o HTTP lleve al menos una prueba
   contra la cosa real.
7. **No hay entrega continua.** El pipeline valida cada Pull Request pero no despliega a ningún
   ambiente, y la rúbrica de Ingeniería de Software II la pide explícitamente (§7).
