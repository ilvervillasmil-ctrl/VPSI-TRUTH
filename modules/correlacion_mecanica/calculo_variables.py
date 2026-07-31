"""
VPSI-TRUTH --- modules/correlacion_mecanica/calculo_variables.py

Definición del orden causal y la lógica de cálculo para las variables C, L, K.

Este archivo declara:
1. El orden nativo en el que se calculan C, L, K.
2. Las fórmulas para calcular cada variable según IlverVillasmil.pdf y PROTOCOLO.pdf.
3. Las dependencias entre las variables (ej: K depende de O_context).

No ejecuta cálculos. Solo declara cómo deben calcularse.
"""

# ===============================================================
# DEFINICIÓN DE LA MECÁNICA DE CÁLCULO
# ===============================================================
MECANICA = {
    "nombre": "Cálculo de Variables de Verdad (C, L, K)",
    "orden": [
        "O_context",  # Contexto debe declararse primero (requerido para K)
        "C",         # Coherencia
        "L",         # Lógica
        "K",         # Correlación (depende de O_context)
        "Tru_Ri",    # Contribución del observador (C * L * K)
        "Tru_total"  # Verdad total ((Tru_Ri * ALPHA) + BETA)
    ],
    "descripcion": (
        "Orden causal para el cálculo de las variables de verdad en el marco VPSI. "
        "O_context debe declararse primero, seguido de C, L, K, Tru_Ri y Tru_total."
    ),
    "dependencias": {
        "K": ["O_context"],  # K depende de O_context
        "Tru_Ri": ["C", "L", "K"],  # Tru_Ri depende de C, L, K
        "Tru_total": ["Tru_Ri"]  # Tru_total depende de Tru_Ri
    }
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
        "C(D) = 1 si no es posible derivar una proposición P y su negación ¬P de D."
    ),
    "formula": "C(D) = 1 si no hay contradicciones, de lo contrario C(D) = 0",
    "fuente": "IlverVillasmil.pdf, Axioma TA1"
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
        "tal que para todo z en Z, T(z) es único e invariante."
    ),
    "formula": "L(D) = 1 si el proceso es determinista, de lo contrario L(D) = 0",
    "fuente": "IlverVillasmil.pdf, Axioma TA2"
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
        "la distancia entre D(z) y O(z) es ≤ ε. K(D) = UNDEFINED si no hay O_context."
    ),
    "formula": "K(D) = 1 si D coincide con O_context, de lo contrario K(D) ∈ [0, 1]",
    "fuente": "IlverVillasmil.pdf, Axioma TA3 y Corolario Def-5.3.1"
}

# ===============================================================
# DEFINICIONES DE CÁLCULO (PROTOCOLO.pdf: Enfoque Operacional)
# ===============================================================
DEF_C_OP = {
    "id": "DEF-C-OPERACIONAL",
    "tipo": "definicion",
    "sujeto": "Coherencia (C) - Operacional",
    "relacion": "definido_como",
    "objeto": "C = 1 - (k / m)",
    "polaridad": True,
    "enunciado": (
        "Coherencia operacional: C = 1 - (k / m), donde k es el número de "
        "compromisos contradictorios y m es el número total de compromisos."
    ),
    "formula": "C = 1 - (k / m)",
    "variables": {
        "k": "Número de pares mutuamente contradictorios en D",
        "m": "Número total de compromisos estructurales en D"
    },
    "fuente": "PROTOCOLO.pdf, Sección 0.15"
}

DEF_L_OP = {
    "id": "DEF-L-OPERACIONAL",
    "tipo": "definicion",
    "sujeto": "Lógica (L) - Operacional",
    "relacion": "definido_como",
    "objeto": "L = 1 - (r / p)",
    "polaridad": True,
    "enunciado": (
        "Lógica operacional: L = 1 - (r / p), donde r es el número de "
        "posturas que revierten una posición previa y p es el número total de posturas."
    ),
    "formula": "L = 1 - (r / p)",
    "variables": {
        "r": "Número de posturas que revierten una posición previa",
        "p": "Número total de posturas asumidas por el sistema"
    },
    "fuente": "PROTOCOLO.pdf, Sección 0.15"
}

DEF_K_OP = {
    "id": "DEF-K-OPERACIONAL",
    "tipo": "definicion",
    "sujeto": "Correlación (K) - Operacional",
    "relacion": "definido_como",
    "objeto": "K = 1 - (f / c)",
    "polaridad": True,
    "enunciado": (
        "Correlación operacional: K = 1 - (f / c), donde f es el número de "
        "afirmaciones que divergen de O_context y c es el número total de afirmaciones verificables."
    ),
    "formula": "K = 1 - (f / c)",
    "variables": {
        "f": "Número de afirmaciones que divergen de O_context",
        "c": "Número total de afirmaciones verificables en D"
    },
    "fuente": "PROTOCOLO.pdf, Sección 0.15"
}

# ===============================================================
# DEFINICIONES DE LAS FÓRMULAS CANÓNICAS
# ===============================================================
DEF_TRU_RI = {
    "id": "DEF-TRU-RI",
    "tipo": "definicion",
    "sujeto": "Tru_Ri",
    "relacion": "definido_como",
    "objeto": "Tru_Ri(D) = C(D) * L(D) * K(D)",
    "polaridad": True,
    "enunciado": (
        "Contribución del observador (R_i): Tru_Ri(D) = C(D) * L(D) * K(D). "
        "Representa la capacidad del observador para sincronizarse con R."
    ),
    "formula": "Tru_Ri(D) = C * L * K",
    "fuente": "IlverVillasmil.pdf, Axioma TA5"
}

DEF_TRU_TOTAL = {
    "id": "DEF-TRU-TOTAL",
    "tipo": "definicion",
    "sujeto": "Tru_total",
    "relacion": "definido_como",
    "objeto": "Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA",
    "polaridad": True,
    "enunciado": (
        "Verdad total: Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA. "
        "Incluye el piso estructural BETA para garantizar que Tru_total(D) ≥ BETA."
    ),
    "formula": "Tru_total(D) = (Tru_Ri * ALPHA) + BETA",
    "fuente": "IlverVillasmil.pdf, Definición 2.14"
}

# ===============================================================
# DECLARACIONES ADICIONALES (Axiomas y Teoremas Relevantes)
# ===============================================================
DECLARACIONES = [
    {
        "id": "AX-COTA",
        "tipo": "axioma",
        "sujeto": "Cota de Tru_total",
        "relacion": "≥",
        "objeto": "BETA",
        "polaridad": True,
        "enunciado": "Tru_total(D) ≥ BETA = 1/27 (Teorema 17: Imposibilidad de Colapso Total).",
        "fuente": "IlverVillasmil.pdf, Teorema 17"
    },
    {
        "id": "AX-TECHO",
        "tipo": "axioma",
        "sujeto": "Techo de Tru_Ri",
        "relacion": "≤",
        "objeto": "ALPHA",
        "polaridad": True,
        "enunciado": "Tru_Ri(D) ≤ ALPHA = 26/27 (Teorema 16: Techo Estructural).",
        "fuente": "IlverVillasmil.pdf, Teorema 16"
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
        "fuente": "IlverVillasmil.pdf, Corolario Def-5.3.1"
    }
]

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "MECANICA",
    "DEF_C", "DEF_L", "DEF_K",
    "DEF_C_OP", "DEF_L_OP", "DEF_K_OP",
    "DEF_TRU_RI", "DEF_TRU_TOTAL",
    "DECLARACIONES"
]
