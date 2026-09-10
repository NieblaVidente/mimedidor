#!/usr/bin/env bash
#
# Vuelve producción a la versión anterior. Se corre EN EL SERVIDOR, como el usuario de
# despliegue:
#
#   ssh despliegue@<host> 'bash /opt/mimedidor/servidor/../revertir.sh'
#
# o, si se copió a mano:
#
#   ssh despliegue@<host> 'bash ~/revertir.sh'
#
# La copia a la que vuelve la deja el job `desplegar` de .github/workflows/ci.yml, en el paso
# «Guardar la versión que está corriendo», justo antes de publicar la nueva.
#
# CUÁNDO USARLO: cuando producción quedó rota y hay que restablecerla YA. La vía normal para
# deshacer un cambio es revertir el commit en `main` y dejar que el pipeline despliegue —
# ver docs/despliegue.md, sección 6. Este script es el atajo de emergencia.
#
# LO QUE NO HACE: no toca la base de datos. Si el despliegue que falló venía con un cambio de
# esquema, revertir el código no deshace ese cambio (ver docs/despliegue.md, sección 5).

set -euo pipefail

VERSIONES=/opt/mimedidor/versiones
CLIENTE_VIVO=/var/www/mimedidor
SERVIDOR_VIVO=/opt/mimedidor/servidor
VENV=/opt/mimedidor/venv

echo "==> Comprobando que exista una versión anterior"

if [ ! -d "$VERSIONES/cliente-anterior" ] || [ ! -d "$VERSIONES/servidor-anterior" ]; then
    echo "ERROR: no hay copia de la versión anterior en $VERSIONES." >&2
    echo "Solo existe después del primer despliegue hecho con el pipeline actual." >&2
    echo "Usá la vía normal: revertí el commit en main y dejá que el pipeline despliegue." >&2
    exit 1
fi

# Se guarda lo que está roto antes de pisarlo. Sin esto, revertir borra la evidencia de por qué
# falló, y el diagnóstico se vuelve adivinanza.
echo "==> Guardando la versión fallida para poder diagnosticarla"
rsync -a --delete "$CLIENTE_VIVO/"  "$VERSIONES/cliente-fallido/"
rsync -a --delete "$SERVIDOR_VIVO/" "$VERSIONES/servidor-fallido/"

echo "==> Restaurando el cliente"
rsync -a --delete "$VERSIONES/cliente-anterior/" "$CLIENTE_VIVO/"

echo "==> Restaurando el servidor"
rsync -a --delete "$VERSIONES/servidor-anterior/" "$SERVIDOR_VIVO/"

# Las dependencias se reinstalan desde el requirements.txt que acaba de volver: la versión
# anterior puede necesitar paquetes distintos de los que dejó instalados la versión rota.
echo "==> Reinstalando dependencias de la versión anterior"
"$VENV/bin/pip" install --quiet --upgrade -r "$SERVIDOR_VIVO/requirements.txt"

echo "==> Reiniciando el servicio"
sudo /usr/bin/systemctl restart mimedidor

# Reiniciar no prueba que arrancó: si el proceso muere al segundo, systemctl devuelve éxito
# igual. Mismo criterio que el paso de verificación del pipeline, y las mismas dos
# comprobaciones:
#
#   /api/salud       → 200. Uvicorn está sirviendo.
#   /api/lecturas    → 404 con un medidor inexistente. Ese 404 solo puede salir después de
#                      consultar PostgreSQL, así que prueba que la base responde.
#
# Se consulta a uvicorn directo (127.0.0.1:8000) y no a través de nginx: lo que este script
# acaba de tocar es la aplicación, no el servidor web. Si nginx estuviera caído, esto igual
# tiene que poder decir si la reversión funcionó.
MEDIDOR_INEXISTENTE=00000000-0000-0000-0000-000000000000
API=http://127.0.0.1:8000

echo "==> Verificando que responda"
for intento in $(seq 1 10); do
    salud=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$API/api/salud" || echo 000)
    base=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
        "$API/api/lecturas?medidor_id=$MEDIDOR_INEXISTENTE" || echo 000)

    if [ "$salud" = "200" ] && [ "$base" = "404" ]; then
        echo "OK: la aplicación responde y llega a la base de datos (intento $intento)."
        echo
        echo "La versión que falló quedó en $VERSIONES/cliente-fallido y"
        echo "$VERSIONES/servidor-fallido. No la borres antes de averiguar qué pasó."
        exit 0
    fi

    echo "    intento $intento — salud: $salud (se espera 200), base: $base (se espera 404)"
    sleep 3
done

echo "ERROR: se revirtió pero la aplicación sigue sin verificar (salud=$salud base=$base)." >&2
echo "Entonces el problema no era el código desplegado. Revisá:" >&2
echo "  sudo systemctl status mimedidor" >&2
echo "  sudo journalctl -u mimedidor -n 50" >&2
echo "  systemctl status postgresql" >&2
exit 1
