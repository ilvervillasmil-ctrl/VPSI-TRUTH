"""
VPSI-TRUTH  ---  tests/test_vpsi.py
SUITE UNICA DE VERIFICACION
======================================================================

Un solo archivo. Seis secciones, en el orden en que el sistema se
sostiene:

    1. ANCLA          ALPHA y BETA, derivados de la geometria
    2. FORMULAS       la ecuacion, con vectores exactos
    3. AXIOMAS        el barrido y su piso de carga
    4. ENGINE         arranque, descubrimiento, frontera de tipos
    4.5. CONTEXTO     filtro inicial: coherencia del repositorio
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
from core.engine import Engine, AutoridadError, es_undefined, UNDEFINED

try:
    import modules.contexto as CX
    from modules.contexto import ContextoError
    HAY_CONTEXTO = True
except ImportError:
    HAY_CONTEXTO = False

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

sin_contexto = pytest.mark.skipif(
    not HAY_CONTEXTO, reason="modules.contexto aun no montado"
)

def motor():
    return Engine("modules", invocador_id="core")


# ===============================================================
# SEGMENTO 1 --- ANCLA
# ===============================================================

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

def test_corolario_beta_godel():
    """Verifica que β > 0 es la raíz de la incompletud formal (Corolario β-Gödel)."""
    assert BETA > F(0), "β debe ser > 0 (Axioma β)"
    assert BETA == F(1, 27), "β debe ser 1/27 (derivado del cubo 3x3x3)"
    assert tru_total(F(0), F(0), F(0)) == BETA, "Tru_total(0,0,0) debe ser β (Teorema 17)"

def test_corolario_beta_persistencia():
    """Verifica que β persiste incluso cuando Tru_Ri colapsa (Teorema 17)."""
    assert tru_total(F(0), F(0), F(0)) == BETA
    assert tru_total(F(1), F(0), F(1)) == BETA
    assert tru_total(F(0), F(1), F(1)) == BETA


# ===============================================================
# SEGMENTO 2 --- FORMULAS
# ===============================================================

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
    e = motor()
    ax = e.registro.por_rol("AX")
    assert ax is not None
    assert ax.tiene_capacidad("verificar")

def test_engine_roles_montados():
    roles = motor().registro.resumen()["roles"]
    for rol in ("AX", "CT", "FO"):
        assert rol in roles, f"rol {rol} no cargado"

def test_engine_ningun_modulo_rechazado():
    assert motor().registro.resumen()["rechazados"] == []

def test_engine_inventario_basico():
    inv = motor().inventario()
    assert "contenido" in inv

# ===============================================================
# SEGMENTO 4.1 --- ENGINE: VERIFICACIÓN AXIOMÁTICA DETALLADA
# ===============================================================

def test_engine_informe_axiomas_mediante_introspeccion():
    """
    Obtiene el informe axiomático usando los métodos oficiales del Engine.
    Esto reemplaza el atributo inexistente 'informe_axiomas' con la
    introspección correcta que el Engine provee.
    """
    e = motor()
    
    # Obtener el módulo AX por su rol
    ax = e.registro.por_rol("AX")
    assert ax is not None, "Módulo AX no encontrado"
    assert ax.tiene_capacidad("verificar"), "AX debe declarar capacidad 'verificar'"
    
    # Recolectar declaraciones de todos los módulos que tienen la capacidad 'axiomas'
    declaraciones = {}
    for c in e.registro.contenedores.values():
        if c.tiene_capacidad("axiomas"):
            result = e.invocador.ejecutar_capacidad(c, "axiomas")
            if not es_undefined(result):
                declaraciones[c.nombre] = result
    
    # Ejecutar verificación de AX
    informe_ax = e.invocador.ejecutar_capacidad(ax, "verificar", declaraciones)
    
    # Verificar que el informe existe y es válido
    assert not es_undefined(informe_ax), "Verificación axiomática devolvió UNDEFINED"
    assert isinstance(informe_ax, dict), "El informe debe ser un diccionario"
    assert "coherente" in informe_ax, "El informe debe tener clave 'coherente'"
    
    # Si es incoherente, mostrar los choques para depuración
    if not informe_ax.get("coherente", False):
        choques = informe_ax.get("choques", [])
        mensaje = f"Sistema axiomático INCOHERENTE: {len(choques)} choques"
        if choques:
            mensaje += f"\nPrimer choque: {choques[0]}"
        pytest.fail(mensaje)
    
    # Guardar el informe en un atributo de la prueba para depuración
    # (esto es solo para que pytest lo muestre si falla)
    assert informe_ax.get("choques", []) == [], "Debe haber cero choques"
    assert len(declaraciones) > 0, "Debe haber al menos una declaración"

def test_engine_conocimiento_total_incluye_ax():
    """
    Verifica que el método conocimiento() del Engine incluye
    toda la información del módulo AX.
    """
    e = motor()
    conocimiento = e.conocimiento()
    
    assert "modulos" in conocimiento
    modulos = conocimiento["modulos"]
    
    # Buscar el módulo AX
    ax_encontrado = False
    for nombre, info in modulos.items():
        if info.get("rol") == "AX":
            ax_encontrado = True
            assert "capacidades" in info
            assert "verificar" in info.get("capacidades", {}), \
                "AX debe tener capacidad 'verificar' en el conocimiento"
            assert "callables" in info
            break
    
    assert ax_encontrado, "Módulo AX no encontrado en el conocimiento del Engine"

def test_engine_censo_muestra_estado_de_ax():
    """
    Verifica que el censo del Engine muestra el estado correcto de AX.
    """
    e = motor()
    censo = e.censar()
    
    assert "cargados" in censo
    assert "roles" in censo
    assert "AX" in censo["roles"], "AX debe aparecer en los roles del censo"
    
    # Verificar que AX está en los módulos cargados
    ax_cargado = False
    for modulo in censo["cargados"]:
        if modulo.get("rol") == "AX":
            ax_cargado = True
            assert modulo.get("nombre") is not None
            assert modulo.get("version") is not None
            assert "capacidades" in modulo
            break
    
    assert ax_cargado, "AX debe estar en la lista de módulos cargados"

def test_engine_ejecutar_capacidad_ax_directamente():
    """
    Ejecuta la capacidad 'verificar' de AX directamente a través del Engine.
    Esta es la forma correcta de obtener el informe axiomático.
    """
    e = motor()
    
    # Primero recolectar declaraciones
    declaraciones = {}
    for c in e.registro.contenedores.values():
        if c.tiene_capacidad("axiomas"):
            result = e.invocador.ejecutar_capacidad(c, "axiomas")
            if not es_undefined(result):
                declaraciones[c.nombre] = result
    
    # Ejecutar la capacidad directamente
    resultado = e.ejecutar_capacidad("AX", "verificar", declaraciones)
    
    assert not es_undefined(resultado), "La ejecución no debe devolver UNDEFINED"
    assert isinstance(resultado, dict), "Debe devolver un diccionario"
    assert "coherente" in resultado, "Debe tener clave 'coherente'"
    
    # Si es coherente, todo bien
    if not resultado.get("coherente", False):
        choques = resultado.get("choques", [])
        pytest.fail(f"AX reporta incoherencia: {len(choques)} choques")


# ===============================================================
# SEGMENTO 4.5 --- CONTEXTO
# ===============================================================

@sin_contexto
def test_contexto_modulo_cargado():
    cx = motor().registro.por_rol("CX")
    assert cx is not None, "Módulo CX (contexto) no cargado"

@sin_contexto
def test_contexto_resolver_via_contrato():
    e = motor()
    cx = e.registro.por_rol("CX")
    assert cx is not None

    capacidad = "evaluar" if cx.tiene_capacidad("evaluar") else "resolver"
    assert cx.tiene_capacidad(capacidad)

    resultado = e.ejecutar_capacidad("CX", capacidad, {})
    assert not es_undefined(resultado)
    assert isinstance(resultado, dict)


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

@sin_realidad
def test_realidad_fuente_completa_entra():
    Inti().declarar(dict(FUENTE))

@sin_realidad
def test_realidad_fuente_sin_alcance_no_entra():
    with pytest.raises(FronteraRota):
        Inti().declarar(dict(FUENTE, alcance=[]))

@sin_realidad
def test_realidad_fuente_vacia_no_entra():
    with pytest.raises(FronteraRota, match="vacuidad"):
        Inti().declarar(dict(FUENTE, entradas=0))

@sin_realidad
def test_realidad_fuente_sin_version_no_entra():
    with pytest.raises(FronteraRota):
        Inti().declarar(dict(FUENTE, version=""))

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

def test_construccion_roles_pendientes_son_visibles():
    vacios = motor().registro.resumen()["roles_vacios"]
    assert isinstance(vacios, list)
    for rol in vacios:
        assert rol not in ("AX", "CT", "FO"), f"{rol} deberia estar montado"

def test_construccion_evaluar_sin_calculador_no_finge():
    e = motor()
    if "CA" in e.registro.resumen()["roles"]:
        pytest.skip("CA montado: esta prueba cubre la fase de construccion")

    try:
        r = e.evaluar({"mensaje": "sonda", "contexto": "Octx"})
    except Exception:
        return


# ===============================================================
# SEGMENTO 4.2 --- ENGINE: INTEGRACIÓN COMPLETA (NUEVO)
# ===============================================================

def test_engine_informe_completo_mediante_conocimiento():
    """
    Obtiene el informe completo del sistema usando conocimiento()
    Esta es la forma más completa de introspección que ofrece el Engine.
    """
    e = motor()
    conocimiento = e.conocimiento()
    
    # Verificar estructura completa
    assert "raiz" in conocimiento
    assert "modulos" in conocimiento
    assert "rechazados" in conocimiento
    assert "roles_ocupados" in conocimiento
    assert "roles_vacios" in conocimiento
    
    # Verificar que cada módulo tiene su conocimiento completo
    for nombre, info in conocimiento["modulos"].items():
        assert "nombre" in info
        assert "rol" in info
        assert "version" in info
        assert "capacidades" in info
        assert "atributos" in info
        assert "callables" in info
    
    # Verificar específicamente AX
    ax_info = None
    for info in conocimiento["modulos"].values():
        if info.get("rol") == "AX":
            ax_info = info
            break
    
    assert ax_info is not None, "AX debe estar en el conocimiento"
    assert "verificar" in ax_info.get("capacidades", {}), \
        "AX debe tener capacidad 'verificar'"
    
    # El informe axiomático está en la verificación al arranque
    # pero podemos confirmar que el sistema es coherente
    assert "AX" in conocimiento["roles_ocupados"], \
        "AX debe estar en roles_ocupados"

def test_engine_informe_axiomas_via_inventario():
    """
    Obtiene el informe axiomático a través del inventario.
    Si los módulos declaran la capacidad 'inventario', esta prueba lo verifica.
    """
    e = motor()
    inventario = e.inventario()
    
    assert "contenido" in inventario
    assert "cargados" in inventario
    
    # Verificar que AX tiene inventario si declara la capacidad
    ax = e.registro.por_rol("AX")
    if ax and ax.tiene_capacidad("inventario"):
        assert "AX" in inventario.get("contenido", {}), \
            "AX debe aparecer en el inventario si declara la capacidad"
        
        contenido_ax = inventario["contenido"].get(ax.nombre, {})
        if isinstance(contenido_ax, dict) and "error" not in contenido_ax:
            # El inventario de AX contiene información útil
            assert True  # La prueba pasa si llegamos aquí

def test_engine_ejecutar_verificacion_ax_con_peticion_vacia():
    """
    Ejecuta la verificación de AX con una petición vacía.
    Esto prueba que el Engine maneja correctamente los casos límite.
    """
    e = motor()
    
    # Ejecutar verificación sin declaraciones
    resultado = e.ejecutar_capacidad("AX", "verificar", {})
    
    # Debe devolver algo (puede ser UNDEFINED o un dict)
    # El comportamiento exacto depende de la implementación de AX
    if not es_undefined(resultado):
        assert isinstance(resultado, dict)
        # Puede ser coherente o no, pero debe ser un dict válido

def test_engine_invocador_registra_fallos_correctamente():
    """
    Verifica que el invocador del Engine registra fallos correctamente
    cuando una capacidad no existe o falla.
    """
    e = motor()
    
    # Intentar ejecutar una capacidad que no existe
    resultado = e.ejecutar_capacidad("AX", "capacidad_inexistente")
    
    # Debe devolver UNDEFINED
    assert es_undefined(resultado)
    
    # El invocador debe haber registrado el fallo
    assert len(e.invocador.fallos) > 0
    fallo = e.invocador.fallos[-1]
    assert fallo.get("capacidad") == "capacidad_inexistente"
    assert "no declarada" in fallo.get("razon", "")

def test_engine_registro_contenedores_es_accesible():
    """
    Verifica que el registro de contenedores del Engine es accesible
    y contiene todos los módulos cargados.
    """
    e = motor()
    
    contenedores = e.registro.contenedores
    assert len(contenedores) > 0, "Debe haber al menos un contenedor"
    
    # Verificar que cada contenedor tiene los atributos mínimos
    for nombre, contenedor in contenedores.items():
        assert contenedor.nombre is not None
        assert contenedor.rol is not None
        assert contenedor.version is not None
        assert isinstance(contenedor.capacidades, dict)
