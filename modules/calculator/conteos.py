"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales con anclas de medición (AM v1.0).

Versión: 2.1
Cambios principales respecto a 2.0:
  - Priorización del léxico de dominio sobre el diccionario de stopwords.
  - Detección mejorada de contradicciones semánticas básicas.
  - Pesos dinámicos para compromisos metodológicos.
  - Validación de axiomas en los conteos.
  - Auditoría detallada con razones para k, r, f.

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
bajo anclas declaradas y reproducibles.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union

# ===============================================================
# CONSTANTES — Retícula de severidad (AM-D5)
# ===============================================================
PESO_ROCE = Fraction(1, 4)   # 0.25  toca sin romper
PESO_PARCIAL = Fraction(1, 2)   # 0.50  rompe parte
PESO_GRAVE = Fraction(3, 4)   # 0.75  rompe casi todo
PESO_TOTAL = Fraction(1, 1)   # 1.00  anula

RETICULA = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)

VERSION = "2.1"

# ===============================================================
# PATRONES DETERMINISTAS (sin modelo, sin estocástico)
# ===============================================================

# Contradicción interna (aporta a k). Orden: más grave primero.
_PATRONES_CONTRADICCION: Tuple[Tuple[str, Fraction], ...] = (
    (r"\by\s+no\b", PESO_TOTAL),
    (r"\bpero\s+no\b", PESO_TOTAL),
    (r"\bes\b.+\bno\s+es\b", PESO_TOTAL),
    (r"\bno\s+es\b.+\bes\b", PESO_TOTAL),
    (r"\bsí\s+y\s+no\b", PESO_TOTAL),
    (r"\bno\s+y\s+sí\b", PESO_TOTAL),
    (r"\bsin\s+embargo\b", PESO_GRAVE),
    (r"\bno\s+obstante\b", PESO_GRAVE),
    (r"\bpor\s+un\s+lado\b.+\bpor\s+(?:el\s+)?otro\b", PESO_GRAVE),
    (r"\baunque\b", PESO_PARCIAL),
    (r"\bmas\s+no\b", PESO_PARCIAL),
    (r"\bsin\s+dejar\s+de\b", PESO_PARCIAL),
)

# Antónimos básicos para detección semántica de contradicciones
_ANTONIMOS = {
    "verdad": ["mentira", "falso"],
    "afirmo": ["niego", "rechazo"],
    "existe": ["no existe", "carece"],
    "comprometo": ["rompo", "incumplo"],
    "adopto": ["rechazo", "descarto"],
}

# Señales de ADOPCIÓN PROPIA → pueden entrar en m / p (AM-D2)
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

# Señales de ACTO (no entran en denominador; pueden aportar a numerador k)
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

# Unidades que no son proposiciones con Π reconocible (AF-C4 / AF-T8)
_SENALES_NO_PROPOSICION = (
    r"^\s*(?:si|cuando|aunque|mientras|donde|como)\b",
    r"\?\s*$",
    r"^\s*(?:¿|¡)",
)

_SEPARADORES = re.compile(
    r"[.;:!?\n]+|"
    r"\by\s+(?=[A-ZÁÉÍÓÚ¿¡])|"  # solo mayúscula (inicio de unidad)
    r"\b(?:además|asimismo|por\s+otra\s+parte|Además|Asimismo)\b",
)

# ===============================================================
# DICCIONARIO REAL DE STOPWORDS (español) — cargado en módulo
# ===============================================================
_DICCIONARIO_STOP: frozenset = frozenset({
    # artículos / determinantes
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "lo", "al", "del",
    # preposiciones
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para",
    "por", "según", "sin", "so", "sobre", "tras", "versus", "vía",
    # conjunciones
    "y", "e", "ni", "o", "u", "pero", "sino", "aunque", "porque",
    "pues", "que", "si", "como", "cuando", "mientras", "donde",
    "además", "asimismo", "también", "tampoco",
    # pronombres
    "yo", "tú", "ella", "nosotros", "nosotras", "vosotros",
    "vosotras", "ellos", "ellas", "usted", "ustedes",
    "me", "te", "se", "nos", "os", "le", "les",
    "mi", "tu", "su", "mis", "tus", "sus", "nuestro", "nuestra",
    "nuestros", "nuestras", "vuestro", "vuestra",
    "mío", "mía", "tuyo", "tuya", "suyo", "suya",
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas",
    "aquel", "aquella", "aquellos", "aquellas",
    "esto", "eso", "aquello", "quién", "quiénes", "cual", "cuales",
    "cuyo", "cuya", "cuyos", "cuyas", "cuánto", "cuánta",
    # verbos auxiliares / copulativos de alta frecuencia
    "ser", "estar", "haber", "tener", "ir", "hacer",
    "es", "son", "era", "eran", "fue", "fueron", "será", "serán",
    "está", "están", "estaba", "estaban", "estuvo", "estuvieron",
    "ha", "han", "había", "habían", "hubo", "habrá",
    "tiene", "tienen", "tenía", "tenían",
    "hay",
    # adverbios y partículas frecuentes
    "no", "sí", "ya", "aún", "todavía", "siempre", "nunca", "jamás",
    "más", "menos", "muy", "mucho", "muchos", "muchas", "poco",
    "pocos", "pocas", "todo", "todos", "todas", "nada", "algo",
    "alguien", "nadie", "cada", "cualquier", "cualquiera",
    "aquí", "allí", "ahí", "acá", "allá", "ahora", "después",
    "antes", "luego", "entonces", "así", "bien", "mal",
    "solo", "sólo", "solamente", "apenas", "casi", "tan", "tanto",
    # otros funcionales
    "etc", "etcétera", "vs",
})

