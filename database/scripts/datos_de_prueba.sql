-- MiMedidor — Datos de prueba para desarrollo y pruebas end-to-end (T-22)
--
-- ⚠️ ESTE SCRIPT NO VA A PRODUCCIÓN. No está incluido en `ejecutar_todo.sql` a propósito:
-- inserta datos ficticios que solo sirven para probar.
--
-- Por qué hace falta: el contrato de la API no expone ninguna ruta para crear medidores — la
-- aplicación asume que ya existen. Así que para poder registrar una lectura, sea a mano o desde
-- la prueba end-to-end, tiene que haber un medidor en la base primero.
--
-- Los identificadores son fijos a propósito, para que la prueba pueda referirse a ellos sin
-- tener que averiguarlos antes.
--
-- Uso, desde database/scripts/ y sobre una base que ya tenga el esquema:
--   psql -d mimedidor -v ON_ERROR_STOP=1 -f datos_de_prueba.sql

INSERT INTO mimedidor.usuario (id, nombre, correo)
VALUES ('11111111-1111-1111-1111-111111111111', 'Abonada de prueba', 'prueba@ejemplo.cr')
ON CONFLICT (id) DO NOTHING;

INSERT INTO mimedidor.vivienda (id, usuario_id, direccion, operador)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'Dirección de prueba',
    'ASADA'
)
ON CONFLICT (id) DO NOTHING;

-- Modelo y serie copiados de Medidor2 del dataset de campo, para que los datos de prueba se
-- parezcan a los reales (ver docs/dataset-campo/registro-medidores.md).
INSERT INTO mimedidor.medidor (id, vivienda_id, numero_serie, marca, modelo)
VALUES (
    '33333333-3333-3333-3333-333333333333',
    '22222222-2222-2222-2222-222222222222',
    '2423279',
    'No confirmada',
    'MJ-SDC'
)
ON CONFLICT (id) DO NOTHING;

-- Una lectura histórica, de hace 5 días.
--
-- Hace falta porque la pantalla de captura guarda siempre con la fecha de hoy: no hay forma de
-- registrar una lectura de una fecha pasada desde la interfaz. Sin esta lectura sembrada, todas
-- las lecturas serían del mismo día, el consumo entre lecturas daría "0 días" y la comparación
-- contra factura devolvería nulo por falta de un período real que medir.
--
-- La fecha es relativa a hoy, no fija, para que la prueba end-to-end pueda afirmar "5 días"
-- cualquier día que corra.
--
-- Se registra llamando al procedimiento de T-14, no con un INSERT directo, para que también
-- quede su evento de auditoría y los datos de prueba se parezcan a los reales.
DO $$
DECLARE
    -- El procedimiento devuelve el id por un parámetro de salida, y PL/pgSQL exige que el
    -- argumento correspondiente sea una variable donde poder escribirlo: pasarle NULL falla.
    v_lectura_id uuid;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM mimedidor.lectura
        WHERE medidor_id = '33333333-3333-3333-3333-333333333333'
    ) THEN
        CALL mimedidor.registrar_lectura(
            '33333333-3333-3333-3333-333333333333'::uuid,
            51069::numeric,
            CURRENT_DATE - 5,
            'manual',
            NULL,
            v_lectura_id
        );
    END IF;
END
$$;
