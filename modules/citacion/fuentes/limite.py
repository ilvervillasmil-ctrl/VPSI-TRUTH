"""
VPSI-TRUTH --- modules/citacion/fuentes/limite.py

Fuente de anuncio: límite de precisión (estructural, no moral).

No es autoridad del autor ni del sistema.
No es juicio sobre personas.
Es consecuencia de la mecánica del Teorema de la Verdad:

  Tru_Ri(D)    = C(D) · L(D) · K(D)          ∈ [0, 1]
  Tru_total(D) = (Tru_Ri(D) · α) + β         ∈ [β, 1]
  α = 26/27, β = 1/27

Anclas formales (marco VPSI v9.4 / cuerpo AX del repo):
  - Def-5.3.1 / CX: K indefinido sin O_context explícito
    (K = ∅, no K = 0).
  - T16: techo estructural α — ninguna descripción desde Ri
    se verifica más allá de la fracción observable.
  - T17: piso estructural β — Tru_total ≥ β siempre;
    Tru_total = 0 es formalmente imposible.
  - CA/FO: sin factores C,L,K aportados por el ciclo,
    no se inventa el producto; se anuncia límite.

Citacion:
  - Solo anuncia el límite ya impuesto por el ciclo / la mecánica.
  - No calcula Tru.
  - No rellena C, L, K.
  - No declara mentira personal.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from modules.citacion.esquema import plantilla
from modules.citacion import registro as reg


FUENTE_MODULO = "citacion"
TIPO = "limite"

# Códigos de límite = causas estructurales (no preferencias).
CODIGOS = {
    "K_SIN_O": {
        "id": "LIMITE-K-SIN-O",
        "enunciado": (
            "K indefinido: no hay O_context explícito. "
            "Por Def-5.3.1, K(D)=∅ (no cero); no se precisa Tru_Ri completo."
        ),
        "ids_marco": ["Def-5.3.1", "CX-A14", "CX-C4"],
    },
    "SIN_FACTORES": {
        "id": "LIMITE-SIN-FACTORES",
        "enunciado": (
            "Sin factores C,L,K aportados por CA en el ciclo. "
            "No se inventa el producto; no se precisa Tru_Ri."
        ),
        "ids_marco": ["Def-5.7", "TA", "CA"],
    },
    "O_INDEFINIDO": {
        "id": "LIMITE-O-INDEFINIDO",
        "enunciado": (
            "O de contexto indefinido o inestable en el ciclo. "
            "Sin dominio de medición estable no hay correlación evaluable."
        ),
        "ids_marco": ["CX-A10", "CX-T13", "Def-5.3"],
    },
    "TECHO_ALPHA": {
        "id": "LIMITE-TECHO-ALPHA",
        "enunciado": (
            "Techo estructural α=26/27 (T16): la contribución verificable "
            "desde Ri no supera la fracción observable del cubo 3×3×3."
        ),
        "ids_marco": ["T16", "α=26/27"],
    },
    "PISO_BETA": {
        "id": "LIMITE-PISO-BETA",
        "enunciado": (
            "Piso estructural β=1/27 (T17): Tru_total ≥ β siempre; "
            "Tru_total=0 es formalmente imposible aunque Tru_Ri=0."
        ),
        "ids_marco": ["T17", "β=1/27", "Def-5.9"],
    },
    "EVIDENCIA_INSUFICIENTE": {
        "id": "LIMITE-EVIDENCIA",
        "enunciado": (
            "Evidencia del ciclo insuficiente para fijar C, L o K "
            "bajo el O declarado. Límite de precisión, no veredicto."
        ),
        "ids_marco": ["T9", "VPSI", "F9"],
    },
}


def anunciar(
    *,
    codigo: str,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    detalle: str = "",
    meta: Optional[Dict[str, Any]] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Anuncia un límite estructural por código canónico.

    codigo ∈ CODIGOS. Si el código no existe, no se inventa otro marco:
    se reporta error de forma (no se finge un teorema).
    """
    spec = CODIGOS.get(codigo)
    if spec is None:
        return {
            "ok": False,
            "errores": [
                "codigo de limite desconocido: {0}; "
                "admitidos: {1}".format(codigo, sorted(CODIGOS.keys()))
            ],
            "cita": None,
        }

    enunciado = spec["enunciado"]
    if detalle:
        enunciado = "{0} | detalle: {1}".format(enunciado, detalle)

    m: Dict[str, Any] = {
        "codigo": codigo,
        "ids_marco": list(spec["ids_marco"]),
        "estructural": True,
        "moral": False,
    }
    if meta:
        m.update(meta)

    cita = plantilla(
        id=spec["id"],
        tipo=TIPO,
        fuente_modulo=FUENTE_MODULO,
        enunciado=enunciado,
        descripcion=(
            "Límite arquitectónico del Teorema de la Verdad / VPSI; "
            "citacion no calcula Tru ni rellena factores."
        ),
        evidencia_ref=evidencia_ref,
        o_ref=o_ref,
        contexto_ciclo=contexto_ciclo,
        meta=m,
    )
    if registrar:
        reg.agregar(cita)
    return {"ok": True, "cita": cita, "codigo": codigo}


def anunciar_desde_ciclo(
    *,
    evidencia_ref: str,
    o_ref: Optional[str] = None,
    contexto_ciclo: Optional[str] = None,
    permite_k: Optional[bool] = None,
    tiene_factores: Optional[bool] = None,
    o_estado: Optional[str] = None,
    registrar: bool = True,
) -> Dict[str, Any]:
    """
    Deriva códigos de límite solo desde flags del ciclo (sin interpretación moral).

    - permite_k is False o None con O vacío → K_SIN_O / O_INDEFINIDO
    - tiene_factores is False → SIN_FACTORES
    No inventa valores numéricos.
    """
    codigos: List[str] = []
    if o_estado in ("indefinido", "inestable") or o_estado == "cambio":
        if o_estado != "cambio":
            codigos.append("O_INDEFINIDO")
    if permite_k is False:
        codigos.append("K_SIN_O")
    if tiene_factores is False:
        codigos.append("SIN_FACTORES")

    if not codigos:
        return {
            "ok": True,
            "citas": [],
            "nota": "ciclo sin flags de limite estructurales",
        }

    citas = []
    for c in codigos:
        r = anunciar(
            codigo=c,
            evidencia_ref=evidencia_ref,
            o_ref=o_ref,
            contexto_ciclo=contexto_ciclo,
            registrar=registrar,
        )
        citas.append(r)
    return {"ok": True, "citas": citas, "codigos": codigos}


def inventario_codigos() -> Dict[str, Any]:
    """Lista códigos de límite y anclas de marco (auditoría)."""
    return {
        "n": len(CODIGOS),
        "codigos": {
            k: {
                "id": v["id"],
                "ids_marco": list(v["ids_marco"]),
                "enunciado": v["enunciado"],
            }
            for k, v in CODIGOS.items()
        },
        "nota": (
            "Limites estructurales: Def-5.3.1, T16 (α), T17 (β). "
            "Sin autoridad moral."
        ),
    }


__all__ = [
    "FUENTE_MODULO",
    "TIPO",
    "CODIGOS",
    "anunciar",
    "anunciar_desde_ciclo",
    "inventario_codigos",
]
