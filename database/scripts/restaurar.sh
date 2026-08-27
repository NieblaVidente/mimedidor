#!/usr/bin/env bash
# MiMedidor — Restauración desde un respaldo lógico (T-29)
#
# Siempre contra una base de datos NUEVA, nunca sobre la activa: si algo sale mal a mitad de la
# restauración, la base real nunca estuvo en riesgo. Promover la base restaurada a producción es
# una decisión manual aparte, no algo que este script haga solo.
#
# Uso:
#   PGPASSWORD='...' ./restaurar.sh archivo_respaldo.dump [base_nueva] [host] [puerto] [usuario]

set -euo pipefail

ARCHIVO="${1:?Uso: restaurar.sh archivo_respaldo.dump [base_nueva] [host] [puerto] [usuario]}"
BASE_NUEVA="${2:-mimedidor_restaurada}"
HOST="${3:-localhost}"
PUERTO="${4:-5432}"
USUARIO="${5:-postgres}"

if [ ! -f "$ARCHIVO" ]; then
    echo "No existe el archivo de respaldo: $ARCHIVO" >&2
    exit 1
fi

echo "Creando base de datos nueva '$BASE_NUEVA' (la base activa no se toca)"
createdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" "$BASE_NUEVA"

echo "Restaurando '$ARCHIVO' -> '$BASE_NUEVA'"
pg_restore -h "$HOST" -p "$PUERTO" -U "$USUARIO" -d "$BASE_NUEVA" --no-owner "$ARCHIVO"

echo "Restauración completa en '$BASE_NUEVA'. Verificá los datos antes de promoverla a activa."
