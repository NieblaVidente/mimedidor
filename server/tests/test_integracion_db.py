"""Pruebas de integración contra una base de datos PostgreSQL real (T-21).

**Por qué existen.** El resto de las pruebas del servidor sustituye la conexión por un objeto
falso (`conftest.py`). Eso las hace rápidas y no las ata a tener Postgres instalado, pero tiene
un punto ciego que nos costó un bug real: **un objeto falso nunca se queja de un tipo de SQL.**

El bug concreto que motivó este archivo: `mimedidor.registrar_lectura` declara `p_valor numeric`,
y psycopg manda los `float` de Python como `double precision`. En PostgreSQL ese cast es de
asignación, no implícito, y para resolver a qué procedimiento llamar solo se consideran los
implícitos — así que la llamada fallaba con "no existe el procedimiento" **aunque el
procedimiento existiera**. Las 46 pruebas pasaban en verde y el endpoint devolvía 500 en cuanto
se ejecutaba contra una base real.

Estas pruebas se saltan solas si no hay una base disponible, así que no rompen el trabajo local
de nadie. En CI sí corren: el job `Base de datos` levanta PostgreSQL de verdad.

Configuración por las variables estándar de libpq (PGHOST, PGDATABASE, PGUSER, PGPASSWORD),
las mismas que usa `app/db/conexion.py`.
"""

from datetime import date
from uuid import uuid4

import psycopg
import pytest

from app.db import lecturas as db_lecturas


def _hay_base_de_datos() -> bool:
    try:
        with psycopg.connect(connect_timeout=3):
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _hay_base_de_datos(),
    reason="no hay una base PostgreSQL accesible (configurar PGHOST/PGDATABASE/PGUSER/PGPASSWORD)",
)


@pytest.fixture
def conexion():
    """Conexión real, con todo lo que escriba la prueba revertido al terminar.

    Sin autocommit a propósito: así el `rollback` final borra los datos de prueba y la base
    queda como estaba, corra donde corra.
    """
    con = psycopg.connect()
    try:
        yield con
    finally:
        con.rollback()
        con.close()


