"""
VPSI-TRUTH --- modules/citacion/esquema.py

Esquema de una cita / anuncio.

Acorde al contrato de modules/citacion/__init__.py:
  - Define la forma (campos) de una cita.
  - No calcula C, L, K ni Tru.
  - No fija O.
  - No juzga personas.
  - Solo estructura para registrar y anunciar.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# ===============================================================
# TIPOS ADMITIDOS (alineados al CONTENEDOR / FUNCION del init)
# ===============================================================

TIPOS_CITA: Tuple[str, ...] = (
    "ax",
    "mc",
    "cx",
    "tx",
    "ca",
    "fo",
    "re",
    "ct",
    "ch",
    "sf",
    "limite",
    "evidencia",
    "citacion",
)

CAMPOS_OBLIGATORIOS: Tuple[str, ...] = (
    "id",
    "tipo",
    "fuente_modulo",
    "enunciado",
    "descripcion",
    "evidencia_ref",
)

CAMPOS_OPCIONALES: Tuple[str, ...] = (
    "o_ref",
    "contexto_ciclo",
    "meta",
)


# ===============================================================
# VALIDACIÓN Y NORMALIZACIÓN
# ===============================================================

def validar(cita: Dict[str, Any]) -> List[str]:
    """
    Valida forma de una cita.
    No valida verdad ni recalcula.
    Retorna lista de errores (vacía = forma OK).
    """
    errores: List[str] = []
    if not isinstance(cita, dict):
        return ["cita debe ser dict"]

    tipo = cita.get("tipo")
    if tipo not in TIPOS_CITA:
        errores.append("tipo de cita no admitido: {0}".format(tipo))

    for campo in CAMPOS_OBLIGATORIOS:
        if campo == "id" and tipo == "limite":
            continue
        val = cita.get(campo)
        if val is None or val == "":
            errores.append("falta campo obligatorio: {0}".format(campo))

    if tipo == "limite":
        if not cita.get("descripcion") and not cita.get("enunciado"):
            errores.append("limite requiere enunciado o descripcion")

    return errores


def normalizar(cita: Dict[str, Any]) -> Dict[str, Any]:
    """
    Devuelve cita con campos canónicos.
    No inventa enunciados: solo ordena lo recibido.
    """
    out: Dict[str, Any] = {
        "id": cita.get("id"),
        "tipo": cita.get("tipo"),
        "fuente_modulo": cita.get("fuente_modulo"),
        "enunciado": cita.get("enunciado") if cita.get("enunciado") is not None else "",
        "descripcion": cita.get("descripcion") if cita.get("descripcion") is not None else "",
        "evidencia_ref": cita.get("evidencia_ref") if cita.get("evidencia_ref") is not None else "",
    }
    for c in CAMPOS_OPCIONALES:
        if c in cita and cita[c] is not None:
            out[c] = cita[c]
    return out


def es_valida(cita: Dict[str, Any]) -> bool:
    return len(validar(cita)) == 0


def plantilla(
    *,
    id: Optional[str] = None,
    tipo: str = "evidencia",
    fuente_modulo: str = "",
    enunciado: str = "",
    descripcion: str = "",
    evidencia_ref: str = "",
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Construye un dict de cita en la forma canónica.
    No calcula. Solo arma la estructura.
    """
    cita: Dict[str, Any] = {
        "id": id,
        "tipo": tipo,
        "fuente_modulo": fuente_modulo,
        "enunciado": enunciado,
        "descripcion": descripcion,
        "evidencia_ref": evidencia_ref,
    }
    if o_ref is not None:
        cita["o_ref"] = o_ref
    if contexto_ciclo is not None:
        cita["contexto_ciclo"] = contexto_ciclo
    if meta is not None:
        cita["meta"] = meta
    return normalizar(cita)


def maqueta_anuncio(cita: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forma de anuncio (enunciado + descripcion + refs).
    Usada por anunciar(); sin juicio ni cálculo.
    """
    c = normalizar(cita)
    return {
        "titulo": "[{0}] {1}".format(c.get("fuente_modulo"), c.get("id")),
        "tipo": c.get("tipo"),
        "enunciado": c.get("enunciado"),
        "descripcion": c.get("descripcion"),
        "evidencia_ref": c.get("evidencia_ref"),
        "o_ref": c.get("o_ref"),
        "contexto_ciclo": c.get("contexto_ciclo"),
    }


__all__ = [
    "TIPOS_CITA",
    "CAMPOS_OBLIGATORIOS",
    "CAMPOS_OPCIONALES",
    "validar",
    "normalizar",
    "es_valida",
    "plantilla",
    "maqueta_anuncio",
]
