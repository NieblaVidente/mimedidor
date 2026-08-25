# Sprint 1 — Tarjetas actualizadas

> 🔒 **Archivo congelado.** Este es el respaldo versionado del tablero de Trello con el que se
> gestionó el **Sprint 1**. Desde el Sprint 2 las tareas son
> [Issues del repositorio](../../../../issues) — ver `CLAUDE.md` §9 para el porqué del cambio.
>
> **No se edita más.** Su valor es ser el registro fiel de lo que decía el tablero en su momento,
> y sirve como evidencia de backlog para el profesor de Ingeniería de Software II.

Textos listos para pegar en Trello, corregidos después de cerrar las decisiones de T-01 y T-02.

**Convención:** el título va en el nombre de la tarjeta, el resto en la descripción.

## Resumen de cambios

| Tarjeta | Acción | Puntos |
|---|---|---|
| T-01 | Cerrar → Hecho, con comentario de la decisión | 2 (completados) |
| T-02 | Dividir en T-02a y T-02b | 2 → 1 + 1 |
| T-02a | Cerrar → Hecho (motor de BD confirmado) | 1 (completados) |
| T-02b | **Nueva** — elegir librería de reconocimiento | 1 |
| T-04b | **Nueva** — contrato de la API | 1 |
| T-05 | Reescribir con herramientas concretas | 3 |
| T-09 · T-10 · T-11 | Añadir tecnología y ubicación en el repo | sin cambio |
| T-13 | Corregir vocabulario a PostgreSQL | sin cambio |
| T-14 | **Reescribir** — estaba en T-SQL | sin cambio |
| T-15 · T-16 | Nombrar tecnología y contrato de API | sin cambio |

**Compromiso del sprint: 38 → 39 puntos.** La división de T-02 es neutra (2 = 1 + 1); el punto
adicional es T-04b, que no es alcance nuevo sino trabajo que estaba implícito y sin fecha dentro
de T-15. Anotarlo así en la retrospectiva para que la velocity siga siendo comparable.

---

# 📌 Tarjeta fija — pegar arriba de todo en Sprint Backlog

### 📌 STACK Y REGLAS — leer antes de tomar cualquier tarjeta

```
La fuente de verdad del proyecto es CLAUDE.md en la raíz del repositorio.
Si una tarjeta contradice ese archivo, manda el archivo.

STACK DECIDIDO
· Cliente ......... Vite + React + TypeScript + vite-plugin-pwa
· Backend ......... Python + FastAPI + Uvicorn
· Visión .......... OpenCV (opencv-python) + librería OCR de T-02b
· Base de datos ... PostgreSQL con psycopg — SQL plano, SIN ORM
· Pruebas ......... pytest (server) · Vitest (client) · Cypress (E2E, Sprint 2)
· Linters ......... ruff (server) · ESLint (client)
· CI .............. GitHub Actions, dos jobs: client y server

NO HACER
· Docker, Kubernetes, staging ni Blue/Green — el profesor los retiró en clase
· ORM de ningún tipo
· Sintaxis T-SQL (XACT_ABORT, TRY...CATCH) — usamos PL/pgSQL
· Push directo a main
· Inventar o maquillar el número de exactitud del reconocimiento

IDIOMA DEL CÓDIGO
Nombres del dominio en español (lectura, medidor, factura, /api/lecturas).
Inglés solo en lo que impone el framework.

FLUJO
Una rama por tarjeta: feature/descripcion-corta o bugfix/descripcion-corta.
PR hacia main + 1 aprobación + CI en verde. Título del PR: "T-09 · Descripción".
```

---

# Tarjetas a cerrar

---

### T-01 · Decidir el stack: aplicación web o móvil nativa

**Mover a Hecho.** Pegar como comentario en la tarjeta:

