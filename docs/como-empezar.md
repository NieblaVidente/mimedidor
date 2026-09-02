# Cómo empezar a trabajar — MiMedidor

Guía de arranque para Yariel e Isaac. Seguila una sola vez; después de esto, todos los días
arrancás directo desde el paso "Trabajar en una tarjeta".

Si algo no funciona, no pelees media hora en silencio — avisá en el grupo. Varios de los tropiezos
de abajo ya los sufrimos y están resueltos acá.

---

## 1. Instalar las herramientas

Todo esto es en **Windows**, con `winget` (viene con Windows 11). Abrí **PowerShell** y pegá los
comandos uno por uno.

> Si usás Mac o Linux, decilo en el grupo y ajustamos — los comandos cambian, pero las
> herramientas son las mismas.

### Git — para versionar el código

```bash
winget install --id Git.Git
```

### GitHub CLI (`gh`) — para crear y revisar Pull Requests desde la terminal

Esta es la que se suma a Git. Git maneja el código local; `gh` habla con GitHub (PRs,
aprobaciones, ver si el CI pasó) sin tener que abrir el navegador cada vez.

```bash
winget install --id GitHub.cli
```

### Node.js 24 — para el cliente (la aplicación web)

```bash
winget install --id OpenJS.NodeJS
```

### Python 3.12 — para el servidor y el procesamiento de imagen

**Importante: tiene que ser 3.12 exactamente**, no la más nueva. Ya nos pasó que el CI agarró
Python 3.14 y una dependencia (Pillow) no compiló.

```bash
winget install --id Python.Python.3.12
```

### Tesseract OCR — el motor de reconocimiento de dígitos

Solo lo necesitás si vas a trabajar en el módulo de lectura (T-09, T-10, T-11), pero instalalo
igual: las pruebas del servidor lo usan y sin él te van a fallar.

```bash
winget install --id tesseract-ocr.tesseract
```

**Cerrá y volvé a abrir PowerShell después de instalar todo**, para que reconozca los comandos
nuevos.

Verificá que todo quedó bien:

```bash
git --version; gh --version; node --version; py -3.12 --version
```

---

## 2. Conectar tu cuenta de GitHub

Una sola vez. Corré:

```bash
gh auth login
```

Elegí: **GitHub.com** → **HTTPS** → **Login with a web browser**.

