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

### Node.js 24 — para el cliente (la PWA)

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

### Cliente (la PWA)

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

Ambas tienen que pasar (2 pruebas). Para levantar la API: `.venv\Scripts\uvicorn.exe app.main:app --reload`.

---

## 5. Lo primero que tenés que leer

Abrí **[`CLAUDE.md`](../CLAUDE.md)** en la raíz del repositorio. Es la fuente de verdad del
proyecto: qué es MiMedidor, el stack completo con la justificación de cada decisión, las
convenciones de código, qué evalúa cada curso, y una lista de cosas que **no** hay que hacer.

Dos cosas que conviene que sepas de entrada:

- **Si una tarjeta de Trello contradice `CLAUDE.md`, manda `CLAUDE.md`.** Varias tarjetas se
  escribieron antes de que se cerraran decisiones técnicas; la sección §9 lista cuáles.
- **El contrato de la API está congelado** en
  [`docs/architecture/contrato-api.md`](architecture/contrato-api.md). Si vas a construir una
  pantalla, trabajá contra los ejemplos de ese documento sin esperar a que el backend exista.

---

## 6. Trabajar en una tarjeta

Este es el ciclo de todos los días. **Nunca se trabaja directo sobre `main`** — está protegida y
GitHub va a rechazar el push (ya lo probamos).

**1. Tomá una tarjeta del Sprint Backlog en Trello** y movela a "En curso". Asignate a vos mismo.

**2. Actualizá tu copia local y creá una rama:**

```bash
git checkout main
git pull origin main
git checkout -b feature/descripcion-corta
```

Convención de nombres: `feature/` para funcionalidad nueva, `bugfix/` para correcciones.
Una rama por tarjeta, no una rama por persona.

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
gh pr create --title "T-09 · Descripción de la tarjeta" --body "Qué hace y cómo lo probaste"
```

Poné el código de la tarjeta (`T-09`) en el título. Movela a "En revisión (PR)" en Trello.

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

Movés la tarjeta a "Hecho" en Trello y arrancás con la siguiente.

---

## 7. Definition of Done

Una tarjeta está **Hecha** cuando:

1. El código está en una rama `feature/` o `bugfix/`
2. Se abrió un Pull Request hacia `main`
3. Al menos otro integrante aprobó el PR
4. Los checks de CI pasaron en verde
5. El PR fue mergeado a `main`
6. La documentación asociada quedó actualizada si aplica
7. Los criterios de aceptación de la tarjeta se cumplen y fueron verificados

Tarjetas de tipo `spike`, `campo` o `doc` (que no producen código): solo aplican 6 y 7.

Acordado por los tres el 2026-08-12. Detalle en
[`docs/definition-of-done.md`](definition-of-done.md).

---

## 8. Si usás Claude Code

Abrí Claude Code **parado en la carpeta del repositorio** (`C:\dev\mimedidor`). Va a cargar
`CLAUDE.md` automáticamente y ya va a saber el stack, las convenciones y qué no hacer.

No hace falta que le pegues nada más. Si querés arrancar rápido, un buen primer mensaje es:

> Leé CLAUDE.md y docs/como-empezar.md. Voy a trabajar en la tarjeta T-XX de Trello: [pegá acá la
> descripción de la tarjeta]. Creá la rama y ayudame a implementarla.

Recordale que **no debe pushear a `main` ni aprobar PRs por vos** — la aprobación tiene que ser
una persona real leyendo el código, porque eso es justo lo que evalúa el curso de Ingeniería de
Software II.

---

## 9. Cosas que ya nos pasaron (para que no las sufras de nuevo)

| Síntoma | Causa | Solución |
|---|---|---|
| `git push` a `main` rechazado con `GH013` | `main` está protegida a propósito | Creá una rama y abrí un PR |
| Las pruebas del cliente se cuelgan sin terminar | Ruta del proyecto con espacios | Cloná en una ruta sin espacios (`C:\dev\`) |
| El CI falla instalando Pillow | Python distinto a 3.12 | Está fijado en `server/.python-version`; localmente usá `py -3.12` |
| `pytest` falla en las pruebas de OCR | Falta Tesseract | `winget install --id tesseract-ocr.tesseract` |
| `gh: command not found` después de instalarlo | La terminal no recargó el PATH | Cerrá y reabrí PowerShell |
| Tu aprobación de un PR "desapareció" | Se subió un commit nuevo después de aprobar | Es a propósito (regla de la rama); hay que aprobar de nuevo |

---

## 10. Enlaces

- **Repositorio:** https://github.com/NieblaVidente/mimedidor
- **Tablero de Trello:** https://trello.com/b/St9jsJir/mimedidor
- **Contexto del proyecto:** [`CLAUDE.md`](../CLAUDE.md)
- **Contrato de la API:** [`docs/architecture/contrato-api.md`](architecture/contrato-api.md)
- **Registro de ceremonias:** [`docs/scrum/`](scrum/)
