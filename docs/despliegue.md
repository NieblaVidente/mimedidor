# Despliegue y entrega continua — T-28

Cómo llega a producción lo que se mergea a `main`, por qué se eligió este destino, y qué
**no** está automatizado a propósito.

---

## 1. Destino elegido: un servidor Ubuntu propio

Se descartaron las plataformas gestionadas. La decisión no se tomó por precio sino por dos
restricciones que ya existen en el código y que recortan las opciones antes de comparar
servicios.

### El cliente asume mismo origen

`client/src/api/*.ts` llama rutas relativas (`/api/…`). Es la misma razón por la que
`vite.config.ts` necesita un proxy en desarrollo, y por la que el hilo completo no funcionaba
antes de T-21. El servidor **no monta CORS** (`server/app/main.py`).

Separar el cliente en un alojamiento estático y la API en otro los pondría en orígenes distintos
y obligaría a agregar CORS — o sea, a cambiar el contrato de la interfaz, que está congelado
(`CLAUDE.md` §11). Aquí nginx sirve las dos piezas desde un único origen y la suposición del
código sigue siendo cierta en producción, igual que en desarrollo.

### El servidor necesita Tesseract nativo

`pytesseract` es una envoltura sobre el binario de Tesseract, que se instala con
`apt-get install tesseract-ocr` (`CLAUDE.md` §3). Las plataformas que solo aceptan `pip install`
no sirven, y las que resuelven paquetes de sistema suelen pedir un `Dockerfile` — que está fuera
de alcance por decisión del profesor (`CLAUDE.md` §8).

### Lo que decidió el empate

El pipeline de integración continua **ya provisiona exactamente este stack**: instala Tesseract
con `apt-get` y levanta PostgreSQL 16 nativo, sin contenedores. Desplegar sobre un Ubuntu igual
reutiliza conocimiento que el equipo ya tiene y ya está probado en cada Pull Request, en vez de
sumar el modelo mental de una plataforma nueva a mitad de sprint.

**Lo que cuesta:** el servidor se paga por mes, y hay que administrar una llave SSH como secreto
del repositorio. Queda anotado como el precio de la decisión.

---

## 2. Cómo queda armado

```
Internet → nginx :80
             ├── /            → /var/www/mimedidor        (build del cliente)
             └── /api/        → 127.0.0.1:8000            (uvicorn, systemd)
                                      └── PostgreSQL 16 en localhost
```

Uvicorn escucha **solo en loopback**: no se llega a la API sin pasar por nginx.

Los archivos de configuración viven versionados en [`infra/`](../infra):

| Archivo | Destino en el servidor |
|---|---|
| `infra/nginx-mimedidor.conf` | `/etc/nginx/sites-available/mimedidor` |
| `infra/mimedidor.service` | `/etc/systemd/system/mimedidor.service` |

---

## 3. Preparación del servidor — una sola vez

```bash
sudo apt-get update
sudo apt-get install -y nginx postgresql-16 tesseract-ocr python3.12-venv rsync

sudo useradd --system --home /opt/mimedidor --shell /usr/sbin/nologin mimedidor
sudo mkdir -p /opt/mimedidor/servidor /var/www/mimedidor
sudo python3.12 -m venv /opt/mimedidor/venv
sudo chown -R mimedidor:mimedidor /opt/mimedidor
```

La base de datos se crea siguiendo [`database/README.md`](../../database/README.md) y corriendo
`database/scripts/ejecutar_todo.sql`. **No lo hace el pipeline** — ver la sección 5.

Las credenciales van en `/etc/mimedidor.env`, con las variables estándar de libpq que ya usa
`server/app/db/conexion.py`:

```
PGHOST=localhost
PGPORT=5432
PGDATABASE=mimedidor
PGUSER=mimedidor_app
PGPASSWORD=...
```

```bash
sudo chown root:mimedidor /etc/mimedidor.env
sudo chmod 640 /etc/mimedidor.env      # que no lo lea cualquiera del sistema
```

Ese archivo vive **fuera** de `/opt/mimedidor/servidor` a propósito: el despliegue sincroniza ese
directorio con `rsync --delete`, y una credencial adentro se borraría en el primer despliegue.

### Permiso acotado para reiniciar

El usuario del despliegue necesita reiniciar el servicio, y nada más:

```
# /etc/sudoers.d/mimedidor-despliegue
despliegue ALL=(root) NOPASSWD: /usr/bin/systemctl restart mimedidor
```

Se limita a ese comando exacto. Un `NOPASSWD: ALL` convertiría la llave SSH guardada en GitHub
en acceso completo de administrador al servidor.

---

## 4. Qué hace el pipeline

El job `desplegar` vive en [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) y corre
**solo** cuando se empuja a `main`.

Está encadenado con `needs: [client, server, database, e2e]`. Esa dependencia es lo que hace que
no se pueda desplegar algo en rojo: no es un acuerdo del equipo, es una condición del pipeline.

Pasos: construye el cliente → publica `dist/` y `server/` por `rsync` → instala dependencias y
reinicia el servicio → **verifica que producción responda**.

Ese último paso importa más de lo que parece. Reiniciar un servicio no prueba que haya arrancado:
si el proceso muere al segundo por una dependencia rota o una credencial mal puesta, `systemctl
restart` igual devuelve éxito. El pipeline consulta una ruta real hasta diez veces antes de darse
por vencido, así que un despliegue en verde significa que la aplicación **está respondiendo**.

### Secretos y variables que hay que crear en GitHub

Los crea una persona en `Settings → Secrets and variables → Actions`. **No viven en el
repositorio ni los puede crear una herramienta.**

| Nombre | Tipo | Qué es |
|---|---|---|
| `SSH_HOST` | secreto | IP o dominio del servidor |
| `SSH_USUARIO` | secreto | Usuario de despliegue (el del sudoers de arriba) |
| `SSH_LLAVE_PRIVADA` | secreto | Llave privada, **exclusiva de este uso**, no la personal de nadie |
| `SSH_HOST_KEY` | secreto | Salida de `ssh-keyscan <host>` — fija la identidad del servidor |
| `URL_PRODUCCION` | variable | URL pública, p. ej. `http://203.0.113.10` |

`SSH_HOST_KEY` evita `StrictHostKeyChecking=no`, que aceptaría como válido a cualquier host que
conteste en esa dirección.

---

## 5. Lo que **no** está automatizado, y por qué

**El esquema de base de datos no se aplica en el despliegue.** Es deliberado:

- `database/scripts/02_tablas.sql` y `03_roles_permisos.sql` **no son idempotentes**: no usan
  `IF NOT EXISTS`. Correrlos en cada despliegue fallaría en el segundo.
- Aplicar cambios de esquema automáticamente sobre una base con datos es una decisión mayor que
  lo que pide esta tarjeta, y merece la suya.

Mientras tanto, un cambio de esquema se aplica a mano siguiendo `database/README.md`, con los
scripts numerados de `database/migrations/`. **Queda como limitación conocida, no como olvido.**

Tampoco hay HTTPS todavía. Para la feria conviene resolverlo con Let's Encrypt, que necesita un
dominio: hasta que exista, el sitio va por HTTP. Anotado como pendiente.
