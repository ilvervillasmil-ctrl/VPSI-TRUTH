"""
VPSI-TRUTH --- modules/citacion/fuentes/ax.py

Fuente de anuncio: módulo axiomas (AX).

Acorde al contrato de citacion:
  - Anuncia ids y enunciados que AX ya expone.
  - No calcula Tru.
  - No barre el grafo en lugar de AX.
  - No inventa teoremas: lee declaraciones / informe si están disponibles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "axiomas"
TIPO = "ax"


def _cargar_declaraciones() -> List[Dict[str, Any]]:
    """
    Intenta leer declaraciones desde AX sin recalcular coherencia de más.
    Si AX no expone API, retorna lista vacía (no inventa).
    """
    try:
        from modules import axiomas as ax
    except Exception:
        return []

    if hasattr(ax, "DECLARACIONES") and isinstance(ax.DECLARACIONES, list):
        return list(ax.DECLARACIONES)
    if hasattr(ax, "declaraciones") and callable(ax.declaraciones):
        try:
            d = ax.declaraciones()
            if isinstance(d, list):
                return d
        except Exception:
            return []
    if hasattr(ax, "CUERPO") and isinstance(getattr(ax, "CUERPO", None), list):
        return list(ax.CUERPO)
    return []


def _item_a_cita(
    item: Dict[str, Any],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    descripcion: Optional[str] = None,
) -> Dict[str, Any]:
    id_ = item.get("id") or item.get("ID")
    enunciado = (
        item.get("enunciado")
        or item.get("texto")
        or item.get("statement")
        or ""
    )
    tipo_decl = item.get("tipo") or "declaracion"
    desc = descripcion or (
        "Norma AX ({0}) aportada al ciclo; citacion no valida su verdad, solo anuncia.".format(
            tipo_decl
        )
    )
    return plantilla(
        id=str(id_) if id_ is not None else None,
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=str(enunciado),
        descripcion=desc,
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"tipo_declaracion": tipo_decl},
    )


def anunciar_id(
    id_norma: str,
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    descripcion: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Busca un id en declaraciones AX y arma la cita.
    Si no hay enunciado disponible, no inventa.
    """
    if not id_norma:
        return {"ok": False, "errores": ["id_norma vacío"], "cita": None}

    decls = _cargar_declaraciones()
    encontrado = None
    for d in decls:
        if not isinstance(d, dict):
            continue
        if str(d.get("id") or d.get("ID") or "") == str(id_norma):
            encontrado = d
            break

    if encontrado is None:
        cita = plantilla(
            id=str(id_norma),
            tipo=TIPO,
            fuente_modulo=FUENTE_MODULO,
            enunciado="",
            descripcion=descripcion
            or (
                "Id AX citado en el ciclo; enunciado no resuelto en esta carga "
                "(sin invención)."
            ),
            evidencia_ref=evidencia_ref,
            o_ref=o_ref,
            contexto_ciclo=contexto_ciclo,
            meta={"resuelto": False},
        )
        if registrar:
            reg.agregar(cita)
        return {
            "ok": True,
            "resuelto": False,
            "cita": cita,
            "nota": "id no encontrado en declaraciones cargadas",
        }

    cita = _item_a_cita(
        encontrado,
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        descripcion=descripcion,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "resuelto": True, "cita": cita}


def anunciar_lista(
    ids: List[str],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """Anuncia varios ids AX; no calcula Tru."""
    resultados = []
    for i in ids:
        resultados.append(
            anunciar_id(
                i,
                evidencia_ref=evidencia_ref,
                o_ref=o_ref,
                contexto_ciclo=contexto_ciclo,
                registrar=registrar,
            )
        )
    return {
        "n": len(resultados),
        "resultados": resultados,
        "nota": "fuente AX; sin recálculo de coherencia axiomatica",
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
    Anuncia el hecho de coherencia de ax.barrer() como evidencia de proceso
    (no como Tru_total).
    """
    if not isinstance(informe, dict):
        return {"ok": False, "errores": ["informe debe ser dict"], "cita": None}

    coherente = informe.get("coherente")
    n_decl = informe.get("declaraciones") or informe.get("n") or "?"
    enunciado = (
        "Informe AX.barrer(): coherente={0}, declaraciones={1}.".format(
            coherente, n_decl
        )
    )
    cita = plantilla(
        id="AX-BARRER",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Estado de coherencia axiomatica reportado en el ciclo; "
            "citacion no sustituye a AX.barrer()."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"coherente": coherente, "declaraciones": n_decl},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_id",
    "anunciar_lista",
    "desde_informe_barrer",
]
