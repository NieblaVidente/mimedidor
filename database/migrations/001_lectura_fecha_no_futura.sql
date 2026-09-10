-- MiMedidor — Migración 001 (T-35)
--
-- Agrega a `mimedidor.lectura` la restricción que impide fechar una lectura en el futuro.
--
-- Por qué existe esta migración además del cambio en 02_tablas.sql: ese archivo es el script de
-- **creación**, así que solo alcanza a una base construida desde cero. Cualquier base que ya
-- exista —la de desarrollo de cada integrante y la que quede en el servidor, porque el pipeline
-- de entrega continua no aplica esquema (docs/despliegue.md §5)— no recibiría la restricción, y
-- nadie lo notaría: la API igual rechaza la fecha, así que la capa más profunda de la defensa
-- quedaría existiendo solo en el papel.
--
-- La restricción lleva el mismo nombre que en 02_tablas.sql a propósito. Si se dejara sin
-- nombrar, PostgreSQL generaría uno automático distinto en cada base y comparar el esquema
-- creado desde cero contra el migrado se volvería confuso.
--
-- Uso:
--   psql -d mimedidor -v ON_ERROR_STOP=1 -f 001_lectura_fecha_no_futura.sql

BEGIN;

-- Idempotente a propósito: correrla dos veces no puede fallar. Una migración que revienta al
-- reaplicarse obliga a recordar cuáles ya se corrieron, y eso es justo lo que no hay que
-- depender de la memoria de nadie.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'lectura_fecha_no_futura'
          AND conrelid = 'mimedidor.lectura'::regclass
    ) THEN
        ALTER TABLE mimedidor.lectura
            ADD CONSTRAINT lectura_fecha_no_futura CHECK (fecha <= CURRENT_DATE);
        RAISE NOTICE 'Restricción lectura_fecha_no_futura agregada.';
    ELSE
        RAISE NOTICE 'Restricción lectura_fecha_no_futura ya existía; no se hace nada.';
    END IF;
END
$$;

COMMIT;
