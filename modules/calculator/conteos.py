"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales con anclas de medicion (AM v1.0).

Version: 3.0

Cambios respecto a 2.0 --- todos declarados, ninguno silencioso:

  1. SIMETRIA C / L / K (AM-A5, AF-A2)
     En 2.0 solo L tenia respaldo:
         posturas = compromisos if compromisos else proposiciones
     C no lo tenia, asi que m=0 salvo que apareciera una de veinte
     frases literales. Resultado: C indefinido siempre, L y K definidos.
     Ahora los tres se construyen igual: quien afirma adopta lo
     afirmado como propio (AF-A2, no invasion de Ri), asi que una
     asercion factual entra en m con la misma legitimidad con que
     entra en c.

  2. DOS CAUSAS DE m=0 SEPARADAS (AM-D6)
     - nadie adopto nada        -> base nula, C indefinido
     - se adopto y no se rompio -> C = 1 exacto
     En 2.0 ambas daban base nula. No son lo mismo.

  3. k ACOTADO POR m (AM-A3)
     En 2.0 k sumaba sobre compromisos Y sobre actos, y los actos no
     entran en m. Con m=1 y tres actos graves, k=9/4 y C=-5/4: fuera
     de [0,1]. Ahora el acto que contradice entra tambien en m, asi
     que sube numerador y denominador a la vez y C queda acotado.

  4. DIVERGENCIA CONTINUA (precision)
     En 2.0 _divergencia_peso calculaba ratio = |inter|/|a_tok| y lo
     aplastaba a tres cubos {0, 1/2, 3/4}. Cuatro afirmaciones con
     anclaje distinto colapsaban en 1/2. Ahora el peso es 1 - ratio:
     el denominador pasa de 4 a |a_tok| (8-20 tokens tipicos).
     La reticula sigue siendo el marco de lectura; sus cuatro valores
     son casos particulares del continuo.

  5. SEPARACION POR CLAUSULA (precision)
     El paso minimo de C es 1/(4m). Con m=1 el paso es 0.25. Cortar
     por clausula ademas de por oracion multiplica m, p y c por 3-5,
     que es de donde salen los decimales finos.

  6. CONTRADICCION ACUMULADA (precision)
     En 2.0 _peso_contradiccion_en devolvia al primer patron que
     encontraba. Tres marcas de contradiccion pesaban lo mismo que
     una. Ahora suma con tope en PESO_TOTAL.

  7. r POR SOLAPE (precision)
     En 2.0 r exigia substring literal + "no", asi que r=0 casi
     siempre y L quedaba fijo en 1. Un factor constante no aporta
     granularidad: Tru_Ri = C * 1 * K. Ahora r usa solape de Jaccard,
     continuo como f.

  8. lexico_extra LLEGA A LA AFIRMACION
     En 2.0 se construia y no se pasaba a _tokens(afirmacion). Un
     termino de dominio que coincidiera con stop se borraba del lado
     de la afirmacion aunque estuviera inyectado.

Oficio unico:
    texto + O_context  ->  {
        compromisos, contradicciones,      # m, k  (C = 1 - k/m)
        posturas, reversiones,             # p, r  (L = 1 - r/p)
        afirmaciones, afirmaciones_falsas  # c, f  (K = 1 - f/c)
    }

No calcula C, L, K. No calcula Tru. No inventa factores.

Referencias:
  AM-D1..D6, AM-A1..A5, AM-T1 (anclas_medicion_AX)
  AF-A2, AF-C2, AF-C4, AF-T8 (sm_af_AX)
  Def 5.1-5.3, Def-5.3.1, PROTOCOLO sec. 0.15
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

VERSION = "3.0"

# ===============================================================
# SEGMENTO 1 --- RETICULA DE SEVERIDAD (AM-D5)
# ===============================================================
#
# Marco de lectura, no restriccion. Los pesos continuos que produce
# la divergencia caen entre estos cuatro puntos; la reticula sirve
# para nombrar la severidad, no para truncar la medida.

PESO_ROCE    = Fraction(1, 4)   # 0.25  toca sin romper
PESO_PARCIAL = Fraction(1, 2)   # 0.50  rompe parte
PESO_GRAVE   = Fraction(3, 4)   # 0.75  rompe casi todo
PESO_TOTAL   = Fraction(1, 1)   # 1.00  anula

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


# ===============================================================
# SEGMENTO 2 --- PATRONES DETERMINISTAS (sin modelo, sin azar)
# ===============================================================

