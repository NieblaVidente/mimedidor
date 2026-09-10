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

# Dos usuarios distintos, a propósito:
#   mimedidor  → el que CORRE el servicio. No inicia sesión.
#   despliegue → el que ESCRIBE los archivos por SSH desde el pipeline. No corre nada.
# Separarlos hace que la llave guardada en GitHub no sea también la del proceso en producción.
sudo useradd --system --home /opt/mimedidor --shell /usr/sbin/nologin mimedidor
sudo useradd --create-home --shell /bin/bash despliegue

sudo mkdir -p /opt/mimedidor/servidor /opt/mimedidor/versiones /var/www/mimedidor
sudo python3.12 -m venv /opt/mimedidor/venv
sudo chown -R mimedidor:mimedidor /opt/mimedidor

# El pipeline escribe en estos tres directorios, así que tienen que ser del usuario de
# despliegue; el servicio los lee por el grupo.
sudo chown -R despliegue:mimedidor \
    /opt/mimedidor/servidor /opt/mimedidor/versiones /var/www/mimedidor
sudo chmod -R g+rX /opt/mimedidor/servidor

# El entorno virtual lo escribe `pip` durante el despliegue, corriendo como `despliegue`.
sudo chown -R despliegue:mimedidor /opt/mimedidor/venv
```

Y la llave pública que le corresponde a `SSH_LLAVE_PRIVADA` se autoriza para ese usuario:

```bash
sudo -u despliegue mkdir -p ~despliegue/.ssh
sudo -u despliegue tee -a ~despliegue/.ssh/authorized_keys < llave_de_despliegue.pub
sudo -u despliegue chmod 700 ~despliegue/.ssh
sudo -u despliegue chmod 600 ~despliegue/.ssh/authorized_keys
```

> **Estos dos bloques se corrigieron después de escribir el documento original.** La versión
> anterior creaba solo el usuario `mimedidor`, mientras que el `sudoers` de más abajo daba permiso
> a `despliegue` — un usuario que nunca se creaba. Y aunque hubiera existido, `/var/www/mimedidor`
> quedaba de `root` y `/opt/mimedidor` de `mimedidor`, así que **los dos `rsync` del pipeline
> habrían fallado por permisos en el primer despliegue real.**

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

Es también el único permiso elevado que necesita `infra/revertir.sh` (sección 6): restaura
archivos como `despliegue` y reinicia el servicio con este mismo `sudo` acotado.

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
restart` igual devuelve éxito.

Se comprueban **dos cosas**, hasta diez veces, porque una sola no alcanza:

| Consulta | Se espera | Qué prueba |
|---|---|---|
| `/api/salud` | `200` | Uvicorn está sirviendo detrás de nginx |
| `/api/lecturas?medidor_id=00000000-…` | `404` | La aplicación **consultó PostgreSQL** y contestó |

El segundo es el que atrapa la falla más probable de un servidor recién armado: credenciales de
base de datos mal puestas en `/etc/mimedidor.env`. Con solo `/api/salud` el despliegue daría verde
con la base inalcanzable, porque esa ruta no la toca.

Ese `404` es la respuesta correcta, no un error: lo produce `medidor_existe`, que solo puede
responder después de consultar la base. Por eso el paso compara el código de estado en vez de usar
`curl -f`.

> **Este paso estaba mal y se corrigió junto con la sección 6.** Consultaba `/api/lecturas` **sin
> parámetros** con `curl -fsS`. Como `medidor_id` es obligatorio, la respuesta era `400`, y `-f`
> la trataba como error (salida 22): **todo despliegue habría terminado en rojo aunque hubiera
> funcionado.** No se había detectado porque el job nunca llegó a correr — falta el servidor.
>
> Los tres códigos —`200`, `404` y el `400` de la versión vieja— se comprobaron contra el
> servidor corriendo contra PostgreSQL, no se dedujeron del código.

### El interruptor: `URL_PRODUCCION`

El job **solo corre si `vars.URL_PRODUCCION` está definida**. Mientras no lo esté aparece como
`Skipped`, y `main` no se pone en rojo por una infraestructura que todavía no se creó.

> Un `Skipped` en «Desplegar a producción» **no es un fallo**: significa que el despliegue aún no
> está configurado, o que la corrida viene de un Pull Request (donde nunca debe desplegar).

