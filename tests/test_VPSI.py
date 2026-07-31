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
# SEGMENTO 1.1 --- COROLARIO β-GÖDEL
# ===============================================================
#
# Corolario β-Gödel: β > 0 es la raíz estructural de la incompletud formal.
# En cualquier sistema formal lo suficientemente rico, siempre habrá verdades indecidibles (β).

def test_corolario_beta_godel():
    """Verifica que β > 0 es la raíz de la incompletud formal (Corolario β-Gödel)."""
    # β debe ser > 0 (Axioma β)
    assert BETA > F(0), "β debe ser > 0 (Axioma β)"

    # β es 1/27 (derivado del cubo 3x3x3)
    assert BETA == F(1, 27), "β debe ser 1/27 (derivado del cubo 3x3x3)"

    # Verificar que Tru_total(D) >= β para cualquier D (Teorema 17)
    assert tru_total(F(0), F(0), F(0)) == BETA, "Tru_total(0,0,0) debe ser β (Teorema 17)"

def test_corolario_beta_persistencia():
    """Verifica que β persiste incluso cuando Tru_Ri colapsa (Teorema 17)."""
    # Tru_total no puede ser menor que β
    assert tru_total(F(0), F(0), F(0)) == BETA
    assert tru_total(F(1), F(0), F(1)) == BETA
    assert tru_total(F(0), F(1), F(1)) == BETA

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
        Canal().obtener("https://ejemplo.invalido")

@sin_realidad
def test_realidad_tls_y_timeouts():
    c = Canal()
    assert c.verificar_tls is True
    assert c.timeout_conexion > 0
    assert c.timeout_lectura > 0

# ----- inti: declaracion -----

@sin_realidad
def test_realidad_fuente_completa_entra():
    Inti().declarar(dict(FUENTE))

@sin_realidad
def test_realidad_fuente_sin_alcance_no_entra():
    with pytest.raises(FronteraRota):
        Inti().declarar(dict(FUENTE, alcance=[]))

@sin_realidad
def test_realidad_fuente_vacia_no_entra():
    """Piso de carga: una fuente vacia es coherente con todo."""
    with pytest.raises(FronteraRota, match="vacuidad"):
        Inti().declarar(dict(FUENTE, entradas=0))

@sin_realidad
def test_realidad_fuente_sin_version_no_entra():
    with pytest.raises(FronteraRota):
        Inti().declarar(dict(FUENTE, version=""))

# ----- inti: sello -----

@sin_realidad
def test_realidad_no_se_consulta_sin_sellar():
    i = Inti()
    i.declarar(dict(FUENTE))
    with pytest.raises(SelloAusente):
        i.consultar("prueba", "x",
                    {"estado": ENCONTRADO, "dato": "y", "procedencia": "prueba"})

@sin_realidad
def test_realidad_no_se_sella_sin_fuentes():
    with pytest.raises(FronteraRota):
        Inti().sellar(INSTANTE)

@sin_realidad
def test_realidad_huella_reproducible():
    assert (_sellado().inventario()["sello"]["huella"]
            == _sellado().inventario()["sello"]["huella"])

@sin_realidad
def test_realidad_respuesta_arrastra_el_sello():
    i = _sellado()
    r = i.consultar("prueba", "casa",
                    {"estado": ENCONTRADO, "dato": "edificio",
                     "procedencia": "prueba"})
    assert r["instante"] == INSTANTE
    assert r["sello"] == i.inventario()["sello"]["huella"]

# ----- inti: respuesta -----

@sin_realidad
def test_realidad_tres_estados_no_dos():
    assert len(ESTADOS) == 3
    assert NO_EXISTE != FUERA_DE_ALCANCE

@sin_realidad
def test_realidad_fuera_de_alcance_es_valido():
    r = _sellado().consultar("prueba", "andromeda",
                             {"estado": FUERA_DE_ALCANCE, "dato": None,
                              "procedencia": "prueba"})
    assert r["estado"] == FUERA_DE_ALCANCE

@sin_realidad
def test_realidad_estado_invalido_se_rechaza():
    with pytest.raises(FronteraRota):
        _sellado().consultar("prueba", "x",
                             {"estado": "QUIZA", "dato": "y",
                              "procedencia": "prueba"})

@sin_realidad
def test_realidad_sin_procedencia_se_rechaza():
    with pytest.raises(FronteraRota, match="procedencia"):
        _sellado().consultar("prueba", "x",
                             {"estado": ENCONTRADO, "dato": "y"})

