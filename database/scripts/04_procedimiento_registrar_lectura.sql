-- MiMedidor — Procedimiento transaccional de registro de lecturas (T-14)
--
-- Valida la regla de negocio "un hidrómetro no retrocede" (LECTURA_INVALIDA en
-- docs/architecture/contrato-api.md §1) e inserta la lectura junto con su evento de auditoría
-- (Opción C, docs/architecture/modelo-datos.md §5.2) como una sola operación atómica: si
-- cualquiera de las dos escrituras falla, ninguna de las dos queda registrada.
--
-- Equivalencia con la rúbrica de Base de Datos (tabla completa en database/README.md):
--   TRY...CATCH -> bloque EXCEPTION de PL/pgSQL
--   THROW       -> RAISE EXCEPTION
--   XACT_ABORT  -> no hace falta activarlo: al no capturar la excepción, PostgreSQL revierte
--                  automáticamente todo lo que esta llamada haya hecho.
--
-- Requiere haber corrido 01_esquema.sql, 02_tablas.sql y 03_roles_permisos.sql antes.

CREATE OR REPLACE PROCEDURE mimedidor.registrar_lectura(
    IN  p_medidor_id  uuid,
    IN  p_valor       numeric,
    IN  p_fecha       date,
    IN  p_origen      text,
    IN  p_foto_url    text,
    OUT p_lectura_id  uuid
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_ultimo_valor numeric;
BEGIN
    SELECT valor INTO v_ultimo_valor
    FROM mimedidor.lectura
    WHERE medidor_id = p_medidor_id
    ORDER BY fecha DESC, creado_en DESC
    LIMIT 1;

    IF v_ultimo_valor IS NOT NULL AND p_valor < v_ultimo_valor THEN
        RAISE EXCEPTION 'LECTURA_INVALIDA: el valor % es menor que la última lectura registrada (%)',
            p_valor, v_ultimo_valor;
    END IF;

    INSERT INTO mimedidor.lectura (medidor_id, valor, fecha, origen, foto_url)
    VALUES (p_medidor_id, p_valor, p_fecha, p_origen, p_foto_url)
    RETURNING id INTO p_lectura_id;

    INSERT INTO mimedidor.lectura_evento (lectura_id, medidor_id, valor, origen)
    VALUES (p_lectura_id, p_medidor_id, p_valor, p_origen);
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'No se pudo registrar la lectura: %', SQLERRM;
END;
$$;

GRANT EXECUTE ON PROCEDURE mimedidor.registrar_lectura TO mimedidor_app;
