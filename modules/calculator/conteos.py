"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales con anclas de medición (AM v1.0).

Versión: 2.1
Cambio principal respecto a 2.0:
  - Simetría C/L en base de conteo: si no hay señales de adopción
    metodológica explícita, m se forma con proposiciones asertivas
    del mensaje (igual que p ya hacía fallback). Sin eso, prosa
    factual legítima dejaba m=0 → C=null y el ciclo quedaba PARCIAL
    aunque hubiera contenido evaluable.
  - Actos siguen fuera del denominador (AM-D2).
  - Base nula solo cuando no hay unidades que puedan anclar el factor.
  - Retícula de severidad (AM-D5) intacta.
  - Sin O_context → K saturado / señal para UNDEFINED (Def-5.3.1).

Oficio único:
    texto + O_context  ->  {
        compromisos, contradicciones,   # m, k  (C = 1 - k/m)
        posturas, reversiones,          # p, r  (L = 1 - r/p)
        afirmaciones, afirmaciones_falsas  # c, f  (K = 1 - f/c)
    }

No calcula C, L, K.
No calcula Tru.
No inventa factores.
Solo materializa los conteos que la ruta operacional de CA exige.

Referencias:
  AM-D1..D6, AM-A1..A5, AM-T1 (anclas_medicion_AX)
  Def 5.1–5.3, Def-5.3.1, PROTOCOLO sec. 0.15
  AF-C2, AF-C4, AF-T8 (sm_af_AX)
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union


# ===============================================================
# CONSTANTES — Retícula de severidad (AM-D5)
# ===============================================================
PESO_ROCE    = Fraction(1, 4)
PESO_PARCIAL = Fraction(1, 2)
PESO_GRAVE   = Fraction(3, 4)
PESO_TOTAL   = Fraction(1, 1)

RETICULA = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)

VERSION = "2.1"


# ===============================================================
# PATRONES DETERMINISTAS (sin modelo, sin estocástico)
# ===============================================================

_PATRONES_CONTRADICCION: Tuple[Tuple[str, Fraction], ...] = (
    (r"\by\s+no\b",                 PESO_TOTAL),
    (r"\bpero\s+no\b",              PESO_TOTAL),
    (r"\bes\b.+\bno\s+es\b",        PESO_TOTAL),
    (r"\bno\s+es\b.+\bes\b",        PESO_TOTAL),
    (r"\bsí\s+y\s+no\b",            PESO_TOTAL),
    (r"\bno\s+y\s+sí\b",            PESO_TOTAL),
    (r"\bsin\s+embargo\b",          PESO_GRAVE),
    (r"\bno\s+obstante\b",          PESO_GRAVE),
    (r"\bpor\s+un\s+lado\b.+\bpor\s+(?:el\s+)?otro\b", PESO_GRAVE),
    (r"\baunque\b",                 PESO_PARCIAL),
    (r"\bmas\s+no\b",               PESO_PARCIAL),
    (r"\bsin\s+dejar\s+de\b",       PESO_PARCIAL),
)

# Señales de ADOPCIÓN METODOLÓGICA / autoatribución fuerte (AM-D2 prioritario)
_SENALES_ADOPCION = (
    r"\bno\s+invento\b",
    r"\bno\s+decido\b",
    r"\bno\s+salgo\b",
    r"\bno\s+modifico\b",
    r"\bno\s+altero\b",
    r"\bno\s+tomo\s+decisiones\b",
    r"\bmantengo\b",
    r"\bafirmo\b",
    r"\bdeclaro\b",
    r"\bsostengo\b",
    r"\bme\s+comprometo\b",
    r"\bestablezco\b",
    r"\badopto\b",
    r"\bproh[ií]bo\b",
    r"\bobligo\b",
    r"\bqueda\s+fijado\b",
    r"\bqueda\s+establecido\b",
    r"\bes\s+un\s+hecho\b",
    r"\bsoy\s+determinista\b",
    r"\bqueda\s+registrado\b",
)

