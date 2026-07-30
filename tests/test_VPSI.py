"""
======================================================================
VPSI-TRUTH  ---  tests/test_vpsi.py
SUITE UNICA DE VERIFICACION
======================================================================

Un solo archivo. Seis secciones, en el orden en que el sistema se
sostiene:

    1. ANCLA          ALPHA y BETA, derivados de la geometria
    2. FORMULAS       la ecuacion, con vectores exactos
    3. AXIOMAS        el barrido y su piso de carga
    4. ENGINE         arranque, descubrimiento, frontera de tipos
    5. REALIDAD       acceso e INTI (se salta si aun no existe)
    6. CONSTRUCCION   lo que falta debe ser visible, no silencioso

Nada aqui toca la red ni depende del reloj. Un test que dependiera de
Internet no seria determinista y fallaria en un runner sin salida.
======================================================================
"""

from fractions import Fraction

import pytest

F = Fraction

# ===============================================================
# SEGMENTO 0 --- IMPORTACIONES Y DISPONIBILIDAD
# ===============================================================

from modules.constante import ALPHA, BETA
from modules.formulas.truth import tru_ri, tru_total
import modules.axiomas as AX
from core.engine import (
    Engine, DominioError, AutoridadError,
    normalizar, es_undefined, UNDEFINED,
    FACTORES, ORDEN_FACTORES,
)

try:
    import modules.realidad as RE
    from modules.realidad import (
        Canal, Inti, ENCONTRADO, NO_EXISTE, FUERA_DE_ALCANCE, ESTADOS,
        FronteraRota, SelloAusente, FuenteIndisponible,
    )
    HAY_REALIDAD = True
except ImportError:
    HAY_REALIDAD = False

sin_realidad = pytest.mark.skipif(
    not HAY_REALIDAD, reason="modules.realidad aun no montado"
)


def motor():
    return Engine("modules", invocador_id="core")


# ===============================================================
# SEGMENTO 1 --- ANCLA
# ===============================================================
#
# CONSTANTES es el unico modulo sin segundo canal contra el cual
# contrastarse: si ALPHA falla, todos los modulos coinciden y
# coinciden mal. Por eso el valor esperado no se importa: se
# reconstruye desde la geometria, que es mas primitiva que la
# constante.

def test_ancla_alpha_beta_son_exactos():
    assert isinstance(ALPHA, Fraction)
    assert isinstance(BETA, Fraction)
    assert not isinstance(ALPHA, float)
    assert not isinstance(BETA, float)


def test_ancla_suma_es_uno_exacto():
    assert ALPHA + BETA == F(1)


def test_ancla_se_deriva_del_cubo():
    """Cubo 3x3x3: 27 celdas, 26 tocan el exterior, 1 queda encerrada."""
    n = 3
    total = n ** 3
    encerradas = (n - 2) ** 3
    accesibles = total - encerradas

    assert (total, encerradas, accesibles) == (27, 1, 26)
    assert BETA == F(encerradas, total)
    assert ALPHA == F(accesibles, total)


def test_ancla_techo_no_alcanza_la_unidad():
    assert ALPHA < F(1)
    assert BETA > F(0)


# ===============================================================
# SEGMENTO 2 --- FORMULAS
# ===============================================================
#
# FORMULAS es la ecuacion: fija, sin estado. Se verifica con
# vectores y aritmetica exacta, de una vez y para siempre.

VECTORES = [
    (F(1),       F(1),     F(1),      "sincronizacion total"),
    (F(1),       F(1),     F(9, 10),  "una particion sin discriminante"),
    (F(1),       F(1),     F(0),      "K colapsada: forma impecable, ancla rota"),
    (F(0),       F(1),     F(1),      "C colapsada"),
    (F(1),       F(0),     F(1),      "L colapsada"),
    (F(0),       F(0),     F(0),      "colapso de los tres"),
    (F(85, 100), F(9, 10), F(7, 10),  "caso intermedio"),
]


def test_formula_tru_ri_es_el_producto():
    for C, L, K, _ in VECTORES:
        assert tru_ri(C, L, K) == C * L * K


def test_formula_tru_total_es_la_canonica():
    for C, L, K, _ in VECTORES:
        assert tru_total(C, L, K) == (C * L * K * ALPHA) + BETA


def test_formula_devuelve_fraction_no_float():
    for C, L, K, _ in VECTORES:
        assert isinstance(tru_ri(C, L, K), Fraction)
        assert isinstance(tru_total(C, L, K), Fraction)


def test_formula_piso_es_beta():
    """TA5: la nulidad de un solo factor colapsa la ecuacion entera."""
    assert tru_total(F(0), F(0), F(0)) == BETA
    assert tru_total(F(1), F(1), F(0)) == BETA
    assert tru_total(F(0), F(1), F(1)) == BETA
    assert tru_total(F(1), F(0), F(1)) == BETA


def test_formula_techo_es_alpha_mas_beta():
    assert tru_total(F(1), F(1), F(1)) == ALPHA + BETA


def test_formula_siempre_dentro_de_cota():
    for C, L, K, _ in VECTORES:
        assert BETA <= tru_total(C, L, K) <= ALPHA + BETA


