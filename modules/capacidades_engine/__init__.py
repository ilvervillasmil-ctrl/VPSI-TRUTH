# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/capacidades_engine/__init__.py

Rol CE — skills complementarios del Engine.

EXCLUSIVO DEL ENGINE
  Este módulo es solo para el Engine.
  Ningún otro módulo (FO, CA, CX, TT, CIT, …) invoca ni interpreta CE.
  Engine lee lo que hay debajo y amplía su repertorio de orquestación.

FUNCIÓN
  Cada archivo bajo capacidades/ es UN skill.
  CE lee todos los archivos y expone el catálogo de skills.
  Skills coherentes con los contratos de los módulos que nombran.
  No contradicen oficios ajenos: complementan la orquestación.

  Más adelante: nueva necesidad → nuevo archivo en capacidades/
  → Engine lo ve al barrer. Sin tocar core.engine ni este INIT.

NO HACE
  Calcular Tru / C / L / K.
  Ejecutar fórmulas.
  Sustituir CA, FO, CX, TT, CIT.
  Ser invocado por módulos que no sean Engine.

CONTRATO
  Engine consulta ids() / por_id() / capacidades().
  Cada skill declara a qué módulos apunta y qué salida espera.
  La ejecución sigue en los módulos de oficio; CE solo lista skills.
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
_CAP_DIR = _DIR / "capacidades"

__version__ = "1.1"

ESQUEMA_SKILL: Dict[str, Any] = {
    "obligatorios": ["id", "nombre", "enunciado", "modulos_objetivo"],
    "opcionales": [
        "version",
        "requiere_roles",
        "entrada",
        "salida_esperada",
        "sincroniza_con",
        "notas",
        "prioridad",
    ],
    "prohibidos": [
        "Tru_Ri", "Tru_total", "C", "L", "K",
        "alpha", "beta", "ALPHA", "BETA", "Fraction",
    ],
    "nota": (
        "Un archivo = un skill. Declarar CAPACIDAD o CAPACIDADES (o SKILL / SKILLS). "
        "CE solo organiza. Engine orquesta. Los módulos de oficio ejecutan."
    ),
    "exclusivo": "Engine",
}

_OBL = tuple(ESQUEMA_SKILL["obligatorios"])
_PROH = tuple(ESQUEMA_SKILL["prohibidos"])