# Actos: no entran en denominador m/p/c
_SENALES_ACTO = (
    r"\bpropongo\b",
    r"\bpropongamos\b",
    r"\bintroduzcamos\b",
    r"\bintroduzco\b",
    r"\bpodr[ií]amos\b",
    r"\bsugerir[ií]a\b",
    r"\bsugiero\b",
    r"\bplanteo\b",
    r"\bte\s+invito\b",
    r"\bvamos\s+a\s+llamar\b",
    r"\bvamos\s+a\s+definir\b",
    r"\bdefinamos\b",
    r"\bcreo\s+el\s+s[ií]mbolo\b",
    r"(?<!no\s)\binvento\b",
)

_SENALES_NO_PROPOSICION = (
    r"^\s*(?:si|cuando|aunque|mientras|donde|como)\b",
    r"\?\s*$",
    r"^\s*(?:¿|¡)",
)

_SEPARADORES = re.compile(
    r"[.;:!?\n]+|"
    r"\by\s+(?=[A-ZÁÉÍÓÚ¿¡])|"
    r"\b(?:además|asimismo|por\s+otra\s+parte|Además|Asimismo)\b",
)

_STOP = {
    "el", "la", "los", "las", "un", "una", "de", "del",
    "en", "y", "o", "a", "que", "es", "se", "por", "con",
    "al", "lo", "su", "sus", "mi", "tu", "le", "les",
}


# ===============================================================
# HELPERS
# ===============================================================

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _partir_unidades(texto: str) -> List[str]:
    if not texto or not str(texto).strip():
        return []
    partes = _SEPARADORES.split(str(texto))
    return [p.strip() for p in partes if p and p.strip()]


def _es_acto(unidad: str) -> bool:
    low = _norm(unidad)
    for pat in _SENALES_ACTO:
        if re.search(pat, low):
            return True
    return False


def _es_adopcion_metodologica(unidad: str) -> bool:
    """
    AM-D2 prioritario: señal explícita de compromiso / autoatribución.
    """
    low = _norm(unidad)
    if not low:
        return False
    for pat in _SENALES_ADOPCION:
        if re.search(pat, low):
            return True
    return False


def _es_proposicion(unidad: str) -> bool:
    """
    AF-C4 / AF-T8: forma asertiva con contenido reconocible.
    Excluye actos, preguntas y condicionantes puros.
    """
    low = _norm(unidad)
    if not low:
        return False
    if _es_acto(unidad):
        return False
    for pat in _SENALES_NO_PROPOSICION:
        if re.search(pat, low):
            return False
    toks = low.split()
    if len(toks) >= 2:
        return True
    if re.search(r"[0-9=+\-*/^ββα]", low):
        return True
    return False


def _peso_contradiccion_en(unidad: str) -> Fraction:
    low = _norm(unidad)
    for pat, peso in _PATRONES_CONTRADICCION:
        if re.search(pat, low):
            return peso
    return Fraction(0)


def _peso_acto_contra_compromiso(acto: str, base_norm: List[str]) -> Fraction:
    low = _norm(acto)
    if not _es_acto(acto):
        return Fraction(0)
    hay_restriccion = any(
        re.search(
            r"\bno\s+invento\b|\bno\s+decido\b|\bno\s+salgo\b|"
            r"\bno\s+modifico\b|\bno\s+altero\b|\bno\s+tomo\s+decisiones\b",
            c,
        )
        for c in base_norm
    )
    if not hay_restriccion:
        return Fraction(0)
    if re.search(
        r"\bpropongo\b|\bpropongamos\b|\bintroduzco\b|\bintroduzcamos\b|"
        r"\binvento\b|\bcreo\s+el\s+s[ií]mbolo\b|\bdefinamos\b|\bplanteo\b",
        low,
    ):
        return PESO_GRAVE
    return PESO_PARCIAL


