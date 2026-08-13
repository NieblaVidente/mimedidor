-- MiMedidor — Creación del esquema (T-13)
--
-- Se usa un esquema propio en vez de "public" a propósito: la rúbrica de Base de Datos pide
-- explícitamente "usuarios, roles y esquemas (schemas)" como evidencia del criterio de
-- seguridad, y separar el esquema de aplicación del esquema por defecto es lo que permite
-- otorgar permisos acotados a ese esquema en 03_roles_permisos.sql.

CREATE SCHEMA IF NOT EXISTS mimedidor;

COMMENT ON SCHEMA mimedidor IS 'Esquema de aplicación de MiMedidor (T-12/T-13).';

-- Nadie tiene acceso por defecto — cada rol lo recibe explícitamente en 03_roles_permisos.sql.
REVOKE ALL ON SCHEMA mimedidor FROM PUBLIC;