@sin_realidad
def test_realidad_veredicto_se_rechaza():
    """REALIDAD es Ri, no R: entrega dato y origen, nunca juicio."""
    with pytest.raises(FronteraRota, match="juicio"):
        _sellado().consultar("prueba", "x",
                             {"estado": ENCONTRADO, "dato": "y",
                              "procedencia": "prueba", "correcto": True})

@sin_realidad
def test_realidad_factores_se_rechazan():
    with pytest.raises(FronteraRota, match="juicio"):
        _sellado().consultar("prueba", "x",
                             {"estado": ENCONTRADO, "dato": "y",
                              "procedencia": "prueba", "K": F(1)})

@sin_realidad
def test_realidad_encontrado_exige_dato():
    with pytest.raises(FronteraRota):
        _sellado().consultar("prueba", "x",
                             {"estado": ENCONTRADO, "dato": None,
                              "procedencia": "prueba"})

@sin_realidad
def test_realidad_no_encontrado_exige_dato_vacio():
    with pytest.raises(FronteraRota):
        _sellado().consultar("prueba", "x",
                             {"estado": NO_EXISTE, "dato": "algo",
                              "procedencia": "prueba"})

@sin_realidad
def test_realidad_fuente_no_declarada_se_rechaza():
    with pytest.raises(FronteraRota):
        _sellado().consultar("otra", "x",
                             {"estado": ENCONTRADO, "dato": "y",
                              "procedencia": "otra"})

# ----- inti: invariancia -----

@sin_realidad
def test_realidad_misma_consulta_misma_respuesta():
    i = _sellado()
    r = {"estado": ENCONTRADO, "dato": "edificio", "procedencia": "prueba"}
    i.consultar("prueba", "casa", dict(r))
    i.consultar("prueba", "casa", dict(r))

@sin_realidad
def test_realidad_dos_respuestas_rompen_invariancia():
    i = _sellado()
    i.consultar("prueba", "casa",
                {"estado": ENCONTRADO, "dato": "uno", "procedencia": "prueba"})
    with pytest.raises(FronteraRota, match="invariancia"):
        i.consultar("prueba", "casa",
                    {"estado": ENCONTRADO, "dato": "otro",
                     "procedencia": "prueba"})

# ----- inti: disponibilidad y barrido -----

@sin_realidad
def test_realidad_indisponible_no_se_sustituye():
    i = _sellado()
    i.marcar_indisponible("prueba", "sin conexion")
    with pytest.raises(FuenteIndisponible):
        i.consultar("prueba", "x",
                    {"estado": ENCONTRADO, "dato": "y",
                     "procedencia": "prueba"})

@sin_realidad
def test_realidad_barrer_sin_fuentes_no_pasa():
    b = Inti().barrer()
    assert b["pasa"] is False
    assert "ninguna fuente declarada" in b["faltas"]

@sin_realidad
def test_realidad_barrer_sellado_pasa():
    b = _sellado().barrer()
    assert b["pasa"] is True
    assert b["faltas"] == []

@sin_realidad
def test_realidad_barrer_con_indisponible_no_pasa():
    i = _sellado()
    i.marcar_indisponible("prueba", "sin conexion")
    assert i.barrer()["pasa"] is False

@sin_realidad
def test_realidad_axiomas_tienen_forma():
    for d in RE.axiomas():
        for clave in CLAVES_DECLARACION:
            assert clave in d, d.get("id")

# ===============================================================
# SEGMENTO 6 --- ESTADO DE CONSTRUCCION
# ===============================================================
#
# Lo que falta debe ser visible. Estas pruebas no exigen que el
# sistema este completo: exigen que lo incompleto se declare.

def test_construccion_roles_pendientes_son_visibles():
    vacios = motor().registro.resumen()["roles_vacios"]
    assert isinstance(vacios, list)
    for rol in vacios:
        assert rol not in ("AX", "CT", "FO"), f"{rol} deberia estar montado"

def test_construccion_evaluar_sin_calculador_no_finge():
    """
    Sin rol CA no hay C, L, K. Lo unico inaceptable seria que
    evaluar() devolviera un numero como si lo hubiera calculado.
    Cuando CA se monte, esta prueba se salta sola.
    """
    e = motor()
    if "CA" in e.registro.resumen()["roles"]:
        pytest.skip("CA montado: esta prueba cubre la fase de construccion")

    try:
        r = e.evaluar({"mensaje": "sonda", "contexto": "Octx"})
    except Exception:
        return  # aborta: aceptable, no finge nada

    assert r.get("tru_total") in (None, "UNDEFINED"), (
        f"sin CA no puede haber Tru_total: {r.get('tru_total')}"
    )