_PATRONES_CONTRADICCION: Tuple[Tuple[str, Fraction], ...] = (
    (r"\by\s+no\b",                 PESO_TOTAL),
    (r"\bpero\s+no\b",              PESO_TOTAL),
    (r"\bes\b.+\bno\s+es\b",        PESO_TOTAL),
    (r"\bno\s+es\b.+\bes\b",        PESO_TOTAL),
    (r"\bs[ií]\s+y\s+no\b",         PESO_TOTAL),
    (r"\bno\s+y\s+s[ií]\b",         PESO_TOTAL),
    (r"\bsin\s+embargo\b",          PESO_GRAVE),
    (r"\bno\s+obstante\b",          PESO_GRAVE),
    (r"\bpor\s+un\s+lado\b.+\bpor\s+(?:el\s+)?otro\b", PESO_GRAVE),
    (r"\baunque\b",                 PESO_PARCIAL),
    (r"\bmas\s+no\b",               PESO_PARCIAL),
    (r"\bsin\s+dejar\s+de\b",       PESO_PARCIAL),
)

# Adopcion EXPLICITA: compromiso metodologico declarado.
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

# Separacion por CLAUSULA, no solo por oracion (cambio 5).
# El paso minimo de C es 1/(4m); cortar mas fino sube m y por tanto
# la resolucion de los tres factores.
_SEPARADORES = re.compile(
    r"[.;:!?\n]+|"                                   # oracion
    r",\s*|"                                         # clausula
    r"\s+(?:pero|porque|aunque|mientras|sino|pues)\s+|"
    r"\by\s+(?=[A-ZÁÉÍÓÚ¿¡])|"
    r"\b(?:además|asimismo|por\s+otra\s+parte)\b",
    re.IGNORECASE,
)

# Longitud minima de una unidad para que cuente. Evita que la
# separacion fina produzca fragmentos vacios de contenido.
_MIN_TOKENS_UNIDAD = 2


# ===============================================================
# SEGMENTO 3 --- DICCIONARIO DE STOPWORDS (es)
# ===============================================================

_DICCIONARIO_STOP: frozenset = frozenset({
    # articulos / determinantes
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
    # auxiliares / copulativos
    "ser", "estar", "haber", "tener", "ir", "hacer",
    "es", "son", "era", "eran", "fue", "fueron", "será", "serán",
    "está", "están", "estaba", "estaban", "estuvo", "estuvieron",
    "ha", "han", "había", "habían", "hubo", "habrá",
    "tiene", "tienen", "tenía", "tenían",
    "hay",
    # adverbios y particulas
    "no", "sí", "ya", "aún", "todavía", "siempre", "nunca", "jamás",
    "más", "menos", "muy", "mucho", "muchos", "muchas", "poco",
    "pocos", "pocas", "todo", "todos", "todas", "nada", "algo",
    "alguien", "nadie", "cada", "cualquier", "cualquiera",
    "aquí", "allí", "ahí", "acá", "allá", "ahora", "después",
    "antes", "luego", "entonces", "así", "bien", "mal",
    "solo", "sólo", "solamente", "apenas", "casi", "tan", "tanto",
    # funcionales
    "etc", "etcétera", "vs",
})

_STOP = _DICCIONARIO_STOP


# ===============================================================
# SEGMENTO 4 --- HELPERS
# ===============================================================

def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", (str(s) if s is not None else "").strip().lower())


def _partir_unidades(texto: str) -> List[str]:
    """
    Parte por clausula. Descarta fragmentos sin contenido minimo:
    la separacion fina no debe inflar los denominadores con restos.
    """
    if not texto or not str(texto).strip():
        return []
    partes = _SEPARADORES.split(str(texto))
    salida: List[str] = []
    for p in partes:
        if not p:
            continue
        p = p.strip()
        if not p:
            continue
        if len(p.split()) < _MIN_TOKENS_UNIDAD and not re.search(r"[0-9=+\-*/^]", p):
            continue
        salida.append(p)
    return salida


def _es_acto(unidad: str) -> bool:
    """Acto o propuesta. Aporta a k y, desde 3.0, tambien a m."""
    low = _norm(unidad)
    return any(re.search(pat, low) for pat in _SENALES_ACTO)


def _es_adopcion_explicita(unidad: str) -> bool:
    """Compromiso metodologico declarado con una de las senales."""
    low = _norm(unidad)
    if not low:
        return False
    return any(re.search(pat, low) for pat in _SENALES_ADOPCION)


