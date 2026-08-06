# ==============================================================
# tests/test_contratos_init.py
# Verificación automática de TODOS los CONTENEDOR (__init__.py)
# No hardcodea cantidad de módulos. Los descubre.
# ==============================================================

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.engine import Engine, ArranqueError


# ==============================================================
# FIXTURE: Engine que descubre automáticamente todo
# ==============================================================

@pytest.fixture(scope="module")
def engine():
    return Engine(Path("modules"), invocador_id="test_contratos", strict=True)


# ==============================================================
# 1. DESCUBRIMIENTO AUTOMÁTICO
# ==============================================================

def test_engine_descubre_modulos(engine):
    """El Engine debe haber descubierto al menos un módulo."""
    assert engine.registro.total() >= 1
    assert len(engine.registro.contenedores) >= 1


def test_todos_los_init_tienen_contenedor(engine):
    """
    Todo módulo descubierto debe tener un CONTENEDOR válido.
    No se hardcodea cuántos hay: se itera sobre lo que el Engine encontró.
    """
    for nombre, cont in engine.registro.contenedores.items():
        assert cont.meta is not None, f"{nombre}: sin meta/CONTENEDOR"
        assert isinstance(cont.meta, dict), f"{nombre}: CONTENEDOR no es dict"


# ==============================================================
# 2. ESTRUCTURA DEL CONTRATO (forma mínima)
# ==============================================================

def test_contrato_campos_obligatorios(engine):
    """
    Cada CONTENEDOR debe declarar los campos mínimos del Contrato Universal.
    """
    campos_obligatorios = ("nombre", "rol", "version", "requiere", "capacidades")

    for nombre, cont in engine.registro.contenedores.items():
        meta = cont.meta
        for campo in campos_obligatorios:
            assert campo in meta, (
                f"{nombre}: falta campo obligatorio '{campo}' en CONTENEDOR"
            )


def test_contrato_tipos_correctos(engine):
    """Los campos del CONTENEDOR deben tener los tipos correctos."""
    for nombre, cont in engine.registro.contenedores.items():
        meta = cont.meta

        assert isinstance(meta.get("nombre"), str) and meta["nombre"], (
            f"{nombre}: 'nombre' debe ser str no vacío"
        )
        assert isinstance(meta.get("rol"), str) and meta["rol"], (
            f"{nombre}: 'rol' debe ser str no vacío"
        )
        assert isinstance(meta.get("version"), str), (
            f"{nombre}: 'version' debe ser str"
        )
        assert isinstance(meta.get("requiere"), list), (
            f"{nombre}: 'requiere' debe ser list"
        )
        assert isinstance(meta.get("capacidades"), dict), (
            f"{nombre}: 'capacidades' debe ser dict"
        )


# ==============================================================
# 3. COHERENCIA NOMBRE / ROL
# ==============================================================

def test_nombre_coincide_con_registro(engine):
    """El nombre declarado en CONTENEDOR debe coincidir con la clave del registro."""
    for nombre, cont in engine.registro.contenedores.items():
        assert cont.nombre == nombre, (
            f"Clave de registro '{nombre}' != cont.nombre '{cont.nombre}'"
        )


def test_roles_no_vacios(engine):
    """Ningún módulo debe tener rol vacío."""
    for nombre, cont in engine.registro.contenedores.items():
        assert cont.rol.strip(), f"{nombre}: rol vacío"


# ==============================================================
# 4. CAPACIDADES RESOLUBLES
# ==============================================================

def test_todas_las_capacidades_son_resolubles(engine):
    """
    Toda capacidad declarada en cualquier CONTENEDOR debe ser callable.
    Se verifica automáticamente sobre todos los módulos descubiertos.
    """
    fallos = []

    for nombre, cont in engine.registro.contenedores.items():
        for clave in cont.capacidades:
            fn = cont.fn(clave)
            if not callable(fn):
                fallos.append(f"{nombre}.{clave} → no callable")

    assert not fallos, (
        "Capacidades no resolubles encontradas:\n  - " + "\n  - ".join(fallos)
    )


def test_capacidades_claves_son_str(engine):
    """Las claves de capacidades deben ser strings."""
    for nombre, cont in engine.registro.contenedores.items():
        for clave in cont.capacidades:
            assert isinstance(clave, str), (
                f"{nombre}: clave de capacidad no es str → {clave!r}"
            )


# ==============================================================
# 5. RESOLUCIÓN DEL ENGINE
# ==============================================================

def test_resolucion_coincide_con_capacidades(engine):
    """
    La resolución hecha por el Engine debe reflejar exactamente
    las capacidades declaradas en cada CONTENEDOR.
    """
    if not hasattr(engine, "_resolucion"):
        pytest.skip("_resolucion no disponible")

    for nombre, cont in engine.registro.contenedores.items():
        resol = engine._resolucion.get(nombre)
        assert resol is not None, f"{nombre}: sin entrada en _resolucion"

        declaradas = set(cont.capacidades.keys())
        resolubles = set(resol.get("resolubles", []))
        no_resolubles = set(resol.get("no_resolubles", []))

        assert resolubles | no_resolubles == declaradas, (
            f"{nombre}: resolución no cubre todas las capacidades declaradas"
        )
        assert len(no_resolubles) == 0, (
            f"{nombre}: capacidades no resolubles → {no_resolubles}"
        )


# ==============================================================
# 6. AUDITORÍA ESTRUCTURAL
# ==============================================================

def test_auditoria_todos_coherentes(engine):
    """Todos los módulos deben resultar coherentes en la auditoría del Engine."""
    if not hasattr(engine, "_auditoria"):
        pytest.skip("_auditoria no disponible")

    incoherentes = []
    for nombre, aud in engine._auditoria.items():
        if not aud.get("coherente", False):
            incoherentes.append(nombre)

    assert not incoherentes, (
        "Módulos incoherentes según auditoría del Engine:\n  - "
        + "\n  - ".join(incoherentes)
    )


# ==============================================================
# 7. DESCUBRIMIENTO vs DISCO (consistencia)
# ==============================================================

def test_modulos_en_disco_estan_registrados(engine):
    """
    Toda carpeta con __init__.py dentro de modules/ debe haber sido
    registrada por el Engine (o rechazada con error explícito).
    """
    en_disco = set()
    for p in Path("modules").iterdir():
        if p.is_dir() and (p / "__init__.py").exists():
            en_disco.add(p.name)

    registrados = set(engine.registro.contenedores.keys())
    # También consideramos los que fallaron al cargar
    rechazados = set()
    for err in engine.errores_arranque:
        # Los errores suelen contener el nombre de la carpeta
        for carpeta in en_disco:
            if carpeta in err:
                rechazados.add(carpeta)

    no_vistos = en_disco - registrados - rechazados
    assert not no_vistos, (
        "Carpetas con __init__.py no registradas ni rechazadas:\n  - "
        + "\n  - ".join(sorted(no_vistos))
    )
