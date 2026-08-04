"""
VPSI-TRUTH --- modules/calculator/correlacion_k.py

Cálculo del factor de correlación K.

Versión: 2.0
Cambio principal respecto a 1.x:
  - Ancla de base nula (AM-D6 / AM-A3): si c == 0 (o base_nula_K),
    K = UNDEFINED. No se maquilla como 1.
  - Ancla de dominio (Def-5.3.1): sin O_context explícito,
    K = UNDEFINED (no se inventa correspondencia).
  - Acepta f (afirmaciones_falsas / divergencias) como Fraction
    de la retícula AM-D5 (no solo enteros binarios).
  - K = 1 - f/c  (exacto, Fraction) cuando c > 0 y O presente.
  - Comentarios explícitos de las anclas para que el código
    documente la fórmula de medición.

Fórmula canónica (operacional):
    K(D) = 1 - f/c
    donde
        c = número de afirmaciones verificables respecto de O
        f = suma de pesos de severidad de las divergencias (AM-D5)
        O = dominio observable declarado (O_context)

Definición formal de referencia (Def 5.3 + Def-5.3.1):
    K exige un O_context explícito. Sin él el factor no está definido.
    La correlación mide correspondencia con hechos del dominio,
    no coherencia interna ni lógica de punto fijo (ortogonalidad AM-A4).

Referencias:
  Def 5.3, Def-5.3.1, AM-D2, AM-D5, AM-D6, AM-A3, AM-A4
  PROTOCOLO sec. 0.15
  conteos.py v2.0 (productor de c y f)
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


def _calcular_k_operacional(
    c: int,
    f: Union[int, Fraction],
    o_presente: bool = False,
    base_nula: bool = False,
) -> Any:
    """
    Ruta operacional pura.

    Def-5.3.1:
        Sin O_context → UNDEFINED.
        (No se inventa un dominio para forzar un número.)

    AM-A3 / AM-D6:
        Si c == 0 o base_nula → UNDEFINED.
        (Antes se devolvía 1; eso inflaba Tru_Ri artificialmente.)

    AM-D5:
        f puede ser Fraction (suma de pesos de la retícula).
        K = 1 - f/c  se calcula en Fraction exacta.
    """
    if not o_presente:
        return UNDEFINED

    if base_nula or c <= 0:
        return UNDEFINED

    f_f = _a_fraction(f)
    # f no puede superar c en peso efectivo
    if f_f > c:
        f_f = Fraction(c)

    k = Fraction(1) - (f_f / Fraction(c))
    # K ∈ [0, 1]
    if k < 0:
        k = Fraction(0)
    if k > 1:
        k = Fraction(1)
    return k


def _calcular_k_teorico(peticion: Dict[str, Any]) -> Any:
    """
    Ruta teórica (si el llamador ya aporta K explícito o
    una señal dura de no-correspondencia con O).
    No inventa valores.
    """
    if "K" in peticion and peticion["K"] is not None:
        val = peticion["K"]
        if val == UNDEFINED or str(val).upper() == "UNDEFINED":
            return UNDEFINED
        return _a_fraction(val)

    # Señal dura de divergencia total con el dominio
    if peticion.get("sin_correspondencia") is True:
        return Fraction(0)

    return None  # no hay dato teórico → se cae a operacional


def calcular_k(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Oficio público de correlación.

    Entrada esperada (inyectada por conteos.inyectar_en_peticion
    o por el ciclo de Engine):
        afirmaciones           : list
        afirmaciones_falsas    : int | Fraction   (f)
        contexto / O_context   : str | None
        _conteos_meta          : dict opcional con base_nula_K, c, o_presente, ...

    Salida:
        {
            "K": Fraction | UNDEFINED,
            "c": int,
            "f": Fraction,
            "o_presente": bool,
            "ruta": "operacional" | "teorico",
            "version": "2.0",
            "notas": list[str],
        }
    """
    peticion = dict(peticion or {})
    notas: list[str] = []

    # ----- Intento teórico primero -----
    k_teo = _calcular_k_teorico(peticion)
    if k_teo is not None:
        return {
            "K": k_teo,
            "c": peticion.get("c") or len(peticion.get("afirmaciones") or []),
            "f": _a_fraction(peticion.get("afirmaciones_falsas") or 0),
            "o_presente": bool(
                peticion.get("contexto")
                or peticion.get("O_context")
                or peticion.get("o_context")
            ),
            "ruta": "teorico",
            "version": VERSION,
            "notas": ["K tomado de ruta teórica"],
        }

    # ----- Ruta operacional -----
    meta = peticion.get("_conteos_meta") or {}
    afirmaciones = peticion.get("afirmaciones") or []
    c = meta.get("c")
    if c is None:
        c = len(afirmaciones)
    c = int(c)

    f = peticion.get("afirmaciones_falsas")
    if f is None:
        f = meta.get("f") or 0
    f_f = _a_fraction(f)

    o_ctx = (
        peticion.get("contexto")
        or peticion.get("O_context")
        or peticion.get("o_context")
    )
    o_presente = bool(meta.get("o_presente", False)) or bool(o_ctx and str(o_ctx).strip())

    base_nula = bool(meta.get("base_nula_K", False)) or (c <= 0)

    k = _calcular_k_operacional(
        c, f_f, o_presente=o_presente, base_nula=base_nula
    )

    if k is UNDEFINED:
        if not o_presente:
            notas.append(
                "K = UNDEFINED (Def-5.3.1): O_context ausente. "
                "No se inventa dominio ni correspondencia."
            )
        else:
            notas.append(
                "K = UNDEFINED (AM-D6 / AM-A3): c=0 tras ancla de inclusión. "
                "No se asigna 1 artificialmente."
            )
    else:
        notas.append(
            "K = 1 - f/c = 1 - {0}/{1} = {2} (Fraction exacta, AM-D5)".format(
                str(f_f), c, str(k)
            )
        )
        if f_f == 0 and c > 0:
            notas.append(
                "Sin divergencias detectadas respecto de O: "
                "correspondencia plena bajo la evidencia disponible."
            )

    return {
        "K": k,
        "c": c,
        "f": f_f,
        "o_presente": o_presente,
        "ruta": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def verificar_k(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    if "K" not in salida:
        return False
    val = salida["K"]
    if val is UNDEFINED or str(val).upper() == "UNDEFINED":
        return True
    if isinstance(val, Fraction):
        return Fraction(0) <= val <= Fraction(1)
    return False


__all__ = [
    "calcular_k",
    "verificar_k",
    "VERSION",
    "UNDEFINED",
]
