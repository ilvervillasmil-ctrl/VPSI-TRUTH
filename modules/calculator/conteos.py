"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales.

Version: 3.4.0

Oficio unico:
    texto + O_context  ->  {
        compromisos, contradicciones,      # m, k  (C = 1 - k/m)
        posturas, reversiones,             # p, r  (L = 1 - r/p)
        afirmaciones, afirmaciones_falsas  # c, f  (K = 1 - f/c)
    }

No calcula C, L, K. No calcula Tru. No inventa factores.
Sin componentes estocasticos: solo patrones fijos y aritmetica exacta.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

VERSION = "3.4.0"

# ===============================================================
# SEGMENTO 1 --- RETICULA DE SEVERIDAD Y ESCALA ARMONICA EXACTA
# =================================================PathComponent
PESO_ROCE    = Fraction(1, 4)   # 0.25
PESO_PARCIAL = Fraction(1, 2)   # 0.50
PESO_GRAVE   = Fraction(3, 4)   # 0.75
PESO_TOTAL   = Fraction(1, 1)   # 1.00

RETICULA = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)


def nombre_reticula(peso: Fraction) -> str:
    """Nombra la severidad de un peso continuo sin alterarlo."""
    if peso <= Fraction(0):
        return "nulo"
    if peso <= PESO_ROCE:
        return "roce"
    if peso <= PESO_PARCIAL:
        return "parcial"
    if peso <= PESO_GRAVE:
        return "grave"
    return "total"


def _peso_armonico(ratio: Fraction) -> Fraction:
    """
    Aplica estrictamente la escala armónica exacta basada en fracciones (1/x)
    para ponderar la divergencia de forma visible y matemáticamente pura.
    """
    if ratio >= Fraction(3, 5):  # Convergencia alta (>= 60% solape): sin penalización
        return Fraction(0)
    
    # Calculamos la divergencia d = 1 - ratio (de 0 a 1)
    d = Fraction(1) - ratio
    if d <= Fraction(0):
        return Fraction(0)
    
    # Mapeo directo a los pesos armónicos exactos definidos por la escala (1/x):
    # - Divergencia leve      -> 1/9     (Fraction(1, 9)     = ~0.111)
    # - Divergencia moderada  -> 1/1.53  (Fraction(100, 153) = ~0.654)
    # - Divergencia profunda  -> 1/1.31  (Fraction(100, 131) = ~0.763)
    # - Divergencia crítica   -> 1/1.01  (Fraction(100, 101) = ~0.990)
    # - Divergencia total     -> 1/1     (Fraction(1, 1)     =  1.000)
    
    if d <= Fraction(1, 4):
        return Fraction(1, 9)
    elif d <= Fraction(1, 2):
        return Fraction(100, 153)
    elif d <= Fraction(3, 4):
        return Fraction(100, 131)
    elif d < Fraction(1, 1):
        return Fraction(100, 101)
    else:
        return Fraction(1, 1)


# ===============================================================
# SEGMENTO 2 --- PATRONES DETERMINISTAS (CALIBRADOS)
# ===============================================================

_PATRONES_CONTRADICCION: Tuple[Tuple[str, Fraction], ...] = (
    (r"\by\s+no\b",                 PESO_TOTAL),
    (r"\bpero\s+no\b",              PESO_TOTAL),
    (r"\bes\b.+\bno\s+es\b",        PESO_TOTAL),
    (r"\bno\s+es\b.+\bes\b",        PESO_TOTAL),
    (r"\bs[ií]\s+y\s+no\b",         PESO_TOTAL),
    (r"\bno\s+y\s+s[ií]\b",         PESO_TOTAL),
    (r"\bsin\s+embargo\b",          PESO_PARCIAL),
    (r"\bno\s+obstante\b",          PESO_PARCIAL),
    (r"\bpor\s+un\s+lado\b.+\bpor\s+(?:el\s+)?otro\b", PESO_PARCIAL),
    (r"\baunque\b",                 PESO_ROCE),
    (r"\bmas\s+no\b",               PESO_PARCIAL),
    (r"\bsin\s+dejar\s+de\b",       PESO_ROCE),
)

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

