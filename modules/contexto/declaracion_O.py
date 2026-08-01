"""
modules/contexto/declaracion_O.py
=================================
Regla interna CX — declaración y estabilidad del registro O.

Anclas: CX-A14, CX-A1, CX-A10, CX-C4, Def-5.3.1

No calcula Tru. No asigna K. Solo clasifica si el registro
operativo es estable, cambio o indefinido.
"""

from __future__ import annotations

from typing import Any, Dict

REGLA = {
    "id": "CX-R-DECL-O",
    "nombre": "declaracion_O",
    "version": "1.0",
    "descripcion": (
        "Exige registro operativo mínimo (O_id + enunciado_O) para estado estable. "
        "Sin ellos el tramo queda indefinido y no se reclama K/Tru completo."
    ),
    "anclas_cx": ["CX-A14", "CX-A1", "CX-A10", "CX-C4", "Def-5.3.1"],
}


def validar() -> Dict[str, Any]:
    """Auto-chequeo de la regla (sin petición)."""
    return {
        "ok": True,
        "regla": REGLA["id"],
        "exige": ["O_id", "enunciado_O"],
        "estados": ["estable", "cambio", "indefinido"],
    }


def clasificar(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clasifica el registro declarado en la petición.

    Entrada típica (campos opcionales):
      O_id, enunciado_O | enunciado | contexto | O_context,
      escala, estado, evento, ligaduras, modo_entrada

    Salida:
      estado, evento, incompleto, mensajes, ids_cx
    """
    peticion = peticion or {}

    o_id = peticion.get("O_id") or peticion.get("o_id")
    enunciado = (
        peticion.get("enunciado_O")
        or peticion.get("enunciado")
        or peticion.get("contexto")
        or peticion.get("O_context")
    )
    estado_decl = peticion.get("estado")
    evento_decl = peticion.get("evento")

    o_id_ok = bool(o_id and str(o_id).strip())
    enunciado_ok = bool(enunciado and str(enunciado).strip())
    incompleto = not (o_id_ok and enunciado_ok)

    mensajes = []
    ids_cx = ["CX-A14"]

    if incompleto:
        estado = "indefinido"
        evento = "indefinido"
        mensajes.append(
            "registro incompleto: faltan O_id y/o enunciado_O → "
            "estado indefinido (CX-A14, CX-A10)"
        )
        ids_cx.extend(["CX-A10", "CX-C4", "Def-5.3.1"])
    elif estado_decl == "cambio":
        estado = "cambio"
        evento = evento_decl if evento_decl in ("cambio", "expansion") else "cambio"
        mensajes.append("estado declarado: cambio de O")
        ids_cx.extend(["CX-A8", "CX-T6"])
    elif estado_decl == "indefinido":
        estado = "indefinido"
        evento = "indefinido"
        mensajes.append("estado declarado: indefinido")
        ids_cx.extend(["CX-A10", "CX-T13"])
    else:
        estado = "estable"
        if evento_decl in ("mismo_O", "expansion", "cambio", "indefinido"):
            evento = evento_decl
        else:
            evento = "mismo_O"
        mensajes.append("registro mínimo completo → estable")
        ids_cx.append("CX-A1")

    return {
        "ok": not incompleto or estado_decl in ("cambio", "indefinido"),
        "estado": estado,
        "evento": evento,
        "incompleto": incompleto,
        "O_id": str(o_id).strip() if o_id_ok else None,
        "enunciado_O": str(enunciado).strip() if enunciado_ok else None,
        "mensajes": mensajes,
        "ids_cx": ids_cx,
        "permite_k_sugerido": estado == "estable" and not incompleto,
    }
