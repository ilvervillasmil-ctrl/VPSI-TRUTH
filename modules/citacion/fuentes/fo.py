"""
VPSI-TRUTH --- modules/citacion/fuentes/fo.py

Fuente de anuncio: fórmulas (FO).

Acorde al contrato de citacion:
  - Anuncia la expresión / resultado que FO ya aplicó en el ciclo.
  - No recalcula Tru_Ri ni Tru_total.
  - No inventa factores.
  - Documenta ancla α/β solo como referencia de fórmula aplicada.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "formulas"
TIPO = "fo"


def anunciar_formula_aplicada(
    *,
    tru_ri: Any,
    tru_total: Any,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    C: Any = None,
    L: Any = None,
    K: Any = None,
    descripcion: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia valores de fórmula ya producidos en el ciclo.
    Citacion no llama a tru_total().
    """
    enunciado = (
        "FO aplicada: Tru_Ri={0}, Tru_total={1} "
        "(Tru_total = (C·L·K)·α + β).".format(tru_ri, tru_total)
    )
    meta: Dict[str, Any] = {"Tru_Ri": tru_ri, "Tru_total": tru_total}
    if C is not None:
        meta["C"] = C
    if L is not None:
        meta["L"] = L
    if K is not None:
        meta["K"] = K

    cita = plantilla(
        id="FO-APLICADA",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=descripcion
        or (
            "Resultado de fórmula reportado en el ciclo; "
            "citacion no recomputa FO."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta=meta,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_expresion(
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia la expresión canónica de la fórmula (sin valores).
    Útil para citación de norma de cálculo.
    """
    enunciado = (
        "Fórmula canónica VPSI: "
        "Tru_Ri(D)=C(D)·L(D)·K(D); "
        "Tru_total(D)=(Tru_Ri(D)·α)+β; "
        "α=26/27, β=1/27."
    )
    cita = plantilla(
        id="FO-EXPRESION",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Expresión de fórmula del marco; "
            "citacion no evalúa la expresión."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"alpha": "26/27", "beta": "1/27"},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_rechazo_tipo(
    *,
    motivo: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia rechazo de tipo (ej. float) ya ocurrido en FO.
    """
    cita = plantilla(
        id="FO-RECHAZO-TIPO",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado="FO rechazó entrada por tipo/dominio en el ciclo.",
        descripcion=motivo
        or (
            "Rechazo de tipo reportado por fórmulas; "
            "citacion no reintenta el cálculo."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"rechazo": True},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def desde_resultado(
    resultado_fo: Dict[str, Any],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia un dict de salida FO / evaluación que ya trae Tru_*.
    """
    if not isinstance(resultado_fo, dict):
        return {"ok": False, "errores": ["resultado_fo debe ser dict"], "cita": None}

    tru_ri = resultado_fo.get("Tru_Ri", resultado_fo.get("tru_ri"))
    tru_total = resultado_fo.get("Tru_total", resultado_fo.get("tru_total"))

    if tru_ri is None and tru_total is None:
        return {
            "ok": False,
            "errores": ["resultado_fo sin Tru_Ri ni Tru_total"],
            "cita": None,
        }

    return anunciar_formula_aplicada(
        tru_ri=tru_ri,
        tru_total=tru_total,
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        C=resultado_fo.get("C", resultado_fo.get("c")),
        L=resultado_fo.get("L", resultado_fo.get("l")),
        K=resultado_fo.get("K", resultado_fo.get("k")),
        registrar=registrar,
    )


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_formula_aplicada",
    "anunciar_expresion",
    "anunciar_rechazo_tipo",
    "desde_resultado",
]
