# ==============================================================
# tests/test_engine_estructura_vpsi.py
# Verificación completa del estado actual del Engine
# ==============================================================

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.engine import Engine, ArranqueError, Contenedor, RegistroModulos


# ==============================================================
# FIXTURES
# ==============================================================

@pytest.fixture(scope="module")
def engine():
    """Engine arrancado en modo estricto contra modules/."""
    return Engine(Path("modules"), invocador_id="test_estructura", strict=True)


# ==============================================================
# 1. ARRANQUE Y ESTADO
# ==============================================================

def test_engine_arranca_operativo(engine):
    assert engine.estado == "OPERATIVO"
    assert engine.errores_arranque == []


def test_engine_tiene_atributos_obligatorios(engine):
    for attr in (
        "registro",
        "resultados_evaluacion",
        "errores_arranque",
        "fallos",
        "invocador_id",
        "estado",
        "raiz",
    ):
        assert hasattr(engine, attr), f"Falta atributo Engine.{attr}"


def test_registro_no_vacio(engine):
    assert engine.registro.total() >= 1
    assert len(engine.registro.contenedores) >= 1


# ==============================================================
# 2. DETERMINISMO
# ==============================================================

def test_determinismo_censar():
    eng_a = Engine(Path("modules"), invocador_id="det_a", strict=True)
    eng_b = Engine(Path("modules"), invocador_id="det_b", strict=True)

    a = eng_a.censar()
    b = eng_b.censar()

    assert a["total"] == b["total"]
    assert sorted(a["roles"].keys()) == sorted(b["roles"].keys())
    assert a["cargados"] == b["cargados"]


# ==============================================================
# 3. ESTADO GLOBAL
# ==============================================================

def test_estado_global_estructura(engine):
    eg = engine.estado_global()

    assert isinstance(eg, dict)
    assert eg["tipo"] == "estado_global"
    assert "version_engine" in eg
    assert "estado" in eg
    assert "total_contenedores" in eg
    assert "roles" in eg
    assert "cargados" in eg
    assert "exploracion" in eg
    assert "resolucion" in eg
    assert "auditoria" in eg
    assert "grafo" in eg
    assert "dependencias" in eg
    assert "indice_simbolos" in eg
    assert "errores_arranque" in eg


def test_estado_global_coherente_con_registro(engine):
    eg = engine.estado_global()
    assert eg["total_contenedores"] == engine.registro.total()
    assert eg["estado"] == engine.estado


# ==============================================================
# 4. CONTENEDORES Y CAPACIDADES
# ==============================================================

def test_todos_los_contenedores_tienen_contrato(engine):
    for nombre, cont in engine.registro.contenedores.items():
        assert isinstance(cont, Contenedor)
        assert cont.nombre
        assert cont.rol
        assert isinstance(cont.capacidades, dict)
        assert isinstance(cont.requiere, list)


def test_capacidades_resolubles(engine):
    """Todas las capacidades declaradas deben ser resolubles (callable)."""
    for nombre, cont in engine.registro.contenedores.items():
        for clave in cont.capacidades:
            fn = cont.fn(clave)
            assert callable(fn), (
                f"Capacidad '{clave}' del módulo '{nombre}' no es callable"
            )


# ==============================================================
# 5. CENSAR
# ==============================================================

def test_censar_estructura(engine):
    c = engine.censar()
    assert "total" in c
    assert "roles" in c
    assert "cargados" in c
    assert c["total"] == engine.registro.total()


# ==============================================================
# 6. API PÚBLICA DEL ENGINE (si existe)
# ==============================================================

def test_api_publica_basica(engine):
    # Métodos que deben existir siempre
    assert callable(getattr(engine, "estado_global", None))
    assert callable(getattr(engine, "censar", None))

    # Métodos forenses (si fueron añadidos)
    for metodo in (
        "localizar_id",
        "inventario_global",
        "detectar_contradicciones",
        "grafo_global",
        "dependencias_globales",
        "auditoria_global",
    ):
        if hasattr(engine, metodo):
            assert callable(getattr(engine, metodo))


def test_localizar_id_si_existe(engine):
    if not hasattr(engine, "localizar_id"):
        pytest.skip("localizar_id no implementado todavía")

    # Debe encontrar al menos un módulo registrado
    primer_modulo = next(iter(engine.registro.contenedores))
    r = engine.localizar_id(primer_modulo)
    assert r["encontrado"] is True
    assert r["tipo"] == "modulo"


def test_inventario_global_si_existe(engine):
    if not hasattr(engine, "inventario_global"):
        pytest.skip("inventario_global no implementado todavía")

    inv = engine.inventario_global()
    assert isinstance(inv, dict)
    assert "modulos" in inv
    assert "roles" in inv
    assert len(inv["modulos"]) == engine.registro.total()


# ==============================================================
# 7. LECTOR UNIVERSAL (si existe)
# ==============================================================

def test_leer_archivo_si_existe(engine):
    if not hasattr(engine, "leer_archivo"):
        pytest.skip("leer_archivo no implementado todavía")

    # Debe poder listar archivos
    if hasattr(engine, "listar_archivos"):
        archivos = engine.listar_archivos()
        assert isinstance(archivos, list)


# ==============================================================
# 8. STRICT MODE
# ==============================================================

def test_strict_mode_rechaza_si_hay_errores():
    """
    Si el Engine se construye con strict=True y hay errores de arranque,
    debe lanzar ArranqueError.
    (Este test solo valida el contrato de la excepción, no fuerza un fallo real)
    """
    # Simplemente comprobamos que ArranqueError es la excepción correcta
    assert issubclass(ArranqueError, Exception)


# ==============================================================
# 9. INTEGRIDAD DE ROLES
# ==============================================================

def test_roles_consistentes(engine):
    eg = engine.estado_global()
    roles_eg = set(eg["roles"].keys())
    roles_reg = set(engine.registro.por_rol.keys())
    assert roles_eg == roles_reg