_ACTO_CONTRA_COMPROMISO = re.compile(
    r"\bpropongo\b|\bpropongamos\b|\bintroduzco\b|\bintroduzcamos\b|"
    r"\binvento\b|\bcreo\s+el\s+s[ií]mbolo\b|\bdefinamos\b|\bplanteo\b"
)

_RESTRICCION = re.compile(
    r"\bno\s+invento\b|\bno\s+decido\b|\bno\s+salgo\b|"
    r"\bno\s+modifico\b|\bno\s+altero\b|\bno\s+tomo\s+decisiones\b"
)

_NEGACION = re.compile(r"\bno\b|\bnunca\b|\bjam[aá]s\b|\btampoco\b")

_SEPARADORES = re.compile(
    r"[.;:!?\n]+|"
    r",\s*|"
    r"\s+(?:pero|porque|aunque|mientras|sino|pues)\s+|"
    r"\by\s+(?=[A-ZÁÉÍÓÚ¿¡])|"
    r"\b(?:además|asimismo|por\s+otra\s+parte)\b",
    re.IGNORECASE,
)

_TOKEN = re.compile(r"[a-záéíóúüñ0-9/αβ]+")
_SIMBOLICO = re.compile(r"[0-9=+\-*/^αβ]")

_MIN_TOKENS_UNIDAD = 2
_UMBRAL_SOLAPE_REVERSION = Fraction(1, 4)


# ===============================================================
# SEGMENTO 3 --- STOPWORDS (es) Y REFERENCIAS LÉXICAS
# ===============================================================

_DICCIONARIO_STOP: frozenset = frozenset({
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "lo", "al", "del",
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde",
    "durante", "en", "entre", "hacia", "hasta", "mediante", "para",
    "por", "según", "sin", "so", "sobre", "tras", "versus", "vía",
    "y", "e", "ni", "o", "u", "pero", "sino", "aunque", "porque",
    "pues", "que", "si", "como", "cuando", "mientras", "donde",
    "además", "asimismo", "también", "tampoco",
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
    "ser", "estar", "haber", "tener", "ir", "hacer",
    "es", "son", "era", "eran", "fue", "fueron", "será", "serán",
    "está", "están", "estaba", "estaban", "estuvo", "estuvieron",
    "ha", "han", "había", "habían", "hubo", "habrá",
    "tiene", "tienen", "tenía", "tenían",
    "hay",
    "no", "sí", "ya", "aún", "todavía", "siempre", "nunca", "jamás",
    "más", "menos", "muy", "mucho", "muchos", "muchas", "poco",
    "pocos", "pocas", "todo", "todos", "todas", "nada", "algo",
    "alguien", "nadie", "cada", "cualquier", "cualquiera",
    "aquí", "allí", "ahí", "acá", "allá", "ahora", "después",
    "antes", "luego", "entonces", "así", "bien", "mal",
    "solo", "sólo", "solamente", "apenas", "casi", "tan", "tanto",
    "etc", "etcétera", "vs",
})

_STOP = _DICCIONARIO_STOP


def obtener_referencias() -> Dict[str, Any]:
    return {
        "stopwords": list(_DICCIONARIO_STOP),
        "senales_adopcion": list(_SENALES_ADOPCION),
        "senales_acto": list(_SENALES_ACTO),
        "senales_no_proposicion": list(_SENALES_NO_PROPOSICION),
        "patrones_contradiccion": [(pat, str(peso)) for pat, peso in _PATRONES_CONTRADICCION],
        "umbral_min_tokens": _MIN_TOKENS_UNIDAD,
        "version": VERSION,
    }


# ===============================================================
# SEGMENTO 4 --- LECTURA DEL MATERIAL
# ===============================================================

_CLAVES_TEXTO = ("mensaje", "descripcion", "texto", "D")
_CLAVES_O = ("contexto", "O_context", "o_context", "O")
_CLAVES_O_LECTURA = ("enunciado_O", "contexto", "O_context", "o_context")