def _cargar(archivo: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    errores: List[str] = []
    if archivo.name.startswith("_") or archivo.name == "__init__.py":
        return [], errores
    nombre = f"ce_skill_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre, archivo)
    if spec is None or spec.loader is None:
        return [], [f"{archivo.name}: sin spec"]
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        return [], [f"{archivo.name}: {type(e).__name__}: {e}"]
    halladas: List[Dict[str, Any]] = []
    for attr in ("CAPACIDAD", "SKILL", "CAPACIDADES", "SKILLS"):
        val = getattr(mod, attr, None)
        if isinstance(val, dict):
            halladas.append(val)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    halladas.append(item)
    if not halladas:
        errores.append(
            f"{archivo.name}: sin CAPACIDAD/SKILL/CAPACIDADES/SKILLS"
        )
    return halladas, errores


def _validar(c: Dict[str, Any], origen: str) -> List[str]:
    errs: List[str] = []
    if not isinstance(c, dict):
        return [f"{origen}: no es dict"]
    for k in _OBL:
        if k not in c:
            errs.append(f"{origen}: falta '{k}'")
        elif k == "modulos_objetivo":
            if not isinstance(c[k], (list, tuple)) or not c[k]:
                errs.append(f"{origen}: modulos_objetivo lista no vacía")
        elif not str(c.get(k, "")).strip():
            errs.append(f"{origen}: '{k}' vacío")
    for p in _PROH:
        if p in c and c[p] is not None:
            errs.append(f"{origen}: prohibido '{p}' (skill no calcula)")
    return errs


def _normalizar(c: Dict[str, Any], origen: str) -> Dict[str, Any]:
    return {
        "id": str(c["id"]).strip().lower(),
        "nombre": str(c["nombre"]).strip(),
        "enunciado": str(c["enunciado"]).strip(),
        "modulos_objetivo": [str(x) for x in c["modulos_objetivo"]],
        "requiere_roles": [str(x) for x in (c.get("requiere_roles") or [])],
        "entrada": [str(x) for x in (c.get("entrada") or [])],
        "salida_esperada": [str(x) for x in (c.get("salida_esperada") or [])],
        "sincroniza_con": [str(x) for x in (c.get("sincroniza_con") or [])],
        "prioridad": int(c["prioridad"]) if c.get("prioridad") is not None else None,
        "origen": origen,
        "version": str(c.get("version") or "1.0"),
        "notas": str(c.get("notas") or ""),
    }


def recolectar() -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    items: List[Dict[str, Any]] = []
    errores: List[Dict[str, str]] = []
    if not _CAP_DIR.is_dir():
        return items, errores
    vistos: set = set()
    for archivo in sorted(_CAP_DIR.glob("*.py")):
        if archivo.name.startswith("_"):
            continue
        key = str(archivo.resolve())
        if key in vistos:
            continue
        vistos.add(key)
        halladas, errs = _cargar(archivo)
        for e in errs:
            errores.append({"archivo": archivo.name, "error": e})
        for raw in halladas:
            ve = _validar(raw, archivo.name)
            if ve:
                for e in ve:
                    errores.append({"archivo": archivo.name, "error": e})
                continue
            try:
                items.append(_normalizar(raw, archivo.stem))
            except Exception as e:  # noqa: BLE001
                errores.append({
                    "archivo": archivo.name,
                    "error": f"normalizar: {type(e).__name__}: {e}",
                })
    por_id: Dict[str, List[str]] = {}
    for it in items:
        por_id.setdefault(it["id"], []).append(it["origen"])
    for cid, orgs in por_id.items():
        if len(orgs) > 1:
            errores.append({
                "archivo": ",".join(orgs),
                "error": f"id duplicado '{cid}'",
            })
    items.sort(key=lambda x: (x["prioridad"] is None, x["prioridad"] or 0, x["id"]))
    return items, errores


def barrer() -> Dict[str, Any]:
    items, errores = recolectar()
    if errores:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="capacidades_engine",
                errores=[{"tipo": "error_skill", "detalle": e} for e in errores],
            )
        except Exception:
            pass
    return {
        "contenedor": "capacidades_engine",
        "rol": "CE",
        "coherente": not errores,
        "skills": len(items),
        "ids": [i["id"] for i in items],
        "errores": errores,
        "version": __version__,
        "oficio": "skills complementarios exclusivos del Engine",
        "exclusivo": "Engine",
        "esquema": ESQUEMA_SKILL,
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return isinstance(salida, dict) and "coherente" in salida


def capacidades() -> List[Dict[str, Any]]:
    """Alias: lista de skills (mismo contrato)."""
    r = barrer()
    if not r.get("coherente", False):
        return []
    items, _ = recolectar()
    return items


def skills() -> List[Dict[str, Any]]:
    return capacidades()


def por_id(skill_id: str) -> Optional[Dict[str, Any]]:
    key = str(skill_id or "").strip().lower()
    for i in capacidades():
        if i["id"] == key:
            return dict(i)
    return None


def ids() -> List[str]:
    return [i["id"] for i in capacidades()]


def esquema() -> Dict[str, Any]:
    return dict(ESQUEMA_SKILL)


def inventario(peticion: Any = None) -> Dict[str, Any]:
    items, errores = recolectar()
    return {
        "contenedor": "capacidades_engine",
        "version": __version__,
        "rol": "CE",
        "exclusivo": "Engine",
        "funcion": (
            "Repertorio de skills del Engine. "
            "Un archivo en capacidades/ = un skill. "
            "Solo el Engine consulta este módulo."
        ),
        "para_engine": (
            "Lee todos los skills. Orquesta con los módulos de oficio "
            "según modulos_objetivo y salida_esperada. "
            "CE no ejecuta el skill."
        ),
        "skills": items,
        "ids": [i["id"] for i in items],
        "total": len(items),
        "errores": errores,
        "coherente": not errores,
        "no_hace": [
            "calcular",
            "evaluar en lugar del Engine",
            "ser usado por FO/CA/CX/TT/CIT",
        ],
        "extension": (
            "Nueva necesidad → nuevo .py en capacidades/ → "
            "Engine lo ve al barrer. Sin tocar core.engine."
        ),
    }


CONTENEDOR = {
    "nombre": "capacidades_engine",
    "rol": "CE",
    "version": __version__,
    "requiere": [],
    "descripcion": (
        "Skills complementarios del Engine. Rol CE. "
        "Exclusivo del Engine: ningún otro módulo lo interpreta. "
        "Un archivo = un skill. Coherente con contratos de módulos de oficio. "
        "No calcula. No sustituye CA/FO/CX/TT. "
        "Anexo de repertorio sin tocar core.engine."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "capacidades": capacidades,
        "skills": skills,
        "por_id": por_id,
        "ids": ids,
        "esquema": esquema,
    },
}


__all__ = [
    "CONTENEDOR",
    "ESQUEMA_SKILL",
    "recolectar",
    "barrer",
    "verificar_salida",
    "capacidades",
    "skills",
    "por_id",
    "ids",
    "esquema",
    "inventario",
]
