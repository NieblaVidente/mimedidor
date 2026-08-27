#!/usr/bin/env bash
# MiMedidor — Respaldo lógico de la base de datos (T-29)
#
# Modelo de respaldo (documentado en database/README.md):
#   Tipo:       lógico completo, pg_dump en formato "custom" (-Fc) — permite restauración
#               selectiva con pg_restore, a diferencia de un volcado plano en texto.
#   Alcance:    la base completa, más los roles del clúster aparte con
#               pg_dumpall --roles-only — los roles no son objetos de la base de datos sino
#               del clúster (ver la nota sobre esto en database/README.md, T-13).
#   Frecuencia: diaria en desarrollo activo, y obligatorio antes de cada entrega.
#   Retención:  los últimos 7 respaldos de cada tipo, en rotación.
#
# Uso:
#   PGPASSWORD='...' ./respaldar.sh [directorio_destino] [base_datos] [host] [puerto] [usuario]
#
# La contraseña se pasa por la variable de entorno PGPASSWORD (o un archivo ~/.pgpass), nunca
# como argumento ni escrita en este script. Ningún respaldo se sube al repositorio — ver
# .gitignore — vive en almacenamiento compartido, igual que las fotos del dataset de campo.

set -euo pipefail

DESTINO="${1:-database/backups}"
BASE_DATOS="${2:-mimedidor}"
HOST="${3:-localhost}"
PUERTO="${4:-5432}"
USUARIO="${5:-postgres}"
RETENCION=7

mkdir -p "$DESTINO"

MARCA_TIEMPO="$(date +%Y%m%d_%H%M%S)"
ARCHIVO_BASE="$DESTINO/${BASE_DATOS}_${MARCA_TIEMPO}.dump"
ARCHIVO_ROLES="$DESTINO/roles_${MARCA_TIEMPO}.sql"

echo "Respaldando base de datos '$BASE_DATOS' -> $ARCHIVO_BASE"
pg_dump -Fc -h "$HOST" -p "$PUERTO" -U "$USUARIO" -d "$BASE_DATOS" -f "$ARCHIVO_BASE"

echo "Respaldando roles del clúster -> $ARCHIVO_ROLES"
pg_dumpall -h "$HOST" -p "$PUERTO" -U "$USUARIO" --roles-only -f "$ARCHIVO_ROLES"

echo "Aplicando retención: conservar los últimos $RETENCION respaldos de cada tipo"
ls -1t "$DESTINO"/"${BASE_DATOS}"_*.dump 2>/dev/null | tail -n "+$((RETENCION + 1))" | xargs -r rm -v --
ls -1t "$DESTINO"/roles_*.sql 2>/dev/null | tail -n "+$((RETENCION + 1))" | xargs -r rm -v --

echo "Respaldo completo: $ARCHIVO_BASE"
