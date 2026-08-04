"""
VPSI-TRUTH --- modules/axiomas/diccionario_AX.py

Cuerpo axiomático: diccionario como ancla de significado.

NO redefine qué es un diccionario.
NO inventa glosas.
Ancla el diccionario oficial del idioma del ciclo (p. ej. RAE en español)
como fuente provisional de significado léxico, subordinada a TODO el
cuerpo axiomático ya cargado (VPSI, realidad, sentido, contexto,
indefinido, anclas de medición, …).

Regla de oro:
  Una entrada de diccionario es representación de significado, no R.
  Puede contradecirse si falla coherencia, lógica o correlación con R
  bajo el O del ciclo. Si no se resuelve, el significado de esa unidad
  queda indefinido (no se fabrica).

Versión: 1.0
"""

from __future__ import annotations

from typing import Any, Dict, List

# ===============================================================
# METADATOS DEL CUERPO
# ===============================================================

CUERPO = {
    "id": "diccionario_AX",
    "nombre": "Diccionario como ancla de significado",
    "version": "1.0",
    "idioma_ancla_default": "es",
    "fuente_ancla_default": "RAE",
    "nota": (
        "El diccionario oficial del idioma del ciclo es ancla léxica. "
        "No es verdad absoluta. Queda pegado a VPSI / realidad / sentido / "
        "contexto / indefinido / AM. Contradicción legítima exige evidencia."
    ),
}


# ===============================================================
# DECLARACIONES
# ===============================================================