# Alias de solo lectura
_STOP = _DICCIONARIO_STOP

# ===============================================================
# HELPERS
# ===============================================================

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def _partir_unidades(texto: str) -> List[str]:
    """Parte el texto en unidades candidatas (determinista)."""
    if not texto or not str(texto).strip():
        return []
    partes = _SEPARADORES.split(str(texto))
    return [p.strip() for p in partes if p and p.strip()]

def _es_acto(unidad: str) -> bool:
    """True si la unidad es un acto/propuesta (no entra en m ni, por defecto, en c)."""
    low = _norm(unidad)
    for pat in _SENALES_ACTO:
        if re.search(pat, low):
            return True
    return False

def _es_adopcion_propia(unidad: str) -> bool:
    """
    AM-D2: True solo si la unidad adopta algo como propio
    (compromiso metodológico, autoatribución, obligación, afirmación adoptada).
    """
    low = _norm(unidad)
    if not low:
        return False
    for pat in _SENALES_ADOPCION:
        if re.search(pat, low):
            return True
    if _es_acto(unidad):
        return False
    return False

def _detectar_contradiccion_semantica(unidad: str) -> Fraction:
    """
    Detecta contradicciones semánticas básicas usando el diccionario de antónimos.
    """
    low = _norm(unidad)
    for palabra, antonimos in _ANTONIMOS.items():
        if palabra in low:
            for antonimo in antonimos:
                if antonimo in low:
                    return PESO_TOTAL
    return Fraction(0)

def _es_proposicion(unidad: str) -> bool:
    """
    Aproximación determinista a AF-C4 / AF-T8:
    tiene forma asertiva con Π potencialmente reconocible.
    Excluye actos puros, preguntas y condicionantes puros.
    Acepta aserciones cortas con contenido simbólico/numérico.
    """
    low = _norm(unidad)
    if not low:
        return False
    if _es_acto(unidad):
        return False
    for pat in _SENALES_NO_PROPOSICION:
        if re.search(pat, low):
            return False
    # Contenido mínimo: ≥2 tokens léxicos, o presencia de dígito/operador/símbolo
    toks = low.split()
    if len(toks) >= 2:
        return True
    if re.search(r"[0-9=+\-*/^ββα]", low):
        return True
    return False

def _peso_contradiccion_en(unidad: str, es_compromiso: bool = False) -> Fraction:
    """
    AM-D5: devuelve el peso de retícula de la contradicción más grave
    presente en la unidad, o 0 si no hay.
    Si es_compromiso=True, aplica PESO_TOTAL para cualquier contradicción.
    """
    low = _norm(unidad)
    for pat, peso in _PATRONES_CONTRADICCION:
        if re.search(pat, low):
            return PESO_TOTAL if es_compromiso else peso
    return _detectar_contradiccion_semantica(unidad)

