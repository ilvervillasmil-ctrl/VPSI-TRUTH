"""
VPSI-TRUTH --- modules/calculator/logica.py

Cálculo del factor de lógica L.

Versión: 2.0
Cambio principal respecto a 1.x:
  - Ancla de base nula (AM-D6 / AM-A3): si p == 0 (o base_nula_L),
    L = UNDEFINED. No se maquilla como 1.
  - Acepta r (reversiones) como Fraction de la retícula AM-D5
    (no solo enteros binarios).
  - L = 1 - r/p  (exacto, Fraction) cuando p > 0.
  - Comentarios explícitos de las anclas para que el código
    documente la fórmula de medición.

Fórmula canónica (operacional):
    L(D) = 1 - r/p
    donde
        p = número de posturas / puntos de fijación (AM-D2)
        r = suma de pesos de severidad de las reversiones (AM-D5)

Definición formal de referencia (Def 5.2):
    L es la existencia de un punto fijo / salida única e invariante
    bajo las reglas del dominio. Una reversión de postura
    degrada ese punto fijo.

Referencias:
  Def 5.2 (Lógica), AM-D2, AM-D5, AM-D6, AM-A3
  PROTOCOLO sec. 0.15
  conteos.py v2.0 (productor de p y r)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, Optional, Union

# Sentinel compartido con el resto de CA
try:
    from modules.calculator import UNDEFINED
except Exception:
    UNDEFINED = "UNDEFINED"


VERSION = "2.0"


def _a_fraction(x: Any) -> Fraction:
    """Convierte a Fraction de forma determinista. No inventa."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, (int, float)):
        return Fraction(x).limit_denominator(10_000)
    if isinstance(x, str):
        try:
            return Fraction(x)
        except Exception:
            return Fraction(0)
    return Fraction(0)


def _calcular_l_operacional(
    p: int,
    r: Union[int, Fraction],
    base_nula: bool = False,
) -> Any:
    """
    Ruta operacional pura.

    AM-A3 / AM-D6:
        Si p == 0 o base_nula → UNDEFINED.
        (Antes se devolvía 1; eso inflaba Tru_Ri artificialmente.)

    AM-D5:
        r puede ser Fraction (suma de pesos de la retícula).
        L = 1 - r/p  se calcula en Fraction exacta.
    """
    if base_nula or p <= 0:
        return UNDEFINED

    r_f = _a_fraction(r)
    # r no puede superar p en peso efectivo
    if r_f > p:
        r_f = Fraction(p)

    l = Fraction(1) - (r_f / Fraction(p))
    # L ∈ [0, 1]
    if l < 0:
        l = Fraction(0)
    if l > 1:
        l = Fraction(1)
    return l


def _calcular_l_teorico(peticion: Dict[str, Any]) -> Any:
    """
    Ruta teórica (si el llamador ya aporta L explícito o
    una señal de no-determinismo / contradicción de punto fijo).
    No inventa valores.
    """
    if "L" in peticion and peticion["L"] is not None:
        val = peticion["L"]
        if val == UNDEFINED or str(val).upper() == "UNDEFINED":
            return UNDEFINED
        return _a_fraction(val)

    # Señal dura de no-determinismo (dos salidas incompatibles)
    if peticion.get("no_determinista") is True:
        return Fraction(0)

    # Contradicción de punto fijo explícita
    if peticion.get("punto_fijo_roto") is True:
        return Fraction(0)

    return None  # no hay dato teórico → se cae a operacional


def calcular_l(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Oficio público de lógica.

    Entrada esperada (inyectada por conteos.inyectar_en_peticion
    o por el ciclo de Engine):
        posturas             : list
        reversiones          : int | Fraction   (r)
        _conteos_meta        : dict opcional con base_nula_L, p, ...

    Salida:
        {
            "L": Fraction | UNDEFINED,
            "p": int,
            "r": Fraction,
            "ruta": "operacional" | "teorico",
            "version": "2.0",
            "notas": list[str],
        }
    """
    peticion = dict(peticion or {})
    notas: list[str] = []

    # ----- Intento teórico primero -----
    l_teo = _calcular_l_teorico(peticion)
    if l_teo is not None:
        return {
            "L": l_teo,
            "p": peticion.get("p") or len(peticion.get("posturas") or []),
            "r": _a_fraction(peticion.get("reversiones") or 0),
            "ruta": "teorico",
            "version": VERSION,
            "notas": ["L tomado de ruta teórica"],
        }

    # ----- Ruta operacional -----
    meta = peticion.get("_conteos_meta") or {}
    posturas = peticion.get("posturas") or []
    p = meta.get("p")
    if p is None:
        p = len(posturas)
    p = int(p)

    r = peticion.get("reversiones")
    if r is None:
        r = meta.get("r") or 0
    r_f = _a_fraction(r)

    base_nula = bool(meta.get("base_nula_L", False)) or (p <= 0)

    l = _calcular_l_operacional(p, r_f, base_nula=base_nula)

    if l is UNDEFINED:
        notas.append(
            "L = UNDEFINED (AM-D6 / AM-A3): p=0 tras ancla de inclusión. "
            "No se asigna 1 artificialmente."
        )
    else:
        notas.append(
            "L = 1 - r/p = 1 - {0}/{1} = {2} (Fraction exacta, AM-D5)".format(
                str(r_f), p, str(l)
            )
        )
        if r_f == 0 and p > 0:
            notas.append(
                "Sin reversiones detectadas en el turno: punto fijo "
                "preservado bajo la evidencia disponible."
            )

    return {
        "L": l,
        "p": p,
        "r": r_f,
        "ruta": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def verificar_l(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    if "L" not in salida:
        return False
    val = salida["L"]
    if val is UNDEFINED or str(val).upper() == "UNDEFINED":
        return True
    if isinstance(val, Fraction):
        return Fraction(0) <= val <= Fraction(1)
    return False


__all__ = [
    "calcular_l",
    "verificar_l",
    "VERSION",
    "UNDEFINED",
]
