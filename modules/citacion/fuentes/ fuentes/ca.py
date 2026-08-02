"""
VPSI-TRUTH --- modules/citacion/fuentes/ca.py

Fuente de anuncio: calculator (CA).

Acorde al contrato de citacion:
  - Anuncia lo que CA ya reportó en el ciclo (factores, oficio, límites).
  - No calcula C, L, K.
  - No inventa factores.
  - No aplica la fórmula (eso es FO).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "calculator"
TIPO = "ca"


def anunciar_factores(
    *,
    C: Any,
    L: Any,
    K: Any,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    descripcion: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia factores ya producidos por CA en el ciclo.
    Los valores se documentan; no se recomputan aquí.
    """
    enunciado = "CA factores reportados: C={0}, L={1}, K={2}.".format(C, L, K)
    cita = plantilla(
        id="CA-FACTORES",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=descripcion
        or (
            "Factores de calculator aportados al ciclo; "
            "citacion no calcula C, L ni K."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"C": C, "L": L, "K": K},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_oficio(
    *,
    id_oficio: str,
    enunciado: str,
    descripcion: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia un oficio puntual de CA ya ejecutado (ej. k_sin_contexto).
    """
    if not id_oficio:
        return {"ok": False, "errores": ["id_oficio vacío"], "cita": None}
    cita = plantilla(
        id=str(id_oficio),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado or "",
        descripcion=descripcion
        or "Oficio de calculator reportado; citacion no reejecuta CA.",
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta=meta,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_sin_factores(
    *,
    motivo: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia que CA no asignó factores completos (límite de precisión).
    No rellena C,L,K.
    """
    cita = plantilla(
        id="CA-SIN-FACTORES",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado="Calculator no asignó factores completos en este ciclo.",
        descripcion=motivo
        or (
            "Sin C,L,K completos bajo el O y la evidencia; "
            "citacion no inventa factores."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"factores_completos": False},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def desde_resultado(
    resultado_ca: Dict[str, Any],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia un dict de salida de CA ya producido.
    Si trae C,L,K los documenta; si no, anuncia límite.
    """
    if not isinstance(resultado_ca, dict):
        return {"ok": False, "errores": ["resultado_ca debe ser dict"], "cita": None}

    C = resultado_ca.get("C", resultado_ca.get("c"))
    L = resultado_ca.get("L", resultado_ca.get("l"))
    K = resultado_ca.get("K", resultado_ca.get("k"))

    if C is None and L is None and K is None:
        return anunciar_sin_factores(
            motivo=str(
                resultado_ca.get("motivo")
                or resultado_ca.get("nota")
                or "CA sin factores en resultado"
            ),
            evidencia_ref=evidencia_ref,
            o_ref=o_ref,
            contexto_ciclo=contexto_ciclo,
            registrar=registrar,
        )

    return anunciar_factores(
        C=C,
        L=L,
        K=K,
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        descripcion=(
            "Factores tomados de resultado CA del ciclo; "
            "citacion no recalcula."
        ),
        registrar=registrar,
    )


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_factores",
    "anunciar_oficio",
    "anunciar_sin_factores",
    "desde_resultado",
]
