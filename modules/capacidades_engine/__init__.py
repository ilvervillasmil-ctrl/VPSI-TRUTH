"""
VPSI-TRUTH --- modules/capacidades_engine/__init__.py

Rol CE — capacidades / skills del Engine (mandatos).

FUNCIÓN
  Inventario de skills bajo capacidades/*.py.
  Cada skill declara SKILL = {id, nombre, version, descripcion, ...}.
  Engine lee el catálogo de mandatos; CE no calcula Tru ni orquesta el ciclo.

NO HACE
  - Calcular C, L, K, Tru_Ri, Tru_total.
  - Depositar resultado.sujetos (eso es Engine al evaluar).
  - Sustituir CA, FO, TT, AX, MC, CX, CIT.

El Engine dirige. Este módulo solo expone el contrato CE y el centinela
de skills. El rol "CE" debe estar en ROLES del core/engine.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_DIR = Path(__file__).parent
_CAP = _DIR / "capacidades"

# Campos mínimos de un SKILL (forma de dominio CE)
_SKILL_CAMPOS = ("id", "nombre", "version", "descripcion")


# ===============================================================
# DESCUBRIMIENTO DE SKILLS
# ===============================================================
def _cargar_skills() -> Dict[str, Dict[str, Any]]:
    """
    Carga automática de capacidades/*.py que declaran SKILL o CAPACIDAD.
    Archivo sin dict de skill → no participa.
    """
    hallado: Dict[str, Dict[str, Any]] = {}
    if not _CAP.is_dir():
        return hallado

    for f in sorted(_CAP.glob("*.py")):
        if f.name.startswith("_"):
            continue
        clave = "ce_skill_{0}".format(f.stem)
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            hallado[f.stem] = {
                "archivo": f.name,
                "error": "{0}: {1}".format(type(e).__name__, e),
            }
            continue

        meta = None
        for attr in ("SKILL", "CAPACIDAD", "SKILLS", "CAPACIDADES"):
            raw = getattr(mod, attr, None)
            if isinstance(raw, dict) and raw.get("id"):
                meta = raw
                break
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict) and item.get("id"):
                        meta = item
                        break
            if meta is not None:
                break

        if not isinstance(meta, dict):
            continue

        sid = str(meta.get("id") or "").strip().lower()
        if not sid:
            continue

        entrada: Dict[str, Any] = {
            "archivo": f.name,
            "id": sid,
            "nombre": meta.get("nombre") or f.stem,
            "version": str(meta.get("version") or "0.0"),
            "descripcion": str(meta.get("descripcion") or ""),
            "oficio": meta.get("oficio"),
            "material": meta.get("material"),
            "requiere_catalogo": meta.get("requiere_catalogo"),
            "raw": meta,
        }
        hallado[sid] = entrada

    return hallado


def _validar_skills(hallado: Dict[str, Dict[str, Any]]) -> List[str]:
    errores: List[str] = []
    por_id: Dict[str, List[str]] = {}

    for sid, meta in sorted(hallado.items()):
        if meta.get("error"):
            errores.append("{0}: {1}".format(sid, meta["error"]))
            continue
        for k in _SKILL_CAMPOS:
            if not str(meta.get(k) or "").strip():
                errores.append("skill '{0}': falta campo '{1}'".format(sid, k))
        por_id.setdefault(sid, []).append(meta.get("archivo") or sid)

    for sid, archivos in por_id.items():
        if len(archivos) > 1:
            errores.append(
                "id de skill '{0}' repetido en {1}".format(sid, archivos)
            )
    return errores


# ===============================================================
# API PÚBLICA
# ===============================================================
def skills() -> List[Dict[str, Any]]:
    """Lista de skills descubiertos (sin raw pesado)."""
    hallado = _cargar_skills()
    out: List[Dict[str, Any]] = []
    for sid, meta in sorted(hallado.items()):
        if meta.get("error"):
            continue
        out.append({
            "id": meta.get("id"),
            "nombre": meta.get("nombre"),
            "version": meta.get("version"),
            "descripcion": meta.get("descripcion"),
            "archivo": meta.get("archivo"),
            "oficio": meta.get("oficio"),
            "material": meta.get("material"),
        })
    return out


def ids() -> List[str]:
    """Solo ids de skill (para el diagnóstico y Engine)."""
    return [s["id"] for s in skills() if s.get("id")]


def por_id(skill_id: str) -> Optional[Dict[str, Any]]:
    if not skill_id:
        return None
    clave = str(skill_id).strip().lower()
    for s in skills():
        if s.get("id") == clave:
            return s
    return None


def barrer() -> Dict[str, Any]:
    """
    Centinela CE: coherencia de skills bajo capacidades/.
    No calcula Tru. No deposita sujetos.
    """
    hallado = _cargar_skills()
    errores = _validar_skills(hallado)
    lista_ids = [
        sid for sid, m in sorted(hallado.items()) if not m.get("error")
    ]
    notas: List[str] = []
    if not _CAP.is_dir():
        notas.append(
            "capacidades/ aún no existe (vacío legítimo hasta montar skills)"
        )
    elif not hallado:
        notas.append("ningún skill declarado todavía (vacío legítimo)")

    return {
        "contenedor": "capacidades_engine",
        "rol": "CE",
        "coherente": not errores,
        "errores": errores,
        "choques": [],
        "ids": lista_ids,
        "n": len(lista_ids),
        "notas": notas,
        "nota": (
            "CE: inventario de mandatos del Engine. "
            "Rol CE debe figurar en ROLES de core/engine.py. "
            "No calcula Tru. No deposita resultado.sujetos."
        ),
    }


def verificar() -> Dict[str, Any]:
    return barrer()


def inventario(peticion: Any = None) -> Dict[str, Any]:
    b = barrer()
    return {
        "contenedor": "capacidades_engine",
        "rol": "CE",
        "version": "1.0",
        "ids": b.get("ids"),
        "n": b.get("n"),
        "coherente": b.get("coherente"),
        "skills": skills(),
        "funcion": (
            "Inventario de skills/mandatos del Engine bajo capacidades/. "
            "Engine lee ids; CE no calcula Tru ni orquesta el ciclo."
        ),
    }


def verificar_salida(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    return "coherente" in salida or "ids" in salida


# ===============================================================
# CONTENEDOR (contrato con Engine — al final, como el resto de módulos)
# ===============================================================
CONTENEDOR = {
    "nombre": "capacidades_engine",
    "rol": "CE",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Capacidades / skills del Engine (mandatos). "
        "Descubre SKILL bajo capacidades/*.py. "
        "Expone ids de mandato (ce_mandato_catalogo, ce_mandato_escala_tt, "
        "ce_mandato_sujetos, ce_mandato_aplicar_escala, …). "
        "No calcula C/L/K/Tru. No deposita sujetos. "
        "Engine orquesta; CE solo inventaría. "
        "Requisito de arranque: 'CE' en ROLES de core/engine.py."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "skills": skills,
        "ids": ids,
        "por_id": por_id,
    },
}


__all__ = [
    "CONTENEDOR",
    "barrer",
    "verificar",
    "inventario",
    "skills",
    "ids",
    "por_id",
    "verificar_salida",
]
