"""
VPSI-TRUTH --- modules/citacion/registro.py

Registro de citas del ciclo de evaluación.

Acorde al contrato de modules/citacion/__init__.py:
  - Acumula citas validadas por esquema.
  - No calcula C, L, K ni Tru.
  - No fija O.
  - No persiste "verdad"; solo registro de proceso del ciclo.
  - limpiar no borra artefactos en disco.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.citacion.esquema import (
    TIPOS_CITA,
    es_valida,
    maqueta_anuncio,
    normalizar,
    validar,
)

# ===============================================================
# ESTADO DE CICLO (memoria de proceso)
# ===============================================================

_REGISTRO: List[Dict[str, Any]] = []


def limpiar() -> Dict[str, Any]:
    """Vacía el registro del ciclo actual."""
    n = len(_REGISTRO)
    _REGISTRO.clear()
    return {"ok": True, "limpiadas": n}


def agregar(cita: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida forma y acumula una cita.
    Retorna ok + cita normalizada, o errores de forma.
    """
    errores = validar(cita)
    if errores:
        return {"ok": False, "errores": errores, "cita": None}
    normalizada = normalizar(cita)
    _REGISTRO.append(normalizada)
    return {"ok": True, "n": len(_REGISTRO), "cita": normalizada}


def listar(filtro: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Lista citas del ciclo, con filtro opcional:
      modulo | tipo | o_ref | id
    """
    pet = filtro or {}
    out = list(_REGISTRO)
    if pet.get("modulo"):
        out = [c for c in out if c.get("fuente_modulo") == pet["modulo"]]
    if pet.get("tipo"):
        out = [c for c in out if c.get("tipo") == pet["tipo"]]
    if pet.get("o_ref"):
        out = [c for c in out if c.get("o_ref") == pet["o_ref"]]
    if pet.get("id"):
        out = [c for c in out if c.get("id") == pet["id"]]
    return {
        "citas": out,
        "n": len(out),
        "filtro": pet,
        "nota": "solo exposición; sin recálculo",
    }


def obtener_por_id(id_norma: str) -> Dict[str, Any]:
    """Primera cita del ciclo con ese id, si existe."""
    if not id_norma:
        return {"ok": False, "cita": None, "nota": "id vacío"}
    for c in _REGISTRO:
        if c.get("id") == id_norma:
            return {"ok": True, "cita": c}
    return {"ok": False, "cita": None, "nota": "id no encontrado en registro de ciclo"}


def anuncios(filtro: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Todas las citas del ciclo (o filtradas) en maqueta de anuncio.
    No calcula.
    """
    pack = listar(filtro)
    bloques = [maqueta_anuncio(c) for c in pack["citas"]]
    return {
        "anuncios": bloques,
        "n": len(bloques),
        "filtro": filtro or {},
        "nota": (
            "capacidad total de anuncio; "
            "presentación puede filtrar sin limitar el universo citable"
        ),
    }


def resumen() -> Dict[str, Any]:
    """Conteo por tipo y por módulo; sin valores de Tru."""
    por_tipo: Dict[str, int] = {}
    por_modulo: Dict[str, int] = {}
    for c in _REGISTRO:
        t = str(c.get("tipo") or "?")
        m = str(c.get("fuente_modulo") or "?")
        por_tipo[t] = por_tipo.get(t, 0) + 1
        por_modulo[m] = por_modulo.get(m, 0) + 1
    return {
        "n": len(_REGISTRO),
        "por_tipo": por_tipo,
        "por_modulo": por_modulo,
        "tipos_admitidos": list(TIPOS_CITA),
    }


def estado() -> Dict[str, Any]:
    return {
        "n": len(_REGISTRO),
        "vacio": len(_REGISTRO) == 0,
        "resumen": resumen(),
    }


__all__ = [
    "limpiar",
    "agregar",
    "listar",
    "obtener_por_id",
    "anuncios",
    "resumen",
    "estado",
    "es_valida",
    "validar",
    "normalizar",
]