```
DECISIÓN: Aplicación Web Progresiva (PWA).

Justificación:
1. Cypress funciona directo para las pruebas end-to-end que pidió el profesor de
   Ingeniería de Software II. Con nativo habría que usar Appium o Detox y
   confirmar con él que los acepta.
2. El despliegue continuo a un servidor es viable en el plazo del curso; el
   despliegue continuo a una tienda de aplicaciones no lo es.
3. Se instala desde el navegador, sin pasar por Play Store.
4. La decisión es reversible a nativo si el proyecto continúa después del trimestre.

Contra asumido: el acceso a la cámara es menos fino que en nativo (enfoque,
resolución, linterna) y la experiencia offline es más limitada. Se acepta porque
ninguna de las dos cosas bloquea el hilo funcional del Sprint 1.

Stack concreto derivado: Vite + React + TypeScript con vite-plugin-pwa, cámara
vía getUserMedia. Backend en Python + FastAPI (ver comentario en T-02b).

Registrado en CLAUDE.md §3 para el documento técnico de la semana 7.
```

---

### T-02a · Confirmar motor de base de datos

**Mover a Hecho.** Reemplaza la mitad de base de datos de la T-02 original.

**Etiquetas:** `1` `BD` `spike`

Pegar como comentario:

```
DECISIÓN: PostgreSQL.

Confirmado con el profesor de Base de Datos: la rúbrica exige un motor relacional,
no SQL Server específicamente. El vocabulario T-SQL de la rúbrica (TRY...CATCH,
THROW, XACT_ABORT) se traduce así, y la equivalencia queda documentada en la
entrega:

  TRY...CATCH  →  BEGIN ... EXCEPTION WHEN ... THEN ... END  (PL/pgSQL)
  THROW        →  RAISE EXCEPTION 'mensaje'
  XACT_ABORT   →  no existe y no hace falta: PostgreSQL aborta la transacción
                  completa por defecto ante cualquier error no capturado

Acceso desde el backend con psycopg v3, SQL plano y sin ORM: la rúbrica exige
procedimientos almacenados, roles con mínimo privilegio y control transaccional
propios, y un ORM esconde justamente lo que hay que demostrar.

Documentado en database/README.md y en CLAUDE.md §6.
```

---

# Tarjetas nuevas

---

### T-02b · Elegir librería de reconocimiento de dígitos

**Etiquetas:** `1` `CG` `spike`
**Bloquea:** T-11
**Hacer el lunes.** Es lo único que quedó abierto de la T-02 original.

**Descripción**

En este sprint **no se entrena un modelo propio**. Se toma una librería existente y se mide qué tan
mal funciona sobre fotos reales de campo. Ese número es el punto de partida que justifica el
trabajo del Sprint 2.

Opciones a evaluar, en orden de esfuerzo:

- **Tesseract** (`pytesseract`) — la más establecida; requiere instalar el binario aparte, lo cual
  también hay que resolver en el runner de CI.
- **EasyOCR** — más simple de instalar desde `pip`, pero descarga modelos pesados la primera vez.
- **El reconocimiento de texto de OpenCV** — evita una dependencia extra, ya que OpenCV entra igual
  por T-09.

Criterio de decisión: que funcione hoy sobre una imagen cualquiera con dígitos y que se pueda
instalar en el pipeline de CI sin pelear media tarde. La exactitud sobre hidrómetros **no** es
criterio de selección en este sprint, justamente porque medirla es el objetivo de T-11.

**Criterios de aceptación**
- [ ] Librería elegida, con la razón anotada en un comentario de la tarjeta
- [ ] Declarada en las dependencias de `server/` y instalable con un solo comando
- [ ] Prueba mínima: lee dígitos de una imagen cualquiera y devuelve texto
- [ ] Se verificó que se puede instalar en el runner de GitHub Actions
- [ ] La decisión quedó reflejada en `CLAUDE.md` §3

---

### T-04b · Definir y congelar el contrato de la API

**Etiquetas:** `1` `IS2` `doc`
**Depende de:** T-01
**Bloquea:** T-15, T-16
**Hacer lunes o martes — no esperar a T-15**

