"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales con anclas de medición (AM v1.0).

Versión: 2.0
Cambio principal respecto a 1.x:
  - Ancla de inclusión (AM-D2 / D3 / D4): solo entra en m/p/c lo que el
    mensaje adopta como propio. Actos ("propongo…") no inflan el denominador.
  - Retícula de severidad (AM-D5): k, r, f son sumas de pesos
    {1/4, 1/2, 3/4, 1}, no solo enteros binarios.
  - Base nula (AM-D6 / AM-A3): m=0 / p=0 / c=0 no se maquilla como 1;
    se señala para que C/L/K devuelvan UNDEFINED.
  - Ortogonalidad de origen (AM-A4): un mismo evento causal no inventa
    orígenes múltiples; puede derivar efectos en más de un factor.

Oficio único:
    texto + O_context  ->  {
        compromisos, contradicciones,   # m, k  (C = 1 - k/m)
        posturas, reversiones,          # p, r  (L = 1 - r/p)
        afirmaciones, afirmaciones_falsas  # c, f  (K = 1 - f/c)
    }

No calcula C, L, K.
No calcula Tru.
No inventa factores.
Solo materializa los conteos que la ruta operacional de CA exige,
ahora bajo anclas declaradas y reproducibles.

Referencias:
  AM-D1..D6, AM-A1..A5, AM-T1 (anclas_medicion_AX)
  Def 5.1–5.3, Def-5.3.1, PROTOCOLO sec. 0.15
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple


# ===============================================================
# CONSTANTES — Retícula de severidad (AM-D5)
# ===============================================================
PESO_ROCE    = Fraction(1, 4)   # 0.25  toca sin romper
PESO_PARCIAL = Fraction(1, 2)   # 0.50  rompe parte
PESO_GRAVE   = Fraction(3, 4)   # 0.75  rompe casi todo
PESO_TOTAL   = Fraction(1, 1)   # 1.00  anula

RETICULA = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)

VERSION = "2.0"


# ===============================================================
# PATRONES DETERMINISTAS (sin modelo, sin estocástico)
# ===============================================================

# Contradicción interna (aporta a k). Orden: más grave primero.
_PATRONES_CONTRADICCION: Tuple[Tuple[str, Fraction], ...] = (
    (r"\by\s+no\b",           PESO_TOTAL),
    (r"\bpero\s+no\b",        PESO_TOTAL),
    (r"\bes\b.+\bno\s+es\b",  PESO_TOTAL),
    (r"\bno\s+es\b.+\bes\b",  PESO_TOTAL),
    (r"\bsin\s+embargo\b",    PESO_GRAVE),
    (r"\bno\s+obstante\b",    PESO_GRAVE),
    (r"\baunque\b",           PESO_PARCIAL),
    (r"\bmas\s+no\b",         PESO_PARCIAL),
)

# Señales de ADOPCIÓN PROPIA → pueden entrar en m / p / c (AM-D2)
_SENALES_ADOPCION = (
    r"\bno\s+invento\b",
    r"\bno\s+decido\b",
    r"\bno\s+salgo\b",
    r"\bmantengo\b",
    r"\bafirmo\b",
    r"\bme\s+comprometo\b",
    r"\bestablezco\b",
    r"\badopto\b",
    r"\bproh[ií]bo\b",
    r"\bobligo\b",
    r"\bqueda\s+fijado\b",
    r"\bes\s+un\s+hecho\b",
    r"\bno\s+modifico\b",
    r"\bno\s+tomo\s+decisiones\b",
    r"\bsoy\s+determinista\b",
)

# Señales de ACTO (no entran en denominador; pueden aportar a numerador)
_SENALES_ACTO = (
    r"\bpropongo\b",
    r"\bintroduzcamos\b",
    r"\bpodr[ií]amos\b",
    r"\bsugerir[ií]a\b",
    r"\bte\s+invito\b",
    r"\bvamos\s+a\s+llamar\b",
    r"\bintroduzco\b",
    r"\bcreo\s+el\s+s[ií]mbolo\b",
    r"\binvento\b",
)

_SEPARADORES = re.compile(r"[.;:\n]+|\by\s+(?=[A-ZÁÉÍÓÚ])")

_STOP = {
    "el", "la", "los", "las", "un", "una", "de", "del",
    "en", "y", "o", "a", "que", "es", "se", "por", "con",
    "al", "lo", "su", "sus", "mi", "tu",
}


