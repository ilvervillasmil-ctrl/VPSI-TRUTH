"""
VPSI-TRUTH --- modules/citacion/fuentes/cx.py

Fuente de anuncio: contexto (CX).

Acorde al contrato de citacion:
  - Anuncia O, estado de contexto y resoluciones que CX ya produjo.
  - No fija O.
  - No calcula Tru.
  - No inventa enunciados de contexto.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "contexto"
TIPO = "cx"


def anunciar_o(
    *,
    o_id: str,
    enunciado_o: str,
    evidencia_ref: str,
    estado: Optional[str] = None,
    permite_k: Optional[bool] = None,
    contexto_ciclo: Optional[str] = None,
    descripcion: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia un O ya fijado o resuelto en el ciclo.
    Citacion no crea el O; solo lo documenta.
    """
    if not enunciado_o and not o_id:
        return {"ok": False, "errores": ["o_id o enunciado_o requerido"], "cita": None}

    meta: Dict[str, Any] = {}
    if estado is not None:
        meta["estado"] = estado
    if permite_k is not None:
        meta["permite_k"] = bool(permite_k)

    cita = plantilla(
        id=str(o_id or "O-SIN-ID"),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado_o or "",
        descripcion=descripcion
        or (
            "O de contexto aportado al ciclo; "
            "citacion no fija ni reinterpreta el contexto."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=str(o_id) if o_id else None,
        contexto_ciclo=contexto_ciclo,
        meta=meta or None,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_estado(
    *,
    estado: str,
    enunciado: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia estado de contexto (estable / indefinido / cambio / …)
    ya determinado por CX.
    """
    cita = plantilla(
        id="CX-ESTADO-{0}".format(estado or "NA"),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado or "estado_contexto={0}".format(estado),
        descripcion=(
            "Estado de contexto reportado en el ciclo; "
            "citacion no clasifica de nuevo."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"estado": estado},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def desde_resolver(
    salida_cx: Dict[str, Any],
    *,
    evidencia_ref: str,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia lo esencial de una salida de contexto.resolver() / equivalente.
    No llama a CX; solo anuncia el dict ya producido.
    """
    if not isinstance(salida_cx, dict):
        return {"ok": False, "errores": ["salida_cx debe ser dict"], "cita": None}

    o_ctx = (
        salida_cx.get("O_context")
        or salida_cx.get("enunciado_O")
        or salida_cx.get("O_id")
        or ""
    )
    o_id = str(salida_cx.get("O_id") or salida_cx.get("o_id") or "O-RESOLVER")
    estado = None
    registro = salida_cx.get("registro")
    if isinstance(registro, dict):
        estado = registro.get("estado")
    estado = estado or salida_cx.get("estado")

    permite = salida_cx.get("permite_k")
    coherente = salida_cx.get("coherente")

    enunciado = "CX resolver: O={0}".format(o_ctx)
    if estado is not None:
        enunciado += "; estado={0}".format(estado)
    if permite is not None:
        enunciado += "; permite_k={0}".format(permite)
    if coherente is not None:
        enunciado += "; coherente={0}".format(coherente)

    cita = plantilla(
        id="CX-RESOLVER",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=str(enunciado),
        descripcion=(
            "Salida de resolución de contexto en el ciclo; "
            "citacion no ejecuta contexto.resolver()."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_id,
        contexto_ciclo=contexto_ciclo,
        meta={
            "estado": estado,
            "permite_k": permite,
            "coherente": coherente,
        },
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_indefinido(
    *,
    motivo: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia que el contexto quedó indefinido según CX (evidencia del ciclo).
    """
    cita = plantilla(
        id="CX-INDEFINIDO",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado="Contexto indefinido en el ciclo.",
        descripcion=motivo
        or "CX reportó contexto indefinido; citacion no completa el O.",
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"estado": "indefinido"},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_o",
    "anunciar_estado",
    "desde_resolver",
    "anunciar_indefinido",
]