def _crear_medidor_de_prueba(conexion, digitos_decimales: int = 0) -> str:
    """Crea la cadena mínima usuario → vivienda → medidor y devuelve el id del medidor.

    `digitos_decimales` es cuántos dígitos marca en rojo el odómetro (T-39).
    """
    usuario_id, vivienda_id, medidor_id = str(uuid4()), str(uuid4()), str(uuid4())
    with conexion.cursor() as cur:
        cur.execute(
            "INSERT INTO mimedidor.usuario (id, nombre, correo) VALUES (%s, %s, %s)",
            (usuario_id, "Prueba de integración", f"prueba-{usuario_id}@ejemplo.cr"),
        )
        cur.execute(
            """
            INSERT INTO mimedidor.vivienda (id, usuario_id, direccion, operador)
            VALUES (%s, %s, %s, %s)
            """,
            (vivienda_id, usuario_id, "Dirección de prueba", "ASADA"),
        )
        cur.execute(
            """
            INSERT INTO mimedidor.medidor
                (id, vivienda_id, numero_serie, marca, digitos_decimales)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                medidor_id,
                vivienda_id,
                f"serie-{medidor_id}",
                "Marca de prueba",
                digitos_decimales,
            ),
        )
    return medidor_id


def test_registrar_lectura_acepta_un_float_de_python(conexion):
    """Regresión del bug de tipos: `valor` viaja como `float`, igual que desde el endpoint."""
    medidor_id = _crear_medidor_de_prueba(conexion)

    lectura_id = db_lecturas.llamar_registrar_lectura(
        conexion, medidor_id, 51069.0, date(2026, 8, 16), "manual", None
    )

    assert lectura_id


def test_registrar_lectura_escribe_la_lectura_y_su_evento_de_auditoria(conexion):
    """Las dos escrituras del procedimiento de T-14, verificadas sobre tablas reales."""
    medidor_id = _crear_medidor_de_prueba(conexion)

    lectura_id = db_lecturas.llamar_registrar_lectura(
        conexion, medidor_id, 51069.0, date(2026, 8, 16), "manual", None
    )

    with conexion.cursor() as cur:
        cur.execute("SELECT valor FROM mimedidor.lectura WHERE id = %s", (lectura_id,))
        assert cur.fetchone()[0] == 51069
        cur.execute(
            "SELECT count(*) FROM mimedidor.lectura_evento WHERE lectura_id = %s", (lectura_id,)
        )
        assert cur.fetchone()[0] == 1


def test_una_lectura_menor_que_la_anterior_no_deja_nada_a_medias(conexion):
    """El `ROLLBACK` de T-14 sobre la base real: ni la lectura ni su evento quedan escritos."""
    medidor_id = _crear_medidor_de_prueba(conexion)
    db_lecturas.llamar_registrar_lectura(
        conexion, medidor_id, 51069.0, date(2026, 8, 16), "manual", None
    )

    with pytest.raises(Exception, match="LECTURA_INVALIDA"):
        db_lecturas.llamar_registrar_lectura(
            conexion, medidor_id, 100.0, date(2026, 8, 21), "manual", None
        )

    # La transacción quedó abortada por el error; hay que limpiarla para poder consultar.
    conexion.rollback()
    with conexion.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM mimedidor.lectura WHERE medidor_id = %s", (medidor_id,)
        )
        # El rollback revirtió también el medidor de prueba, así que no debe quedar ninguna.
        assert cur.fetchone()[0] == 0


def test_listar_lecturas_devuelve_las_columnas_que_espera_el_endpoint(conexion):
    """`listar_lecturas` arma la respuesta de `GET /api/lecturas` desde estas cuatro columnas."""
    medidor_id = _crear_medidor_de_prueba(conexion)
    db_lecturas.llamar_registrar_lectura(
        conexion, medidor_id, 51069.0, date(2026, 8, 16), "manual", None
    )

    filas = db_lecturas.listar_lecturas(conexion, medidor_id)

    assert len(filas) == 1
    _id, valor, fecha, origen = filas[0]
    assert float(valor) == 51069.0
    assert fecha == date(2026, 8, 16)
    assert origen == "manual"


# ══════════════════════════════════════════════════════════════════════════════════════════════
# T-39 — La escala decimal es del medidor, no del código
#
# Estas van contra la base real y no contra un objeto falso por el mismo motivo que las de
# arriba: lo que se está verificando es que la columna existe, que acepta el rango, y que un
# `numeric(12, 3)` conserva el tercer decimal. Nada de eso lo detecta una conexión sustituida.
# ══════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    "digitos_rojos, valor_mostrado, volumen_esperado",
    [
        (1, 25888.0, 2588.8),    # ARAD del dataset de campo
        (2, 452991.0, 4529.91),  # ACTARIS y MJ-SDC del dataset de campo
        (3, 510694.0, 510.694),  # tres rojos: el caso que numeric(10,2) habría redondeado
        (0, 1284.0, 1284.0),     # sin rojos: el volumen es la cadena mostrada
    ],
)
def test_escala_decimal_por_medidor(
    conexion, digitos_rojos, valor_mostrado, volumen_esperado
):
    """Dos medidores con escalas distintas conviven, y el volumen se guarda con su precisión."""
    from app.api.lecturas import a_volumen_m3

    medidor_id = _crear_medidor_de_prueba(conexion, digitos_decimales=digitos_rojos)

    leidos = db_lecturas.digitos_decimales_del_medidor(conexion, medidor_id)
    assert leidos == digitos_rojos

    volumen = a_volumen_m3(valor_mostrado, leidos)
    assert volumen == volumen_esperado

    lectura_id = db_lecturas.llamar_registrar_lectura(
        conexion, medidor_id, volumen, date(2026, 8, 16), "manual", None
    )
    with conexion.cursor() as cur:
        cur.execute("SELECT valor FROM mimedidor.lectura WHERE id = %s", (lectura_id,))
        guardado = float(cur.fetchone()[0])

    # La igualdad exacta es el punto: si la columna redondeara, este assert fallaría.
    assert guardado == volumen_esperado


def test_medidor_inexistente_se_distingue_de_cero_decimales(conexion):
    """`None` (no existe) y `0` (sin dígitos rojos) no se pueden confundir.

    Si se confundieran, una lectura de un medidor inexistente se guardaría sin convertir en vez
    de devolver 404.
    """
    assert db_lecturas.digitos_decimales_del_medidor(conexion, str(uuid4())) is None
    assert db_lecturas.digitos_decimales_del_medidor(
        conexion, _crear_medidor_de_prueba(conexion, digitos_decimales=0)
    ) == 0