En cuanto se defina la variable, el despliegue se activa solo, sin volver a tocar el workflow. Es
a propósito: un job desactivado a mano dentro del archivo es un job que se queda apagado para
siempre, porque nadie se acuerda de volver a prenderlo.

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

---

## 6. Cómo revertir un despliegue que salió mal

Hay **dos caminos**, y la diferencia entre ellos es cuánto tiempo puede estar caída la
aplicación. El primero es el normal; el segundo es para cuando no se puede esperar.

### 6.1 La vía normal: revertir el commit en `main`

```bash
git revert <hash-del-merge-que-rompió> -m 1
git push origin main
```

El pipeline corre solo y despliega la versión revertida.

**Es la vía correcta casi siempre**, porque deja `main` y producción diciendo lo mismo. Si en vez
de esto se arregla el servidor a mano, el repositorio pasa a mentir sobre lo que está corriendo, y
el próximo despliegue vuelve a poner la versión rota.

**Lo que cuesta:** entre 3 y 5 minutos, porque tienen que pasar de nuevo los cuatro verificadores
antes de que el job de despliegue arranque. **La aplicación sigue caída todo ese rato.** Y si
GitHub Actions está con problemas, este camino no existe.

### 6.2 La vía de emergencia: volver a la versión anterior en el servidor

```bash
ssh despliegue@<host> 'bash ~/revertir.sh'
```

Tarda segundos. El script [`infra/revertir.sh`](../infra/revertir.sh) restaura la copia de la
versión anterior, reinstala sus dependencias, reinicia el servicio y **verifica que responda**
antes de darse por exitoso.

**El pipeline lo deja en el servidor en cada despliegue**, en el home del usuario `despliegue`.
Dos motivos: que el script sea siempre el de la versión que está corriendo, y que no viva dentro
de `/opt/mimedidor/servidor/`, que se sincroniza con `--delete` — un despliegue roto podría
llevarse puesta la herramienta para deshacerlo.

Esa copia la deja el propio pipeline en `/opt/mimedidor/versiones/`, en el paso «Guardar la
versión que está corriendo», **antes** de publicar la nueva. Sin ese paso no habría nada a qué
volver: los `rsync --delete` pisan la versión viva.

El script también guarda la versión que falló, en `cliente-fallido` y `servidor-fallido`.
**No la borren antes de averiguar qué pasó**, o revertir se lleva puesta la evidencia.

> **Después de usar 6.2 hay que hacer 6.1 igual.** El servidor quedó en la versión anterior y
> `main` sigue con la rota: el próximo merge la vuelve a desplegar. La emergencia se resuelve con
> 6.2; el repositorio se ordena con 6.1.

### 6.3 Qué NO revierte ninguno de los dos

**La base de datos.** Si el despliegue que falló venía acompañado de un cambio de esquema
aplicado a mano (sección 5), revertir el código no lo deshace, y **la versión anterior puede no
entender el esquema nuevo**.

En ese caso hay que revertir la migración a mano, y ahí sirve la estrategia de respaldo de T-29
(`database/scripts/restaurar.sh`). Restaurar un respaldo **pierde los datos posteriores**, así
que es la última opción, no la primera.

Es la razón concreta por la que las migraciones no se aplican automáticamente: un despliegue de
código se deshace en segundos, un cambio de esquema no.

### 6.4 Cuándo cada uno

| Situación | Camino |
|---|---|
| Un error visible pero la aplicación funciona | **6.1**. No hay apuro |
| Producción caída, o rota en medio de la feria | **6.2** primero, **6.1** después |
| El despliegue falló pero el anterior sigue en pie | **Ninguno.** El job verifica antes de terminar; si el `rsync` falló a mitad, revisá el log antes de tocar nada |
| El fallo vino con un cambio de esquema | **6.2** y leer 6.3 antes de seguir |

### 6.5 Lo que todavía no está probado

**Este procedimiento no se ha ejecutado nunca contra un servidor real**, porque el servidor aún no
existe. Está escrito a partir de cómo funciona el pipeline, no de haberlo visto funcionar.

Queda anotado así en vez de darlo por bueno. **El primer despliegue real tiene que incluir una
prueba de reversión**: desplegar, revertir, comprobar que la aplicación vuelve. Un procedimiento
de emergencia que se estrena durante la emergencia no es un procedimiento.
