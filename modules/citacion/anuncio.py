"""
VPSI-TRUTH --- modules/citacion/anuncio.py

Maqueta de anuncio de citas.

Acorde al contrato de modules/citacion/__init__.py:
  - Serializa citas a bloques de anuncio (enunciado + descripción + refs).
  - No calcula C, L, K ni Tru.
  - No fija O.
  - No juzga personas.
  - Omega u otro visor puede filtrar; este archivo no limita el universo citable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.citacion.esquema import maqueta_anuncio, normalizar, validar
from modules.citacion import registro as reg


def de_cita(cita: Dict[str, Any]) -> Dict[str, Any]:
    """
    Una cita → un bloque de anuncio.
    Si la forma falla, ok=False y errores.
    """
    errores = validar(cita)
    if errores:
        return {"ok": False, "errores": errores, "anuncio": None}
    return {"ok": True, "anuncio": maqueta_anuncio(cita)}


def de_registro(filtro: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Anuncia todas las citas del registro de ciclo (o filtradas).
    Delega listado en registro; no recalcula.
    """
    return reg.anuncios(filtro)


def texto(anuncio: Dict[str, Any]) -> str:
    """
    Bloque de anuncio → texto plano legible.
    Solo formato; sin juicio.
    """
    if not isinstance(anuncio, dict):
        return ""
    lineas = [
        str(anuncio.get("titulo") or ""),
        "  tipo        : {0}".format(anuncio.get("tipo")),
        "  enunciado   : {0}".format(anuncio.get("enunciado")),
        "  descripcion : {0}".format(anuncio.get("descripcion")),
        "  evidencia   : {0}".format(anuncio.get("evidencia_ref")),
    ]
    if anuncio.get("o_ref") is not None:
        lineas.append("  o_ref       : {0}".format(anuncio.get("o_ref")))
    if anuncio.get("contexto_ciclo") is not None:
        lineas.append("  ciclo       : {0}".format(anuncio.get("contexto_ciclo")))
    return "\n".join(lineas)


def texto_todo(filtro: Optional[Dict[str, Any]] = None) -> str:
    """
    Todos los anuncios del ciclo en texto plano (auditoría completa).
    """
    pack = de_registro(filtro)
    bloques = pack.get("anuncios") or []
    if not bloques:
        return "(sin citas en el ciclo)"
    partes = [texto(b) for b in bloques]
    return "\n---\n".join(partes)


def para_omega(
    filtro: Optional[Dict[str, Any]] = None,
    *,
    max_n: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Paquete listo para presentación en Omega Report.
    max_n: si se indica, recorta la lista (filtro de presentación, no del universo).
    """
    pack = de_registro(filtro)
    anuncios: List[Dict[str, Any]] = list(pack.get("anuncios") or [])
    total = len(anuncios)
    recortado = False
    if max_n is not None and max_n >= 0 and len(anuncios) > max_n:
        anuncios = anuncios[:max_n]
        recortado = True
    return {
        "seccion": "citacion",
        "anuncios": anuncios,
        "n_mostrados": len(anuncios),
        "n_total_ciclo": total,
        "recortado": recortado,
        "filtro": filtro or {},
        "nota": (
            "citacion puede anunciar todo; "
            "este paquete es presentación (posible recorte max_n)"
        ),
    }


def anunciar_limite(
    *,
    descripcion: str,
    evidencia_ref: str = "",
    o_ref: Optional[str] = None,
    fuente_modulo: str = "citacion",
    contexto_ciclo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Anuncio de límite de precisión (no hay base suficiente).
    No rellena Tru; solo estructura de cita tipo limite.
    """
    cita = {
        "id": None,
        "tipo": "limite",
        "fuente_modulo": fuente_modulo,
        "enunciado": (
            "No hay base suficiente para precisar el valor "
            "bajo el O y la evidencia dados."
        ),
        "descripcion": descripcion,
        "evidencia_ref": evidencia_ref,
    }
    if o_ref is not None:
        cita["o_ref"] = o_ref
    if contexto_ciclo is not None:
        cita["contexto_ciclo"] = contexto_ciclo
    reg.agregar(cita)
    return de_cita(normalizar(cita))


__all__ = [
    "de_cita",
    "de_registro",
    "texto",
    "texto_todo",
    "para_omega",
    "anunciar_limite",
]
