# Evidencia — Prueba de restauración real (T-29)

**Qué prueba esto:** que un respaldo generado con `database/scripts/respaldar.sh` se puede
restaurar de vuelta con `database/scripts/restaurar.sh` y que los datos sobreviven intactos —
no solo que los comandos terminan sin error.

**Cómo se generó:** corriendo `database/scripts/verificar_restauracion.sh` contra una instancia
local de PostgreSQL 16, sobre la base `mimedidor` ya armada con `ejecutar_todo.sql` (T-13/T-14).
El mismo script corre en el job `database` de CI en cada Pull Request — esto es la primera
corrida real, documentada como prueba puntual del criterio de aceptación de T-29.

**Fecha:** 2026-08-26.

## Qué hizo el script

1. Insertó una fila "canario" en `usuario` con un correo único
   (`canario-t29-1787800485@test.cr`) en la base `mimedidor`.
2. La respaldó con `pg_dump -Fc` (más los roles del clúster con `pg_dumpall --roles-only`).
3. Restauró ese respaldo en una base nueva (`mimedidor_verificacion_restauracion`), nunca sobre
   la base activa.
4. Confirmó que la fila canario existe en la base restaurada, con el mismo valor.
5. Limpió: borró la fila canario de `mimedidor` y la base restaurada de prueba.

## Salida real

```
1. Insertando fila canario (canario-t29-1787800485@test.cr) en 'mimedidor'
INSERT 0 1
2. Respaldando 'mimedidor'
Respaldando base de datos 'mimedidor' -> /tmp/tmp.6d9ZV6LXV5/mimedidor_20260826_211446.dump
Respaldando roles del clúster -> /tmp/tmp.6d9ZV6LXV5/roles_20260826_211446.sql
Aplicando retención: conservar los últimos 7 respaldos de cada tipo
Respaldo completo: /tmp/tmp.6d9ZV6LXV5/mimedidor_20260826_211446.dump
3. Restaurando '/tmp/tmp.6d9ZV6LXV5/mimedidor_20260826_211446.dump' -> 'mimedidor_verificacion_restauracion'
Creando base de datos nueva 'mimedidor_verificacion_restauracion' (la base activa no se toca)
Restaurando '/tmp/tmp.6d9ZV6LXV5/mimedidor_20260826_211446.dump' -> 'mimedidor_verificacion_restauracion'
Restauración completa en 'mimedidor_verificacion_restauracion'. Verificá los datos antes de promoverla a activa.
4. Verificando que la fila canario sobrevivió a la restauración
T-29: la restauración conservó los datos correctamente. Prueba superada.
```

Verificación posterior de que la limpieza no dejó residuos:

```
$ psql -d postgres -c "\l" | grep mimedidor
 mimedidor | postgres | UTF8 | ...     -- solo la base activa, la de verificación ya no existe

$ psql -d mimedidor -c "SELECT count(*) FROM mimedidor.usuario WHERE correo LIKE 'canario%';"
 count
-------
     0
```

## Por qué esto es una prueba real y no un simulacro

No se limitó a correr `pg_dump`/`pg_restore` y mirar el código de salida — comparó un dato
concreto insertado antes del respaldo contra ese mismo dato después de la restauración. Un
respaldo corrupto o una versión de `pg_restore` incompatible habría hecho fallar el paso 4, no
solo el paso 2 o 3.
