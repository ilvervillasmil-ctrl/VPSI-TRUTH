"""
VPSI-TRUTH --- modules/correlacion_mecanica/calculo_variables.py

Definición del orden causal y la lógica de cálculo para las variables C, L, K
bajo anclas de medición (AM v1.0).

Versión: 2.0
Cambio principal respecto a 1.x:
  - Ancla de inclusión (AM-D2): solo adopción propia entra en m / p / c.
  - Retícula de severidad (AM-D5): k, r, f son sumas de pesos
    {1/4, 1/2, 3/4, 1}, no solo enteros binarios.
  - Base nula (AM-D6 / AM-A3): m=0 / p=0 / c=0 → UNDEFINED (no 1).
  - Sin O_context → K = UNDEFINED (Def-5.3.1, ya estaba; se refuerza).
  - Declaraciones nuevas de las anclas para que el grafo MC las conozca.

Este archivo declara:
1. El orden nativo en el que se calculan C, L, K.
2. Las fórmulas teóricas y operacionales (con anclas).
3. Las dependencias entre variables.
4. Las anclas de medición que el Calculator (CA) debe respetar.

No ejecuta cálculos. Solo declara cómo deben calcularse.
CA (conteos / coherencia / logica / correlacion_k v2.0) es quien ejecuta.

Referencias:
  IlverVillasmil.pdf (Def 5.1–5.3, Def-5.3.1, TA1–TA5, T16, T17)
  PROTOCOLO.pdf sec. 0.15
  anclas_medicion_AX (AM-D2, AM-D5, AM-D6, AM-A3, AM-A4)
  modules/calculator/* v2.0
"""

from __future__ import annotations

from fractions import Fraction

# ===============================================================
# CONSTANTES DE LA RETÍCULA (AM-D5)
# ===============================================================
PESO_ROCE    = Fraction(1, 4)   # 0.25
PESO_PARCIAL = Fraction(1, 2)   # 0.50
PESO_GRAVE   = Fraction(3, 4)   # 0.75
PESO_TOTAL   = Fraction(1, 1)   # 1.00

RETICULA_SEVERIDAD = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)

VERSION = "2.0"

# ===============================================================
# DEFINICIÓN DE LA MECÁNICA DE CÁLCULO
# ===============================================================
MECANICA = {
    "nombre": "Cálculo de Variables de Verdad (C, L, K) bajo anclas AM",
    "version": VERSION,
    "orden": [
        "O_context",   # Debe declararse primero (requerido para K)
        "inclusion",   # Ancla: filtrar solo adopción propia → m, p, c
        "severidad",   # Ancla: asignar pesos de retícula → k, r, f
        "C",           # Coherencia (1 - k/m) o UNDEFINED si m=0
        "L",           # Lógica     (1 - r/p) o UNDEFINED si p=0
        "K",           # Correlación (1 - f/c) o UNDEFINED si c=0 o sin O
        "Tru_Ri",      # C * L * K  (solo si los tres están definidos)
        "Tru_total",   # (Tru_Ri * ALPHA) + BETA
    ],
    "descripcion": (
        "Orden causal para el cálculo de las variables de verdad en el marco VPSI. "
        "Primero se declara O_context. Luego se aplican las anclas de inclusión y "
        "severidad. Después se calculan C, L, K. Tru_Ri solo se forma si los tres "
        "factores están definidos. Tru_total aplica el techo α y el piso β."
    ),
    "dependencias": {
        "inclusion": [],
        "severidad": ["inclusion"],
        "C": ["inclusion", "severidad"],
        "L": ["inclusion", "severidad"],
        "K": ["O_context", "inclusion", "severidad"],
        "Tru_Ri": ["C", "L", "K"],
        "Tru_total": ["Tru_Ri"],
    },
    "anclas": {
        "inclusion": "AM-D2: solo adopción propia entra en m/p/c; actos no inflan denominador",
        "severidad": "AM-D5: k/r/f ∈ retícula {1/4, 1/2, 3/4, 1}",
        "base_nula": "AM-D6 / AM-A3: m=0|p=0|c=0 → UNDEFINED (no 1)",
        "dominio": "Def-5.3.1: sin O_context → K = UNDEFINED",
        "ortogonalidad": "AM-A4: un mismo evento no inventa orígenes múltiples",
    },
}

