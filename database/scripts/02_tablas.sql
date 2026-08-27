-- MiMedidor — Creación de tablas (T-13)
--
-- Implementa exactamente el modelo de docs/architecture/modelo-datos.md (T-12). Si algo cambia
-- acá, ese documento se actualiza en el mismo PR.
--
-- Requiere haber corrido 01_esquema.sql antes. gen_random_uuid() es una función nativa desde
-- PostgreSQL 13, no requiere CREATE EXTENSION.

CREATE TABLE mimedidor.usuario (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      text NOT NULL,
    correo      text NOT NULL UNIQUE,
    creado_en   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE mimedidor.vivienda (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id  uuid NOT NULL REFERENCES mimedidor.usuario(id),
    direccion   text NOT NULL,
    -- Territorio geográfico, no del aparato — decisión de equipo documentada en
    -- docs/architecture/modelo-datos.md §5.1.
    operador    text NOT NULL CHECK (operador IN ('AyA', 'ASADA', 'Municipalidad')),
    creado_en   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_vivienda_usuario_id ON mimedidor.vivienda(usuario_id);

CREATE TABLE mimedidor.medidor (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    vivienda_id         uuid NOT NULL REFERENCES mimedidor.vivienda(id),
    numero_serie        text NOT NULL UNIQUE,
    -- Clave para el riesgo de fragmentación del parque de medidores (CLAUDE.md §13).
    marca               text NOT NULL,
    modelo              text,
    fecha_instalacion   date,
    creado_en           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_medidor_vivienda_id ON mimedidor.medidor(vivienda_id);

CREATE TABLE mimedidor.lectura (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    medidor_id  uuid NOT NULL REFERENCES mimedidor.medidor(id),
    valor       numeric(10, 2) NOT NULL CHECK (valor >= 0),
    -- Defensa en profundidad de T-35: la API ya rechaza una fecha futura antes de llegar acá
    -- (server/app/api/lecturas.py), pero este CHECK protege también a quien escriba en la
    -- tabla sin pasar por la API (ej. un script de datos futuro).
    fecha       date NOT NULL CHECK (fecha <= CURRENT_DATE),
    -- Permite calcular la exactitud real del reconocimiento en T-11.
    origen      text NOT NULL CHECK (origen IN ('reconocimiento', 'manual')),
    foto_url    text,
    creado_en   timestamptz NOT NULL DEFAULT now()
);

-- Un hidrómetro no retrocede: el procedimiento de T-14 valida cada lectura nueva contra la
-- última de este medidor, ordenando por fecha — este índice es lo que hace esa consulta barata.
CREATE INDEX idx_lectura_medidor_id_fecha ON mimedidor.lectura(medidor_id, fecha);

CREATE TABLE mimedidor.factura (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    medidor_id              uuid NOT NULL REFERENCES mimedidor.medidor(id),
    periodo_inicio          date NOT NULL,
    periodo_fin             date NOT NULL CHECK (periodo_fin > periodo_inicio),
    consumo_facturado_m3    numeric(10, 2) NOT NULL,
    -- Colones costarricenses, sin símbolo ni separadores — igual que el contrato de la API.
    monto                   numeric(12, 2) NOT NULL,
    creado_en               timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_factura_medidor_id ON mimedidor.factura(medidor_id);

-- Bitácora de auditoría — decisión de equipo (Opción C) documentada en
-- docs/architecture/modelo-datos.md §5.2. Es la única tabla con redundancia deliberada
-- (medidor_id y valor son derivables vía lectura_id): existe para que el procedimiento de T-14
-- tenga una segunda escritura real dentro de la misma transacción, y para preservar el estado
-- histórico del evento aunque "lectura" cambie de forma más adelante.
CREATE TABLE mimedidor.lectura_evento (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    lectura_id  uuid NOT NULL REFERENCES mimedidor.lectura(id),
    medidor_id  uuid NOT NULL REFERENCES mimedidor.medidor(id),
    valor       numeric(10, 2) NOT NULL,
    origen      text NOT NULL,
    creado_en   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_lectura_evento_medidor_id ON mimedidor.lectura_evento(medidor_id);
