"""
VPSI-TRUTH --- modules/calculator/coherencia.py

Cálculo del factor de coherencia C.

Versión: 2.0
Cambio principal respecto a 1.x:
  - Ancla de base nula (AM-D6 / AM-A3): si m == 0 (o base_nula_C),
    C = UNDEFINED. No se maquilla como 1.
  - Acepta k (contradicciones) como Fraction de la retícula AM-D5
    (no solo enteros binarios).
  - C = 1 - k/m  (exacto, Fraction) cuando m > 0.
  - Comentarios explícitos de las anclas para que el código
    documente la fórmula de medición.

Fórmula canónica (operacional):
    C(D) = 1 - k/m
    donde
        m = número de compromisos de adopción propia (AM-D2)
        k = suma de pesos de severidad de las contradicciones (AM-D5)

Referencias:
  Def 5.1 (Coherencia), AM-D2, AM-D5, AM-D6, AM-A3
  PROTOCOLO sec. 0.15
  conteos.py v2.0 (productor de m y k)
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


def _calcular_c_operacional(
    m: int,
    k: Union[int, Fraction],
    base_nula: bool = False,
) -> Any:
    """
    Ruta operacional pura.

    AM-A3 / AM-D6:
        Si m == 0 o base_nula → UNDEFINED.
        (Antes se devolvía 1; eso inflaba Tru_Ri artificialmente.)

    AM-D5:
        k puede ser Fraction (suma de pesos de la retícula).
        C = 1 - k/m  se calcula en Fraction exacta.
    """
    if base_nula or m <= 0:
        return UNDEFINED

    k_f = _a_fraction(k)
    # k no puede superar m en peso efectivo; se acota por seguridad
    # (un peso total > m no tiene sentido físico en la definición)
    if k_f > m:
        k_f = Fraction(m)

    c = Fraction(1) - (k_f / Fraction(m))
    # C ∈ [0, 1]
    if c < 0:
        c = Fraction(0)
    if c > 1:
        c = Fraction(1)
    return c


def _calcular_c_teorico(peticion: Dict[str, Any]) -> Any:
    """
    Ruta teórica (si el llamador ya aporta C explícito o
    una lista de contradicciones lógicas formales).
    No inventa valores.
    """
    if "C" in peticion and peticion["C"] is not None:
        val = peticion["C"]
        if val == UNDEFINED or str(val).upper() == "UNDEFINED":
            return UNDEFINED
        return _a_fraction(val)

    # Si hay flag de contradicción lógica dura
    if peticion.get("contradiccion_logica") is True:
        return Fraction(0)

    return None  # no hay dato teórico → se cae a operacional


def calcular_c(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Oficio público de coherencia.

    Entrada esperada (inyectada por conteos.inyectar_en_peticion
    o por el ciclo de Engine):
        compromisos          : list
        contradicciones      : int | Fraction   (k)
        _conteos_meta        : dict opcional con base_nula_C, m, ...

    Salida:
        {
            "C": Fraction | UNDEFINED,
            "m": int,
            "k": Fraction,
            "ruta": "operacional" | "teorico",
            "version": "2.0",
            "notas": list[str],
        }
    """
    peticion = dict(peticion or {})
    notas: list[str] = []

    # ----- Intento teórico primero -----
    c_teo = _calcular_c_teorico(peticion)
    if c_teo is not None:
        return {
            "C": c_teo,
            "m": peticion.get("m") or len(peticion.get("compromisos") or []),
            "k": _a_fraction(peticion.get("contradicciones") or 0),
            "ruta": "teorico",
            "version": VERSION,
            "notas": ["C tomado de ruta teórica"],
        }

    # ----- Ruta operacional -----
    meta = peticion.get("_conteos_meta") or {}
    compromisos = peticion.get("compromisos") or []
    m = meta.get("m")
    if m is None:
        m = len(compromisos)
    m = int(m)

    k = peticion.get("contradicciones")
    if k is None:
        k = meta.get("k") or 0
    k_f = _a_fraction(k)

    base_nula = bool(meta.get("base_nula_C", False)) or (m <= 0)

    c = _calcular_c_operacional(m, k_f, base_nula=base_nula)

    if c is UNDEFINED:
        notas.append(
            "C = UNDEFINED (AM-D6 / AM-A3): m=0 tras ancla de inclusión. "
            "No se asigna 1 artificialmente."
        )
    else:
        notas.append(
            "C = 1 - k/m = 1 - {0}/{1} = {2} (Fraction exacta, AM-D5)".format(
                str(k_f), m, str(c)
            )
        )

    return {
        "C": c,
        "m": m,
        "k": k_f,
        "ruta": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def verificar_c(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    if "C" not in salida:
        return False
    val = salida["C"]
    if val is UNDEFINED or str(val).upper() == "UNDEFINED":
        return True
    if isinstance(val, Fraction):
        return Fraction(0) <= val <= Fraction(1)
    return False


__all__ = [
    "calcular_c",
    "verificar_c",
    "VERSION",
    "UNDEFINED",
]