# ===============================================================
# HELPERS
# ===============================================================

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _partir_unidades(texto: str) -> List[str]:
    """Parte el texto en unidades candidatas."""
    if not texto or not str(texto).strip():
        return []
    partes = _SEPARADORES.split(str(texto))
    return [p.strip() for p in partes if p and p.strip()]


def _es_adopcion_propia(unidad: str) -> bool:
    """
    AM-D2: True solo si la unidad adopta algo como propio
    (afirmación, obligación, autoatribución, compromiso metodológico).
    """
    low = _norm(unidad)
    if not low:
        return False
    # Si es claramente un acto, no es adopción
    for pat in _SENALES_ACTO:
        if re.search(pat, low):
            return False
    # Señales positivas de adopción
    for pat in _SENALES_ADOPCION:
        if re.search(pat, low):
            return True
    # Afirmación factual simple (contiene verbo copulativo o predicación)
    # Criterio mínimo determinista: no empieza por acto y tiene contenido
    if len(low.split()) >= 2 and not low.startswith(("si ", "cuando ", "aunque ")):
        # Heurística conservadora: exigir señal explícita o forma asertiva corta
        # Para no inflar m, preferimos señal explícita.
        # Las afirmaciones factuales puras ("el sol irradia") entran por
        # la vía de afirmaciones (c), no necesariamente como compromiso (m).
        return False
    return False


def _es_acto(unidad: str) -> bool:
    """True si la unidad es un acto/propuesta (no entra en m)."""
    low = _norm(unidad)
    for pat in _SENALES_ACTO:
        if re.search(pat, low):
            return True
    return False


def _peso_contradiccion_en(unidad: str) -> Fraction:
    """
    AM-D5: devuelve el peso de retícula de la contradicción más grave
    presente en la unidad, o 0 si no hay.
    """
    low = _norm(unidad)
    for pat, peso in _PATRONES_CONTRADICCION:
        if re.search(pat, low):
            return peso
    return Fraction(0)


def _peso_acto_contra_compromiso(acto: str, compromisos_norm: List[str]) -> Fraction:
    """
    Si un acto contradice un compromiso metodológico previo
    (p. ej. 'no invento' + 'propongo Σ'), aporta peso a k (y luego a f).
    """
    low = _norm(acto)
    if not _es_acto(acto):
        return Fraction(0)
    # ¿Hay compromiso de no inventar / no decidir / no salir?
    hay_no_invento = any(
        re.search(r"\bno\s+invento\b|\bno\s+decido\b|\bno\s+salgo\b|\bno\s+modifico\b", c)
        for c in compromisos_norm
    )
    if not hay_no_invento:
        return Fraction(0)
    # El acto de introducir/proponer bajo 'no invento' es grave
    if re.search(r"\bpropongo\b|\bintroduzco\b|\bintroduzcamos\b|\binvento\b|\bcreo\s+el\s+s[ií]mbolo\b", low):
        return PESO_GRAVE
    return PESO_PARCIAL


def _tokens(s: str) -> set:
    return set(re.findall(r"[a-záéíóúñ0-9/]+", _norm(s))) - _STOP


def _divergencia_peso(afirmacion: str, o_tokens: set) -> Fraction:
    """
    AM-D5 aplicado a K:
      - sin ancla en O → PESO_TOTAL
      - ancla parcial (pocos tokens en común) → PESO_PARCIAL / GRAVE
      - ancla clara → 0
    """
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
        return Fraction(0)          # correspondencia suficiente
    if ratio >= Fraction(1, 4):
        return PESO_PARCIAL
    return PESO_GRAVE


# ===============================================================
# OFICIO PÚBLICO
# ===============================================================