def _leer_texto(peticion: Dict[str, Any]) -> Tuple[str, str]:
    for clave in _CLAVES_TEXTO:
        v = peticion.get(clave)
        if v is not None and str(v).strip():
            return str(v), clave
    entrada = peticion.get("entrada")
    if isinstance(entrada, dict):
        for clave in _CLAVES_TEXTO:
            v = entrada.get(clave)
            if v is not None and str(v).strip():
                return str(v), "entrada.{0}".format(clave)
    elif entrada is not None and str(entrada).strip():
        return str(entrada), "entrada"
    for clave in _CLAVES_O_LECTURA:
        v = peticion.get(clave)
        if v is not None and str(v).strip():
            return str(v), clave
    return "", "ninguna"


def _leer_o(peticion: Dict[str, Any]) -> Tuple[str, str]:
    for clave in _CLAVES_O:
        v = peticion.get(clave)
        if v is not None and str(v).strip():
            return str(v), clave
    v = peticion.get("enunciado_O")
    if v is not None and str(v).strip():
        return str(v), "enunciado_O"
    return "", "ninguna"


def _leer_lexico(peticion: Dict[str, Any]) -> set:
    crudo = (
        peticion.get("diccionario")
        or peticion.get("lexico")
        or peticion.get("vocabulario")
        or peticion.get("terminos_O")
    )
    if not crudo:
        return set()
    if isinstance(crudo, dict):
        return {_norm(t) for t in crudo.keys() if t}
    if isinstance(crudo, (set, frozenset, list, tuple)):
        return {_norm(t) for t in crudo if t}
    if isinstance(crudo, str):
        return _tokens(crudo)
    return set()


# ===============================================================
# SEGMENTO 5 --- HELPERS
# ===============================================================

def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", (str(s) if s is not None else "").strip().lower())


def _partir_unidades(texto: str) -> List[str]:
    if not texto or not str(texto).strip():
        return []
    salida: List[str] = []
    for p in _SEPARADORES.split(str(texto)):
        if not p:
            continue
        p = p.strip()
        if not p:
            continue
        if len(p.split()) < _MIN_TOKENS_UNIDAD and not _SIMBOLICO.search(p):
            continue
        salida.append(p)
    return salida


def _es_acto(unidad: str) -> bool:
    low = _norm(unidad)
    return any(re.search(pat, low) for pat in _SENALES_ACTO)


def _es_adopcion_explicita(unidad: str) -> bool:
    low = _norm(unidad)
    if not low:
        return False
    return any(re.search(pat, low) for pat in _SENALES_ADOPCION)


def _es_proposicion(unidad: str) -> bool:
    low = _norm(unidad)
    if not low or _es_acto(unidad):
        return False
    for pat in _SENALES_NO_PROPOSICION:
        if re.search(pat, low):
            return False
    if len(low.split()) >= _MIN_TOKENS_UNIDAD:
        return True
    return bool(_SIMBOLICO.search(low))


def _es_adopcion_propia(unidad: str) -> bool:
    if not _norm(unidad):
        return False
    if _es_adopcion_explicita(unidad):
        return True
    if _es_acto(unidad):
        return False
    return _es_proposicion(unidad)


def _peso_contradiccion_en(unidad: str) -> Fraction:
    low = _norm(unidad)
    acum = Fraction(0)
    for pat, peso in _PATRONES_CONTRADICCION:
        if re.search(pat, low):
            acum += peso
            if acum >= PESO_TOTAL:
                return PESO_TOTAL
    return acum


def _hay_restriccion(compromisos_norm: List[str]) -> bool:
    return any(_RESTRICCION.search(c) for c in compromisos_norm)


def _peso_acto_contra_compromiso(acto: str, hay_restr: bool) -> Fraction:
    if not hay_restr or not _es_acto(acto):
        return Fraction(0)
    if _ACTO_CONTRA_COMPROMISO.search(_norm(acto)):
        return PESO_GRAVE
    return PESO_PARCIAL


def _tokens(s: Any, lexico_extra: Optional[set] = None) -> set:
    toks = set(_TOKEN.findall(_norm(s)))
    stop = _DICCIONARIO_STOP
    if lexico_extra:
        stop = stop - {str(t).lower() for t in lexico_extra}
    return toks - stop


def _tokens_brutos(s: Any) -> set:
    return set(_TOKEN.findall(_norm(s)))