**Descripción**

Es la tarjeta que permite que el cliente y el servidor avancen en paralelo. Sin ella, quien hace la
pantalla de captura (T-16) queda bloqueado hasta el jueves esperando el endpoint (T-15). Con el
contrato definido el lunes, trabaja contra datos falsos desde el primer día.

Acordar entre los tres las rutas, la forma de cada petición y respuesta, y la forma de los errores.
Propuesta base en `CLAUDE.md` §11:

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/api/lecturas/reconocer` | Recibe la imagen, devuelve la lectura reconocida **sin guardar** |
| `POST` | `/api/lecturas` | Guarda la lectura ya confirmada o corregida |
| `GET` | `/api/lecturas` | Historial por fecha, con consumo entre lecturas consecutivas |
| `POST` | `/api/facturas` | Registra una factura ingresada a mano |
| `GET` | `/api/facturas/{id}/comparacion` | Consumo medido vs. facturado, y la diferencia |

Reconocer y guardar están separados a propósito: el usuario tiene que poder corregir la lectura
antes de confirmarla, porque el reconocimiento va a fallar seguido en este sprint.

Los errores tienen una sola forma en toda la API:

```json
{ "error": { "codigo": "IMAGEN_ILEGIBLE", "mensaje": "No se pudo detectar la carátula" } }
```

**Criterios de aceptación**
- [ ] Contrato escrito en `docs/architecture/contrato-api.md` y mergeado a `main`
- [ ] Incluye ejemplo de petición y de respuesta para cada ruta
- [ ] Incluye la lista de códigos de error y qué significa cada uno
- [ ] Los tres integrantes lo revisaron y lo aprobaron en el PR
- [ ] El cliente puede construir datos falsos a partir de él sin preguntar nada más

---

# Tarjetas reescritas

---

### T-05 · Configurar pipeline de integración continua

**Etiquetas:** `3` `IS2` `infra`
**Depende de:** T-03, T-04
*(ya no depende de T-01: el stack está decidido)*

**Descripción**

Workflow de GitHub Actions en `.github/workflows/ci.yml`, disparado en cada push y en cada pull
request hacia `main`.

**Dos jobs en paralelo**, porque el repositorio tiene dos lenguajes:

*Job `client`* — trabaja sobre `client/`
- Checkout e instalación de Node en la versión fijada en `.nvmrc`
- Instalación de dependencias
- ESLint
- Build de producción de Vite
- Vitest

*Job `server`* — trabaja sobre `server/`
- Checkout e instalación de Python en la versión fijada en `pyproject.toml`
- Instalación de dependencias
- `ruff check`
- `pytest`

Esta es una de las tarjetas que el profesor de Ingeniería de Software II revisa directamente, junto
con T-04. Lo que le importa es que el pipeline **exista, corra y bloquee el merge cuando algo
falla** — no que cubra mucho.

Las pruebas de integración y el análisis con SonarQube quedan para el Sprint 2 (P-09).

**Criterios de aceptación**
- [ ] `.github/workflows/ci.yml` con los dos jobs
- [ ] El pipeline se dispara automáticamente al abrir un PR
- [ ] Existe al menos una prueba unitaria real por job, que el pipeline ejecuta
- [ ] Los dos checks están marcados como obligatorios en la protección de `main`
- [ ] **Verificado con un PR de prueba con un test fallando: el merge quedó bloqueado**
- [ ] Captura de pantalla del merge bloqueado guardada en `docs/` como evidencia

---

### T-14 · Control transaccional y manejo de errores

**Etiquetas:** `2` `BD` `feature`
**Depende de:** T-13

> ⚠️ **Esta tarjeta se reescribió.** La versión anterior estaba redactada en T-SQL (SQL Server).
> El proyecto usa PostgreSQL — ver T-02a.

**Descripción**

Implementar al menos un procedimiento almacenado en **PL/pgSQL** que registre una lectura con
control transaccional completo y manejo de errores.

El caso de uso natural: insertar una lectura y actualizar el consumo calculado del período en una
sola operación atómica. Si cualquiera de los dos pasos falla, no debe quedar nada a medias.

Estructura esperada:

```sql
CREATE OR REPLACE PROCEDURE registrar_lectura(...)
LANGUAGE plpgsql
AS $$
BEGIN
    -- inserción de la lectura y actualización del consumo del período
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'No se pudo registrar la lectura: %', SQLERRM;
END;
$$;
```

**Sobre `XACT_ABORT`:** no existe en PostgreSQL y no hace falta activarlo. PostgreSQL aborta la
transacción completa por defecto ante cualquier error no capturado, que es exactamente el
comportamiento que la rúbrica busca garantizar con esa opción en SQL Server. **Esa equivalencia hay
que dejarla escrita en la entrega**, porque el profesor va a buscar el mecanismo de la rúbrica y
tiene que encontrar su justificación.

**Criterios de aceptación**
- [ ] Procedimiento en PL/pgSQL con transacción explícita y bloque `EXCEPTION`
- [ ] Errores propagados con `RAISE EXCEPTION` y un mensaje entendible
- [ ] Prueba que **fuerza un error a propósito** y verifica que la transacción se revirtió completa
- [ ] La tabla de equivalencias T-SQL ↔ PL/pgSQL documentada en `database/README.md`
- [ ] Script versionado en `database/scripts/`

---

### T-13 · Scripts de creación, usuarios y roles

**Etiquetas:** `3` `BD` `feature`
**Depende de:** T-12

**Descripción**

Scripts de creación de la base de datos y sus objetos, más los scripts de seguridad, **en
PostgreSQL**.

La rúbrica pide explícitamente usuarios, roles y esquemas aplicando el principio de mínimo
privilegio. Definir al menos:

- Un **rol de aplicación** con `SELECT`, `INSERT` y `UPDATE` solo sobre las tablas que la aplicación
  realmente toca. Sin `DELETE` salvo que se justifique, y sin permisos sobre el esquema.
- Un **rol de solo lectura** con `SELECT`, para consultas y reportes.

Detalle de PostgreSQL que cambia respecto a SQL Server: **el usuario es un rol con `LOGIN`**, no un
objeto separado. Se crean con `CREATE ROLE ... LOGIN PASSWORD ...` y los permisos se otorgan con
`GRANT` sobre el esquema y las tablas.

Las contraseñas **no** se commitean. Los scripts usan variables o marcadores de posición.

**Criterios de aceptación**
- [ ] Script de creación de base de datos, esquema, tablas y restricciones
- [ ] Script de creación de roles y usuarios, con `GRANT` explícito por rol
- [ ] Justificación escrita, rol por rol, de por qué tiene esos permisos y no más
- [ ] Los scripts corren de cero sobre una instancia limpia sin errores
- [ ] Ninguna contraseña real quedó en el repositorio

---

# Tarjetas con ajustes menores

Mantienen su texto original; agregar estos bloques al final de la descripción.

---

### T-09 · Preprocesamiento: detección de carátula y corrección de perspectiva

```
TECNOLOGÍA: Python + OpenCV (opencv-python).

