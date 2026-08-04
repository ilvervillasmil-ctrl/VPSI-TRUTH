"""
VPSI-TRUTH --- modules/calculator/__init__.py

Orquestador del módulo Calculator (CA).

Versión: 2.0
Cambio principal respecto a 1.x:
  - Integra conteos.py v2.0 (anclas de inclusión + retícula + base nula).
  - Propaga UNDEFINED desde C, L o K sin maquillar a 1.
  - Tru_Ri solo se forma cuando C, L y K están todos definidos.
  - Tru_total = (Tru_Ri · α) + β  permanece canónico e intacto.
  - Meta de anclas (_conteos_meta) viaja completa para auditoría.

Oficio del módulo:
    1. Extraer conteos (conteos.inyectar_en_peticion)
    2. Calcular C, L, K (coherencia / logica / correlacion_k)
    3. Formar Tru_Ri = C · L · K   (solo si los tres están definidos)
    4. Formar Tru_total = (Tru_Ri · ALPHA) + BETA
    5. Devolver paquete completo + notas de anclas

No inventa factores.
No inventa dominios.
No suaviza bases nulas.

Referencias:
  Def 5.1–5.3, Def-5.3.1, AM-D2/D5/D6, AM-A3/A4
  Teorema de la Verdad (Tru_total = C·L·K·α + β)
  conteos.py / coherencia.py / logica.py / correlacion_k.py  v2.0
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List, Optional

from modules.constante import ALPHA, BETA

from . import conteos
from . import coherencia
from . import logica
from . import correlacion_k

# Sentinel canónico
UNDEFINED = "UNDEFINED"

VERSION = "2.0"

# ---------------------------------------------------------------
# Contrato del contenedor (Engine lo lee)
# ---------------------------------------------------------------
CONTENEDOR = {
    "nombre": "calculator",
    "rol": "CA",
    "version": VERSION,
    "descripcion": (
        "Calcula C, L, K, Tru_Ri y Tru_total bajo anclas de medición. "
        "Base nula → UNDEFINED. Sin O_context → K UNDEFINED."
    ),
    "requiere": ["rol:CT", "rol:FO"],
    "capacidades": {
        "calcular": "calcular",
        "barrer": "barrer",
    },
}


# ---------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------

def _es_undefined(val: Any) -> bool:
    return val is UNDEFINED or str(val).upper() == "UNDEFINED"


def _a_fraction(x: Any) -> Optional[Fraction]:
    if _es_undefined(x):
        return None
    if isinstance(x, Fraction):
        return x
    if isinstance(x, (int, float)):
        return Fraction(x).limit_denominator(10_000)
    if isinstance(x, str):
        try:
            return Fraction(x)
        except Exception:
            return None
    return None


def _asegurar_conteos(peticion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Garantiza que la petición ya trae los conteos de conteos.py v2.0.
    Si no, los inyecta.
    """
    meta = peticion.get("_conteos_meta")
    if isinstance(meta, dict) and meta.get("version") == conteos.VERSION:
        return peticion
    return conteos.inyectar_en_peticion(peticion)


# ---------------------------------------------------------------
# Oficio principal
# ---------------------------------------------------------------

