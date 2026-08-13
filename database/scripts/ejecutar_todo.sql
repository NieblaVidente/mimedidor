-- MiMedidor — Corre los scripts de T-13 en orden sobre una base vacía.
--
-- Uso (con la base de datos "mimedidor" ya creada, ver database/README.md):
--   psql -d mimedidor -v password_app='...' -v password_lectura='...' -f ejecutar_todo.sql

\i 01_esquema.sql
\i 02_tablas.sql
\i 03_roles_permisos.sql
