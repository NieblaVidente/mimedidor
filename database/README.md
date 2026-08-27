# Base de datos — MiMedidor

Motor: **PostgreSQL 16**, confirmado como opción válida por el profesor del componente de Base de Datos (rúbrica exige motor relacional, no un motor específico). Versión fijada en `CLAUDE.md` §3.

## Equivalencia de mecanismos respecto a la rúbrica

La rúbrica describe los mecanismos de control transaccional con vocabulario de T-SQL (SQL Server). La siguiente tabla documenta su equivalente en PostgreSQL/PL-pgSQL, usado en este proyecto:

| Mecanismo en la rúbrica | Equivalente en PostgreSQL |
|---|---|
| `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK` | Igual — sintaxis estándar SQL, soportada tal cual |
| `TRY...CATCH` | Bloque `BEGIN ... EXCEPTION WHEN ... END` dentro de una función o procedimiento en PL/pgSQL |
| `THROW` | `RAISE EXCEPTION 'mensaje'` |
| `XACT_ABORT` | No requiere activación explícita: PostgreSQL aborta automáticamente la transacción completa ante cualquier error no capturado |

## Estructura

- `scripts/` — creación de base de datos, tablas, esquemas, roles y permisos.
- `migrations/` — cambios incrementales al esquema, en orden.

## Modelo

Diagrama entidad-relación, diccionario de datos y justificación de 3FN en
[`docs/architecture/modelo-datos.md`](../docs/architecture/modelo-datos.md) (tarjeta T-12).

## Cómo correr los scripts (T-13)

Sobre una instancia de PostgreSQL 16 limpia, con la base de datos ya creada:

```bash
createdb mimedidor

psql -d mimedidor \
     -v password_app='cambiar-esta-clave' \
     -v password_lectura='cambiar-esta-clave' \
     -f database/scripts/ejecutar_todo.sql
```

Las contraseñas se pasan como variables de `psql` (`-v`), nunca quedan escritas en los scripts
ni en el repositorio. En local usá cualquier valor; en un entorno real, generalas aparte y
pasalas desde una variable de entorno, no las tipees en el historial de la terminal.

`ejecutar_todo.sql` corre en orden `01_esquema.sql` → `02_tablas.sql` →
`03_roles_permisos.sql` → `04_procedimiento_registrar_lectura.sql`. Se puede correr cada
archivo por separado en ese mismo orden si se prefiere revisar paso a paso.

**Nota si volvés a correrlo sobre la misma instancia local:** los roles (`CREATE ROLE`) son
objetos del clúster, no de la base de datos — borrar y recrear `mimedidor` con `dropdb`/`createdb`
no borra `mimedidor_app` ni `mimedidor_lectura`. Si `03_roles_permisos.sql` falla con
`el rol "mimedidor_app" ya existe`, borralos primero: `DROP ROLE mimedidor_app;` y
`DROP ROLE mimedidor_lectura;` (conectado como superusuario). En CI no hace falta — cada corrida
arranca con un clúster nuevo.

## Procedimiento `registrar_lectura` (T-14)

Valida que la lectura nueva no sea menor que la última registrada para ese medidor
(`LECTURA_INVALIDA` en `docs/architecture/contrato-api.md`) e inserta la lectura junto con su
evento de auditoría (`lectura_evento`, Opción C — ver
`docs/architecture/modelo-datos.md` §5.2) como una sola operación atómica.

Corre con los privilegios de quien lo llama (comportamiento por defecto de PostgreSQL, sin
`SECURITY DEFINER`), así que el rol `mimedidor_app` solo puede hacer con el procedimiento lo
mismo que ya podría hacer con `INSERT` directo sobre `lectura`/`lectura_evento` — no hay
elevación de privilegios escondida en el procedimiento.

`verificar_registrar_lectura.sql` es la prueba que exige el criterio de aceptación de T-14: crea
datos de prueba, registra una lectura válida, **fuerza a propósito** una lectura inválida (menor
a la anterior) y confirma que la transacción no dejó nada a medias. Todo el script corre dentro
de un `BEGIN`/`ROLLBACK` explícito, así que no deja residuos — se puede correr tantas veces como
haga falta, y el job `database` de CI lo corre en cada PR.