# ===============================================================
# DEFINICIONES DE CÁLCULO (IlverVillasmil.pdf: Enfoque Teórico)
# ===============================================================
DEF_C = {
    "id": "DEF-C-TEORICO",
    "tipo": "definicion",
    "sujeto": "Coherencia (C)",
    "relacion": "definido_como",
    "objeto": "C(D) = 1 si no existe P tal que (D ⊢ P) ∧ (D ⊢ ¬P)",
    "polaridad": True,
    "enunciado": (
        "Coherencia interna de D: ausencia de contradicciones lógicas. "
        "C(D) = 1 si no es posible derivar una proposición P y su negación ¬P de D. "
        "C(D) = 0 si existe al menos un par contradictorio."
    ),
    "formula": "C(D) = 1 si no hay contradicciones; C(D) = 0 si las hay",
    "fuente": "IlverVillasmil.pdf, Axioma TA1 / Def 5.1",
}

DEF_L = {
    "id": "DEF-L-TEORICO",
    "tipo": "definicion",
    "sujeto": "Lógica (L)",
    "relacion": "definido_como",
    "objeto": "L(D) = 1 si ∃ espacio Z y transformación T: ∀z ∈ Z, T(z) es único e invariante",
    "polaridad": True,
    "enunciado": (
        "Lógica del proceso: L(D) = 1 si existe un espacio Z y una transformación T "
        "tal que para todo z en Z, T(z) es único e invariante. "
        "L(D) = 0 si el proceso admite salidas incompatibles (no-determinismo)."
    ),
    "formula": "L(D) = 1 si el proceso es determinista; L(D) = 0 si no lo es",
    "fuente": "IlverVillasmil.pdf, Axioma TA2 / Def 5.2",
}

DEF_K = {
    "id": "DEF-K-TEORICO",
    "tipo": "definicion",
    "sujeto": "Correlación (K)",
    "relacion": "definido_como",
    "objeto": "K(D) = 1 si ||D(z) - O(z)|| ≤ ε para todo z en el dominio",
    "polaridad": True,
    "enunciado": (
        "Correlación con el dominio observable O_context: K(D) = 1 si para todo z, "
        "la distancia entre D(z) y O(z) es ≤ ε. "
        "K(D) = UNDEFINED si no hay O_context explícito (Def-5.3.1)."
    ),
    "formula": "K(D) = 1 si D coincide con O; K(D) ∈ [0,1] si hay divergencia parcial; UNDEFINED sin O",
    "fuente": "IlverVillasmil.pdf, Axioma TA3 y Corolario Def-5.3.1",
}

# ===============================================================
# DEFINICIONES DE CÁLCULO (PROTOCOLO + Anclas AM: Enfoque Operacional)
# ===============================================================
DEF_C_OP = {
    "id": "DEF-C-OPERACIONAL",
    "tipo": "definicion",
    "sujeto": "Coherencia (C) - Operacional bajo anclas",
    "relacion": "definido_como",
    "objeto": "C = 1 - (k / m)  si m > 0;  UNDEFINED si m = 0",
    "polaridad": True,
    "enunciado": (
        "Coherencia operacional con anclas de medición:\n"
        "  1. m = número de compromisos de adopción propia (AM-D2).\n"
        "     Actos ('propongo…') no entran en el denominador.\n"
        "  2. k = suma de pesos de severidad de las contradicciones (AM-D5).\n"
        "     Pesos ∈ {1/4, 1/2, 3/4, 1}.\n"
        "  3. Si m = 0 → C = UNDEFINED (AM-D6 / AM-A3). No se asigna 1.\n"
        "  4. Si m > 0 → C = 1 - k/m  (Fraction exacta)."
    ),
    "formula": "C = 1 - (k / m)  si m > 0;  UNDEFINED si m = 0",
    "variables": {
        "m": "Número de compromisos de adopción propia (ancla de inclusión)",
        "k": "Suma de pesos de severidad de contradicciones (retícula AM-D5)",
    },
    "anclas": ["AM-D2", "AM-D5", "AM-D6", "AM-A3"],
    "fuente": "PROTOCOLO.pdf sec. 0.15 + anclas_medicion_AX + calculator/coherencia.py v2.0",
}

DEF_L_OP = {
    "id": "DEF-L-OPERACIONAL",
    "tipo": "definicion",
    "sujeto": "Lógica (L) - Operacional bajo anclas",
    "relacion": "definido_como",
    "objeto": "L = 1 - (r / p)  si p > 0;  UNDEFINED si p = 0",
    "polaridad": True,
    "enunciado": (
        "Lógica operacional con anclas de medición:\n"
        "  1. p = número de posturas / puntos de fijación (AM-D2).\n"
        "  2. r = suma de pesos de severidad de las reversiones (AM-D5).\n"
        "  3. Si p = 0 → L = UNDEFINED (AM-D6 / AM-A3). No se asigna 1.\n"
        "  4. Si p > 0 → L = 1 - r/p  (Fraction exacta)."
    ),
    "formula": "L = 1 - (r / p)  si p > 0;  UNDEFINED si p = 0",
    "variables": {
        "p": "Número de posturas / puntos de fijación (ancla de inclusión)",
        "r": "Suma de pesos de severidad de reversiones (retícula AM-D5)",
    },
    "anclas": ["AM-D2", "AM-D5", "AM-D6", "AM-A3"],
    "fuente": "PROTOCOLO.pdf sec. 0.15 + anclas_medicion_AX + calculator/logica.py v2.0",
}

