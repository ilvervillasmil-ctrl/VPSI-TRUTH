"""
Test mínimo del módulo realidad (RE).

Comprueba:
  1. barrer() coherente (o vacío legítimo sin choques de contrato).
  2. Cada FUNCION de conocimiento_humano tiene contrato de simbiosis.
  3. No hay nombres de función duplicados.
  4. categoria == conocimiento_humano en disciplinas de esa carpeta.
  5. pide_evaluacion_engine implica requiere_aprobacion_dominio.
  6. acceso e inventario exportan lo básico.

No llama a Internet.
No calcula Tru.
No exige que existan las 27 disciplinas: solo valida las que haya.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Raíz del repo en path (CI y local)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _import_realidad():
    from modules import realidad

    return realidad


def test_realidad_importa_y_exporta_contenedor():
    re = _import_realidad()
    assert hasattr(re, "CONTENEDOR")
    c = re.CONTENEDOR
    assert c.get("nombre") == "realidad"
    assert c.get("rol") == "RE"
    assert "verificar" in (c.get("capacidades") or {})
    assert "inventario" in (c.get("capacidades") or {})


def test_barrer_coherente_o_vacio_legitimo():
    re = _import_realidad()
    informe = re.barrer()
    assert isinstance(informe, dict)
    assert "coherente" in informe
    assert "choques" in informe
    assert "errores" in informe
    # Si hay choques o errores de contrato, coherente debe ser False
    if informe.get("choques") or informe.get("errores"):
        assert informe["coherente"] is False
    else:
        assert informe["coherente"] is True


def test_simbiosis_pide_evaluacion_exige_aprobacion():
    """Contrato: no se puede pedir evaluación a Engine sin aprobación de dominio."""
    re = _import_realidad()
    informe = re.barrer()
    # Si el init marca choque de simbiosis, debe aparecer en choques
    for c in informe.get("choques") or []:
        if "pide_evaluacion_engine" in str(c) and "requiere_aprobacion_dominio" in str(c):
            pytest.fail("choque de simbiosis detectado: {0}".format(c))


def test_funciones_descubiertas_tienen_nombre_y_hace():
    re = _import_realidad()
    inv = re.inventario()
    funciones = inv.get("funciones") or {}
    for nombre, meta in funciones.items():
        assert nombre, "nombre de función vacío"
        assert meta.get("nombre"), "FUNCION sin nombre: {0}".format(meta)
        assert meta.get("hace"), "FUNCION sin hace: {0}".format(nombre)


def test_nombres_de_funcion_unicos():
    re = _import_realidad()
    informe = re.barrer()
    funciones = informe.get("funciones") or []
    if isinstance(funciones, list):
        assert len(funciones) == len(set(funciones)), (
            "nombres de función duplicados: {0}".format(funciones)
        )


def test_conocimiento_humano_categoria_y_simbiosis():
    """
    Disciplinas bajo conocimiento_humano (si existen) deben declarar
    categoria y contrato de simbiosis.
    """
    base = ROOT / "modules" / "realidad" / "conocimiento_humano"
    if not base.is_dir():
        pytest.skip("carpeta conocimiento_humano aún no montada")

    import importlib.util

    vistos = []
    for path in sorted(base.glob("*.py")):
        if path.name.startswith("_") or path.name == "__init__.py":
            continue
        nombre_mod = "test_ch_{0}".format(path.stem)
        spec = importlib.util.spec_from_file_location(nombre_mod, path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, "FUNCION", None)
        assert isinstance(fn, dict), "{0}: sin FUNCION".format(path.name)
        assert fn.get("nombre"), "{0}: FUNCION.nombre vacío".format(path.name)
        assert fn.get("hace"), "{0}: FUNCION.hace vacío".format(path.name)
        assert fn.get("categoria") == "conocimiento_humano", (
            "{0}: categoria debe ser conocimiento_humano".format(path.name)
        )
        assert fn.get("pide_evaluacion_engine") is True, (
            "{0}: pide_evaluacion_engine debe ser True".format(path.name)
        )
        assert fn.get("requiere_aprobacion_dominio") is True, (
            "{0}: requiere_aprobacion_dominio debe ser True".format(path.name)
        )
        assert fn.get("o_evaluacion"), (
            "{0}: falta o_evaluacion".format(path.name)
        )
        vistos.append(fn["nombre"])

    assert len(vistos) == len(set(vistos)), (
        "nombres duplicados en conocimiento_humano: {0}".format(vistos)
    )


def test_acceso_exporta_canal_y_sondas():
    re = _import_realidad()
    assert hasattr(re, "Canal")
    assert hasattr(re, "hay_acceso")
    assert hasattr(re, "hay_dns")
    assert callable(re.hay_acceso)
    assert callable(re.hay_dns)


def test_inventario_contrato_simbiosis_documentado():
    re = _import_realidad()
    inv = re.inventario()
    assert inv.get("contenedor") == "realidad"
    assert inv.get("rol") == "RE"
    cs = inv.get("contrato_simbiosis")
    if cs is not None:
        assert isinstance(cs, dict)
        assert cs.get("quien_calcula")
        assert cs.get("quien_aprueba_material")
        assert cs.get("material_sin_aprobacion")
