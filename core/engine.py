"""
VPSI-TRUTH --- tests/test_vpsi.py

Suite única de verificación axiomática y estructural.
Basada en los principios del framework VPSI-TRUTH (v9.4):

1. **Ancla**: ALPHA y BETA (derivados del cubo 3x3x3 en ℝ³).
2. **Fórmulas**: La ecuación canónica Tru_total = (C * L * K * α) + β.
3. **Axiomas**: Barrido axiomático y coherencia (TA4, TA5, etc.).
4. **Engine**: Arranque, descubrimiento de módulos y ejecución de contratos.
5. **Contexto**: Filtro inicial (coherencia del repositorio).
6. **Construcción**: Verificación de que lo que falta sea visible.

Principios clave aplicados:
- TA4: R ⊥ Observer (el Engine no modifica R).
- TA5: Multiplicatividad de la verdad (Tru_Ri = C * L * K).
- TA7: Sin acceso directo a R (solo a través de X).
- Teorema 16: Techo estructural α (Tru_total ≤ 26/27).
- Teorema 17: Imposibilidad de colapso total (Tru_total ≥ β = 1/27).
- Teorema TR1: Generatividad estructural (el framework genera más verdades que postula).
- Corolario Def-5.3.1: K es indefinido sin O_context explícito.
"""

from fractions import Fraction
import pytest
from core.engine import Engine, AutoridadError, es_undefined, UNDEFINED

# Constantes para pruebas
F = Fraction
ALPHA = F(26, 27)
BETA = F(1, 27)

# Fixture para el Engine (evita reinicializar en cada prueba)
@pytest.fixture(scope="module")
def engine():
    """Fixture para el Engine. Se inicializa una vez por módulo de pruebas."""
    return Engine(raiz_modulos="modules", invocador_id="core")

# Fixture para declaraciones axiomáticas (evita duplicación de lógica)
@pytest.fixture
def declaraciones_axiomaticas(engine):
    """Recopila declaraciones axiomáticas de todos los módulos con capacidad 'axiomas'."""
    declaraciones = {}
    for contenedor in engine.registro.contenedores.values():
        if contenedor.tiene_capacidad("axiomas"):
            result = engine.invocador.ejecutar_capacidad(contenedor, "axiomas")
            if not es_undefined(result):
                declaraciones[contenedor.nombre] = result
    return declaraciones

# Fixture para reiniciar el invocador (evita estado global compartido)
@pytest.fixture(autouse=True)
def reiniciar_invocador(engine):
    """Reinicia el invocador antes de cada prueba para evitar estado compartido."""
    engine.invocador.reiniciar()
    yield
    engine.invocador.reiniciar()

# ===============================================================
# SEGMENTO 1 --- ANCLA (ALPHA y BETA)
# ===============================================================
# Axioma β: β = 1/27 es la fracción interior irreducible del cubo 3x3x3.
# Teorema M.1: N=3 es el mínimo único con interior estructural.
# ===============================================================

def test_ancla_alpha_y_beta_son_fracciones_exactas(engine):
    """Axioma β: ALPHA y BETA deben ser Fraction (no float)."""
    ct = engine.registro.por_rol("CT")
    assert ct is not None, "Módulo CT no encontrado"

    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    assert isinstance(alpha, Fraction), "ALPHA debe ser Fraction"
    assert isinstance(beta, Fraction), "BETA debe ser Fraction"
    assert alpha == ALPHA, f"ALPHA debe ser {ALPHA}"
    assert beta == BETA, f"BETA debe ser {BETA}"

def test_ancla_suma_es_uno_exacto(engine):
    """Teorema: ALPHA + BETA = 1 (Ley de Conservación)."""
    ct = engine.registro.por_rol("CT")
    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    assert alpha + beta == F(1), "ALPHA + BETA debe ser 1 exacto"

def test_ancla_derivados_del_cubo_3x3x3(engine):
    """Teorema M.1: ALPHA y BETA se derivan del cubo 3x3x3 (26/27 y 1/27)."""
    ct = engine.registro.por_rol("CT")
    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    n = 3
    total_celdas = n ** 3
    celdas_interiores = (n - 2) ** 3
    celdas_exteriores = total_celdas - celdas_interiores

    assert beta == F(celdas_interiores, total_celdas), "BETA debe ser 1/27 (celdas interiores)"
    assert alpha == F(celdas_exteriores, total_celdas), "ALPHA debe ser 26/27 (celdas exteriores)"