DEF_K_OP = {
    "id": "DEF-K-OPERACIONAL",
    "tipo": "definicion",
    "sujeto": "Correlación (K) - Operacional bajo anclas",
    "relacion": "definido_como",
    "objeto": "K = 1 - (f / c)  si c > 0 y O presente;  UNDEFINED si c = 0 o sin O",
    "polaridad": True,
    "enunciado": (
        "Correlación operacional con anclas de medición:\n"
        "  1. Exige O_context explícito (Def-5.3.1). Sin él → UNDEFINED.\n"
        "  2. c = número de afirmaciones verificables respecto de O (AM-D2).\n"
        "  3. f = suma de pesos de severidad de las divergencias (AM-D5).\n"
        "  4. Si c = 0 → K = UNDEFINED (AM-D6 / AM-A3). No se asigna 1.\n"
        "  5. Si c > 0 y O presente → K = 1 - f/c  (Fraction exacta)."
    ),
    "formula": "K = 1 - (f / c)  si c > 0 ∧ O;  UNDEFINED si c = 0 ∨ ¬O",
    "variables": {
        "c": "Número de afirmaciones verificables respecto de O (ancla de inclusión)",
        "f": "Suma de pesos de severidad de divergencias con O (retícula AM-D5)",
        "O": "Dominio observable declarado (O_context)",
    },
    "anclas": ["AM-D2", "AM-D5", "AM-D6", "AM-A3", "Def-5.3.1"],
    "fuente": "PROTOCOLO.pdf sec. 0.15 + anclas_medicion_AX + calculator/correlacion_k.py v2.0",
}

# ===============================================================
# DEFINICIONES DE LAS FÓRMULAS CANÓNICAS
# ===============================================================
DEF_TRU_RI = {
    "id": "DEF-TRU-RI",
    "tipo": "definicion",
    "sujeto": "Tru_Ri",
    "relacion": "definido_como",
    "objeto": "Tru_Ri(D) = C(D) · L(D) · K(D)   (solo si C, L, K definidos)",
    "polaridad": True,
    "enunciado": (
        "Contribución del observador (R_i): Tru_Ri(D) = C(D) · L(D) · K(D). "
        "Si alguno de C, L, K es UNDEFINED, Tru_Ri = UNDEFINED. "
        "No se forma producto parcial ni se sustituye el factor faltante por 1."
    ),
    "formula": "Tru_Ri(D) = C · L · K  si todos definidos;  UNDEFINED en caso contrario",
    "fuente": "IlverVillasmil.pdf, Axioma TA5 + AM-A3",
}

DEF_TRU_TOTAL = {
    "id": "DEF-TRU-TOTAL",
    "tipo": "definicion",
    "sujeto": "Tru_total",
    "relacion": "definido_como",
    "objeto": "Tru_total(D) = (Tru_Ri(D) · ALPHA) + BETA",
    "polaridad": True,
    "enunciado": (
        "Verdad total: Tru_total(D) = (Tru_Ri(D) · α) + β. "
        "α = 26/27 (techo observable). β = 1/27 (piso estructural). "
        "Si Tru_Ri es UNDEFINED, Tru_total se reporta UNDEFINED; "
        "el piso β permanece como referencia estructural (T17)."
    ),
    "formula": "Tru_total(D) = (Tru_Ri · α) + β",
    "fuente": "IlverVillasmil.pdf, Definición 2.14 / Teorema 16 y 17",
}

