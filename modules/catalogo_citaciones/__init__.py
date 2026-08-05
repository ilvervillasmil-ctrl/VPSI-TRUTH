# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/catalogo_citaciones/__init__.py

Rol CC — glosario / catálogo de IDs del repositorio.

FUNCIÓN
  Esta carpeta es de IDs.
  Lee y organiza todo lo que está debajo (categorias/*.py).
  Expone esos IDs a Engine.
  Nada más.

  Engine consulta aquí los IDs que necesite cuando Omega
  o un usuario los pidan (citar, reportar, referenciar).
  Los IDs viven en los archivos de categorias/, no en este INIT.

  Ejemplos de lo que puede haber debajo (cuando se escriban):
    - IDs de axiomas
    - IDs de escalas
    - IDs de contratos / roles
    - IDs de cualquier casilla del repositorio que deba poder citarse

NO HACE
  Calcular Tru / C / L / K.
  Aplicar α β.
  Conteos.
  Clasificar O.
  Orquestar el ciclo.
  Anunciar en lugar de CIT.
  Ejecutar CA, FO, AX, MC, RE, TX, CH.

CONTRATO CON ENGINE
  Capacidades: barrer, inventario, categorias, por_id, ids, esquema.
  Engine ejecuta solo lo que CONTENEDOR declara.
  Engine busca IDs aquí cuando se los piden; este módulo solo informa.
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

# Forma de cada casilla bajo categorias/.
# Los IDs NO se listan en este INIT: viven en los archivos.
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
        "Cada uno aporta uno o más IDs del repositorio. "
        "CC los lee y expone. No calcula. "
        "Este INIT no embebe IDs."
    ),
}

_CAMPOS_OBLIGATORIOS = tuple(ESQUEMA_CATEGORIA["obligatorios"])
_VALORES_PROHIBIDOS = tuple(ESQUEMA_CATEGORIA["prohibidos"])


def _cargar_desde_archivo(archivo: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    errores: List[str] = []
    if archivo.name.startswith("_") or archivo.name == "__init__.py":
        return [], errores
    nombre_mod = "citaciones_cat_{0}".format(archivo.stem)
    spec = importlib.util.spec_from_file_location(nombre_mod, str(archivo))
    if spec is None or spec.loader is None:
        return [], ["{0}: no se pudo crear spec".format(archivo.name)]
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        return [], [
            "{0}: import {1}: {2}".format(archivo.name, type(e).__name__, e)
        ]
    halladas: List[Dict[str, Any]] = []
    una = getattr(mod, "CATEGORIA", None)
    if isinstance(una, dict):
        halladas.append(una)
    varias = getattr(mod, "CATEGORIAS", None)
    if isinstance(varias, list):
        for item in varias:
            if isinstance(item, dict):
                halladas.append(item)
    raw_ids = getattr(mod, "IDS", None)
    if isinstance(raw_ids, list):
        for item in raw_ids:
            if isinstance(item, str) and item.strip():
                halladas.append({
                    "id": item.strip().lower(),
                    "nombre": item.strip(),
                    "unidad": "id",
                    "enunciado": "ID del repositorio: {0}".format(item.strip()),
                })
            elif isinstance(item, dict) and item.get("id"):
                halladas.append(item)
    if not halladas:
        errores.append(
            "{0}: sin CATEGORIA/CATEGORIAS/IDS exportada".format(archivo.name)
        )
    return halladas, errores


def _validar_categoria(cat: Dict[str, Any], origen: str) -> List[str]:
    errs: List[str] = []
    if not isinstance(cat, dict):
        return ["{0}: CATEGORIA no es dict".format(origen)]
    for k in _CAMPOS_OBLIGATORIOS:
        if k not in cat or not str(cat.get(k, "")).strip():
            errs.append("{0}: falta campo obligatorio '{1}'".format(origen, k))
    for prohibido in _VALORES_PROHIBIDOS:
        if prohibido in cat and cat[prohibido] is not None:
            errs.append(
                "{0}: campo prohibido '{1}' "
                "(oficio ajeno; CC solo organiza IDs)".format(origen, prohibido)
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
        "factores_evaluables": [
            str(x) for x in (cat.get("factores_evaluables") or [])
        ],
        "agrega_desde": [str(x) for x in (cat.get("agrega_desde") or [])],
        "fuente_modulo": str(fuente).strip() if fuente else None,
        "senales": [str(x).lower() for x in (cat.get("senales") or [])],
        "anclas": [str(x) for x in (cat.get("anclas") or [])],
        "origen": origen,
        "version": str(cat.get("version") or "1.0"),
        "notas": str(cat.get("notas") or ""),
    }


def recolectar() -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Lee categorias/*.py (y *.py no privados junto al INIT).
    Los IDs salen de esos archivos, nunca de una lista fija en este INIT.
    """
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
                    "error": "normalizar: {0}: {1}".format(type(e).__name__, e),
                })
    por_id: Dict[str, List[str]] = {}
    for c in cats:
        por_id.setdefault(c["id"], []).append(c["origen"])
    for cid, origenes in por_id.items():
        if len(origenes) > 1:
            errores.append({
                "archivo": ",".join(origenes),
                "error": "id duplicado '{0}' en {1}".format(cid, origenes),
            })
    cats.sort(
        key=lambda c: (
            c["nivel_fractal"] is None,
            c["nivel_fractal"] or 0,
            c["id"],
        )
    )
    return cats, errores


def barrer() -> Dict[str, Any]:
    cats, errores = recolectar()
    if errores:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="catalogo_citaciones",
                errores=[
                    {"tipo": "error_categoria", "detalle": e} for e in errores
                ],
            )
        except Exception:
            pass
    notas: List[str] = []
    if not cats and not errores:
        notas.append(
            "glosario vacío (legítimo hasta montar archivos en categorias/)"
        )
    return {
        "contenedor": "catalogo_citaciones",
        "rol": "CC",
        "coherente": not errores,
        "categorias": len(cats),
        "ids": [c["id"] for c in cats],
        "errores": errores,
        "notas": notas,
        "version": __version__,
        "oficio": (
            "Glosario de IDs del repositorio. "
            "Engine consulta cuando Omega o un usuario piden citar/reportar."
        ),
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
    key = str(cat