def test_ancla_techo_no_alcanza_unidad(engine):
    """Teorema 16: ALPHA < 1 (techo estructural)."""
    ct = engine.registro.por_rol("CT")
    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    assert alpha < F(1), "ALPHA debe ser < 1"

def test_ancla_piso_es_positivo(engine):
    """Axioma β: BETA > 0 (piso estructural)."""
    ct = engine.registro.por_rol("CT")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")
    assert beta > F(0), "BETA debe ser > 0"

# ===============================================================
# SEGMENTO 1.1 --- COROLARIO β-GÖDEL
# ===============================================================
# Corolario β-Gödel: La incompletud formal es una instancia de β en el dominio lógico.
# Teorema 17: Tru_total(D) ≥ β siempre (imposibilidad de colapso total).
# ===============================================================

def test_corolario_beta_godel(engine):
    """Corolario β-Gödel: β > 0 es la raíz de la incompletud formal."""
    ct = engine.registro.por_rol("CT")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")
    assert beta > F(0), "β debe ser > 0 (Axioma β)"
    assert beta == F(1, 27), "β debe ser 1/27 (derivado del cubo 3x3x3)"

def test_corolario_beta_persistencia(engine):
    """Teorema 17: Tru_total(0,0,0) = β (piso estructural)."""
    fo = engine.registro.por_rol("FO")
    assert fo is not None, "Módulo FO no encontrado"

    # Tru_total(0,0,0) = (0 * 0 * 0 * α) + β = β
    tru_total = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(0), "L": F(0), "K": F(0)}
    )
    assert tru_total == beta, f"Tru_total(0,0,0) debe ser β = {beta}"

# ===============================================================
# SEGMENTO 2 --- FÓRMULAS (Tru_Ri y Tru_total)
# ===============================================================
# Axioma TA5: Tru_Ri = C * L * K (multiplicatividad de la verdad).
# Teorema 16: Tru_total = (Tru_Ri * α) + β (techo estructural α).
# Teorema 17: Tru_total ≥ β (piso estructural β).
# ===============================================================

VECTORES_PRUEBA = [
    (F(1), F(1), F(1), "sincronización total"),
    (F(1), F(1), F(0), "K colapsada: forma impecable, ancla rota"),
    (F(0), F(1), F(1), "C colapsada"),
    (F(1), F(0), F(1), "L colapsada"),
    (F(0), F(0), F(0), "colapso de los tres factores"),
    (F(85, 100), F(9, 10), F(7, 10), "caso intermedio"),
]

def test_formula_tru_ri_es_producto(engine):
    """Axioma TA5: Tru_Ri = C * L * K."""
    fo = engine.registro.por_rol("FO")
    assert fo is not None, "Módulo FO no encontrado"

    for C, L, K, _ in VECTORES_PRUEBA:
        tru_ri = engine.invocador.ejecutar_capacidad(
            fo, "evaluar", {"C": C, "L": L, "K": K}
        ).get("tru_ri")
        assert tru_ri == C * L * K, f"Tru_Ri debe ser C*L*K = {C*L*K}"

def test_formula_tru_total_es_canonica(engine):
    """Teorema: Tru_total = (Tru_Ri * α) + β."""
    fo = engine.registro.por_rol("FO")
    ct = engine.registro.por_rol("CT")
    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    for C, L, K, _ in VECTORES_PRUEBA:
        tru_ri = C * L * K
        tru_total_esperado = (tru_ri * alpha) + beta
        tru_total = engine.invocador.ejecutar_capacidad(
            fo, "evaluar", {"C": C, "L": L, "K": K}
        ).get("tru_total")
        assert tru_total == tru_total_esperado, (
            f"Tru_total debe ser (Tru_Ri * α) + β = {tru_total_esperado}"
        )

def test_formula_devuelve_fraction(engine):
    """Axioma F4: Las fórmulas deben devolver Fraction (no float)."""
    fo = engine.registro.por_rol("FO")
    for C, L, K, _ in VECTORES_PRUEBA:
        resultado = engine.invocador.ejecutar_capacidad(
            fo, "evaluar", {"C": C, "L": L, "K": K}
        )
        assert isinstance(resultado.get("tru_ri"), Fraction), "Tru_Ri debe ser Fraction"
        assert isinstance(resultado.get("tru_total"), Fraction), "Tru_total debe ser Fraction"

