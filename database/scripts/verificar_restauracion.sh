#!/usr/bin/env bash
# MiMedidor — Prueba de restauración real (T-29)
#
# Criterio de aceptación de T-29: "prueba de restauración real ejecutada al menos una vez, con
# la evidencia guardada — no basta con que el respaldo se genere, hay que comprobar que sirve".
#
# Este script automatiza esa prueba de punta a punta para que sea repetible (no un intento
# manual que solo alguien vio una vez):
#   1. Inserta una fila "canario" con un valor único en la base de origen.
#   2. Respalda con respaldar.sh.
#   3. Restaura ese respaldo en una base nueva con restaurar.sh.
#   4. Confirma que la fila canario existe en la base restaurada con el mismo valor.
#   5. Limpia: borra la fila canario y la base restaurada.
#
# Uso:
#   PGPASSWORD='...' ./verificar_restauracion.sh [base_datos] [host] [puerto] [usuario]

set -euo pipefail

BASE_DATOS="${1:-mimedidor}"
HOST="${2:-localhost}"
PUERTO="${3:-5432}"
USUARIO="${4:-postgres}"
BASE_RESTAURADA="mimedidor_verificacion_restauracion"
DESTINO_RESPALDO="$(mktemp -d)"

CORREO_CANARIO="canario-t29-$(date +%s)@test.cr"

limpiar() {
    psql -h "$HOST" -p "$PUERTO" -U "$USUARIO" -d "$BASE_DATOS" -v ON_ERROR_STOP=1 -c \
        "DELETE FROM mimedidor.usuario WHERE correo = '$CORREO_CANARIO';" >/dev/null 2>&1 || true
    dropdb -h "$HOST" -p "$PUERTO" -U "$USUARIO" --if-exists "$BASE_RESTAURADA" >/dev/null 2>&1 || true
    rm -rf "$DESTINO_RESPALDO"
}
trap limpiar EXIT

echo "1. Insertando fila canario ($CORREO_CANARIO) en '$BASE_DATOS'"
psql -h "$HOST" -p "$PUERTO" -U "$USUARIO" -d "$BASE_DATOS" -v ON_ERROR_STOP=1 -c \
    "INSERT INTO mimedidor.usuario (nombre, correo) VALUES ('Canario T-29', '$CORREO_CANARIO');"

echo "2. Respaldando '$BASE_DATOS'"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/respaldar.sh" "$DESTINO_RESPALDO" "$BASE_DATOS" "$HOST" "$PUERTO" "$USUARIO"
ARCHIVO_RESPALDO="$(ls -t "$DESTINO_RESPALDO"/"${BASE_DATOS}"_*.dump | head -n 1)"

echo "3. Restaurando '$ARCHIVO_RESPALDO' -> '$BASE_RESTAURADA'"
"$SCRIPT_DIR/restaurar.sh" "$ARCHIVO_RESPALDO" "$BASE_RESTAURADA" "$HOST" "$PUERTO" "$USUARIO"

echo "4. Verificando que la fila canario sobrevivió a la restauración"
ENCONTRADO="$(psql -h "$HOST" -p "$PUERTO" -U "$USUARIO" -d "$BASE_RESTAURADA" -t -A -c \
    "SELECT count(*) FROM mimedidor.usuario WHERE correo = '$CORREO_CANARIO';")"

if [ "$ENCONTRADO" != "1" ]; then
    echo "T-29 FALLÓ: se esperaba 1 fila canario en la base restaurada y se encontraron $ENCONTRADO" >&2
    exit 1
fi

echo "T-29: la restauración conservó los datos correctamente. Prueba superada."
