# Base de datos — MiMedidor

Motor: **PostgreSQL**, confirmado como opción válida por el profesor del componente de Base de Datos (rúbrica exige motor relacional, no un motor específico).

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

Ver diagrama entidad-relación en `docs/architecture/` (tarjeta T-12).