UBICACIÓN: server/app/vision/preprocesamiento.py

REGLA DE ARQUITECTURA: este módulo NO importa nada de FastAPI. Son funciones
puras que reciben una imagen y devuelven un resultado, para poder probarlas con
pytest sin levantar el servidor y para que el trabajo de Computación Gráfica
quede aislado y demostrable por separado.

PRUEBAS: pytest, en server/tests/, con imágenes reales del dataset de T-07.

SEÑALES Y SISTEMAS: documentar cada filtro aplicado y por qué se eligió. El
suavizado y la detección de bordes son convoluciones sobre una señal 2D. Ese
texto se reutiliza cuando salga la rúbrica de ese curso, que todavía no se
publica.
```

---

### T-10 · Segmentación de la ventana del odómetro

```
TECNOLOGÍA: Python + OpenCV.
UBICACIÓN: server/app/vision/segmentacion.py
Misma regla: sin dependencias de FastAPI. Pruebas con pytest.

Si se toma el atajo de posición relativa fija en vez de detección automática,
registrarlo como deuda técnica en docs/ y crear la tarjeta de Sprint 2.
```

---

### T-11 · Reconocimiento de dígitos y medición de exactitud

```
TECNOLOGÍA: Python + la librería elegida en T-02b.
UBICACIÓN: server/app/vision/reconocimiento.py
DEPENDE DE: T-02b (ya no de T-02) y T-10.