def calcular(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Ciclo completo de cálculo bajo anclas de medición v2.0.

    Entrada:
        mensaje / descripcion / texto / D
        contexto / O_context / o_context   (obligatorio para K)

    Salida:
        {
            "C": Fraction | UNDEFINED,
            "L": Fraction | UNDEFINED,
            "K": Fraction | UNDEFINED,
            "Tru_Ri": Fraction | UNDEFINED,
            "Tru_total": Fraction | UNDEFINED,
            "conteos": {...},
            "meta": {...},
            "ruta": "operacional",
            "version": "2.0",
            "notas": list[str],
            "coherente": bool,
        }
    """
    peticion = dict(peticion or {})
    notas: List[str] = []

    # 1. Conteos con anclas
    peticion = _asegurar_conteos(peticion)
    meta_conteos = dict(peticion.get("_conteos_meta") or {})
    notas.extend(meta_conteos.get("notas") or [])

    # 2. Factores
    out_c = coherencia.calcular_c(peticion)
    out_l = logica.calcular_l(peticion)
    out_k = correlacion_k.calcular_k(peticion)

    C = out_c.get("C")
    L = out_l.get("L")
    K = out_k.get("K")

    notas.extend(out_c.get("notas") or [])
    notas.extend(out_l.get("notas") or [])
    notas.extend(out_k.get("notas") or [])

    # 3. Tru_Ri = C · L · K  (solo si los tres están definidos)
    if _es_undefined(C) or _es_undefined(L) or _es_undefined(K):
        tru_ri: Any = UNDEFINED
        notas.append(
            "Tru_Ri = UNDEFINED: al menos un factor (C/L/K) está indefinido "
            "(AM-A3 / Def-5.3.1). No se forma producto parcial."
        )
    else:
        c_f = _a_fraction(C)
        l_f = _a_fraction(L)
        k_f = _a_fraction(K)
        if c_f is None or l_f is None or k_f is None:
            tru_ri = UNDEFINED
            notas.append("Tru_Ri = UNDEFINED: conversión a Fraction falló.")
        else:
            tru_ri = c_f * l_f * k_f
            notas.append(
                "Tru_Ri = C·L·K = {0}·{1}·{2} = {3}".format(
                    str(c_f), str(l_f), str(k_f), str(tru_ri)
                )
            )

    # 4. Tru_total = (Tru_Ri · α) + β
    if _es_undefined(tru_ri):
        # Incluso sin Tru_Ri, el piso estructural β permanece
        # (Teorema de la Verdad: el interior irreducible no se anula).
        # Política: si no hay Tru_Ri, reportamos UNDEFINED en Tru_total
        # para no confundir "solo β" con un cálculo completo.
        # El llamador (Omega / Engine) puede decidir mostrar β como piso.
        tru_total: Any = UNDEFINED
        notas.append(
            "Tru_total = UNDEFINED (sin Tru_Ri). "
            "Piso estructural β = {0} sigue disponible como referencia.".format(
                str(BETA)
            )
        )
    else:
        tru_total = (tru_ri * ALPHA) + BETA
        notas.append(
            "Tru_total = (Tru_Ri · α) + β = ({0} · {1}) + {2} = {3}".format(
                str(tru_ri), str(ALPHA), str(BETA), str(tru_total)
            )
        )

    # 5. Paquete final
    coherente = not (
        _es_undefined(C)
        or _es_undefined(L)
        or _es_undefined(K)
        or _es_undefined(tru_ri)
        or _es_undefined(tru_total)
    )

    return {
        "C": C,
        "L": L,
        "K": K,
        "Tru_Ri": tru_ri,
        "Tru_total": tru_total,
        "ALPHA": ALPHA,
        "BETA": BETA,
        "conteos": {
            "compromisos": peticion.get("compromisos"),
            "contradicciones": peticion.get("contradicciones"),
            "posturas": peticion.get("posturas"),
            "reversiones": peticion.get("reversiones"),
            "afirmaciones": peticion.get("afirmaciones"),
            "afirmaciones_falsas": peticion.get("afirmaciones_falsas"),
        },
        "meta": {
            "m": meta_conteos.get("m"),
            "p": meta_conteos.get("p"),
            "c": meta_conteos.get("c"),
            "base_nula_C": meta_conteos.get("base_nula_C"),
            "base_nula_L": meta_conteos.get("base_nula_L"),
            "base_nula_K": meta_conteos.get("base_nula_K"),
            "o_presente": meta_conteos.get("o_presente"),
            "k_detalle": meta_conteos.get("k_detalle"),
            "f_detalle": meta_conteos.get("f_detalle"),
            "conteos_version": meta_conteos.get("version"),
            "detalle_C": {"m": out_c.get("m"), "k": out_c.get("k")},
            "detalle_L": {"p": out_l.get("p"), "r": out_l.get("r")},
            "detalle_K": {
                "c": out_k.get("c"),
                "f": out_k.get("f"),
                "o_presente": out_k.get("o_presente"),
            },
        },
        "ruta": "operacional",
        "version": VERSION,
        "notas": notas,
        "coherente": coherente,
    }


def barrer(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Oficio de auditoría rápida del módulo CA.
    Verifica que conteos + tres factores + orquestador responden
    sin lanzar y que las anclas de base nula se respetan.
    """
    errores: List[str] = []
    avisos: List[str] = []

    # Caso vacío → debe producir UNDEFINED en C/L/K
    vacio = calcular({"mensaje": "", "contexto": None})
    for factor in ("C", "L", "K"):
        if not _es_undefined(vacio.get(factor)):
            errores.append(
                "base nula no respetada: {0} debió ser UNDEFINED y fue {1}".format(
                    factor, vacio.get(factor)
                )
            )

    # Caso con O y afirmación simple
    simple = calcular({
        "mensaje": "El sol irradia luz.",
        "contexto": "hechos observables del sistema solar",
    })
    if _es_undefined(simple.get("K")):
        avisos.append(
            "K UNDEFINED en caso simple con O: revisar ancla de inclusión "
            "o tokens de correspondencia."
        )

    # Versiones alineadas
    if conteos.VERSION != "2.0":
        errores.append("conteos.VERSION != 2.0")
    if coherencia.VERSION != "2.0":
        errores.append("coherencia.VERSION != 2.0")
    if logica.VERSION != "2.0":
        errores.append("logica.VERSION != 2.0")
    if correlacion_k.VERSION != "2.0":
        errores.append("correlacion_k.VERSION != 2.0")

    return {
        "modulo": "calculator",
        "version": VERSION,
        "coherente": len(errores) == 0,
        "errores": errores,
        "avisos": avisos,
        "caso_vacio": {
            "C": vacio.get("C"),
            "L": vacio.get("L"),
            "K": vacio.get("K"),
            "Tru_Ri": vacio.get("Tru_Ri"),
        },
        "caso_simple": {
            "C": simple.get("C"),
            "L": simple.get("L"),
            "K": simple.get("K"),
            "Tru_Ri": simple.get("Tru_Ri"),
            "Tru_total": simple.get("Tru_total"),
        },
    }


__all__ = [
    "CONTENEDOR",
    "calcular",
    "barrer",
    "UNDEFINED",
    "VERSION",
    "ALPHA",
    "BETA",
]
