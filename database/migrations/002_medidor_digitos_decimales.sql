-- MiMedidor — Migración 002 (T-39)
--
-- Agrega a `mimedidor.medidor` la cantidad de dígitos que el odómetro marca en rojo, o sea la
-- parte fraccionaria de metro cúbico.
--
-- Por qué es una columna del medidor y no una constante del código: en el dataset de campo la
-- cantidad **cambia según el aparato**. El ARAD marca 1 dígito en rojo (factor ×10); el MJ-SDC y
-- el ACTARIS marcan 2 (factor ×100). Con un solo modelo esto parecía un desfase global que se
-- arreglaba dividiendo por una constante; con dos escalas distintas queda claro que la posición
-- del punto decimal tiene que viajar con el medidor.
--
-- `DEFAULT 0` es deliberado: un medidor ya registrado del que no se sabe cuántos rojos tiene
-- conserva el comportamiento anterior (la cadena mostrada se guarda tal cual) en vez de quedar
-- convertido con un factor inventado. Corregirlo es actualizar su fila, no adivinar acá.
--
-- Uso:
--   psql -d mimedidor -v ON_ERROR_STOP=1 -f 002_medidor_digitos_decimales.sql

BEGIN;

-- Idempotente: correrla dos veces no puede fallar (misma regla que la migración 001).
ALTER TABLE mimedidor.medidor
    ADD COLUMN IF NOT EXISTS digitos_decimales smallint NOT NULL DEFAULT 0;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'medidor_digitos_decimales_rango'
          AND conrelid = 'mimedidor.medidor'::regclass
    ) THEN
        ALTER TABLE mimedidor.medidor
            ADD CONSTRAINT medidor_digitos_decimales_rango
            CHECK (digitos_decimales BETWEEN 0 AND 3);
        RAISE NOTICE 'Restriccion medidor_digitos_decimales_rango agregada.';
    ELSE
        RAISE NOTICE 'Restriccion medidor_digitos_decimales_rango ya existia.';
    END IF;
END
$$;

-- La lectura pasa a 3 decimales. El CHECK de arriba admite hasta 3 digitos rojos (litros), y
-- `numeric(10,2)` redondearia el tercero al guardar, sin error y sin aviso: exactamente el tipo
-- de perdida silenciosa que esta tarjeta existe para eliminar. Ampliar la escala de un numeric
-- no reescribe la tabla ni pierde datos.
ALTER TABLE mimedidor.lectura        ALTER COLUMN valor TYPE numeric(12, 3);
ALTER TABLE mimedidor.lectura_evento ALTER COLUMN valor TYPE numeric(12, 3);

COMMIT;

-- ------------------------------------------------------------------------------------------
-- ⚠️ Las lecturas YA guardadas no se convierten acá.
--
-- Esta migración no toca `mimedidor.lectura` a propósito. Convertir filas existentes exige
-- saber con qué escala se guardó cada una, y hasta ahora se guardaban todas como la cadena
-- mostrada: una conversión automática le aplicaría el factor nuevo a datos que no lo tenían.
--
-- Los datos de prueba se resiembran con `datos_de_prueba.sql`, que ya viene corregido. Si
-- alguna vez hay datos reales, la conversión va en su propia migración, con su propio respaldo
-- previo y verificada contra una copia antes de correrla.
-- ------------------------------------------------------------------------------------------
