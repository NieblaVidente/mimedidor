-- MiMedidor — Prueba del procedimiento registrar_lectura (T-14) y de sus CHECK (T-35)
--
-- Criterio de aceptación de T-14: "fuerza un error a propósito y verifica que la transacción
-- se revirtió completa". Este script lo hace de punta a punta y no deja datos de prueba: todo
-- corre dentro de un BEGIN/ROLLBACK explícito, así se puede correr las veces que haga falta
-- (incluido en cada corrida de CI) sin ensuciar la base.
--
-- El caso 3 (T-35) prueba, además, que el CHECK de fecha futura en `lectura` funciona incluso
-- saltándose el procedimiento — la defensa en profundidad de la que habla
-- docs/architecture/contrato-api.md.
--
-- Uso: psql -d mimedidor -U mimedidor_app -v ON_ERROR_STOP=1 -f verificar_registrar_lectura.sql
-- Si algo falla, el RAISE EXCEPTION correspondiente explica cuál verificación no pasó y psql
-- termina con código de salida distinto de cero.

BEGIN;

DO $$
DECLARE
    v_usuario_id  uuid;
    v_vivienda_id uuid;
    v_medidor_id  uuid;
    v_lectura_id  uuid;
    v_conteo      int;
    v_fallo       boolean := false;
BEGIN
    -- Datos base de la prueba
    INSERT INTO mimedidor.usuario (nombre, correo)
    VALUES ('Prueba T-14', 'prueba-t14@test.cr')
    RETURNING id INTO v_usuario_id;

    INSERT INTO mimedidor.vivienda (usuario_id, direccion, operador)
    VALUES (v_usuario_id, 'Dirección de prueba', 'AyA')
    RETURNING id INTO v_vivienda_id;

    INSERT INTO mimedidor.medidor (vivienda_id, numero_serie, marca)
    VALUES (v_vivienda_id, 'SERIE-PRUEBA-T14', 'MarcaPrueba')
    RETURNING id INTO v_medidor_id;

    -- Caso 1: primera lectura del medidor — debe insertar lectura Y evento juntos
    CALL mimedidor.registrar_lectura(v_medidor_id, 100.00, '2026-01-01', 'manual', NULL, v_lectura_id);

    SELECT count(*) INTO v_conteo FROM mimedidor.lectura WHERE medidor_id = v_medidor_id;
    IF v_conteo != 1 THEN
        RAISE EXCEPTION 'T-14 FALLÓ (caso 1): se esperaba 1 fila en lectura y hay %', v_conteo;
    END IF;

    SELECT count(*) INTO v_conteo FROM mimedidor.lectura_evento WHERE medidor_id = v_medidor_id;
    IF v_conteo != 1 THEN
        RAISE EXCEPTION 'T-14 FALLÓ (caso 1): se esperaba 1 fila en lectura_evento y hay %', v_conteo;
    END IF;

    -- Caso 2: forzar el error a propósito — un valor menor al último no debe registrarse
    BEGIN
        CALL mimedidor.registrar_lectura(v_medidor_id, 50.00, '2026-02-01', 'manual', NULL, v_lectura_id);
        -- Si llegamos hasta acá, el procedimiento no lanzó la excepción esperada.
        v_fallo := true;
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM NOT LIKE '%LECTURA_INVALIDA%' THEN
                RAISE EXCEPTION 'T-14 FALLÓ (caso 2): se esperaba error LECTURA_INVALIDA, llegó: %', SQLERRM;
            END IF;
            RAISE NOTICE 'Caso 2 correcto: la lectura inválida fue rechazada (%)', SQLERRM;
    END;

    IF v_fallo THEN
        RAISE EXCEPTION 'T-14 FALLÓ (caso 2): el procedimiento aceptó una lectura menor que la anterior';
    END IF;

    -- La lectura rechazada no debe haber dejado nada a medias: mismo conteo que después del caso 1.
    SELECT count(*) INTO v_conteo FROM mimedidor.lectura WHERE medidor_id = v_medidor_id;
    IF v_conteo != 1 THEN
        RAISE EXCEPTION 'T-14 FALLÓ (caso 2): quedaron % filas en lectura, se esperaba 1 sin cambios', v_conteo;
    END IF;

    SELECT count(*) INTO v_conteo FROM mimedidor.lectura_evento WHERE medidor_id = v_medidor_id;
    IF v_conteo != 1 THEN
        RAISE EXCEPTION 'T-14 FALLÓ (caso 2): quedaron % filas en lectura_evento, se esperaba 1 sin cambios', v_conteo;
    END IF;

    -- Caso 3 (T-35): el CHECK de la tabla rechaza una fecha futura aunque se salte el
    -- procedimiento — defensa en profundidad, no solo la validación de la API.
    v_fallo := false;
    BEGIN
        INSERT INTO mimedidor.lectura (medidor_id, valor, fecha, origen)
        VALUES (v_medidor_id, 200.00, CURRENT_DATE + 1, 'manual');
        v_fallo := true;
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Caso 3 correcto: el CHECK de la tabla rechazó la fecha futura';
    END;

    IF v_fallo THEN
        RAISE EXCEPTION 'T-35 FALLÓ (caso 3): la tabla aceptó una lectura con fecha futura';
    END IF;

    RAISE NOTICE 'T-14/T-35: todas las verificaciones pasaron';
END;
$$;

-- Descarta los datos de prueba — este script nunca deja residuos en la base.
ROLLBACK;