def _es_proposicion(unidad: str) -> bool:
    """
    AF-C4 / AF-T8: forma asertiva con particion potencialmente
    reconocible. Excluye actos puros, preguntas y condicionantes.
    """
    low = _norm(unidad)
    if not low:
        return False
    if _es_acto(unidad):
        return False
    for pat in _SENALES_NO_PROPOSICION:
        if re.search(pat, low):
            return False
    if len(low.split()) >= _MIN_TOKENS_UNIDAD:
        return True
    return bool(re.search(r"[0-9=+\-*/^αβ]", low))


def _es_adopcion_propia(unidad: str) -> bool:
    """
    AM-D2 + AF-A2 (cambio 1).

    Adopcion propia es:
      (a) compromiso metodologico explicito, o
      (b) asercion factual: quien afirma adopta lo afirmado como
          propio. AF-A2 lo dice para la no invasion de Ri --- lo
          declarado se registra como premisa del emisor --- y esa es
          exactamente la relacion que C mide.

    Un acto ("propongo X") NO es adopcion por si mismo: es un acto.
    Pero si contradice un compromiso vigente, entra en m por la via
    de _compromisos_y_k (cambio 3), para que k no exceda a m.
    """
    if not _norm(unidad):
        return False
    if _es_adopcion_explicita(unidad):
        return True
    if _es_acto(unidad):
        return False
    return _es_proposicion(unidad)


def _peso_contradiccion_en(unidad: str) -> Fraction:
    """
    AM-D5 (cambio 6): suma de todos los patrones presentes, con tope
    en PESO_TOTAL. Tres marcas de contradiccion no pesan lo mismo que
    una.
    """
    low = _norm(unidad)
    acum = Fraction(0)
    for pat, peso in _PATRONES_CONTRADICCION:
        if re.search(pat, low):
            acum += peso
            if acum >= PESO_TOTAL:
                return PESO_TOTAL
    return acum


def _hay_restriccion(compromisos_norm: List[str]) -> bool:
    return any(
        re.search(
            r"\bno\s+invento\b|\bno\s+decido\b|\bno\s+salgo\b|"
            r"\bno\s+modifico\b|\bno\s+altero\b|\bno\s+tomo\s+decisiones\b",
            c,
        )
        for c in compromisos_norm
    )


def _peso_acto_contra_compromiso(acto: str, hay_restr: bool) -> Fraction:
    """Peso del acto que rompe un compromiso metodologico vigente."""
    if not hay_restr or not _es_acto(acto):
        return Fraction(0)
    low = _norm(acto)
    if re.search(
        r"\bpropongo\b|\bpropongamos\b|\bintroduzco\b|\bintroduzcamos\b|"
        r"\binvento\b|\bcreo\s+el\s+s[ií]mbolo\b|\bdefinamos\b|\bplanteo\b",
        low,
    ):
        return PESO_GRAVE
    return PESO_PARCIAL


def _tokens(s: Any, lexico_extra: Optional[set] = None) -> set:
    """
    Tokens lexicos menos stopwords. Los terminos de dominio inyectados
    tienen prioridad de ancla: no se eliminan aunque esten en stop.
    """
    toks = set(re.findall(r"[a-záéíóúñ0-9/αβ]+", _norm(s)))
    stop = set(_DICCIONARIO_STOP)
    if lexico_extra:
        stop = stop - {str(t).lower() for t in lexico_extra}
    return toks - stop


def _divergencia_peso(
    afirmacion: str,
    o_tokens: set,
    lexico_extra: Optional[set] = None,
) -> Fraction:
    """
    AM-D5 aplicado a K (cambio 4 y 8).

    peso = 1 - |inter| / |a_tok|

    Continuo y exacto. El denominador es el numero de tokens de la
    afirmacion, no 4. En 2.0 este mismo ratio se calculaba y se
    aplastaba a tres cubos: 0.5833, 0.4167, 0.3333 y 0.2500 daban
    todos 1/2.
    """
    a_tok = _tokens(afirmacion, lexico_extra)
    if not a_tok or not o_tokens:
        return PESO_TOTAL
    inter = a_tok & o_tokens
    if not inter:
        return PESO_TOTAL
    return Fraction(1) - Fraction(len(inter), len(a_tok))


def _peso_reversion(unidad: str, prev_tokens: List[set]) -> Fraction:
    """
    Reversion por solape (cambio 7).

    En 2.0 se exigia substring literal + "no", asi que r = 0 casi
    siempre y L quedaba fijo en 1. Un factor constante no aporta
    granularidad: Tru_Ri = C * 1 * K.

    Solape de Jaccard entre la unidad y cada postura previa. Se exige
    negacion explicita para no confundir continuidad con reversion.
    """
    low = _norm(unidad)
    if not re.search(r"\bno\b|\bnunca\b|\bjam[aá]s\b|\btampoco\b", low):
        return Fraction(0)
    u_tok = _tokens(unidad)
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
    return mejor if mejor >= Fraction(1, 4) else Fraction(0)


