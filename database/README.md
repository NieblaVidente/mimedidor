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
`03_roles_permisos.sql`. Se puede correr cada archivo por separado en ese mismo orden si se
prefiere revisar paso a paso.

## Roles — justificación de mínimo privilegio

| Rol | Permisos | Por qué esos y no más |
|---|---|---|
| `mimedidor_app` | `USAGE` sobre el esquema; `SELECT`, `INSERT`, `UPDATE` sobre todas las tablas; `EXECUTE` sobre funciones/procedimientos | Es la credencial que usa el backend (FastAPI vía `psycopg`). Necesita leer y escribir lecturas/facturas, pero **nunca borra nada** — no hay ningún flujo del contrato de la API (`docs/architecture/contrato-api.md`) que borre una fila — y no tiene permiso de `DDL`: si esa credencial se filtra, quien la tenga no puede alterar el esquema ni crear objetos nuevos. |
| `mimedidor_lectura` | `USAGE` sobre el esquema; `SELECT` sobre todas las tablas | Pensado para reportes o paneles del Sprint 2 que solo necesitan consultar. Aunque hoy nada de la aplicación lo use todavía, existe para no tener que reusar la credencial de escritura (`mimedidor_app`) el día que haga falta un acceso de solo lectura — eso rompería el principio de mínimo privilegio de la credencial de escritura. |

Ningún rol tiene privilegios sobre `PUBLIC` ni fuera del esquema `mimedidor` — `01_esquema.sql`
revoca explícitamente el acceso por defecto al esquema antes de otorgar nada.