RECORDATORIO: el objetivo de esta tarjeta NO es acertar. Es tener el hilo
conectado y medir la exactitud real de partida sobre fotos de campo. Un número
malo, bien explicado, es un resultado válido para la semana 7 y es la línea base
que justifica el Sprint 2.

No maquillar el número. No excluir del cálculo las fotos difíciles.
Reportar el porcentaje sobre TODO el dataset, y aparte el desglose por
condición si aporta.
```

---

### T-15 · Endpoint de recepción de fotografía

```
TECNOLOGÍA: Python + FastAPI + Uvicorn.
UBICACIÓN: server/app/api/
DEPENDE DE: T-04b (contrato de la API), T-05.

Implementa POST /api/lecturas/reconocer y POST /api/lecturas según el contrato
congelado en T-04b. Encadena T-09 → T-10 → T-11 y persiste mediante el
procedimiento almacenado de T-14.

LOGS: estructurados a stdout desde el primer endpoint. Cada petición registra
momento, ruta, código de respuesta, duración e identificador de petición. El
profesor de ISW2 pide logs centralizados (P-05) y agregarlos después sale más
caro. Nunca loguear la imagen completa ni datos personales del abonado.

ERRORES: la respuesta usa la forma uniforme del contrato. Las trazas internas
van al log, nunca al cliente.
```

---

### T-16 · Pantalla de captura en la aplicación

```
TECNOLOGÍA: React + TypeScript sobre Vite. Cámara vía getUserMedia.
UBICACIÓN: client/src/
DEPENDE DE: T-04b (contrato de la API), T-15.

NO ESPERES A T-15. Con el contrato de T-04b congelado desde el lunes, esta
pantalla se construye contra datos falsos y se conecta al backend real cuando
esté listo. Ese es todo el motivo por el que T-04b existe.

La guía visual de encuadre en pantalla no es cosmética: mejora la calidad de la
foto y le baja trabajo al preprocesamiento de T-09.

La corrección manual de la lectura es obligatoria, no opcional. Sabemos que el
reconocimiento va a fallar seguido en este sprint.
```

---

# Sin cambios

T-03, T-04, T-06, T-07, T-08, T-12, T-17, T-18, T-19, T-20 quedan tal cual están en
`MiMedidor_Sprint1_Trello.md`. El Product Backlog (P-01 a P-15) tampoco cambia.

---

# Orden de ejecución actualizado

```
Lunes S6      T-03  T-04  T-02b  T-04b  T-07(inicio)
Martes S6     T-05  T-06  T-07(continúa)
Miércoles S6  T-08  T-09  T-12
Jueves S6     T-09  T-13  T-15
Viernes S6    T-10  T-14  T-15
Lunes S7      T-11  T-16
Martes S7     T-16  T-17
Miércoles S7  T-18  T-19
Jueves S7     T-20 · Sprint Review · Retrospectiva · ENTREGA
```

T-01 y T-02a ya están cerradas. T-04b entra el lunes porque desbloquea a dos personas a la vez.

Orden de corte si el sprint se atrasa: **T-19 primero, luego T-14, luego T-10** (sustituyéndola por
posición fija). **T-18 no se corta nunca** — sin ella no hay hilo de punta a punta y se pierde el
objetivo del sprint.