def _normalizar_entrada(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Acepta:
        extraer_conteos(peticion_dict)
        extraer_conteos(texto)
        extraer_conteos(texto, o_context)
        extraer_conteos(descripcion=..., o_context=..., ...)
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


def _compromisos_y_k(
    unidades: List[str],
) -> Tuple[List[str], Fraction, List[Tuple[str, str]]]:
    """
    Construye m y k juntos (cambio 3).

    En 2.0 k sumaba sobre compromisos Y sobre actos, y los actos no
    entraban en m. Con m=1 y tres actos graves: k=9/4, C=-5/4.

    Aqui el acto que contradice entra tambien en el denominador: sube
    numerador y denominador a la vez, y C queda acotado en [0,1] sin
    truncar nada.
    """
    compromisos = [u for u in unidades if _es_adopcion_propia(u)]
    compromisos_norm = [_norm(c) for c in compromisos]
    hay_restr = _hay_restriccion(compromisos_norm)

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
            compromisos.append(u)          # entra en m: acota C
            k += w
            detalle.append((
                u, "{0} ({1}, acto vs compromiso)".format(w, nombre_reticula(w))
            ))

    if k > len(compromisos):               # cinturon: nunca C < 0
        k = Fraction(len(compromisos))
        detalle.append(("(tope)", "k acotado a m por AM-A3"))

    return compromisos, k, detalle


# ===============================================================
# SEGMENTO 5 --- OFICIO PUBLICO
# ===============================================================

def extraer_conteos(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    texto + O_context -> conteos que la ruta operacional de CA exige.

    Salida (claves que CA consume):
        compromisos          List[str]
        contradicciones      Fraction   k
        posturas             List[str]
        reversiones          Fraction   r
        afirmaciones         List[str]
        afirmaciones_falsas  Fraction   f

    Meta:
        m, p, c                        int
        base_nula_C / L / K            bool
        cumplimiento_puro_C            bool   m>0 y k=0 -> C = 1
        o_presente                     bool
        k_detalle, r_detalle, f_detalle
        resolucion_C / L / K           str    paso minimo alcanzable
        version, notas
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

    # ----- lexico de dominio inyectado -----
    lexico_raw = (
        peticion.get("diccionario")
        or peticion.get("lexico")
        or peticion.get("vocabulario")
        or peticion.get("terminos_O")
    )
    lexico_extra: set = set()
    if lexico_raw:
        if isinstance(lexico_raw, (set, frozenset, list, tuple)):
            lexico_extra = {_norm(t) for t in lexico_raw if t}
        elif isinstance(lexico_raw, str):
            lexico_extra = _tokens(lexico_raw)
        elif isinstance(lexico_raw, dict):
            lexico_extra = {_norm(t) for t in lexico_raw.keys() if t}

    o_tokens = _tokens(o_ctx, lexico_extra) if o_presente else set()
    if lexico_extra:
        o_tokens |= lexico_extra

    # ----- C: compromisos + k acotado -----
    compromisos, k, k_detalle = _compromisos_y_k(unidades)
    m = len(compromisos)
    base_nula_C = m == 0
    cumplimiento_puro_C = (m > 0 and k == 0)

    # ----- L: posturas + r continuo -----
    # Simetria con C: la base de L es la misma que la de C cuando hay
    # compromisos, y las proposiciones cuando no. Ya no es un respaldo
    # exclusivo de L: los tres factores parten del mismo material.
    posturas = list(compromisos) if compromisos else [
        u for u in unidades if _es_proposicion(u)
    ]

    r = Fraction(0)
    r_detalle: List[Tuple[str, str]] = []
    historial = peticion.get("historial_posturas")
    if isinstance(historial, (list, tuple)) and historial:
        prev_tokens = [_tokens(x, lexico_extra) for x in historial if x]
        for u in posturas:
            w = _peso_reversion(u, prev_tokens)
            if w > 0:
                r += w
                r_detalle.append((
                    u, "{0} ({1}, solape vs historial)".format(
                        w, nombre_reticula(w)
                    )
                ))
        if r > len(posturas):
            r = Fraction(len(posturas))
            r_detalle.append(("(tope)", "r acotado a p por AM-A3"))

    p = len(posturas)
    base_nula_L = p == 0

    # ----- K: afirmaciones + f continuo -----
    afirmaciones = [u for u in unidades if _es_proposicion(u)]

    f = Fraction(0)
    f_detalle: List[Tuple[str, str]] = []
    if not o_presente:
        f = Fraction(len(afirmaciones))
        for a in afirmaciones:
            f_detalle.append((a, "1 (sin O_context)"))
        if afirmaciones:
            notas.append(
                "O_context ausente -> f saturado; "
                "K debe quedar UNDEFINED (Def-5.3.1)"
            )
    else:
        for a in afirmaciones:
            w = _divergencia_peso(a, o_tokens, lexico_extra)
            if w > 0:
                f += w
                f_detalle.append((
                    a, "{0} ({1})".format(w, nombre_reticula(w))
                ))

    c = len(afirmaciones)
    base_nula_K = c == 0

    # ----- resolucion alcanzable -----
    def _res(base: int) -> str:
        if base <= 0:
            return "indefinida"
        return str(Fraction(1, base))

    # ----- notas -----
    if base_nula_C:
        notas.append(
            "base_nula_C: m=0 -> nadie adopto nada; C indefinido (AM-D6)"
        )
    elif cumplimiento_puro_C:
        notas.append(
            "cumplimiento_puro_C: m={0} y k=0 -> C = 1 exacto, "
            "no base nula".format(m)
        )
    if base_nula_L:
        notas.append("base_nula_L: p=0 -> L indefinido")
    if base_nula_K:
        notas.append("base_nula_K: c=0 -> K indefinido")
    if k > 0:
        notas.append("k={0} ({1})".format(k, nombre_reticula(k)))
    if r > 0:
        notas.append("r={0} ({1})".format(r, nombre_reticula(r)))
    if f > 0 and o_presente:
        notas.append("f={0}".format(f))

    actos = [u for u in unidades if _es_acto(u)]
    if actos:
        notas.append("actos detectados: {0}".format(len(actos)))
    no_prop = [
        u for u in unidades if not _es_proposicion(u) and not _es_acto(u)
    ]
    if no_prop:
        notas.append(
            "fuera de c por AF-C4 (no proposicion): {0}".format(len(no_prop))
        )
    if lexico_extra:
        notas.append(
            "lexico de dominio inyectado: {0} terminos".format(len(lexico_extra))
        )
    notas.append(
        "unidades={0}  resolucion C={1} L={2} K={3}".format(
            len(unidades), _res(m), _res(p), _res(c)
        )
    )

    return {
        # claves que CA consume
        "compromisos": compromisos,
        "contradicciones": k,
        "posturas": posturas,
        "reversiones": r,
        "afirmaciones": afirmaciones,
        "afirmaciones_falsas": f,
        # meta
        "m": m,
        "p": p,
        "c": c,
        "base_nula_C": base_nula_C,
        "base_nula_L": base_nula_L,
        "base_nula_K": base_nula_K,
        "cumplimiento_puro_C": cumplimiento_puro_C,
        "o_presente": o_presente,
        "unidades": unidades,
        "k_detalle": k_detalle,
        "r_detalle": r_detalle,
        "f_detalle": f_detalle,
        "resolucion_C": _res(m),
        "resolucion_L": _res(p),
        "resolucion_K": _res(c),
        "diccionario_stop_size": len(_DICCIONARIO_STOP),
        "lexico_dominio_size": len(lexico_extra),
        "metodo_sugerido": "operacional",
        "version": VERSION,
        "notas": notas,
    }


def inyectar_en_peticion(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Copia de la peticion con los conteos ya insertados."""
    base = dict(peticion or {})
    conteos = extraer_conteos(base)
    for clave in (
        "compromisos", "contradicciones",
        "posturas", "reversiones",
        "afirmaciones", "afirmaciones_falsas",
    ):
        base[clave] = conteos[clave]
    base["_conteos_meta"] = {
        k: conteos[k] for k in (
            "m", "p", "c",
            "base_nula_C", "base_nula_L", "base_nula_K",
            "cumplimiento_puro_C", "o_presente",
            "k_detalle", "r_detalle", "f_detalle",
            "resolucion_C", "resolucion_L", "resolucion_K",
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
    return all(k in salida for k in requeridas)


__all__ = [
    "extraer_conteos",
    "inyectar_en_peticion",
    "verificar_conteos",
    "nombre_reticula",
    "VERSION",
    "PESO_ROCE",
    "PESO_PARCIAL",
    "PESO_GRAVE",
    "PESO_TOTAL",
    "RETICULA",
    "_DICCIONARIO_STOP",
]