# ===============================================================
# DECLARACIONES (Axiomas, anclas y teoremas relevantes)
# ===============================================================
DECLARACIONES = [
    # --- Anclas de medición (nuevas) ---
    {
        "id": "AM-D2",
        "tipo": "definicion",
        "sujeto": "Ancla de inclusión",
        "relacion": "exige",
        "objeto": "adopcion_propia_para_entrar_en_m_p_c",
        "polaridad": True,
        "enunciado": (
            "AM-D2: Solo las unidades de adopción propia (afirmación, obligación, "
            "autoatribución, compromiso metodológico) entran en los denominadores "
            "m, p, c. Los actos ('propongo', 'podríamos') no inflan el denominador."
        ),
        "fuente": "anclas_medicion_AX",
    },
    {
        "id": "AM-D5",
        "tipo": "definicion",
        "sujeto": "Retícula de severidad",
        "relacion": "restringe",
        "objeto": "pesos_de_k_r_f",
        "polaridad": True,
        "enunciado": (
            "AM-D5: k, r, f son sumas de pesos tomados de la retícula "
            "{1/4, 1/2, 3/4, 1}. No se usan pesos continuos arbitrarios."
        ),
        "fuente": "anclas_medicion_AX",
    },
    {
        "id": "AM-D6",
        "tipo": "definicion",
        "sujeto": "Base nula",
        "relacion": "implica",
        "objeto": "UNDEFINED",
        "polaridad": True,
        "enunciado": (
            "AM-D6: Si tras aplicar el ancla de inclusión m=0 (o p=0, o c=0), "
            "el factor correspondiente es UNDEFINED. No se asigna 1."
        ),
        "fuente": "anclas_medicion_AX",
    },
    {
        "id": "AM-A3",
        "tipo": "axioma",
        "sujeto": "Prohibición de maquillaje de base nula",
        "relacion": "prohíbe",
        "objeto": "asignar_1_cuando_denominador_es_0",
        "polaridad": True,
        "enunciado": (
            "AM-A3: Está prohibido devolver C=1, L=1 o K=1 cuando el denominador "
            "respectivo es 0. Eso inflaba Tru_Ri de forma artificial."
        ),
        "fuente": "anclas_medicion_AX",
    },
    {
        "id": "AM-A4",
        "tipo": "axioma",
        "sujeto": "Ortogonalidad de origen",
        "relacion": "exige",
        "objeto": "no_inventar_origenes_multiples_del_mismo_evento",
        "polaridad": True,
        "enunciado": (
            "AM-A4: Un mismo evento causal no inventa orígenes múltiples. "
            "Puede derivar efectos en más de un factor, pero el origen se declara una vez."
        ),
        "fuente": "anclas_medicion_AX",
    },
    # --- Ya existentes, reforzados ---
    {
        "id": "AX-COTA",
        "tipo": "axioma",
        "sujeto": "Cota de Tru_total",
        "relacion": "≥",
        "objeto": "BETA",
        "polaridad": True,
        "enunciado": "Tru_total(D) ≥ β = 1/27 (Teorema 17: Imposibilidad de Colapso Total).",
        "fuente": "IlverVillasmil.pdf, Teorema 17",
    },
    {
        "id": "AX-TECHO",
        "tipo": "axioma",
        "sujeto": "Techo de Tru_Ri",
        "relacion": "≤",
        "objeto": "1",
        "polaridad": True,
        "enunciado": (
            "Tru_Ri(D) ≤ 1. Tras multiplicar por α el aporte observable "
            "no supera 26/27 (Teorema 16: Techo Estructural)."
        ),
        "fuente": "IlverVillasmil.pdf, Teorema 16",
    },
    {
        "id": "AX-K-UNDEFINED",
        "tipo": "axioma",
        "sujeto": "K sin O_context",
        "relacion": "=",
        "objeto": "UNDEFINED",
        "polaridad": True,
        "enunciado": (
            "K(D) = UNDEFINED si no hay un O_context explícito. "
            "No es 0, es indefinido (Corolario Def-5.3.1)."
        ),
        "fuente": "IlverVillasmil.pdf, Corolario Def-5.3.1",
    },
    {
        "id": "AX-TRU-RI-UNDEFINED",
        "tipo": "axioma",
        "sujeto": "Tru_Ri con factor indefinido",
        "relacion": "=",
        "objeto": "UNDEFINED",
        "polaridad": True,
        "enunciado": (
            "Si C, L o K es UNDEFINED, Tru_Ri = UNDEFINED. "
            "No se forma producto parcial ni se sustituye el factor faltante por 1."
        ),
        "fuente": "AM-A3 + Axioma TA5",
    },
]

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "MECANICA",
    "VERSION",
    "PESO_ROCE",
    "PESO_PARCIAL",
    "PESO_GRAVE",
    "PESO_TOTAL",
    "RETICULA_SEVERIDAD",
    "DEF_C",
    "DEF_L",
    "DEF_K",
    "DEF_C_OP",
    "DEF_L_OP",
    "DEF_K_OP",
    "DEF_TRU_RI",
    "DEF_TRU_TOTAL",
    "DECLARACIONES",
]