```bash
psql -d mimedidor -U mimedidor_app -v ON_ERROR_STOP=1 -f database/scripts/verificar_registrar_lectura.sql
```

## Respaldo y recuperación (T-29)

| | |
|---|---|
| Tipo | Lógico completo, `pg_dump -Fc` (formato *custom*: comprimido y con restauración selectiva vía `pg_restore`, a diferencia de un volcado plano en texto) |
| Alcance | La base completa, más los roles del clúster aparte con `pg_dumpall --roles-only` — los roles no son objetos de la base de datos sino del clúster (ver la nota de §"Cómo correr los scripts" arriba) |
| Frecuencia | Diaria en desarrollo activo, y **obligatoria antes de cada entrega** |
| Retención | Los últimos 7 respaldos de cada tipo, en rotación — `respaldar.sh` borra los más viejos automáticamente |
| Restauración | Siempre contra una base de datos **nueva** (`createdb` + `pg_restore`), nunca sobre la activa |

```bash
# Respaldar (destino, base, host, puerto y usuario son opcionales; valores por defecto abajo)
PGPASSWORD='...' database/scripts/respaldar.sh database/backups mimedidor localhost 5432 postgres

# Restaurar un respaldo puntual en una base nueva, para verificarlo o recuperarse de un desastre
PGPASSWORD='...' database/scripts/restaurar.sh database/backups/mimedidor_20260825_030000.dump

# Prueba automatizada de extremo a extremo (inserta un dato, respalda, restaura, verifica y limpia)
PGPASSWORD='...' database/scripts/verificar_restauracion.sh
```

Los respaldos reales (`.dump`/`.sql` generados) **nunca se suben al repositorio** — `.gitignore`
los excluye de `database/backups/`, igual que las fotos del dataset de campo viven en
almacenamiento compartido y no en git. Lo que sí queda versionado son los scripts que los
generan y los restauran, que es lo reproducible.

**Por qué esta prueba no es solo "correr el script una vez y confiar":**
`verificar_restauracion.sh` no solo ejecuta `pg_dump`/`pg_restore` — inserta una fila con un
valor único, respalda, restaura en una base aparte, y **confirma que esa fila específica
sobrevivió** con el mismo valor. Un respaldo que se genera sin errores pero no se puede leer de
vuelta (por ejemplo, por una versión de `pg_dump` incompatible con `pg_restore`) pasaría
desapercibido si solo se mira que el comando no falló; esta prueba lo detecta porque compara el
dato, no solo el código de salida. El job `database` de CI la corre en cada PR, así que la
evidencia de que la restauración funciona no depende de que alguien la haya corrido a mano una
vez y lo recuerde.

## Roles — justificación de mínimo privilegio

| Rol | Permisos | Por qué esos y no más |
|---|---|---|
| `mimedidor_app` | `USAGE` sobre el esquema; `SELECT`, `INSERT`, `UPDATE` sobre todas las tablas; `EXECUTE` sobre funciones/procedimientos | Es la credencial que usa el backend (FastAPI vía `psycopg`). Necesita leer y escribir lecturas/facturas, pero **nunca borra nada** — no hay ningún flujo del contrato de la API (`docs/architecture/contrato-api.md`) que borre una fila — y no tiene permiso de `DDL`: si esa credencial se filtra, quien la tenga no puede alterar el esquema ni crear objetos nuevos. |
| `mimedidor_lectura` | `USAGE` sobre el esquema; `SELECT` sobre todas las tablas | Pensado para reportes o paneles del Sprint 2 que solo necesitan consultar. Aunque hoy nada de la aplicación lo use todavía, existe para no tener que reusar la credencial de escritura (`mimedidor_app`) el día que haga falta un acceso de solo lectura — eso rompería el principio de mínimo privilegio de la credencial de escritura. |

Ningún rol tiene privilegios sobre `PUBLIC` ni fuera del esquema `mimedidor` — `01_esquema.sql`
revoca explícitamente el acceso por defecto al esquema antes de otorgar nada.
