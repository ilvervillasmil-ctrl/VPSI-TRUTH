"""
VPSI-TRUTH --- modules/citacion/fuentes/ch.py
Fuente cache (CH): anuncia evidencia persistida. No modifica cache. No calcula Tru.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg

FUENTE_MODULO = "cache"
TIPO = "ch"


def anunciar_evidencia(
    *,
    evidencia_ref: str,
    enunciado: str = "",
    descripcion: str = "",
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    if not evidencia_ref:
        return {"ok": False, "errores": ["evidencia_ref vacío"], "cita": None}
    cita = plantilla(
        id="CH-EVIDENCIA",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado or "Evidencia en cache: {0}".format(evidencia_ref),
        descripcion=descripcion
        or "Referencia de evidencia persistida; citacion no altera cache.",
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta=meta,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_secuencia(
    *,
    n: int,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    cita = plantilla(
        id="CH-SECUENCIA",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado="Cache secuencia/n evidencias reportadas: n={0}.".format(n),
        descripcion="Conteo de evidencia de cache; citacion no escribe en cache.",
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"n": n},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


__all__ = ["FUENTE_MODULO", "TIPO", "anunciar_evidencia", "anunciar_secuencia"]
