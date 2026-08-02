"""
VPSI-TRUTH --- modules/citacion/fuentes/mc.py

Fuente de anuncio: correlación mecánica (MC).

Acorde al contrato de citacion:
  - Anuncia pasos / reglas / informes que MC ya expone en el ciclo.
  - No ejecuta la mecánica en lugar de MC.
  - No calcula Tru.
  - No inventa pasos causales.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "correlacion_mecanica"
TIPO = "mc"


def anunciar_paso(
    *,
    id_paso: str,
    enunciado: str,
    descripcion: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia un paso o regla de mecánica ya determinado en el ciclo.
    El contenido lo aporta quien orquesta (Engine / MC); citacion solo forma.
    """
    if not id_paso:
        return {"ok": False, "errores": ["id_paso vacío"], "cita": None}
    cita = plantilla(
        id=str(id_paso),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado or "",
        descripcion=descripcion
        or "Paso de correlación mecánica aportado al ciclo; sin recálculo.",
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta=meta,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_lista_pasos(
    pasos: List[Dict[str, Any]],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    pasos: lista de dicts con id / enunciado / descripcion (opcionales).
    No valida la verdad del orden causal; solo anuncia.
    """
    resultados = []
    for i, p in enumerate(pasos):
        if not isinstance(p, dict):
            resultados.append(
                {"ok": False, "errores": ["paso no es dict"], "cita": None}
            )
            continue
        resultados.append(
            anunciar_paso(
                id_paso=str(p.get("id") or "MC-PASO-{0}".format(i)),
                enunciado=str(p.get("enunciado") or p.get("texto") or ""),
                descripcion=str(
                    p.get("descripcion")
                    or "Paso MC en secuencia de ciclo; citacion no reordena."
                ),
                evidencia_ref=evidencia_ref,
                o_ref=o_ref,
                contexto_ciclo=contexto_ciclo,
                meta=p.get("meta") if isinstance(p.get("meta"), dict) else None,
                registrar=registrar,
            )
        )
    return {
        "n": len(resultados),
        "resultados": resultados,
        "nota": "fuente MC; sin ejecutar correlacion_mecanica.barrer()",
    }


def desde_informe_barrer(
    informe: Dict[str, Any],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia el informe de MC.barrer() como evidencia de proceso del ciclo.
    No sustituye a MC.
    """
    if not isinstance(informe, dict):
        return {"ok": False, "errores": ["informe debe ser dict"], "cita": None}

    coherente = informe.get("coherente")
    enunciado = "Informe MC.barrer(): coherente={0}.".format(coherente)
    if informe.get("errores"):
        enunciado += " errores={0}.".format(len(informe.get("errores") or []))
    if informe.get("choques"):
        enunciado += " choques={0}.".format(len(informe.get("choques") or []))

    cita = plantilla(
        id="MC-BARRER",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Estado de coherencia de correlación mecánica reportado en el ciclo; "
            "citacion no ejecuta la mecánica."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={
            "coherente": coherente,
            "errores_n": len(informe.get("errores") or []),
            "choques_n": len(informe.get("choques") or []),
        },
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_permite_k(
    *,
    permite_k: bool,
    enunciado: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia una decisión de permite_k ya tomada en el ciclo (CX/MC).
    No recalcula permite_k.
    """
    cita = plantilla(
        id="MC-PERMITE-K",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado
        or "permite_k={0} según mecánica/contexto del ciclo.".format(permite_k),
        descripcion=(
            "Reporte de permite_k aportado al ciclo; "
            "citacion no decide correlación K."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"permite_k": bool(permite_k)},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_paso",
    "anunciar_lista_pasos",
    "desde_informe_barrer",
    "anunciar_permite_k",
]
