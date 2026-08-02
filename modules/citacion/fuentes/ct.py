"""
VPSI-TRUTH --- modules/citacion/fuentes/ct.py

Fuente de anuncio: constantes / ancla (CT).
Anuncia α, β ya leídos. No recalcula. No calcula Tru.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg

FUENTE_MODULO = "constante"
TIPO = "ct"


def _leer_ancla() -> Dict[str, Any]:
    try:
        from modules.constante import ALPHA, BETA
    except Exception as e:
        return {"ok": False, "error": str(e), "ALPHA": None, "BETA": None}
    return {"ok": True, "ALPHA": ALPHA, "BETA": BETA, "error": None}


def anunciar_ancla(
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    pack = _leer_ancla()
    if not pack.get("ok"):
        cita = plantilla(
            id="CT-ANCLA",
            tipo=TIPO,
            fuente_modulo=FUENTE_MODULO,
            enunciado="Ancla CT no legible en este ciclo.",
            descripcion=str(pack.get("error") or "fallo de import constante"),
            evidencia_ref=evidencia_ref,
            o_ref=o_ref,
            contexto_ciclo=contexto_ciclo,
            meta={"resuelto": False},
        )
        if registrar:
            reg.agregar(cita)
        return {"ok": False, "cita": cita, "nota": pack.get("error")}

    alpha, beta = pack["ALPHA"], pack["BETA"]
    try:
        suma = alpha + beta
    except Exception:
        suma = None

    cita = plantilla(
        id="CT-ANCLA",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado="Ancla CT: ALPHA={0}, BETA={1}, ALPHA+BETA={2}.".format(
            alpha, beta, suma
        ),
        descripcion=(
            "Constantes estructurales del marco leídas en el ciclo; "
            "citacion no modifica ni recalcula la ancla."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"ALPHA": alpha, "BETA": beta, "suma": suma, "resuelto": True},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_valores(
    *,
    alpha: Any,
    beta: Any,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    cita = plantilla(
        id="CT-VALORES",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado="CT valores reportados: ALPHA={0}, BETA={1}.".format(alpha, beta),
        descripcion=(
            "Valores de constante reportados en el ciclo; "
            "citacion no valida aritmética de la ancla."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"ALPHA": alpha, "BETA": beta},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


__all__ = ["FUENTE_MODULO", "TIPO", "anunciar_ancla", "anunciar_valores"]