def _divergencia_peso(
    afirmacion: str,
    o_tokens: set,
    lexico_extra: Optional[set] = None,
) -> Fraction:
    a_tok = _tokens(afirmacion, lexico_extra)
    if not a_tok or not o_tokens:
        return PESO_TOTAL
    inter = a_tok & o_tokens
    if not inter:
        return PESO_TOTAL
    ratio = Fraction(len(inter), len(a_tok))
    return _peso_armonico(ratio)


def _peso_reversion(
    unidad: str,
    prev_tokens: List[set],
    lexico_extra: Optional[set] = None,
) -> Fraction:
    if not _NEGACION.search(_norm(unidad)):
        return Fraction(0)
    u_tok = _tokens(unidad, lexico_extra)
    if not u_tok:
        return Fraction(0)
    mejor = Fraction(0)
    for pt in prev_tokens:
        if not pt:
            continue
        union = u_tok | pt
        if not union:
            continue
        solape = Fraction(len(u_tok & pt), len(union))
        if solape > mejor:
            mejor = solape
    return mejor if mejor >= _UMBRAL_SOLAPE_REVERSION else Fraction(0)


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


def _compromisos_y_k(
    unidades: List[str],
) -> Tuple[List[str], Fraction, List[Tuple[str, str]]]:
    compromisos = [u for u in unidades if _es_adopcion_propia(u)]
    hay_restr = _hay_restriccion([_norm(c) for c in compromisos])
    k = Fraction(0)
    detalle: List[Tuple[str, str]] = []

    for u in compromisos:
        w = _peso_contradiccion_en(u)
        if w > 0:
            k += w
            detalle.append((u, "{0} ({1})".format(w, nombre_reticula(w))))

    for u in unidades:
        if not _es_acto(u):
            continue
        w = _peso_acto_contra_compromiso(u, hay_restr)
        if w > 0:
            compromisos.append(u)
            k += w
            detalle.append((
                u,
                "{0} ({1}, acto vs compromiso)".format(w, nombre_reticula(w)),
            ))

    if k > len(compromisos):
        k = Fraction(len(compromisos))
        detalle.append(("(tope)", "k acotado a m"))

    return compromisos, k, detalle


# ===============================================================
# SEGMENTO 6 --- OFICIO PUBLICO
# ===============================================================

