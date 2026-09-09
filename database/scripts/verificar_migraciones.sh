#!/usr/bin/env bash
# MiMedidor — Verifica que las migraciones y los scripts produzcan el mismo esquema
#
# POR QUÉ EXISTE
#
# Desde T-28 hay despliegue a producción, y eso abre una grieta silenciosa:
#
#   · El CI y cualquier instalación nueva construyen la base **desde cero** con
#     `database/scripts/` (01_esquema.sql + 02_tablas.sql).
#   · Producción, en cambio, ya existe: se actualiza **aplicando migraciones** sobre el esquema
#     que ya tenía.
#
# Si esos dos caminos se separan, el CI puede quedar en verde sobre un esquema que no es el que
# corre en producción. El caso peligroso es el más fácil de cometer: alguien agrega una columna a
# `02_tablas.sql` y se le olvida escribir la migración. Desde cero funciona, en producción no
# existe la columna, y nada avisa hasta que algo se rompe con datos reales.
#
# Este script arma las dos bases y compara el esquema resultante.
#
# QUÉ COMPARA (y qué no)
#
# Compara el esquema de forma **canónica**, no textual: columnas con su tipo, nulabilidad y
# valor por defecto; restricciones con su definición; e índices. Todo ordenado por nombre.
#
# No compara el **orden de las columnas**, a propósito: `ALTER TABLE ADD COLUMN` siempre agrega
# al final, así que una base migrada nunca va a tener el mismo orden que una creada desde cero.
# Esa diferencia no afecta a este proyecto — ninguna consulta usa `SELECT *` ni `INSERT` sin
# nombrar columnas — y exigir que coincida obligaría a reescribir tablas sin ganar nada.
#
# Solo se comparan tablas. `03_roles_permisos.sql` crea roles, que son objetos del clúster y no
# de la base, y las migraciones no los tocan.
#
# Uso:
#   PGPASSWORD='...' ./verificar_migraciones.sh [host] [puerto] [usuario]

set -euo pipefail

HOST="${1:-localhost}"
PUERTO="${2:-5432}"
USUARIO="${3:-postgres}"

BASE_DESDE_CERO="mimedidor_verif_desde_cero"
BASE_MIGRADA="mimedidor_verif_migrada"

# Punto de partida de la cadena de migraciones: el último `02_tablas.sql` anterior a que
# existiera cualquier migración (T-13). Es el esquema desde el que la migración 001 asume que
# arranca.
#
# Este SHA solo cambia si algún día se aplasta el historial de migraciones en una línea base
# nueva. Agregar una migración NO lo cambia — ese es justamente el punto.
SHA_BASE="7a238c2"

RAIZ_REPO="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
TMP="$(mktemp -d)"

limpiar() {
    dropdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" --if-exists "$BASE_DESDE_CERO" >/dev/null 2>&1 || true
    dropdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" --if-exists "$BASE_MIGRADA" >/dev/null 2>&1 || true
    rm -rf "$TMP"
}
trap limpiar EXIT

psql_q() {
    psql -h "$HOST" -p "$PUERTO" -U "$USUARIO" -v ON_ERROR_STOP=1 -q "$@"
}

# Descripción canónica del esquema: ordenada por nombre, sin posición de columna.
volcar_esquema() {
    local base="$1" destino="$2"
    {
        echo "== COLUMNAS =="
        psql_q -d "$base" -t -A -F '|' -c "
            SELECT table_name, column_name, data_type,
                   coalesce(numeric_precision::text, '-'),
                   coalesce(numeric_scale::text, '-'),
                   is_nullable,
                   coalesce(column_default, '-')
            FROM information_schema.columns
            WHERE table_schema = 'mimedidor'
            ORDER BY table_name, column_name;"

        echo "== RESTRICCIONES =="
        psql_q -d "$base" -t -A -F '|' -c "
            SELECT conrelid::regclass::text, conname, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE connamespace = 'mimedidor'::regnamespace
            ORDER BY 1, 2;"

        echo "== INDICES =="
        psql_q -d "$base" -t -A -F '|' -c "
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'mimedidor'
            ORDER BY 1, 2;"
    } > "$destino"
}

echo "Base de partida de las migraciones: $SHA_BASE (database/scripts/02_tablas.sql)"
git -C "$RAIZ_REPO" show "$SHA_BASE:database/scripts/02_tablas.sql" > "$TMP/02_base.sql"

dropdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" --if-exists "$BASE_DESDE_CERO" >/dev/null 2>&1 || true
dropdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" --if-exists "$BASE_MIGRADA" >/dev/null 2>&1 || true
createdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" "$BASE_DESDE_CERO"
createdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" "$BASE_MIGRADA"

echo "1. Construyendo '$BASE_DESDE_CERO' con los scripts actuales"
psql_q -d "$BASE_DESDE_CERO" \
    -f "$RAIZ_REPO/database/scripts/01_esquema.sql" \
    -f "$RAIZ_REPO/database/scripts/02_tablas.sql"

echo "2. Construyendo '$BASE_MIGRADA' desde el esquema base y aplicando las migraciones en orden"
psql_q -d "$BASE_MIGRADA" -f "$RAIZ_REPO/database/scripts/01_esquema.sql" -f "$TMP/02_base.sql"
for migracion in "$RAIZ_REPO"/database/migrations/*.sql; do
    echo "   → $(basename "$migracion")"
    psql_q -d "$BASE_MIGRADA" -f "$migracion"
done

# Las migraciones se declaran idempotentes (lo dicen en su propio encabezado). Se comprueba en
# vez de creerlo: correrlas dos veces no puede fallar ni cambiar el resultado.
echo "3. Reaplicando las migraciones para comprobar que son idempotentes"
for migracion in "$RAIZ_REPO"/database/migrations/*.sql; do
    psql_q -d "$BASE_MIGRADA" -f "$migracion" >/dev/null
done

echo "4. Comparando los esquemas"
volcar_esquema "$BASE_DESDE_CERO" "$TMP/desde_cero.txt"
volcar_esquema "$BASE_MIGRADA" "$TMP/migrada.txt"

if diff -u "$TMP/desde_cero.txt" "$TMP/migrada.txt" > "$TMP/diferencias.txt"; then
    echo ""
    echo "✅ Los dos caminos producen el mismo esquema."
    echo "   Una instalación nueva y una migrada quedan iguales."
else
    echo ""
    echo "❌ FALLÓ: el esquema creado desde cero NO coincide con el migrado." >&2
    echo "" >&2
    echo "   '-' es lo que tienen los scripts; '+' lo que produce la cadena de migraciones." >&2
    echo "   Lo más probable: se cambió 02_tablas.sql sin escribir la migración equivalente," >&2
    echo "   o al revés. Producción y CI quedarían con esquemas distintos." >&2
    echo "" >&2
    cat "$TMP/diferencias.txt" >&2
    exit 1
fi