def _tokens(s: str) -> set:
    return set(re.findall(r"[a-záéíóúñ0-9/]+", _norm(s))) - _STOP


def _divergencia_peso(afirmacion: str, o_tokens: set) -> Fraction:
    a_tok = _tokens(afirmacion)
    if not a_tok:
        return PESO_TOTAL
    if not o_tokens:
        return PESO_TOTAL
    inter = a_tok & o_tokens
    if not inter:
        return PESO_TOTAL
    ratio = Fraction(len(inter), len(a_tok))
    if ratio >= Fraction(1, 2):
        return Fraction(0)
    if ratio >= Fraction(1, 4):
        return PESO_PARCIAL
    return PESO_GRAVE


def _normalizar_entrada(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {}
    if len(args) == 1 and isinstance(args[0], dict):
        base.update(args[0])
    elif len(args) >= 1:
        base["texto"] = args[0]
        if len(args) >= 2 and args[1] is not None:
            base["o_context"] = args[1]
    base.update({k: v for k, v in kwargs.items() if v is not None})
    return base


def _texto_de(peticion: Dict[str, Any]) -> str:
    """
    Extrae el enunciado evaluable desde las claves habituales del pipeline.
    Incluye entrada anidada (tests / Engine).
    """
    if not isinstance(peticion, dict):
        return ""
    for k in ("mensaje", "descripcion", "texto", "D", "enunciado"):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            return str(v)
    ent = peticion.get("entrada")
    if isinstance(ent, dict):
        for k in ("texto", "mensaje", "descripcion"):
            v = ent.get(k)
            if v is not None and str(v).strip():
                return str(v)
    return ""


def _o_de(peticion: Dict[str, Any]) -> Any:
    if not isinstance(peticion, dict):
        return None
    for k in ("contexto", "O_context", "o_context", "O", "enunciado_O"):
        v = peticion.get(k)
        if v is not None and str(v).strip():
            return v
    ent = peticion.get("entrada")
    if isinstance(ent, dict):
        for k in ("contexto", "O_context", "o_context"):
            v = ent.get(k)
            if v is not None and str(v).strip():
                return v
    return None


# ===============================================================
# OFICIO PÚBLICO
# ===============================================================

def extraer_conteos(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    texto + O_context → conteos para CA.operacional.

    Firmas:
        extraer_conteos(peticion: dict)
        extraer_conteos(texto: str)
        extraer_conteos(texto: str, o_context: str)
        extraer_conteos(descripcion=..., o_context=..., ...)

    Regla de base (simétrica C/L):
      1) Si hay adopción metodológica explícita → esa es la base de m.
      2) Si no, y hay proposiciones asertivas → esas forman m
         (mismo criterio que p; evita C=null en prosa factual evaluable).
      3) Si no hay unidades anclables → base_nula_C (C indefinido de verdad).

    Actos nunca entran en denominador.
    """
    peticion = _normalizar_entrada(*args, **kwargs)
    notas: List[str] = []

    texto = _texto_de(peticion)
    o_ctx = _o_de(peticion)

    unidades = _partir_unidades(str(texto))
    o_presente = bool(o_ctx and str(o_ctx).strip())
    o_tokens = _tokens(str(o_ctx)) if o_presente else set()

    proposiciones = [u for u in unidades if _es_proposicion(u)]
    adopciones = [u for u in unidades if _es_adopcion_metodologica(u)]

    # ----- C: base m + k ponderado -----
    # Prioridad AM-D2; fallback simétrico a L para no dejar C sin base
    # cuando el mensaje trae aserciones evaluables.
    if adopciones:
        compromisos = list(adopciones)
        notas.append("base_C: adopción metodológica explícita (AM-D2)")
    elif proposiciones:
        compromisos = list(proposiciones)
        notas.append(
            "base_C: proposiciones asertivas (fallback simétrico a L; "
            "sin señal metodológica explícita)"
        )
    else:
        compromisos = []

    compromisos_norm = [_norm(c) for c in compromisos]

    k = Fraction(0)
    k_detalle: List[Tuple[str, str]] = []

    for u in compromisos:
        w = _peso_contradiccion_en(u)
        if w > 0:
            k += w
            k_detalle.append((u, str(w)))

    for u in unidades:
        if _es_acto(u):
            w = _peso_acto_contra_compromiso(u, compromisos_norm)
            if w > 0:
                k += w
                k_detalle.append((u, str(w) + " (acto vs compromiso)"))

    m = len(compromisos)
    base_nula_C = m == 0

    # ----- L: posturas + r (misma lógica de fallback) -----
    if adopciones:
        posturas = list(adopciones)
    elif proposiciones:
        posturas = list(proposiciones)
    else:
        posturas = []

    r = Fraction(0)
    r_detalle: List[Tuple[str, str]] = []
    if "historial_posturas" in peticion and isinstance(peticion["historial_posturas"], list):
        prev = {_norm(x) for x in peticion["historial_posturas"] if x}
        for u in posturas:
            low = _norm(u)
            for pnorm in prev:
                if pnorm and pnorm in low and re.search(r"\bno\b", low):
                    r += PESO_TOTAL
                    r_detalle.append((u, "1 (reversión vs historial)"))
                    break

    p = len(posturas)
    base_nula_L = p == 0

    # ----- K: afirmaciones con Π + f ponderado -----
    afirmaciones = list(proposiciones)

    f = Fraction(0)
    f_detalle: List[Tuple[str, str]] = []
    if not o_presente:
        f = Fraction(len(afirmaciones), 1) if afirmaciones else Fraction(0)
        for a in afirmaciones:
            f_detalle.append((a, "1 (sin O_context)"))
        if afirmaciones:
            notas.append(
                "O_context ausente -> f saturado; K debe quedar UNDEFINED (Def-5.3.1)"
            )
    else:
        for a in afirmaciones:
            w = _divergencia_peso(a, o_tokens)
            if w > 0:
                f += w
                f_detalle.append((a, str(w)))

    c = len(afirmaciones)
    base_nula_K = c == 0

    if base_nula_C:
        notas.append("base_nula_C: m=0 (sin unidades anclables) -> C indefinido")
    if base_nula_L:
        notas.append("base_nula_L: p=0 -> L indefinido")
    if base_nula_K:
        notas.append("base_nula_K: c=0 -> K indefinido")
    if k > 0:
        notas.append("k ponderado={0} (retícula AM-D5)".format(str(k)))
    if r > 0:
        notas.append("r ponderado={0} (retícula AM-D5)".format(str(r)))
    if f > 0 and o_presente:
        notas.append("f ponderado={0} (retícula AM-D5)".format(str(f)))

    actos = [u for u in unidades if _es_acto(u)]
    if actos:
        notas.append(
            "actos excluidos del denominador (AM-D2): {0}".format(len(actos))
        )

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
        "base_nula_C": base_nula_C,
        "base_nula_L": base_nula_L,
        "base_nula_K": base_nula_K,
        "o_presente": o_presente,
        "k_detalle": k_detalle,
        "r_detalle": r_detalle,
        "f_detalle": f_detalle,
        "metodo_sugerido": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def inyectar_en_peticion(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Copia de la petición con conteos insertados.
    No calcula C/L/K; solo prepara material para CA.calcular.
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
        "base_nula_C": conteos["base_nula_C"],
        "base_nula_L": conteos["base_nula_L"],
        "base_nula_K": conteos["base_nula_K"],
        "o_presente": conteos["o_presente"],
        "k_detalle": conteos["k_detalle"],
        "r_detalle": conteos["r_detalle"],
        "f_detalle": conteos["f_detalle"],
        "version": conteos["version"],
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
    "VERSION",
    "PESO_ROCE",
    "PESO_PARCIAL",
    "PESO_GRAVE",
    "PESO_TOTAL",
    "RETICULA",
]
