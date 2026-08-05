# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/c_citaciones/__init__.py

Rol CC — catálogo de citaciones.

FUNCIÓN
  Leer y organizar todo lo que está debajo (categorias/*.py).
  Exponer el catálogo de citaciones a Engine (ids y casillas).
  Nada más.

  Engine busca en este catálogo lo que exista y pueda usar en el ciclo.
  Este módulo no calcula. No orquesta. No interpreta pedidos.

NO HACE
  Calcular Tru / C / L / K. Aplicar α β. Conteos. Clasificar O.
  Anunciar en lugar de CIT. Ejecutar CA, FO, AX, MC, RE, TX, CH.

CONTRATO CON ENGINE
  Capacidades: barrer, inventario, categorias, por_id, ids, esquema.
  Engine ejecuta solo lo que CONTENEDOR declara.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from core.diagnostico import DiagnosticoGlobal  # type: ignore
except Exception:  # noqa: BLE001
    class DiagnosticoGlobal:
        @staticmethod
        def recibir_reporte(*args, **kwargs):
            pass

_DIR = Path(__file__).parent
_CAT_DIR = _DIR / "categorias"

__version__ = "1.0"

ESQUEMA_CATEGORIA: Dict[str, Any] = {
    "obligatorios": ["id", "nombre", "unidad", "enunciado"],
    "opcionales": [
        "nivel_fractal",
        "jurisdiccion",
        "requiere",
        "factores_evaluables",
        "agrega_desde",
        "fuente_modulo",
        "senales",
        "anclas",
        "version",
        "notas",
    ],
    "prohibidos": [
        "Tru_Ri", "Tru_total", "tru_ri", "tru_total",
        "C", "L", "K",
        "alpha", "beta", "ALPHA", "BETA", "Fraction",
    ],
    "nota": (
        "Archivos bajo categorias/ declaran CATEGORIA o CATEGORIAS. "
        "ST los lee y expone ids. No calcula."
    ),
}

_CAMPOS_OBLIGATORIOS = tuple(ESQUEMA_CATEGORIA["obligatorios"])
_VALORES_PROHIBIDOS = tuple(ESQUEMA_CATEGORIA["prohibidos"])


def _cargar_desde_archivo(archivo: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    errores: List[str] = []
    if archivo.name.startswith("_") or archivo.name == "__init__.py":
        return [], errores
    nombre_mod = f"citaciones_cat_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return [], [f"{archivo.name}: no se pudo crear spec"]
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        return [], [f"{archivo.name}: import {type(e).__name__}: {e}"]
    halladas: List[Dict[str, Any]] = []
    una = getattr(mod, "CATEGORIA", None)
    if isinstance(una, dict):
        halladas.append(una)
    varias = getattr(mod, "CATEGORIAS", None)
    if isinstance(varias, list):
        for item in varias:
            if isinstance(item, dict):
                halladas.append(item)
    if not halladas:
        errores.append(f"{archivo.name}: sin CATEGORIA/CATEGORIAS exportada")
    return halladas, errores


def _validar_categoria(cat: Dict[str, Any], origen: str) -> List[str]:
    errs: List[str] = []
    if not isinstance(cat, dict):
        return [f"{origen}: CATEGORIA no es dict"]
    for k in _CAMPOS_OBLIGATORIOS:
        if k not in cat or not str(cat.get(k, "")).strip():
            errs.append(f"{origen}: falta campo obligatorio '{k}'")
    for prohibido in _VALORES_PROHIBIDOS:
        if prohibido in cat and cat[prohibido] is not None:
            errs.append(
                f"{origen}: campo prohibido '{prohibido}' "
                f"(oficio ajeno; ST solo organiza el catálogo)"
            )
    return errs


def _normalizar(cat: Dict[str, Any], origen: str) -> Dict[str, Any]:
    nivel = cat.get("nivel_fractal")
    try:
        nivel_n = int(nivel) if nivel is not None else None
    except (TypeError, ValueError):
        nivel_n = None
    juris = cat.get("jurisdiccion")
    fuente = cat.get("fuente_modulo")
    return {
        "id": str(cat["id"]).strip().lower(),
        "nombre": str(cat["nombre"]).strip(),
        "unidad": str(cat["unidad"]).strip(),
        "enunciado": str(cat["enunciado"]).strip(),
        "nivel_fractal": nivel_n,
        "jurisdiccion": str(juris).strip() if juris else None,
        "requiere": [str(x) for x in (cat.get("requiere") or [])],
        "factores_evaluables": [str(x) for x in (cat.get("factores_evaluables") or [])],
        "agrega_desde": [str(x) for x in (cat.get("agrega_desde") or [])],
        "fuente_modulo": str(fuente).strip() if fuente else None,
        "senales": [str(x).lower() for x in (cat.get("senales") or [])],
        "anclas": [str(x) for x in (cat.get("anclas") or [])],
        "origen": origen,
        "version": str(cat.get("version") or "1.0"),
        "notas": str(cat.get("notas") or ""),
    }


def recolectar() -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    cats: List[Dict[str, Any]] = []
    errores: List[Dict[str, str]] = []
    archivos: List[Path] = []
    if _CAT_DIR.is_dir():
        archivos.extend(sorted(_CAT_DIR.glob("*.py")))
    archivos.extend(sorted(_DIR.glob("*.py")))
    vistos: set = set()
    for archivo in archivos:
        if archivo.name == "__init__.py" or archivo.name.startswith("_"):
            continue
        key = str(archivo.resolve())
        if key in vistos:
            continue
        vistos.add(key)
        halladas, errs = _cargar_desde_archivo(archivo)
        for e in errs:
            errores.append({"archivo": archivo.name, "error": e})
        for raw in halladas:
            ve = _validar_categoria(raw, archivo.name)
            if ve:
                for e in ve:
                    errores.append({"archivo": archivo.name, "error": e})
                continue
            try:
                cats.append(_normalizar(raw, archivo.stem))
            except Exception as e:  # noqa: BLE001
                errores.append({
                    "archivo": archivo.name,
                    "error": f"normalizar: {type(e).__name__}: {e}",
                })
    por_id: Dict[str, List[str]] = {}
    for c in cats:
        por_id.setdefault(c["id"], []).append(c["origen"])
    for cid, origenes in por_id.items():
        if len(origenes) > 1:
            errores.append({
                "archivo": ",".join(origenes),
                "error": f"id duplicado '{cid}' en {origenes}",
            })
    cats.sort(key=lambda c: (c["nivel_fractal"] is None, c["nivel_fractal"] or 0, c["id"]))
    return cats, errores


def barrer() -> Dict[str, Any]:
    cats, errores = recolectar()
    if errores:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="citaciones",
                errores=[{"tipo": "error_categoria", "detalle": e} for e in errores],
            )
        except Exception:
            pass
    notas: List[str] = []
    if not cats and not errores:
        notas.append("catálogo vacío (legítimo hasta montar archivos en categorias/)")
    return {
        "contenedor": "citaciones",
        "rol": "CC",
        "coherente": not errores,
        "categorias": len(cats),
        "ids": [c["id"] for c in cats],
        "errores": errores,
        "notas": notas,
        "version": __version__,
        "oficio": "organizar y exponer el catálogo de citaciones",
        "esquema": ESQUEMA_CATEGORIA,
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return isinstance(salida, dict) and "coherente" in salida


def categorias() -> List[Dict[str, Any]]:
    r = barrer()
    if not r.get("coherente", False):
        return []
    cats, _ = recolectar()
    return cats


def por_id(cat_id: str) -> Optional[Dict[str, Any]]:
    key = str(cat_id or "").strip().lower()
    for c in categorias():
        if c["id"] == key:
            return dict(c)
    return None


def ids() -> List[str]:
    return [c["id"] for c in categorias()]


def esquema() -> Dict[str, Any]:
    return dict(ESQUEMA_CATEGORIA)


def inventario(peticion: Any = None) -> Dict[str, Any]:
    cats, errores = recolectar()
    return {
        "contenedor": "citaciones",
        "version": __version__,
        "rol": "CC",
        "funcion": (
            "Catálogo de citaciones. "
            "Expone ids y casillas a Engine. No calcula."
        ),
        "para_engine": (
            "Aquí están los ids de citaciones disponibles. "
            "Úsalos con los módulos que ya tienen el oficio correspondiente."
        ),
        "esquema_categoria": ESQUEMA_CATEGORIA,
        "categorias": cats,
        "ids": [c["id"] for c in cats],
        "total": len(cats),
        "errores": errores,
        "coherente": not errores,
        "no_hace": [
            "calcular",
            "orquestar",
            "interpretar pedidos",
            "sustituir CIT / CA / FO / AX / CX / MC / RE / TX / CH",
        ],
        "extension": (
            "Agregar o editar un archivo en categorias/ actualiza el catálogo "
            "sin tocar este INIT."
        ),
    }


CONTENEDOR = {
    "nombre": "citaciones",
    "rol": "CC",
    "version": __version__,
    "requiere": [],
    "descripcion": (
        "Catálogo de citaciones. Rol CC. "
        "Lee y organiza categorias/*.py. Expone ids a Engine. "
        "No calcula. No interpreta pedidos. "
        "El Engine ejecuta solo lo que este contrato declara."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "categorias": categorias,
        "por_id": por_id,
        "ids": ids,
        "esquema": esquema,
    },
}


__all__ = [
    "CONTENEDOR",
    "ESQUEMA_CATEGORIA",
    "recolectar",
    "barrer",
    "verificar_salida",
    "categorias",
    "por_id",
    "ids",
    "esquema",
    "inventario",
]