def extraer_conteos(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    peticion = _normalizar_entrada(*args, **kwargs)
    notas: List[str] = []

    texto, procedencia_texto = _leer_texto(peticion)
    o_ctx, procedencia_o = _leer_o(peticion)
    lexico_extra = _leer_lexico(peticion)

    o_presente = bool(o_ctx and str(o_ctx).strip())
    texto_es_o = bool(
        texto and o_presente and _norm(texto) == _norm(o_ctx)
    )

    unidades = _partir_unidades(texto)

    o_tokens = _tokens(o_ctx, lexico_extra) if o_presente else set()
    if lexico_extra:
        o_tokens = o_tokens | lexico_extra

    compromisos, k, k_detalle = _compromisos_y_k(unidades)
    m = len(compromisos)
    base_nula_C = m == 0
    cumplimiento_puro_C = (m > 0 and k == 0)

    posturas = list(compromisos) if compromisos else [
        u for u in unidades if _es_proposicion(u)
    ]

    r = Fraction(0)
    r_detalle: List[Tuple[str, str]] = []
    historial = peticion.get("historial_posturas")
    if isinstance(historial, (list, tuple)) and historial:
        prev_tokens = [_tokens(x, lexico_extra) for x in historial if x]
        for u in posturas:
            w = _peso_reversion(u, prev_tokens, lexico_extra)
            if w > 0:
                r += w
                r_detalle.append((
                    u,
                    "{0} ({1}, solape vs historial)".format(
                        w, nombre_reticula(w)
                    ),
                ))
        if r > len(posturas):
            r = Fraction(len(posturas))
            r_detalle.append(("(tope)", "r acotado a p"))

    p = len(posturas)
    base_nula_L = p == 0

    afirmaciones = [u for u in unidades if _es_proposicion(u)]

    f = Fraction(0)
    f_detalle: List[Tuple[str, str]] = []
    if not o_presente:
        f = Fraction(len(afirmaciones))
        for a in afirmaciones:
            f_detalle.append((a, "1 (sin O_context)"))
        if afirmaciones:
            notas.append("O_context ausente -> f saturado")
    else:
        for a in afirmaciones:
            w = _divergencia_peso(a, o_tokens, lexico_extra)
            if w > 0:
                f += w
                f_detalle.append((a, "{0} ({1})".format(w, nombre_reticula(w))))

    c = len(afirmaciones)
    base_nula_K = c == 0

    brutos = sum(len(_tokens_brutos(u)) for u in unidades)
    netos = sum(len(_tokens(u, lexico_extra)) for u in unidades)
    tokens_restados = brutos - netos

    def _res(base: int) -> str:
        return "indefinida" if base <= 0 else str(Fraction(1, base))

    notas.append("material leido de: {0}".format(procedencia_texto))
    notas.append("marco leido de: {0}".format(procedencia_o))
    if texto_es_o:
        notas.append(
            "texto_es_o: D y O son la misma cadena. K resultante es "
            "autoverificante, no correlacion medida."
        )
    if base_nula_C:
        notas.append("base_nula_C: m=0, nadie adopto nada")
    elif cumplimiento_puro_C:
        notas.append(
            "cumplimiento_puro_C: m={0} y k=0".format(m)
        )
    if base_nula_L:
        notas.append("base_nula_L: p=0")
    if base_nula_K:
        notas.append("base_nula_K: c=0")
    if k > 0:
        notas.append("k={0} ({1})".format(k, nombre_reticula(k)))
    if r > 0:
        notas.append("r={0} ({1})".format(r, nombre_reticula(r)))
    if f > 0 and o_presente:
        notas.append("f={0}".format(f))

    notas.append(
        "unidades={0}  resolucion C={1} L={2} K={3}".format(
            len(unidades), _res(m), _res(p), _res(c)
        )
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
        "cumplimiento_puro_C": cumplimiento_puro_C,
        "o_presente": o_presente,
        "procedencia_texto": procedencia_texto,
        "procedencia_o": procedencia_o,
        "texto_es_o": texto_es_o,
        "unidades": unidades,
        "k_detalle": k_detalle,
        "r_detalle": r_detalle,
        "f_detalle": f_detalle,
        "resolucion_C": _res(m),
        "resolucion_L": _res(p),
        "resolucion_K": _res(c),
        "tokens_brutos": brutos,
        "tokens_netos": netos,
        "tokens_restados": tokens_restados,
        "diccionario_stop_size": len(_DICCIONARIO_STOP),
        "lexico_dominio_size": len(lexico_extra),
        "metodo_sugerido": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def inyectar_en_peticion(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = dict(peticion or {})
    conteos = extraer_conteos(base)
    for clave in (
        "compromisos", "contradicciones",
        "posturas", "reversiones",
        "afirmaciones", "afirmaciones_falsas",
    ):
        base[clave] = conteos[clave]
    base["_conteos_meta"] = {
        clave: conteos[clave]
        for clave in (
            "m", "p", "c",
            "base_nula_C", "base_nula_L", "base_nula_K",
            "cumplimiento_puro_C", "o_presente",
            "procedencia_texto", "procedencia_o", "texto_es_o",
            "k_detalle", "r_detalle", "f_detalle",
            "resolucion_C", "resolucion_L", "resolucion_K",
            "tokens_brutos", "tokens_netos", "tokens_restados",
            "diccionario_stop_size", "lexico_dominio_size",
            "version", "notas",
        )
    }
    return base


def verificar_conteos(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    requeridas = (
        "compromisos", "contradicciones",
        "posturas", "reversiones",
        "afirmaciones", "afirmaciones_falsas",
    )
    return all(clave in salida for clave in requeridas)


__all__ = [
    "extraer_conteos",
    "inyectar_en_peticion",
    "verificar_conteos",
    "nombre_reticula",
    "obtener_referencias",
    "VERSION",
    "PESO_ROCE",
    "PESO_PARCIAL",
    "PESO_GRAVE",
    "PESO_TOTAL",
    "RETICULA",
    "_DICCIONARIO_STOP",
    "_SENALES_ADOPCION",
    "_SENALES_ACTO",
    "_PATRONES_CONTRADICCION",
]
