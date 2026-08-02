"""
VPSI-TRUTH --- modules/citacion/fuentes/tx.py

Fuente de anuncio: taxonomía (TX) — tácticas T1–T15.

Acorde al contrato de citacion y a modules/taxonomia/manipulation_TX.py:
  - Anuncia id, nombre, degrada, enunciado (estructura = medición, no interpretación).
  - No reclasifica descripciones.
  - No declara mentira personal.
  - No calcula Tru.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "taxonomia"
TIPO = "tx"


def _cargar_tacticas() -> List[Dict[str, Any]]:
    """Lee TACTICAS del módulo de taxonomía; no inventa tácticas."""
    try:
        from modules.taxonomia import manipulation_TX as mtx
    except Exception:
        try:
            from modules.taxonomia.manipulation_TX import TACTICAS

            return list(TACTICAS) if isinstance(TACTICAS, list) else []
        except Exception:
            return []

    if hasattr(mtx, "TACTICAS") and isinstance(mtx.TACTICAS, list):
        return list(mtx.TACTICAS)
    return []


def _por_id(id_regla: str) -> Optional[Dict[str, Any]]:
    for t in _cargar_tacticas():
        if not isinstance(t, dict):
            continue
        if str(t.get("id") or "") == str(id_regla):
            return t
    return None


def anunciar_regla(
    *,
    id_regla: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    descripcion: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia una táctica T1–T15 por id.
    Si el corpus no está cargado, no inventa el enunciado.
    """
    if not id_regla:
        return {"ok": False, "errores": ["id_regla vacío"], "cita": None}

    t = _por_id(id_regla)
    if t is None:
        cita = plantilla(
            id=str(id_regla),
            tipo=TIPO,
            fuente_modulo=FUENTE_MODULO,
            enunciado="",
            descripcion=descripcion
            or (
                "Id de táctica TX citado; enunciado no resuelto en carga "
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
            "nota": "id no encontrado en TACTICAS",
        }

    nombre = t.get("nombre") or ""
    enunciado = t.get("enunciado") or ""
    degrada = t.get("degrada") or []
    estructura = t.get("estructura") or {}

    cita = plantilla(
        id=str(t.get("id")),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=str(enunciado),
        descripcion=descripcion
        or (
            "Táctica TX {0} ({1}); degrada={2}. "
            "Medición por estructura; citacion no interpreta intención.".format(
                t.get("id"), nombre, degrada
            )
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={
            "nombre": nombre,
            "degrada": list(degrada) if isinstance(degrada, list) else degrada,
            "estructura": estructura if isinstance(estructura, dict) else {},
            "resuelto": True,
        },
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "resuelto": True, "cita": cita}


def anunciar_lista_reglas(
    ids: List[str],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """Anuncia varias tácticas por id (T1, T2, …)."""
    resultados = [
        anunciar_regla(
            id_regla=i,
            evidencia_ref=evidencia_ref,
            o_ref=o_ref,
            contexto_ciclo=contexto_ciclo,
            registrar=registrar,
        )
        for i in ids
    ]
    return {
        "n": len(resultados),
        "resultados": resultados,
        "nota": "fuente TX T1–T15; sin reclasificar descripciones",
    }


def inventario_anunciable() -> Dict[str, Any]:
    """Lista ids/nombres disponibles para anunciar (sin calcular Tru)."""
    tacticas = _cargar_tacticas()
    return {
        "total": len(tacticas),
        "ids": [str(t.get("id")) for t in tacticas if isinstance(t, dict)],
        "nombres": {
            str(t.get("id")): t.get("nombre")
            for t in tacticas
            if isinstance(t, dict)
        },
        "fuente": FUENTE_MODULO,
    }


def desde_informe_barrer(
    informe: Dict[str, Any],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """Anuncia informe de barrer/filtro TX como evidencia de proceso."""
    if not isinstance(informe, dict):
        return {"ok": False, "errores": ["informe debe ser dict"], "cita": None}

    coherente = informe.get("coherente")
    enunciado = "Informe TX.barrer/filtro: coherente={0}.".format(coherente)
    if informe.get("errores"):
        enunciado += " errores={0}.".format(len(informe.get("errores") or []))

    cita = plantilla(
        id="TX-BARRER",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Estado de taxonomía reportado en el ciclo; "
            "citacion no sustituye a TX."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"coherente": coherente},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_deteccion(
    *,
    id_regla: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia que en el ciclo se aplicó/detectó la táctica id_regla
    (el hecho lo aportó TX; aquí solo se cita).
    """
    return anunciar_regla(
        id_regla=id_regla,
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        descripcion=(
            "Detección/aplicación de táctica TX {0} reportada en el ciclo; "
            "no es veredicto moral sobre personas.".format(id_regla)
        ),
        registrar=registrar,
    )


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_regla",
    "anunciar_lista_reglas",
    "inventario_anunciable",
    "desde_informe_barrer",
    "anunciar_deteccion",
]