def _peso_acto_contra_compromiso(acto: str, compromisos_norm: List[str]) -> Fraction:
    """
    Si un acto contradice un compromiso metodológico previo,
    aporta peso a k.
    """
    low = _norm(acto)
    if not _es_acto(acto):
        return Fraction(0)
    hay_restriccion = any(
        re.search(
            r"\bno\s+invento\b|\bno\s+decido\b|\bno\s+salgo\b|"
            r"\bno\s+modifico\b|\bno\s+altero\b|\bno\s+tomo\s+decisiones\b",
            c,
        )
        for c in compromisos_norm
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

def _tokens(s: str, lexico_extra: Optional[set] = None) -> set:
    """
    Extrae tokens léxicos restando el diccionario real de stopwords.
    Si se inyecta lexico_extra (términos de dominio / O), esos términos
    se preservan aunque coincidan con stop.
    """
    toks = set(re.findall(r"[a-záéíóúñ0-9/ββα]+", _norm(s)))
    if lexico_extra:
        # Preservar términos de dominio aunque sean stopwords
        toks_extra = {t.lower() for t in lexico_extra}
        toks |= toks_extra
    return toks - _STOP

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
    if len(o_tokens) < 3:  # O muy pequeño
        return PESO_GRAVE
    if ratio >= Fraction(2, 3):  # Umbral más estricto
        return Fraction(0)
    if ratio >= Fraction(1, 3):
        return PESO_PARCIAL
    return PESO_GRAVE

def _normalizar_entrada(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Acepta de forma tolerante:
      - extraer_conteos(peticion_dict)
      - extraer_conteos(texto)
      - extraer_conteos(texto, o_context)
      - extraer_conteos(descripcion=..., o_context=..., mensaje=..., ...)
    y produce un dict unificado.
    """
    base: Dict[str, Any] = {}

    if len(args) == 1 and isinstance(args[0], dict):
        base.update(args[0])
    elif len(args) >= 1:
        base["texto"] = args[0]
        if len(args) >= 2 and args[1] is not None:
            base["o_context"] = args[1]
    base.update({k: v for k, v in kwargs.items() if v is not None})
    return base

def _validar_axiomas(conteos: Dict[str, Any]) -> List[str]:
    """
    Valida que los conteos cumplan con los axiomas de VPSI-TRUTH.
    """
    errores = []
    m, k = conteos["m"], conteos["contradicciones"]
    if m > 0 and k > m * PESO_TOTAL:
        errores.append(f"k ({k}) > m * PESO_TOTAL ({m * PESO_TOTAL})")
    p, r = conteos["p"], conteos["reversiones"]
    if p > 0 and r > p * PESO_TOTAL:
        errores.append(f"r ({r}) > p * PESO_TOTAL ({p * PESO_TOTAL})")
    c, f = conteos["c"], conteos["afirmaciones_falsas"]
    if c > 0 and f > c * PESO_TOTAL:
        errores.append(f"f ({f}) > c * PESO_TOTAL ({c * PESO_TOTAL})")
    return errores

# ===============================================================
# OFICIO PÚBLICO
# ===============================================================

def extraer_conteos(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Transforma texto + O_context en los conteos que CA.operacional espera,
    bajo anclas de medición AM v1.0 y filtro AF-C4.

    Firmas admitidas (compatibilidad con pipeline y tests):
        extraer_conteos(peticion: dict)
        extraer_conteos(texto: str)
        extraer_conteos(texto: str, o_context: str)
        extraer_conteos(descripcion=..., o_context=..., mensaje=..., ...)

    Salida (claves que CA consume):
        compromisos          : List[str]   (solo adopción propia)
        contradicciones      : Fraction    (k = suma de pesos)
        posturas             : List[str]
        reversiones          : Fraction    (r)
        afirmaciones         : List[str]   (solo proposiciones con Π)
        afirmaciones_falsas  : Fraction    (f = suma de pesos)

    Meta:
        m, p, c              : int
        base_nula_C/L/K      : bool
        o_presente           : bool
        k_detalle, r_detalle, f_detalle : listas de (unidad, peso, razón)
        diccionario_stop_size, lexico_dominio_size : int
        version              : str
        notas                : List[str]
        estado               : Dict[str, str]  # {"C": "OK"|"UNDEFINED", ...}
    """
    peticion = _normalizar_entrada(*args, **kwargs)
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
        or peticion.get("O")
    )

    unidades = _partir_unidades(str(texto))
    o_presente = bool(o_ctx and str(o_ctx).strip())

    # Léxico de dominio opcional (diccionario real inyectado por la petición)
    lexico_raw = (
        peticion.get("diccionario")
        or peticion.get("lexico")
        or peticion.get("vocabulario")
        or peticion.get("terminos_O")
    )
    lexico_extra: set = set()
    if lexico_raw:
        if isinstance(lexico_raw, (set, frozenset, list, tuple)):
            lexico_extra = {_norm(str(t)) for t in lexico_raw if t}
        elif isinstance(lexico_raw, str):
            lexico_extra = _tokens(lexico_raw)

    o_tokens = _tokens(str(o_ctx), lexico_extra) if o_presente else set()
    if lexico_extra:
        o_tokens |= lexico_extra

    # ----- C: compromisos (AM-D2) + k ponderado (AM-D5) -----
    compromisos = [u for u in unidades if _es_adopcion_propia(u)]
    compromisos_norm = [_norm(c) for c in compromisos]

    k = Fraction(0)
    k_detalle: List[Tuple[str, str, str]] = []

    for u in compromisos:
        w = _peso_contradiccion_en(u, es_compromiso=True)
        if w > 0:
            k += w
            k_detalle.append((u, str(w), "contradicción en compromiso"))

    # Actos que contradicen compromisos metodológicos → aportan a k (no a m)
    for u in unidades:
        if _es_acto(u):
            w = _peso_acto_contra_compromiso(u, compromisos_norm)
            if w > 0:
                k += w
                k_detalle.append((u, str(w), "acto vs compromiso"))

    m = len(compromisos)
    base_nula_C = m == 0

    # ----- L: posturas + r -----
    posturas = list(compromisos) if compromisos else [
        u for u in unidades if _es_proposicion(u)
    ]

    r = Fraction(0)
    r_detalle: List[Tuple[str, str, str]] = []
    if "historial_posturas" in peticion and isinstance(peticion["historial_posturas"], list):
        prev = {_norm(x) for x in peticion["historial_posturas"] if x}
        for u in posturas:
            low = _norm(u)
            for pnorm in prev:
                if pnorm and pnorm in low and re.search(r"\bno\b", low):
                    r += PESO_TOTAL
                    r_detalle.append((u, "1", f"reversión vs historial: '{pnorm}' → '{low}'"))
                    break

    p = len(posturas)
    base_nula_L = p == 0

    # ----- K: afirmaciones con Π (AF-C4) + f ponderado (AM-D5) -----
    afirmaciones = [u for u in unidades if _es_proposicion(u)]

    f = Fraction(0)
    f_detalle: List[Tuple[str, str, str]] = []
    if not o_presente:
        f = Fraction(len(afirmaciones), 1) if afirmaciones else Fraction(0)
        for a in afirmaciones:
            f_detalle.append((a, "1", "sin O_context"))
        if afirmaciones:
            notas.append(
                "O_context ausente -> f saturado; K debe quedar UNDEFINED (Def-5.3.1)"
            )
    else:
        for a in afirmaciones:
            w = _divergencia_peso(a, o_tokens)
            if w > 0:
                f += w
                inter = _tokens(a) & o_tokens
                f_detalle.append((a, str(w), f"divergencia con O: {inter} tokens en común"))

    c = len(afirmaciones)
    base_nula_K = c == 0

    # ----- Validación de axiomas -----
    axioma_errors = _validar_axiomas({
        "m": m, "contradicciones": k,
        "p": p, "reversiones": r,
        "c": c, "afirmaciones_falsas": f
    })
    if axioma_errors:
        notas.extend([f"ERROR AXIOMÁTICO: {e}" for e in axioma_errors])

    # ----- Notas de anclas -----
    if base_nula_C:
        notas.append("base_nula_C: m=0 tras ancla de inclusión (AM-D6) -> C indefinido")
    if base_nula_L:
        notas.append("base_nula_L: p=0 -> L indefinido")
    if base_nula_K:
        notas.append("base_nula_K: c=0 -> K indefinido")
    if k > 0:
        notas.append(f"k ponderado={k} (retícula AM-D5)")
    if r > 0:
        notas.append(f"r ponderado={r} (retícula AM-D5)")
    if f > 0 and o_presente:
        notas.append(f"f ponderado={f} (retícula AM-D5)")
    actos = [u for u in unidades if _es_acto(u)]
    if actos:
        notas.append(f"actos excluidos del denominador (AM-D2): {len(actos)}")
    no_prop = [u for u in unidades if not _es_proposicion(u) and not _es_acto(u)]
    if no_prop:
        notas.append(f"unidades fuera de c por filtro AF-C4 (no proposición): {len(no_prop)}")
    if lexico_extra:
        notas.append(f"diccionario de dominio inyectado: {len(lexico_extra)} términos")
    notas.append(f"diccionario_stop cargado: {len(_DICCIONARIO_STOP)} entradas")

    # Estado explícito para C, L, K
    estado = {
        "C": "UNDEFINED" if base_nula_C else "OK",
        "L": "UNDEFINED" if base_nula_L else "OK",
        "K": "UNDEFINED" if base_nula_K or not o_presente else "OK"
    }

    return {
        # Claves que CA consume
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
        "r_detalle": r_detalle,
        "f_detalle": f_detalle,
        "diccionario_stop_size": len(_DICCIONARIO_STOP),
        "lexico_dominio_size": len(lexico_extra),
        "metodo_sugerido": "operacional",
        "version": VERSION,
        "notas": notas,
        "estado": estado,
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
        "r_detalle": conteos["r_detalle"],
        "f_detalle": conteos["f_detalle"],
        "diccionario_stop_size": conteos["diccionario_stop_size"],
        "lexico_dominio_size": conteos["lexico_dominio_size"],
        "version": conteos["version"],
        "notas": conteos["notas"],
        "estado": conteos["estado"],
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
    "_DICCIONARIO_STOP",
]
