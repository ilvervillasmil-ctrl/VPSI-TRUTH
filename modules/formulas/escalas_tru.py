# -*- coding: utf-8 -*-
"""
modules/formulas/escalas_tru.py
===============================

Aplicación de la fórmula canónica a las escalas del catálogo TT.

UNA sola ley (truth.py / FO-1, FO-2):
    Tru_Ri(D)    = C(D) * L(D) * K(D)
    Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA

Cinco contextos de aplicación (ids idénticos a modules/tru_totales/categorias/):
    tru_atomo | tru_frase | tru_sujeto | tru_conversacion | tru_repositorio

Este archivo:
  - Declara que la misma fórmula se aplica bajo cada id de escala.
  - Expone wrappers que llaman a tru_ri / tru_total canónicos.
  - No inventa otra expresión por escala.
  - No calcula C, L, K (oficio CA).
  - No segmenta sujetos ni diálogos (oficio de material / orquestación).
  - No deposita resultados (oficio Engine).
  - No sustituye el catálogo TT: solo referencia sus ids.

FO descubre FORMULA; las escalas viven aquí como mapa de aplicación.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Dict, List, Optional, Tuple

from modules.formulas.truth import tru_ri, tru_total

# ---------------------------------------------------------------------------
# Metadato que el descubridor de FO espera (FORMULA)
# ---------------------------------------------------------------------------
FORMULA = {
    "nombre": "escalas_tru",
    "expresion": (
        "Tru_Ri = C*L*K ; "
        "Tru_total = (Tru_Ri * ALPHA) + BETA  "
        "[misma ley bajo ids TT: tru_atomo … tru_repositorio]"
    ),
    "fuente": "Teorema de la Verdad VPSI + catálogo TT (categorias/*.py)",
    "nota": (
        "No hay fórmula distinta por escala. "
        "Hay un único par Tru_Ri / Tru_total aplicado al material de cada alcance."
    ),
}

VERSION = "1.0"

# ---------------------------------------------------------------------------
# Ids = ids del catálogo TT (modules/tru_totales/categorias/)
# ---------------------------------------------------------------------------
ESCALAS: Dict[str, Dict[str, Any]] = {
    "tru_atomo": {
        "id": "tru_atomo",
        "nombre": "Tru de átomo",
        "unidad": "atomo",
        "nivel_fractal": 1,
        "jurisdiccion": "palabra",
        "factores_evaluables": ("Tru_Ri", "Tru_total"),
        "agrega_desde": (),
        "requiere_material": ("segmento_atomo", "O_id", "enunciado_O"),
        "enunciado": (
            "Misma fórmula canónica a escala átomo "
            "(unidad mínima evaluable)."
        ),
    },
    "tru_frase": {
        "id": "tru_frase",
        "nombre": "Tru de frase",
        "unidad": "frase",
        "nivel_fractal": 2,
        "jurisdiccion": "afirmacion",
        "factores_evaluables": ("Tru_Ri", "Tru_total"),
        "agrega_desde": ("tru_atomo",),
        "requiere_material": ("segmento_frase", "O_id", "enunciado_O"),
        "enunciado": (
            "Misma fórmula canónica a escala frase o afirmación unitaria."
        ),
    },
    "tru_sujeto": {
        "id": "tru_sujeto",
        "nombre": "Tru de sujeto",
        "unidad": "sujeto",
        "nivel_fractal": 3,
        "jurisdiccion": "sujeto",
        "factores_evaluables": ("Tru_Ri", "Tru_total"),
        "agrega_desde": ("tru_frase",),
        "requiere_material": (
            "segmentos_del_sujeto",
            "sujeto_indice",
            "O_id",
            "enunciado_O",
        ),
        "enunciado": (
            "Misma fórmula canónica a escala sujeto "
            "(S_i, i = 1…N según el material; N no lo inventa FO)."
        ),
    },
    "tru_conversacion": {
        "id": "tru_conversacion",
        "nombre": "Tru de conversación",
        "unidad": "conversacion",
        "nivel_fractal": 4,
        "jurisdiccion": "dialogo",
        "factores_evaluables": ("Tru_Ri", "Tru_total"),
        "agrega_desde": ("tru_sujeto", "tru_frase"),
        "requiere_material": ("segmentos_dialogo", "O_id", "enunciado_O"),
        "enunciado": (
            "Misma fórmula canónica a escala conversación o diálogo completo."
        ),
    },
    "tru_repositorio": {
        "id": "tru_repositorio",
        "nombre": "Tru de repositorio",
        "unidad": "repositorio",
        "nivel_fractal": 5,
        "jurisdiccion": "sistema",
        "factores_evaluables": ("Tru_Ri", "Tru_total"),
        "agrega_desde": (),
        "requiere_material": ("O_id", "enunciado_O"),
        "enunciado": (
            "Misma fórmula canónica a escala repositorio o sistema."
        ),
    },
}

IDS_ESCALA: Tuple[str, ...] = tuple(ESCALAS.keys())


def ids() -> List[str]:
    """Ids de escala reconocidos (alineados a TT)."""
    return list(IDS_ESCALA)


def meta_escala(escala_id: str) -> Optional[Dict[str, Any]]:
    """Metadato de una escala; None si el id no existe."""
    e = ESCALAS.get(str(escala_id).strip())
    return dict(e) if e else None


def _exigir_fraction(valor: Any, nombre: str) -> Fraction:
    if not isinstance(valor, Fraction):
        raise TypeError(
            "{0} debe ser Fraction, se recibió {1}".format(
                nombre, type(valor).__name__
            )
        )
    return valor


def aplicar(
    escala_id: str,
    C: Fraction,
    L: Fraction,
    K: Fraction,
) -> Dict[str, Any]:
    """
    Aplica la fórmula canónica bajo el id de escala pedido.

    FO no arma el recorte ni calcula C/L/K: solo multiplica y ancla.
    Si escala_id no está en el mapa → error de id, no de fórmula.
    """
    key = str(escala_id).strip()
    if key not in ESCALAS:
        raise KeyError(
            "escala desconocida: {0!r}. Ids válidos (TT): {1}".format(
                escala_id, list(IDS_ESCALA)
            )
        )

    C = _exigir_fraction(C, "C")
    L = _exigir_fraction(L, "L")
    K = _exigir_fraction(K, "K")

    ri = tru_ri(C, L, K)
    tot = tru_total(C, L, K)
    m = ESCALAS[key]

    return {
        "escala_id": key,
        "nombre": m["nombre"],
        "unidad": m["unidad"],
        "nivel_fractal": m["nivel_fractal"],
        "C": C,
        "L": L,
        "K": K,
        "Tru_Ri": ri,
        "Tru_total": tot,
        "factores_evaluables": list(m["factores_evaluables"]),
        "formula": "canonica",
        "nota": (
            "Misma ley FO; alcance = {0}. "
            "C/L/K no los produce este archivo."
        ).format(key),
    }


# Wrappers por escala (misma función; id fijo en el cierre)
def tru_ri_atomo(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_ri(C, L, K)


def tru_total_atomo(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_total(C, L, K)


def tru_ri_frase(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_ri(C, L, K)


def tru_total_frase(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_total(C, L, K)


def tru_ri_sujeto(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_ri(C, L, K)


def tru_total_sujeto(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_total(C, L, K)


def tru_ri_conversacion(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_ri(C, L, K)


def tru_total_conversacion(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_total(C, L, K)


def tru_ri_repositorio(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_ri(C, L, K)


def tru_total_repositorio(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    return tru_total(C, L, K)


# Registro explícito id → (tru_ri_fn, tru_total_fn)
APLICADORES: Dict[str, Tuple[Callable, Callable]] = {
    "tru_atomo": (tru_ri_atomo, tru_total_atomo),
    "tru_frase": (tru_ri_frase, tru_total_frase),
    "tru_sujeto": (tru_ri_sujeto, tru_total_sujeto),
    "tru_conversacion": (tru_ri_conversacion, tru_total_conversacion),
    "tru_repositorio": (tru_ri_repositorio, tru_total_repositorio),
}


def inventario() -> Dict[str, Any]:
    return {
        "archivo": "escalas_tru.py",
        "version": VERSION,
        "formula_canonica": FORMULA,
        "ids": list(IDS_ESCALA),
        "escalas": {k: dict(v) for k, v in ESCALAS.items()},
        "funcion": (
            "Declara y aplica la fórmula canónica bajo los ids del catálogo TT. "
            "No calcula C/L/K. No segmenta. No deposita."
        ),
    }


__all__ = [
    "FORMULA",
    "VERSION",
    "ESCALAS",
    "IDS_ESCALA",
    "APLICADORES",
    "ids",
    "meta_escala",
    "aplicar",
    "inventario",
    "tru_ri_atomo",
    "tru_total_atomo",
    "tru_ri_frase",
    "tru_total_frase",
    "tru_ri_sujeto",
    "tru_total_sujeto",
    "tru_ri_conversacion",
    "tru_total_conversacion",
    "tru_ri_repositorio",
    "tru_total_repositorio",
]