def test_formula_piso_es_beta(engine):
    """Teorema 17: Tru_total(0,0,0) = β (piso estructural)."""
    fo = engine.registro.por_rol("FO")
    ct = engine.registro.por_rol("CT")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    tru_total = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(0), "L": F(0), "K": F(0)}
    ).get("tru_total")
    assert tru_total == beta, f"Tru_total(0,0,0) debe ser β = {beta}"

def test_formula_techo_es_alpha_mas_beta(engine):
    """Teorema 16: Tru_total(1,1,1) = α + β = 1."""
    fo = engine.registro.por_rol("FO")
    ct = engine.registro.por_rol("CT")
    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    tru_total = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(1), "L": F(1), "K": F(1)}
    ).get("tru_total")
    assert tru_total == alpha + beta, f"Tru_total(1,1,1) debe ser α + β = 1"

def test_formula_siempre_dentro_de_cota(engine):
    """Teorema 16 y 17: β ≤ Tru_total ≤ α + β = 1."""
    fo = engine.registro.por_rol("FO")
    ct = engine.registro.por_rol("CT")
    alpha = engine.invocador.ejecutar_capacidad(ct, "alpha")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    for C, L, K, _ in VECTORES_PRUEBA:
        tru_total = engine.invocador.ejecutar_capacidad(
            fo, "evaluar", {"C": C, "L": L, "K": K}
        ).get("tru_total")
        assert beta <= tru_total <= alpha + beta, (
            f"Tru_total debe estar en [β, 1]. Recibido: {tru_total}"
        )

def test_formula_sin_compensacion_entre_factores(engine):
    """Axioma TA5: Un factor nulo anula Tru_Ri (no hay compensación)."""
    fo = engine.registro.por_rol("FO")
    ct = engine.registro.por_rol("CT")
    beta = engine.invocador.ejecutar_capacidad(ct, "beta")

    # Tru_total(1,1,0) = (1*1*0 * α) + β = β
    tru_total_1 = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(1), "L": F(1), "K": F(0)}
    ).get("tru_total")
    # Tru_total(0,0,0) = (0*0*0 * α) + β = β
    tru_total_2 = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(0), "L": F(0), "K": F(0)}
    ).get("tru_total")
    assert tru_total_1 == tru_total_2 == beta, (
        "Tru_total debe ser β cuando cualquier factor es 0"
    )

def test_formula_es_monotona(engine):
    """Teorema: Tru_total aumenta si C, L o K aumentan (monotonicidad)."""
    fo = engine.registro.por_rol("FO")

    # Tru_total(1,1,0.9) > Tru_total(1,1,0.5)
    tru_total_alto = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(1), "L": F(1), "K": F(9, 10)}
    ).get("tru_total")
    tru_total_bajo = engine.invocador.ejecutar_capacidad(
        fo, "evaluar", {"C": F(1), "L": F(1), "K": F(5, 10)}
    ).get("tru_total")
    assert tru_total_alto > tru_total_bajo, (
        "Tru_total debe ser monotónico con respecto a K"
    )

# ===============================================================
# SEGMENTO 3 --- AXIOMAS
# ===============================================================
# Axioma TA4: R ⊥ Observer (independencia de la realidad).
# Teorema 12: La confusión de R_i con R es la fuente de colapso.
# Corolario Def-5.3.1: K es indefinido sin O_context explícito.
# ===============================================================

PISO_DECLARACIONES = 147  # Mínimo de declaraciones para evitar coherencia por vacuidad

def test_axiomas_barrido_coherente(engine):
    """Teorema: El barrido axiomático debe ser coherente (sin choques)."""
    ax = engine.registro.por_rol("AX")
    assert ax is not None, "Módulo AX no encontrado"
    assert ax.tiene_capacidad("verificar"), "AX debe declarar capacidad 'verificar'"

    informe_ax = engine.invocador.ejecutar_capacidad(ax, "verificar")
    assert isinstance(informe_ax, dict), "El informe debe ser un diccionario"
    assert informe_ax.get("coherente", False) is True, (
        f"Barrido axiomático incoherente: {informe_ax.get('choques', [])}"
    )
    assert informe_ax.get("choques", []) == [], "No debe haber choques axiomáticos"