Te va a mostrar un código de 8 caracteres (tipo `ABCD-1234`). Copialo, abrí
[github.com/login/device](https://github.com/login/device), pegá el código y autorizá.

Con eso queda autenticado para siempre en esa máquina — Git y `gh` van a poder pushear sin
pedirte contraseña cada vez.

---

## 3. Clonar el repositorio

> ⚠️ **Elegí una carpeta cuya ruta NO tenga espacios ni tildes.** Nos comimos un problema real por
> esto: las pruebas del cliente (Vitest) se colgaban indefinidamente porque la ruta tenía un
> espacio. Está parcheado en la config, pero es mejor no tentar a la suerte.
>
> ✅ Bien: `C:\dev\mimedidor`
> ❌ Mal: `C:\Users\vos\Documentos\Proyectos 2026\mimedidor`

```bash
cd C:\dev
gh repo clone NieblaVidente/mimedidor
cd mimedidor
```

---

## 4. Preparar el entorno

### Cliente (la aplicación web)

```bash
cd client
npm install
```

Probá que funciona:

```bash
npm run lint; npm run build; npm run test
```

Las tres tienen que pasar. Para levantar la app y verla en el navegador: `npm run dev`.

### Servidor (la API y el procesamiento de imagen)

Desde la raíz del repo:

```bash
cd server
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

El `venv` es un Python aislado solo para este proyecto — así las dependencias no se mezclan con
otras cosas que tengas instaladas. La carpeta `.venv/` no se sube a Git, es tuya y local.

Probá que funciona:

```bash
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pytest -v
```

Ambas tienen que pasar. Para levantar la API: `.venv\Scripts\uvicorn.exe app.main:app --reload`.

### Base de datos

Necesitás PostgreSQL corriendo. Creá la base y corré los scripts **desde `database/scripts/`**
(los scripts se llaman entre sí por ruta relativa, así que desde otra carpeta fallan):

```bash
createdb mimedidor
```

```bash
cd database/scripts
psql -d mimedidor -v ON_ERROR_STOP=1 -v password_app='clave-local' -v password_lectura='clave-local' -f ejecutar_todo.sql
```

Eso crea el esquema, las tablas, los dos roles y el procedimiento transaccional. Si te falla con
*"el rol mimedidor_app ya existe"*, es porque los roles son objetos del clúster y no de la base
— borralos con `DROP ROLE` y volvé a correrlo (está explicado en `database/README.md`).

---

## 4b. Levantar el sistema completo

Las tres piezas por separado no alcanzan: hasta la tarjeta T-21 nunca se habían ejecutado juntas,
y en cuanto se hizo aparecieron dos errores que ninguna prueba unitaria podía ver. Así se levanta
todo, en tres terminales:

**Terminal 1 — la API**, con las credenciales de la base en variables de entorno:

```bash
cd server
PGHOST=localhost PGDATABASE=mimedidor PGUSER=mimedidor_app PGPASSWORD=clave-local .venv/Scripts/uvicorn.exe app.main:app --reload
```

**Terminal 2 — el cliente:**

```bash
cd client
npm run dev
```

**Terminal 3 — comprobar que se hablan entre sí:**

```bash
curl http://localhost:5173/api/salud
```

Tiene que responder `{"estado":"ok"}`. Fijate que el puerto es el **5173** (el de Vite), no el
8000: `client/vite.config.ts` tiene un proxy que manda todo lo que empiece con `/api` al servidor.
Sin ese proxy el navegador le pediría `/api/...` al servidor de Vite y recibiría el `index.html`
en vez de la respuesta de la API — que es exactamente el bug que arregló T-21.

Después abrí `http://localhost:5173` en el navegador. Para probar el hilo completo necesitás un
medidor en la base; podés crear uno con la cadena mínima usuario → vivienda → medidor (hay un
ejemplo en `server/tests/test_integracion_db.py`).

### Pruebas contra la base real

Con la base levantada y las variables de entorno puestas:

```bash
cd server
.venv/Scripts/python.exe -m pytest tests/test_integracion_db.py -v
```

Si no hay base disponible se saltan solas, así que no estorban. En CI sí corren siempre, en el
job `Base de datos`.

### Prueba end-to-end (Cypress)

Recorre el hilo completo como lo haría un abonado: cámara → lectura → historial → factura →
comparación, contra el sistema entero corriendo. Nada sustituido.

Antes de correrla, sembrá un medidor de prueba (la API no tiene ninguna ruta para crear
medidores, así que tiene que existir en la base):

```bash
cd database/scripts
psql -d mimedidor -v ON_ERROR_STOP=1 -f datos_de_prueba.sql
```

Con la API y el cliente levantados (§4b), en otra terminal:

```bash
cd client
npm run e2e
```

Para verla correr paso a paso en una ventana, útil cuando algo falla: `npm run e2e:abrir`.

**Tiene que correr en un navegador Chromium** — Electron (el que Cypress trae y usa por defecto),
Chrome o Edge. La prueba necesita una cámara falsa, que se activa con unos parámetros propios de
Chromium; **en Firefox no existen** y la prueba fallaría por el navegador, no por el código. Para
elegir uno: `npx cypress run --browser edge`.

La prueba deja datos en la base (las lecturas y facturas que registra). No molesta para volver a
correrla, pero si querés partir de cero: borrá la base, volvé a correr `ejecutar_todo.sql` y
después `datos_de_prueba.sql`.

---

## 5. Lo primero que tenés que leer

Abrí **[`CLAUDE.md`](../CLAUDE.md)** en la raíz del repositorio. Es la fuente de verdad del
proyecto: qué es MiMedidor, el stack completo con la justificación de cada decisión, las
convenciones de código, qué evalúa cada curso, y una lista de cosas que **no** hay que hacer.

Dos cosas que conviene que sepas de entrada:

- **Si un Issue contradice `CLAUDE.md`, manda `CLAUDE.md`.** Las decisiones técnicas ya cerradas
  pesan más que lo que diga una tarea escrita antes.
- **El contrato de la API está congelado** en
  [`docs/architecture/contrato-api.md`](architecture/contrato-api.md). Si vas a construir una
  pantalla, trabajá contra los ejemplos de ese documento sin esperar a que el backend exista.

---

## 6. Cómo funciona `git pull` (no es magia)

Esto conviene entenderlo antes de seguir, porque se presta a confusión: **Git nunca actualiza tus
archivos solo.** Cuando clonás el repo, tu compu queda con una copia congelada de cómo estaba
`main` en ese momento. Si otro integrante mergea un PR después, GitHub cambia — pero tu carpeta en
disco se queda exactamente igual hasta que vos se lo pidas explícitamente. Podés tener el proyecto
abierto una semana entera y Git no te va a avisar con ninguna notificación de que hay cambios
nuevos.

El comando que lo hace:

```bash
git pull origin main
```

En realidad son dos pasos en uno:
1. **`fetch`** — baja de GitHub la información de qué cambió, pero todavía no toca tus archivos
2. **`merge`** — recién ahí actualiza tus archivos locales con esos cambios

### Cuándo correrlo

**Siempre antes de crear una rama nueva** (vas a ver `git checkout main` + `git pull origin main`
repetido dos veces más abajo en el ciclo de trabajo) — así tu rama nace desde la versión más
reciente de `main`, no desde una vieja.

Si estás a mitad de una tarjeta y alguien mergea algo mientras tanto, **tu rama actual no se
entera sola.** Normalmente no hace falta hacer nada — tu PR se combina igual al mergear — pero si
en algún momento querés traer esos cambios a tu rama sin esperar:

```bash
git checkout tu-rama
git merge main
```

### Si tenés cambios sin guardar cuando hacés `pull`

Git intenta combinar todo automáticamente. Si los cambios no chocan, lo resuelve solo y no ves
nada raro. Si vos y otro integrante tocaron **la misma línea del mismo archivo**, Git se detiene y
te pide que decidas cuál versión queda — eso se llama **conflicto de merge**. No es un error grave
ni significa que rompiste algo; simplemente Git no puede adivinar cuál de las dos versiones
querés, así que te lo pregunta a vos.

---

## 7. Trabajar en una tarea

Este es el ciclo de todos los días. **Nunca se trabaja directo sobre `main`** — está protegida y
GitHub va a rechazar el push (ya lo probamos).

**1. Tomá un Issue** del milestone de la entrega en curso y asignate a vos mismo:

```bash
gh issue list --milestone "Semana 10 — Segundo avance"
```

```bash
gh issue view 33
```

Para asignártelo: `gh issue edit 33 --add-assignee @me`

**2. Actualizá tu copia local y creá una rama:**

```bash
git checkout main
git pull origin main
git checkout -b feature/descripcion-corta
```

Convención de nombres: `feature/` para funcionalidad nueva, `bugfix/` para correcciones.
Una rama por Issue, no una rama por persona.

**3. Programá.** Corré las pruebas localmente antes de subir nada — si fallan acá, van a fallar en
el CI y te van a bloquear el merge.

**4. Commiteá y subí:**

```bash
git add .
git commit -m "Descripción de lo que hiciste"
git push -u origin feature/descripcion-corta
```

**5. Abrí el Pull Request:**

```bash
gh pr create --title "T-09 · Descripción de la tarea" --body "Qué hace y cómo lo probaste. Closes #33"
```

Poné el código de la tarea (`T-09`) en el título, y **`Closes #33` en la descripción**, con el
número del Issue. Eso hace que el Issue se cierre solo al mergear y quede enlazado al código que
lo resolvió — no hay que acordarse de moverlo a mano, que es justamente lo que se nos olvidaba
con el tablero.

**6. Esperá el CI y la aprobación.** Para ver cómo va el pipeline:

```bash
gh pr checks --watch
```

**Alguien más del equipo tiene que aprobarlo** — GitHub no te deja aprobar tu propio PR. Avisá en
el grupo cuando esté listo. Aprueba quien esté disponible, no hay turnos fijos.

**7. Cuando esté aprobado y en verde, mergealo:**

```bash
gh pr merge --merge
```

**8. Volvé a `main` y limpiá:**

```bash
git checkout main
git pull origin main
git branch -d feature/descripcion-corta
```

El Issue se cerró solo al mergear, gracias al `Closes #N` del Pull Request. Arrancás con el
siguiente.

---

## 8. Definition of Done

Una tarjeta está **Hecha** cuando:

1. **El Issue está asignado** a quien lo trabaja, y el código está en una rama `feature/` o `bugfix/`
2. Se abrió un Pull Request hacia `main`, y **se pidió la revisión a los otros dos integrantes**
3. Al menos otro integrante aprobó el PR
4. Los checks de CI pasaron en verde
5. El PR fue mergeado a `main`
6. La documentación asociada quedó actualizada si aplica
7. Los criterios de aceptación de la tarjeta se cumplen y fueron verificados

Tarjetas de tipo `spike`, `campo` o `doc` (que no producen código): solo aplican 6 y 7.

Acordado por los tres el 2026-08-12. Detalle en
[`docs/definition-of-done.md`](definition-of-done.md).

---

## 9. Si usás Claude Code

Abrí Claude Code **parado en la carpeta del repositorio** (`C:\dev\mimedidor`). Va a cargar
`CLAUDE.md` automáticamente y ya va a saber el stack, las convenciones y qué no hacer.

No hace falta que le pegues nada más. Si querés arrancar rápido, un buen primer mensaje es:

> Leé CLAUDE.md y docs/como-empezar.md. Voy a trabajar en el Issue #NN. Leelo con
> `gh issue view NN`, creá la rama y ayudame a implementarlo.

Recordale que **no debe pushear a `main` ni aprobar PRs por vos** — la aprobación tiene que ser
una persona real leyendo el código, porque eso es justo lo que evalúa el curso de Ingeniería de
Software II.

---

## 10. Cosas que ya nos pasaron (para que no las sufras de nuevo)

| Síntoma | Causa | Solución |
|---|---|---|
| `git push` a `main` rechazado con `GH013` | `main` está protegida a propósito | Creá una rama y abrí un PR |
| Las pruebas del cliente se cuelgan sin terminar | Ruta del proyecto con espacios | Cloná en una ruta sin espacios (`C:\dev\`) |
| El CI falla instalando Pillow | Python distinto a 3.12 | Está fijado en `server/.python-version`; localmente usá `py -3.12` |
| `pytest` falla en las pruebas de OCR | Falta Tesseract | `winget install --id tesseract-ocr.tesseract` |
| `gh: command not found` después de instalarlo | La terminal no recargó el PATH | Cerrá y reabrí PowerShell |
| Tu aprobación de un PR "desapareció" | Se subió un commit nuevo después de aprobar | Es a propósito (regla de la rama); hay que aprobar de nuevo |

---

## 11. Enlaces

- **Repositorio:** https://github.com/NieblaVidente/mimedidor
- **Tareas (Issues):** https://github.com/NieblaVidente/mimedidor/issues
- **Tablero de Trello del Sprint 1** (congelado, solo lectura): https://trello.com/b/St9jsJir/mimedidor
- **Contexto del proyecto:** [`CLAUDE.md`](../CLAUDE.md)
- **Contrato de la API:** [`docs/architecture/contrato-api.md`](architecture/contrato-api.md)
- **Registro de ceremonias:** [`docs/scrum/`](scrum/)
