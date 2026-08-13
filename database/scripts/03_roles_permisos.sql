-- MiMedidor — Roles y permisos, mínimo privilegio (T-13)
--
-- Justificación rol por rol en database/README.md — leerla antes de tocar este archivo.
--
-- Las contraseñas NO se escriben acá. Se pasan como variables de psql al ejecutar:
--   psql -d mimedidor -v password_app='...' -v password_lectura='...' -f 03_roles_permisos.sql

-- --------------------------------------------------------------------------------------------
-- mimedidor_app — la usa el backend (FastAPI vía psycopg). Lee, inserta y actualiza; nunca
-- borra y nunca tiene DDL sobre el esquema.
-- --------------------------------------------------------------------------------------------
CREATE ROLE mimedidor_app WITH LOGIN PASSWORD :'password_app';

GRANT USAGE ON SCHEMA mimedidor TO mimedidor_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA mimedidor TO mimedidor_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA mimedidor TO mimedidor_app;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA mimedidor TO mimedidor_app;

-- Para que las tablas y procedimientos que se agreguen después (T-14) hereden el mismo permiso
-- sin tener que acordarse de repetir el GRANT.
ALTER DEFAULT PRIVILEGES IN SCHEMA mimedidor
    GRANT SELECT, INSERT, UPDATE ON TABLES TO mimedidor_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA mimedidor
    GRANT EXECUTE ON ROUTINES TO mimedidor_app;

-- --------------------------------------------------------------------------------------------
-- mimedidor_lectura — solo consulta. Pensado para reportes/paneles futuros que no deben poder
-- modificar nada aunque se comprometa esa credencial.
-- --------------------------------------------------------------------------------------------
CREATE ROLE mimedidor_lectura WITH LOGIN PASSWORD :'password_lectura';

GRANT USAGE ON SCHEMA mimedidor TO mimedidor_lectura;
GRANT SELECT ON ALL TABLES IN SCHEMA mimedidor TO mimedidor_lectura;

ALTER DEFAULT PRIVILEGES IN SCHEMA mimedidor
    GRANT SELECT ON TABLES TO mimedidor_lectura;