def test_axiomas_piso_de_carga(engine, declaraciones_axiomaticas):
    """Teorema: Coherencia por coherencia, no por vacuidad (mínimo de declaraciones)."""
    ax = engine.registro.por_rol("AX")
    informe_ax = engine.invocador.ejecutar_capacidad(ax, "verificar", declaraciones_axiomaticas)
    n_declaraciones = informe_ax.get("declaraciones", 0)
    assert n_declaraciones >= PISO_DECLARACIONES, (
        f"Se exigen al menos {PISO_DECLARACIONES} declaraciones. Recibido: {n_declaraciones}"
    )

def test_axiomas_ids_unicos(engine):
    """Teorema: Los IDs de las declaraciones axiomáticas deben ser únicos."""
    ax = engine.registro.por_rol("AX")
    axiomas = engine.invocador.ejecutar_capacidad(ax, "axiomas")
    assert isinstance(axiomas, list), "axiomas() debe devolver una lista"

    ids = [d.get("id") for d in axiomas if isinstance(d, dict)]
    ids_unicos = set(ids)
    assert len(ids) == len(ids_unicos), f"IDs duplicados: {sorted(set(ids) - ids_unicos)}"

def test_axiomas_forma_de_cada_declaracion(engine):
    """Corolario Def-5.3.1: Cada declaración debe tener claves obligatorias."""
    ax = engine.registro.por_rol("AX")
    axiomas = engine.invocador.ejecutar_capacidad(ax, "axiomas")
    CLAVES_OBLIGATORIAS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")

    for d in axiomas:
        assert isinstance(d, dict), f"Declaración {d} no es un diccionario"
        for clave in CLAVES_OBLIGATORIAS:
            assert clave in d, f"Declaración {d.get('id')} falta clave '{clave}'"
        assert isinstance(d["polaridad"], bool), (
            f"Declaración {d.get('id')}: polaridad debe ser bool"
        )

def test_axiomas_inventario_cuadra(engine):
    """Teorema: El inventario de AX debe ser consistente con sus declaraciones."""
    ax = engine.registro.por_rol("AX")
    assert ax.tiene_capacidad("inventario"), "AX debe declarar capacidad 'inventario'"

    inventario = engine.invocador.ejecutar_capacidad(ax, "inventario")
    assert isinstance(inventario, dict), "inventario() debe devolver un diccionario"
    assert "declaraciones" in inventario, "Inventario debe incluir 'declaraciones'"
    assert "por_tipo" in inventario, "Inventario debe incluir 'por_tipo'"

    # Verificar que la suma de declaraciones por tipo iguale al total
    total_por_tipo = sum(inventario["por_tipo"].values())
    assert total_por_tipo == inventario["declaraciones"], (
        "La suma de declaraciones por tipo debe igualar al total"
    )

# ===============================================================
# SEGMENTO 4 --- ENGINE (EJECUTOR DE CONTRATOS)
# ===============================================================
# Axioma TA4: R ⊥ Observer (el Engine no modifica R).
# Axioma F4: Y = g(X, U) (el Engine opera sobre contratos, no sobre R).
# Teorema 17: Tru_total ≥ β (el Engine garantiza módulos obligatorios).
# ===============================================================

def test_engine_arranca(engine):
    """Axioma TA4: El Engine debe arrancar si los módulos obligatorios están presentes."""
    assert engine is not None, "El Engine debe inicializarse correctamente"

def test_engine_solo_core_puede_ejecutarlo():
    """Axioma de Autoridad: Solo el módulo 'core' puede ejecutar el Engine."""
    with pytest.raises(AutoridadError):
        Engine(raiz_modulos="modules", invocador_id="no_core")