DECLARACIONES: List[Dict[str, Any]] = [

    # ----- Definiciones -----
    {
        "id": "DIC-D1",
        "tipo": "definicion",
        "sujeto": "diccionario_oficial",
        "relacion": "es",
        "objeto": "fuente_lexica_del_idioma_del_ciclo",
        "polaridad": True,
        "cota": None,
        "depende_de": ["RE-A0", "RE-A1", "SE-D1"],
        "gobierna": ["semantica", "medicion", "contexto"],
        "enunciado": (
            "DIC-D1: Diccionario oficial del idioma del ciclo = fuente léxica "
            "de definiciones de palabras de ese idioma (en español: RAE u "
            "equivalente institucional del mismo rango). No es R; es ancla "
            "de representación de significado."
        ),
    },
    {
        "id": "DIC-D2",
        "tipo": "definicion",
        "sujeto": "entrada_de_diccionario",
        "relacion": "es",
        "objeto": "par_lexema_definicion_citado",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D1", "SE-D1"],
        "gobierna": ["semantica"],
        "enunciado": (
            "DIC-D2: Entrada de diccionario = par (lexema, definición) citado "
            "desde el diccionario oficial, con fuente y, si aplica, acepción. "
            "Es representación; no constituye por sí sola un hecho de R."
        ),
    },
    {
        "id": "DIC-D3",
        "tipo": "definicion",
        "sujeto": "significado_resoluble",
        "relacion": "es",
        "objeto": "lexema_con_entrada_no_contradicida_bajo_O",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D2", "CX-A1", "T14"],
        "gobierna": ["semantica", "medicion"],
        "enunciado": (
            "DIC-D3: Significado resoluble (bajo O) = lexema para el cual "
            "existe al menos una entrada de diccionario del idioma del ciclo "
            "que no ha sido contradicha en el ciclo por fallo de coherencia, "
            "lógica o correlación con R bajo ese O."
        ),
    },
    {
        "id": "DIC-D4",
        "tipo": "definicion",
        "sujeto": "significado_indefinido",
        "relacion": "es",
        "objeto": "lexema_sin_entrada_resoluble_bajo_O",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D3", "IND-D1", "IND-A1"],
        "gobierna": ["semantica", "indefinido"],
        "enunciado": (
            "DIC-D4: Significado indefinido = lexema sin entrada resoluble "
            "bajo O (ausencia de fuente, o todas las acepciones legítimamente "
            "contradicidas). No se inventa glosa."
        ),
    },

    # ----- Axiomas -----
    {
        "id": "DIC-A1",
        "tipo": "axioma",
        "sujeto": "diccionario_oficial",
        "relacion": "es_ancla_provisional_de",
        "objeto": "significado_lexico_del_ciclo",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D1", "RE-A0", "TA4"],
        "gobierna": ["semantica", "realidad", "medicion"],
        "enunciado": (
            "DIC-A1 (Ancla léxica): El diccionario oficial del idioma del "
            "ciclo (RAE en español) es ancla provisional de significado "
            "léxico. Subordinado a R y al cuerpo axiomático completo: no "
            "deroga VPSI, realidad, sentido, contexto ni anclas de medición."
        ),
    },
    {
        "id": "DIC-A2",
        "tipo": "axioma",
        "sujeto": "entrada_de_diccionario",
        "relacion": "no_es",
        "objeto": "R_ni_verdad_absoluta",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D2", "RE-A1", "T1"],
        "gobierna": ["semantica", "ontologia"],
        "enunciado": (
            "DIC-A2: Ninguna entrada de diccionario es R ni verdad absoluta. "
            "Es representación de uso lingüístico. Confundir glosa con R es "
            "error de categoría (Ri ≠ R)."
        ),
    },
    {
        "id": "DIC-A3",
        "tipo": "axioma",
        "sujeto": "contradiccion_legitima_de_entrada",
        "relacion": "exige",
        "objeto": "evidencia_C_L_K_bajo_O",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A2", "T14", "TA3", "TA4"],
        "gobierna": ["semantica", "evaluacion", "realidad"],
        "enunciado": (
            "DIC-A3 (Contradicción legítima): Una entrada de diccionario "
            "puede contradecirse en el ciclo si y solo si hay evidencia de "
            "fallo de coherencia, de lógica o de correlación con R bajo O. "
            "La mera preferencia de Ri no basta."
        ),
    },
    {
        "id": "DIC-A4",
        "tipo": "axioma",
        "sujeto": "significado_no_resoluble",
        "relacion": "no_autoriza",
        "objeto": "invencion_de_glosa",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D4", "IND-A1", "IND-A3"],
        "gobierna": ["semantica", "indefinido", "medicion"],
        "enunciado": (
            "DIC-A4: Si el significado de un lexema no es resoluble bajo O, "
            "queda indefinido. El sistema no inventa definición. El anuncio "
            "de indefinido léxico es evaluable como tal (cuerpo indefinido)."
        ),
    },
    {
        "id": "DIC-A5",
        "tipo": "axioma",
        "sujeto": "adopcion_propia",
        "relacion": "requiere",
        "objeto": "unidad_asertiva_con_significado_resoluble",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D3", "AF-A2", "AM-D2"],
        "gobierna": ["conteos", "medicion", "semantica"],
        "enunciado": (
            "DIC-A5 (Puente a m): Una unidad de adopción propia (compromiso "
            "que alimenta m) exige cláusula asertiva del emisor cuyo núcleo "
            "léxico tenga significado resoluble bajo el diccionario del ciclo. "
            "Sin significado resoluble no se infla m; no se cuenta compromiso "
            "fantasma."
        ),
    },
    {
        "id": "DIC-A6",
        "tipo": "axioma",
        "sujeto": "cuerpo_axiomatico_previo",
        "relacion": "gobierna",
        "objeto": "uso_del_diccionario",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A1", "T1", "T14", "RE-A0"],
        "gobierna": ["semantica", "meta"],
        "enunciado": (
            "DIC-A6 (Pegamento): El uso del diccionario en el ciclo está "
            "gobernado por el cuerpo axiomático ya cargado (VPSI, realidad, "
            "sentido estructural, contexto, indefinido, anclas de medición, "
            "self, correlación). El diccionario no abre un fuero aparte."
        ),
    },

    # ----- Lemas -----
    {
        "id": "DIC-L1",
        "tipo": "lema",
        "sujeto": "idioma_del_ciclo",
        "relacion": "determina",
        "objeto": "diccionario_oficial_aplicable",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D1", "CX-A1"],
        "gobierna": ["semantica", "contexto"],
        "enunciado": (
            "DIC-L1: El idioma del ciclo (fijado por O / modo de entrada) "
            "determina qué diccionario oficial aplica. En español, RAE "
            "(o equivalente institucional). Mezclar glosas de otro idioma "
            "sin declarar cambio de O es error de contexto."
        ),
    },
    {
        "id": "DIC-L2",
        "tipo": "lema",
        "sujeto": "acepcion_multiple",
        "relacion": "exige",
        "objeto": "desambiguacion_bajo_O",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D2", "CX-T4", "CX-A14"],
        "gobierna": ["semantica", "contexto"],
        "enunciado": (
            "DIC-L2: Si un lexema tiene varias acepciones, la acepción "
            "usable es la compatible con O. Sin desambiguación posible, "
            "el significado de esa ocurrencia queda indefinido (DIC-D4)."
        ),
    },
    {
        "id": "DIC-L3",
        "tipo": "lema",
        "sujeto": "entrada_no_contradicida",
        "relacion": "permanece",
        "objeto": "ancla_lexica_del_ciclo",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A1", "DIC-A3"],
        "gobierna": ["semantica", "medicion"],
        "enunciado": (
            "DIC-L3: Mientras una entrada no sea legítimamente contradicha "
            "bajo O, permanece como ancla léxica del ciclo para ese lexema."
        ),
    },

    # ----- Teoremas -----
    {
        "id": "DIC-T1",
        "tipo": "teorema",
        "sujeto": "glosa_sin_C_L_K",
        "relacion": "no_derrota",
        "objeto": "entrada_ancla",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A3", "T14", "TA3"],
        "gobierna": ["semantica", "evaluacion"],
        "enunciado": (
            "DIC-T1: Una objeción a una entrada de diccionario que no aporte "
            "fallo de coherencia, lógica o correlación con R bajo O no "
            "derrota el ancla léxica. Preferencia de Ri ≠ contradicción legítima."
        ),
    },
    {
        "id": "DIC-T2",
        "tipo": "teorema",
        "sujeto": "unidad_asertiva_sin_significado_resoluble",
        "relacion": "no_incrementa",
        "objeto": "m_compromisos",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A5", "AM-D2", "AM-D6"],
        "gobierna": ["conteos", "medicion"],
        "enunciado": (
            "DIC-T2: Una cláusula asertiva cuyo núcleo no tiene significado "
            "resoluble no incrementa m. Evita inflar compromisos con tokens "
            "sin ancla léxica."
        ),
    },
    {
        "id": "DIC-T3",
        "tipo": "teorema",
        "sujeto": "diccionario",
        "relacion": "no_sustituye",
        "objeto": "evaluacion_C_L_K",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A6", "T16", "T17"],
        "gobierna": ["semantica", "truth"],
        "enunciado": (
            "DIC-T3: El diccionario no sustituye la evaluación C·L·K ni la "
            "fórmula Tru. Solo aporta ancla de significado para interpretar "
            "unidades del discurso bajo O."
        ),
    },

    # ----- Corolarios -----
    {
        "id": "DIC-C1",
        "tipo": "corolario",
        "sujeto": "RAE_en_ciclo_es",
        "relacion": "es",
        "objeto": "ancla_lexica_provisional",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A1", "DIC-L1"],
        "gobierna": ["semantica", "realidad"],
        "enunciado": (
            "DIC-C1: En ciclo en español, RAE (o equivalente institucional) "
            "es la ancla léxica provisional por defecto."
        ),
    },
    {
        "id": "DIC-C2",
        "tipo": "corolario",
        "sujeto": "contradiccion_de_glosa_con_hecho",
        "relacion": "activa",
        "objeto": "DIC-A3",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-A3", "RE-T1", "TA4"],
        "gobierna": ["semantica", "realidad"],
        "enunciado": (
            "DIC-C2: Si una glosa choca con un hecho establecido bajo O "
            "(correlación con R fallida), se activa contradicción legítima "
            "de esa entrada (DIC-A3); no se silencia el hecho."
        ),
    },
    {
        "id": "DIC-C3",
        "tipo": "corolario",
        "sujeto": "m_cero_por_falta_de_significado",
        "relacion": "no_equivale_a",
        "objeto": "C_igual_uno_por_vacuidad",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-T2", "AM-D6", "IND-A1"],
        "gobierna": ["conteos", "medicion"],
        "enunciado": (
            "DIC-C3: m=0 por ausencia de significado resoluble no se interpreta "
            "como C=1 por vacuidad. Son casos distintos: sin base léxica no hay "
            "compromiso medible; no se premia el vacío semántico."
        ),
    },
    {
        "id": "DIC-C4",
        "tipo": "corolario",
        "sujeto": "sistema",
        "relacion": "puede_citar",
        "objeto": "entrada_y_fuente_del_diccionario",
        "polaridad": True,
        "cota": None,
        "depende_de": ["DIC-D2", "PA-T1", "CIT-CICLO"],
        "gobierna": ["citacion", "semantica"],
        "enunciado": (
            "DIC-C4: El sistema puede citar lexema, acepción y fuente "
            "diccionarial en la cadena de anuncio del ciclo, sin presentar "
            "la glosa como Tru."
        ),
    },
]


# ===============================================================
# EXPORT
# ===============================================================

def declaraciones() -> List[Dict[str, Any]]:
    return list(DECLARACIONES)


__all__ = ["CUERPO", "DECLARACIONES", "declaraciones"]
