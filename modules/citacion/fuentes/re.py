"""
VPSI-TRUTH --- modules/citacion/fuentes/re.py

Fuente de anuncio: realidad (RE).

Acorde al contrato de citacion y de realidad:
  - Anuncia material etiquetado, dominio, aprobación/rechazo ya ocurridos.
  - No trae Internet.
  - No afirma que una fuente "es R".
  - No calcula Tru.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "realidad"
TIPO = "re"


def anunciar_material(
    *,
    material_id: str,
    dominio: str,
    evidencia_ref: str,
    estado: Optional[str] = None,
    url: Optional[str] = None,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    descripcion: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia material de realidad ya etiquetado en el ciclo.
    """
    if not material_id and not dominio:
        return {
            "ok": False,
            "errores": ["material_id o dominio requerido"],
            "cita": None,
        }

    enunciado = "Material RE dominio={0} id={1}".format(
        dominio or "?", material_id or "?"
    )
    if estado:
        enunciado += "; estado={0}".format(estado)
    if url:
        enunciado += "; origen_ref={0}".format(url)

    meta: Dict[str, Any] = {"dominio": dominio, "material_id": material_id}
    if estado is not None:
        meta["estado"] = estado
    if url is not None:
        meta["url"] = url

    cita = plantilla(
        id=str(material_id or "RE-MATERIAL"),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=descripcion
        or (
            "Material etiquetado por realidad en el ciclo; "
            "candidato a contraste, no ancla de R."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta=meta,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_aprobacion(
    *,
    material_id: str,
    dominio: str,
    aprobado: bool,
    evidencia_ref: str,
    motivo: str = "",
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia aprobación o rechazo de dominio ya decidido en el ciclo.
    Citacion no aprueba de nuevo.
    """
    enunciado = (
        "RE dominio={0} material={1}: {2}.".format(
            dominio,
            material_id,
            "aprobado" if aprobado else "rechazado",
        )
    )
    if motivo:
        enunciado += " motivo={0}".format(motivo)

    cita = plantilla(
        id="RE-APROB-{0}".format(material_id or "NA"),
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Decisión de aprobación de dominio reportada en el ciclo; "
            "citacion no sustituye el contrato de simbiosis RE."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={
            "dominio": dominio,
            "material_id": material_id,
            "aprobado": bool(aprobado),
            "motivo": motivo,
        },
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def desde_informe_barrer(
    informe: Dict[str, Any],
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia realidad.barrer() como evidencia de proceso del módulo RE.
    """
    if not isinstance(informe, dict):
        return {"ok": False, "errores": ["informe debe ser dict"], "cita": None}

    coherente = informe.get("coherente")
    funciones = informe.get("funciones") or []
    enunciado = "Informe RE.barrer(): coherente={0}, funciones={1}.".format(
        coherente, len(funciones) if isinstance(funciones, list) else funciones
    )

    cita = plantilla(
        id="RE-BARRER",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Estado de coherencia de realidad reportado en el ciclo; "
            "citacion no ejecuta RE.barrer()."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={
            "coherente": coherente,
            "funciones_n": len(funciones) if isinstance(funciones, list) else None,
        },
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


def anunciar_canal(
    *,
    hay_acceso: Optional[bool],
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia sonda de acceso ya medida (no vuelve a llamar a Internet).
    """
    enunciado = "RE canal/acceso reportado: hay_acceso={0}.".format(hay_acceso)
    cita = plantilla(
        id="RE-CANAL",
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Estado de canal de realidad en el ciclo; "
            "citacion no abre conexiones."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta={"hay_acceso": hay_acceso},
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita}


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "anunciar_material",
    "anunciar_aprobacion",
    "desde_informe_barrer",
    "anunciar_canal",
]