def extraer_conteos(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Transforma texto + O_context en los conteos que CA.operacional espera,
    bajo anclas de medición AM v1.0.

    Salida (claves que CA consume):
        compromisos          : List[str]   (solo adopción propia)
        contradicciones      : Fraction    (k = suma de pesos)
        posturas             : List[str]
        reversiones          : Fraction    (r)
        afirmaciones         : List[str]
        afirmaciones_falsas  : Fraction    (f = suma de pesos)

    Meta:
        m, p, c              : int
        base_nula_C/L/K      : bool
        o_presente           : bool
        k_detalle, f_detalle : listas de (unidad, peso) para auditoría
        version              : str
        notas                : List[str]
    """
    peticion = dict(peticion or {})
    notas: List[str] = []

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
    o_presente = bool(o_ctx and str(o_ctx).strip())
    o_tokens = _tokens(str(o_ctx)) if o_presente else set()

    # ----- C: compromisos (AM-D2) + k ponderado (AM-D5) -----
    compromisos = [u for u in unidades if _es_adopcion_propia(u)]
    compromisos_norm = [_norm(c) for c in compromisos]

    k = Fraction(0)
    k_detalle: List[Tuple[str, str]] = []

    for u in compromisos:
        w = _peso_contradiccion_en(u)
        if w > 0:
            k += w
            k_detalle.append((u, str(w)))

    # Actos que contradicen compromisos metodológicos → aportan a k (no a m)
    for u in unidades:
        if _es_acto(u):
            w = _peso_acto_contra_compromiso(u, compromisos_norm)
            if w > 0:
                k += w
                k_detalle.append((u, str(w) + " (acto vs compromiso)"))

    m = len(compromisos)
    base_nula_C = m == 0

    # ----- L: posturas + r -----
    # En un solo turno sin historial, posturas = unidades con adopción
    # o afirmaciones asertivas; r = 0 salvo historial explícito.
    posturas = list(compromisos) if compromisos else []
    # Si no hubo compromisos pero hay unidades asertivas, usarlas como posturas
    if not posturas and unidades:
        posturas = [u for u in unidades if not _es_acto(u)]

    r = Fraction(0)
    if "historial_posturas" in peticion and isinstance(peticion["historial_posturas"], list):
        prev = {_norm(x) for x in peticion["historial_posturas"]}
        for u in posturas:
            # Reversión simple: postura actual niega una previa (patrón "no" + token previo)
            # Criterio mínimo determinista; se puede endurecer después.
            low = _norm(u)
            for pnorm in prev:
                if pnorm and pnorm in low and re.search(r"\bno\b", low):
                    r += PESO_TOTAL
                    break

    p = len(posturas)
    base_nula_L = p == 0

    # ----- K: afirmaciones + f ponderado -----
    # Afirmaciones = unidades que no son puro acto (o todas si se quiere
    # medir correspondencia también de propuestas). Criterio: contenido
    # verificable respecto de O.
    afirmaciones = [u for u in unidades if not _es_acto(u)] or list(unidades)

    f = Fraction(0)
    f_detalle: List[Tuple[str, str]] = []
    if not o_presente:
        # Sin O: cada afirmación cuenta como divergencia total (K caerá a UNDEFINED en CA)
        f = Fraction(len(afirmaciones), 1) if afirmaciones else Fraction(0)
        for a in afirmaciones:
            f_detalle.append((a, "1 (sin O_context)"))
        notas.append("O_context ausente -> f saturado; K debe quedar UNDEFINED (Def-5.3.1)")
    else:
        for a in afirmaciones:
            w = _divergencia_peso(a, o_tokens)
            if w > 0:
                f += w
                f_detalle.append((a, str(w)))

    c = len(afirmaciones)
    base_nula_K = c == 0

    # ----- Notas de anclas -----
    if base_nula_C:
        notas.append("base_nula_C: m=0 tras ancla de inclusión (AM-D6) -> C indefinido")
    if base_nula_L:
        notas.append("base_nula_L: p=0 -> L indefinido")
    if base_nula_K:
        notas.append("base_nula_K: c=0 -> K indefinido")
    if k > 0:
        notas.append("k ponderado={0} (retícula AM-D5)".format(str(k)))
    if f > 0 and o_presente:
        notas.append("f ponderado={0} (retícula AM-D5)".format(str(f)))
    actos = [u for u in unidades if _es_acto(u)]
    if actos:
        notas.append(
            "actos excluidos del denominador (AM-D2): {0}".format(len(actos))
        )

    return {
        # Claves que CA consume (contradicciones/reversiones/afirmaciones_falsas
        # ahora pueden ser Fraction; CA/Fraction ya lo soportan)
        "compromisos": compromisos,
        "contradicciones": k,
        "posturas": posturas,
        "reversiones": r,
        "afirmaciones": afirmaciones,
        "afirmaciones_falsas": f,
        # Meta
        "m": m,
        "p": p,
        "c": c,
        "base_nula_C": base_nula_C,
        "base_nula_L": base_nula_L,
        "base_nula_K": base_nula_K,
        "o_presente": o_presente,
        "k_detalle": k_detalle,
        "f_detalle": f_detalle,
        "metodo_sugerido": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def inyectar_en_peticion(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Copia de la petición con los conteos ya insertados.
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
        "base_nula_C": conteos["base_nula_C"],
        "base_nula_L": conteos["base_nula_L"],
        "base_nula_K": conteos["base_nula_K"],
        "o_presente": conteos["o_presente"],
        "k_detalle": conteos["k_detalle"],
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