def test_engine_verifica_contratos_obligatorios(engine):
    """Teorema 17: El Engine verifica que los módulos obligatorios declaren sus capacidades."""
    # AX debe declarar 'verificar'
    ax = engine.registro.por_rol("AX")
    assert ax is not None, "Módulo AX no encontrado"
    assert ax.tiene_capacidad("verificar"), "AX debe declarar capacidad 'verificar'"

    # CT debe declarar 'alpha' y 'beta'
    ct = engine.registro.por_rol("CT")
    assert ct is not None, "Módulo CT no encontrado"
    assert ct.tiene_capacidad("alpha"), "CT debe declarar capacidad 'alpha'"
    assert ct.tiene_capacidad("beta"), "CT debe declarar capacidad 'beta'"

    # FO debe declarar al menos una capacidad
    fo = engine.registro.por_rol("FO")
    assert fo is not None, "Módulo FO no encontrado"
    assert fo.capacidades, "FO debe declarar al menos una capacidad"

    # MC debe declarar 'verificar'
    mc = engine.registro.por_rol("MC")
    assert mc is not None, "Módulo MC no encontrado"
    assert mc.tiene_capacidad("verificar"), "MC debe declarar capacidad 'verificar'"

def test_engine_roles_obligatorios_presentes(engine):
    """Axioma TA4: Los módulos obligatorios (AX, CT, FO, MC) deben estar presentes."""
    roles = engine.registro.resumen()["roles"]
    for rol in ("AX", "CT", "FO", "MC"):
        assert rol in roles, f"Rol {rol} no cargado"

def test_engine_ningun_modulo_rechazado(engine):
    """Teorema: El Engine no debe rechazar módulos válidos."""
    rechazados = engine.registro.resumen()["rechazados"]
    assert rechazados == [], f"Módulos rechazados: {rechazados}"

def test_engine_conocimiento_total_incluye_modulos(engine):
    """Teorema: El Engine debe tener conocimiento completo de los módulos."""
    conocimiento = engine.conocimiento()
    assert "modulos" in conocimiento, "Conocimiento debe incluir 'modulos'"
    assert len(conocimiento["modulos"]) > 0, "Debe haber al menos un módulo"

    for nombre, info in conocimiento["modulos"].items():
        assert "nombre" in info, f"Módulo {nombre} falta clave 'nombre'"
        assert "rol" in info, f"Módulo {nombre} falta clave 'rol'"
        assert "capacidades" in info, f"Módulo {nombre} falta clave 'capacidades'"

def test_engine_ejecutar_capacidad_inexistente(engine):
    """Axioma F4: El Engine debe devolver UNDEFINED si la capacidad no existe."""
    resultado = engine.ejecutar_capacidad("AX", "capacidad_inexistente")
    assert es_undefined(resultado), "Debe devolver UNDEFINED para capacidad inexistente"
    assert len(engine.invocador.fallos) == 1, "Debe registrar un fallo"
    assert engine.invocador.fallos[0]["capacidad"] == "capacidad_inexistente"

def test_engine_ejecutar_capacidad_con_peticion_invalida(engine):
    """Corolario Def-5.3.1: Si falta una clave requerida, debe devolver UNDEFINED."""
    ca = engine.registro.por_rol("CA")
    if ca is None:
        pytest.skip("Módulo CA no disponible")

    # Suponiendo que CA requiere "mensaje" y "contexto"
    resultado = engine.ejecutar_capacidad("CA", "evaluar", {"mensaje": "prueba"})
    if ca.requiere and "contexto" in ca.requiere:
        assert es_undefined(resultado), "Debe devolver UNDEFINED si falta 'contexto'"
        assert len(engine.invocador.fallos) == 1, "Debe registrar un fallo"

def test_engine_evaluar_sin_modulo_ca(engine):
    """Teorema: Si CA no está disponible, evaluar() debe devolver reportes vacíos."""
    # Simular que CA no está disponible (no es obligatorio para evaluar)
    ca = engine.registro.por_rol("CA")
    if ca is not None:
        # Temporalmente eliminar CA del registro (solo para esta prueba)
        engine.registro.contenedores.pop(ca.nombre, None)

    resultado = engine.evaluar({"mensaje": "prueba"})
    assert "reportes" in resultado, "Debe devolver 'reportes'"
    assert "CA" not in resultado["reportes"], "CA no debe estar en reportes si no está disponible"

    # Restaurar CA
    if ca is not None:
        engine.registro.contenedores[ca.nombre] = ca

# ===============================================================
# SEGMENTO 4.5 --- CONTEXTO (FILTRO INICIAL)
# ===============================================================
# Axioma TA4: R ⊥ Observer (el contexto no modifica R).
# Teorema 12: La confusión de R_i con R es la fuente de colapso.
# ===============================================================

