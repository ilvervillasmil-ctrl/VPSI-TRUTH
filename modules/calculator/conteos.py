"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales (PROTOCOLO sec. 0.15).

Oficio unico:
    texto + O_context  ->  {
        compromisos, contradicciones,
        posturas, reversiones,
        afirmaciones, afirmaciones_falsas
    }

No calcula C, L, K.
No calcula Tru.
No inventa factores.
Solo materializa los conteos que la ruta operacional de CA ya exige.

Nodos de ciclo_calculo_MC que materializa:
    CC_Premisas_Registro
    CC_Afirmaciones_D
    CC_Conteo_C / CC_Conteo_L / CC_Conteo_K

Reglas:
    C = 1 - k/m   (k = pares contradictorios, m = compromisos)
    L = 1 - r/p   (r = reversiones, p = posturas)
    K = 1 - f/c   (f = afirmaciones que divergen de O, c = afirmaciones)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ===============================================================
# Patrones deterministas (sin modelo, sin estocastico)
# ===============================================================

_PATRONES_CONTRADICCION = (
    r"\by\s+no\b",
    r"\bpero\s+no\b",
    r"\bsin\s+embargo\b",
    r"\baunque\b",
    r"\bno\s+obstante\b",
    r"\bmas\s+no\b",
    r"\bes\b.+\bno\s+es\b",
    r"\bno\s+es\b.+\bes\b",
)

_SEPARADORES = re.compile(r"[.;:\n]+|\by\s+(?=[A-ZÁÉÍÓÚ])")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


# ===============================================================
# Extraccion de unidades
# ===============================================================

def _partir_unidades(texto: str) -> List[str]:
    """Parte el texto en unidades candidatas a compromiso / afirmacion / postura."""
    if not texto or not str(texto).strip():
        return []
    partes = _SEPARADORES.split(str(texto))
    return [p.strip() for p in partes if p and p.strip()]


def _detectar_contradicciones(unidades: List[str]) -> int:
    """
    k = numero de unidades que contienen patron de contradiccion interna.
    Determinista. No interpreta semantica profunda.
    """
    k = 0
    for u in unidades:
        low = _norm(u)
        for pat in _PATRONES_CONTRADICCION:
            if re.search(pat, low):
                k += 1
                break
    return k


def _divergencias_con_o(afirmaciones: List[str], o_context: Optional[str]) -> int:
    """
    f = numero de afirmaciones que no encuentran ancla literal en O.
    Criterio minimo y determinista:
      - si O esta ausente -> f = len(afirmaciones)
      - si O existe -> cuenta las que no comparten token significativo con O
    """
    if not afirmaciones:
        return 0
    if not o_context or not str(o_context).strip():
        return len(afirmaciones)

    o_tokens = set(re.findall(r"[a-záéíóúñ0-9/]+", _norm(o_context)))
    stop = {
        "el", "la", "los", "las", "un", "una", "de", "del",
        "en", "y", "o", "a", "que", "es", "se", "por", "con",
    }
    o_tokens -= stop

    f = 0
    for a in afirmaciones:
        a_tokens = set(re.findall(r"[a-záéíóúñ0-9/]+", _norm(a))) - stop
        if not a_tokens:
            f += 1
            continue
        if not (a_tokens & o_tokens):
            f += 1
    return f


# ===============================================================
# Oficio publico
# ===============================================================

def extraer_conteos(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Transforma texto + O_context en los conteos que CA.operacional ya espera.

    Entrada (claves admitidas):
        mensaje | descripcion | texto | D
        contexto | O_context | o_context

    Salida (las seis claves que CA consume):
        compromisos          : List[str]
        contradicciones      : int   (k)
        posturas             : List[str]
        reversiones          : int   (r)
        afirmaciones         : List[str]
        afirmaciones_falsas  : int   (f)

    Ademas:
        m, p, c              : enteros derivados
        o_presente           : bool
        metodo_sugerido      : str
        notas                : List[str]
    """
    peticion = dict(peticion or {})

    texto = (
        peticion.get("mensaje")
        or peticion.get("descripcion")
        or peticion.get("texto")
        or peticion.get("D")
        or ""
    )
    o_ctx = (
        peticion.get("contexto")
        or peticion.get("O_context")
        or peticion.get("o_context")
    )

    unidades = _partir_unidades(str(texto))
    notas: List[str] = []

    # C: compromisos / contradicciones (k/m)
    compromisos = list(unidades)
    k = _detectar_contradicciones(compromisos)
    m = len(compromisos)

    # L: posturas / reversiones (r/p)
    # Ciclo de una sola frase: sin historial -> r = 0
    posturas = list(unidades)
    r = 0
    p = len(posturas)
    if "historial_posturas" in peticion and isinstance(peticion["historial_posturas"], list):
        prev = [_norm(x) for x in peticion["historial_posturas"]]
        for u in unidades:
            if _norm(u) in prev:
                pass  # repeticion no cuenta como reversion

    # K: afirmaciones / afirmaciones_falsas (f/c)
    afirmaciones = list(unidades)
    f = _divergencias_con_o(afirmaciones, o_ctx)
    c = len(afirmaciones)

    o_presente = bool(o_ctx and str(o_ctx).strip())

    if not unidades:
        notas.append("texto vacio -> m=p=c=0")
    if not o_presente:
        notas.append("O_context ausente -> f=c (K degradado por Def-5.3.1)")
    if k > 0:
        notas.append("contradicciones detectadas k={0}".format(k))
    if f > 0 and o_presente:
        notas.append("divergencias con O f={0}".format(f))

    return {
        "compromisos": compromisos,
        "contradicciones": k,
        "posturas": posturas,
        "reversiones": r,
        "afirmaciones": afirmaciones,
        "afirmaciones_falsas": f,
        "m": m,
        "p": p,
        "c": c,
        "o_presente": o_presente,
        "metodo_sugerido": "operacional",
        "notas": notas,
    }


def inyectar_en_peticion(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Copia de la peticion con los conteos ya insertados.
    Engine o el ciclo pueden hacer:
        peticion = inyectar_en_peticion(peticion)
        factores = ca.calcular(peticion)
    """
    base = dict(peticion or {})
    conteos = extraer_conteos(base)
    for clave in (
        "compromisos",
        "contradicciones",
        "posturas",
        "reversiones",
        "afirmaciones",
        "afirmaciones_falsas",
    ):
        base[clave] = conteos[clave]
    base["_conteos_meta"] = {
        "m": conteos["m"],
        "p": conteos["p"],
        "c": conteos["c"],
        "o_presente": conteos["o_presente"],
        "notas": conteos["notas"],
    }
    return base


def verificar_conteos(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    requeridas = (
        "compromisos",
        "contradicciones",
        "posturas",
        "reversiones",
        "afirmaciones",
        "afirmaciones_falsas",
    )
    return all(k in salida for k in requeridas)


__all__ = [
    "extraer_conteos",
    "inyectar_en_peticion",
    "verificar_conteos",
]