def test_formula_sin_compensacion_entre_factores():
    """Un factor alto no rescata a un producto con cero."""
    assert tru_total(F(1), F(1), F(0)) == tru_total(F(0), F(0), F(0))
    assert tru_ri(F(1), F(1), F(0)) == F(0)


def test_formula_es_monotona():
    assert tru_total(F(1), F(1), F(9, 10)) > tru_total(F(1), F(1), F(5, 10))


# ===============================================================
# SEGMENTO 3 --- AXIOMAS
# ===============================================================
#
# El barrido solo detecta contradicciones entre lo que cargo. Un
# archivo que no entro no puede contradecir a nadie, y el informe
# sale coherente por vacuidad. De ahi el piso.

PISO_DECLARACIONES = 147

CLAVES_DECLARACION = (
    "id", "tipo", "sujeto", "relacion", "objeto", "polaridad", "enunciado",
)


def test_axiomas_barrido_coherente():
    informe = AX.barrer()
    assert informe["coherente"] is True, informe.get("choques")
    assert informe["choques"] == []
    assert informe["errores"] == []


def test_axiomas_piso_de_carga():
    """Coherente por coherencia, no por vacuidad."""
    n = AX.barrer()["declaraciones"]
    assert n >= PISO_DECLARACIONES, (
        f"cargaron {n}, se exigen {PISO_DECLARACIONES}"
    )


def test_axiomas_ids_unicos():
    ids = [d["id"] for d in AX.axiomas()]
    repetidos = {i for i in ids if ids.count(i) > 1}
    assert not repetidos, f"ids repetidos: {sorted(repetidos)}"


def test_axiomas_forma_de_cada_declaracion():
    for d in AX.axiomas():
        for clave in CLAVES_DECLARACION:
            assert clave in d, f"{d.get('id')} sin clave '{clave}'"
        assert isinstance(d["polaridad"], bool), d["id"]


def test_axiomas_inventario_cuadra():
    inv = AX.inventario()
    assert sum(inv["por_tipo"].values()) == inv["declaraciones"]


# ===============================================================
# SEGMENTO 4 --- ENGINE
# ===============================================================

def test_engine_arranca():
    assert motor() is not None


def test_engine_solo_el_core_despacha():
    with pytest.raises(AutoridadError):
        Engine("modules", invocador_id="cualquiera")


def test_engine_verifica_axiomas_al_arrancar():
    assert motor().informe_axiomas["coherente"] is True


def test_engine_roles_montados():
    roles = motor().registro.resumen()["roles"]
    for rol in ("AX", "CT", "FO"):
        assert rol in roles, f"rol {rol} no cargado"


def test_engine_ningun_modulo_rechazado():
    assert motor().registro.resumen()["rechazados"] == []


def test_engine_inventario_completo():
    inv = motor().inventario()
    for clave in ("roles", "roles_vacios", "constantes",
                  "orden_factores", "axiomas", "contenido"):
        assert clave in inv


def test_engine_constantes_exactas():
    assert motor().inventario()["constantes"]["suma_exacta"] is True


def test_engine_orden_de_factores():
    assert ORDEN_FACTORES == ("C", "L", "K")
    assert set(FACTORES) == {"C", "L", "K"}


# ----- frontera de tipos -----

def test_engine_normalizar_acepta_exactos():
    assert normalizar(F(9, 10), "factor C") == F(9, 10)
    assert normalizar(1, "factor C") == F(1)
    assert normalizar(0, "factor C") == F(0)
    assert normalizar("9/10", "factor K") == F(9, 10)


def test_engine_normalizar_rechaza_float():
    with pytest.raises(DominioError, match="float"):
        normalizar(0.9, "factor C")


def test_engine_normalizar_rechaza_fuera_de_dominio():
    with pytest.raises(DominioError, match="dominio"):
        normalizar(F(3, 2), "factor C")
    with pytest.raises(DominioError, match="dominio"):
        normalizar(F(-1, 2), "factor L")


def test_engine_normalizar_rechaza_tipo_no_admitido():
    with pytest.raises(DominioError):
        normalizar([1], "factor K")


def test_engine_normalizar_propaga_undefined():
    assert es_undefined(normalizar(UNDEFINED, "factor C"))


# ===============================================================
# SEGMENTO 5 --- REALIDAD
# ===============================================================

INSTANTE = "2026-07-30T00:00:00Z"

FUENTE = {
    "nombre": "prueba",
    "funcion": "fuente de prueba",
    "alcance": ["lexico"],
    "version": "1.0",
    "entradas": 10,
}


def _sellado():
    i = Inti()
    i.declarar(dict(FUENTE))
    i.sellar(INSTANTE)
    return i


# ----- acceso -----

@sin_realidad
def test_realidad_canal_abre_y_cierra():
    c = Canal()
    assert c.abierto is False
    c.abrir()
    assert c.abierto is True
    c.cerrar()
    assert c.abierto is False


@sin_realidad
def test_realidad_canal_como_contexto():
    with Canal() as c:
        assert c.abierto is True


@sin_realidad
def test_realidad_canal_cerrado_no_obtiene():
    with pytest.raises(RuntimeError, match="cerrado"):
        Canal().obtener("