@pytest.mark.skipif(
    not any(c.rol == "CX" for c in Engine("modules", "core").registro.contenedores.values()),
    reason="Módulo CX no disponible"
)
def test_contexto_modulo_cargado(engine):
    """Axioma TA4: El módulo CX debe estar cargado si existe."""
    cx = engine.registro.por_rol("CX")
    assert cx is not None, "Módulo CX no encontrado"

@pytest.mark.skipif(
    not any(c.rol == "CX" for c in Engine("modules", "core").registro.contenedores.values()),
    reason="Módulo CX no disponible"
)
def test_contexto_tiene_capacidad_evaluar(engine):
    """Teorema: CX debe declarar capacidad 'evaluar' o 'resolver'."""
    cx = engine.registro.por_rol("CX")
    assert cx is not None, "Módulo CX no encontrado"

    # Verificar que tenga al menos una capacidad de evaluación
    assert cx.tiene_capacidad("evaluar") or cx.tiene_capacidad("resolver"), (
        "CX debe declarar capacidad 'evaluar' o 'resolver'"
    )

@pytest.mark.skipif(
    not any(c.rol == "CX" for c in Engine("modules", "core").registro.contenedores.values()),
    reason="Módulo CX no disponible"
)
def test_contexto_resolver_con_peticion_vacia(engine):
    """Teorema: CX debe poder resolver una petición vacía (o devolver UNDEFINED)."""
    cx = engine.registro.por_rol("CX")
    assert cx is not None, "Módulo CX no encontrado"

    capacidad = "evaluar" if cx.tiene_capacidad("evaluar") else "resolver"
    resultado = engine.ejecutar_capacidad("CX", capacidad, {})

    # Puede ser UNDEFINED o un dict, pero no debe fallar
    assert isinstance(resultado, (dict, type(UNDEFINED))), (
        "CX debe devolver un dict o UNDEFINED"
    )

# ===============================================================
# SEGMENTO 5 --- REALIDAD (ACCESO A R)
# ===============================================================
# Axioma TA7: Sin acceso directo a R (solo a través de X).
# Teorema 14: La propiedad de la verdad pertenece al sistema que la produce.
# ===============================================================

@pytest.mark.skipif(
    not any(c.rol == "RE" for c in Engine("modules", "core").registro.contenedores.values()),
    reason="Módulo RE no disponible"
)
def test_realidad_modulo_cargado(engine):
    """Axioma TA7: El módulo RE debe estar cargado si existe."""
    re = engine.registro.por_rol("RE")
    assert re is not None, "Módulo RE no encontrado"

# ===============================================================
# SEGMENTO 6 --- CONSTRUCCIÓN (VERIFICACIÓN DE LO QUE FALTA)
# ===============================================================
# Teorema TR1: El framework debe ser generativo (|Im(⊕)| > |Θ|).
# Corolario 17.1: Tru_total ∈ [β, 1] (lo que falta debe ser visible).
# ===============================================================

def test_construccion_roles_pendientes_son_visibles(engine):
    """Teorema TR1: Los roles vacíos deben ser visibles para el Engine."""
    vacios = engine.registro.resumen()["roles_vacios"]
    assert isinstance(vacios, list), "roles_vacios debe ser una lista"

    # Los módulos obligatorios no deben estar en roles_vacios
    for rol in ("AX", "CT", "FO", "MC"):
        assert rol not in vacios, f"{rol} debe estar montado (es obligatorio)"

def test_construccion_evaluar_sin_calculador_no_finge(engine):
    """Teorema: Si CA no está disponible, evaluar() no debe fingir resultados."""
    ca = engine.registro.por_rol("CA")
    if ca is None:
        pytest.skip("Módulo CA no disponible")

    # Temporalmente eliminar CA
    engine.registro.contenedores.pop(ca.nombre, None)
    try:
        resultado = engine.evaluar({"mensaje": "sonda", "contexto": "Octx"})
        # CA no debe estar en reportes
        assert "CA" not in resultado.get("reportes", {}), (
            "CA no debe estar en reportes si no está disponible"
        )
    finally:
        # Restaurar CA
        engine.registro.contenedores[ca.nombre] = ca
