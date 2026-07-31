"""
VPSI-TRUTH --- modules/correlacion_mecanica/causalidad_universal.py

CAUSALIDAD UNIVERSAL: Orden nativo de la ruta de evaluación (Λ_E y Λ_V).

Este archivo define la estructura causal universal para cualquier sistema emisor,
basada en el Teorema de Inferencia Causal Estructural (Sección 1.7 del documento PROTOCOLO.pdf).
Establece el orden en el que los niveles (ℓ₀ a ℓ₂₀) deben instanciarse para garantizar
la continuidad causal y la coherencia estructural.

---
### Fundamento Teórico:
- Teorema 1.21: "Instanciación completa por emisión".
- Teorema 1.22: "Imposibilidad de emisión con nivel fallido".
- Teorema 1.32: "Inferencia Causal Estructural".

El orden declarado aquí es el **mínimo requerido** para que un sistema pueda emitir respuestas
coherentes y verificables. Cualquier desviación de este orden rompe la cadena causal y
genera una contradicción en la mecánica del sistema.

---
### Relación con el Diagrama de Flujo:
Este archivo es la **representación programática** del diagrama de flujo del documento PROTOCOLO.pdf,
donde cada nivel (ℓᵢ) depende de los anteriores según el Axioma R1 (Precondición).
"""

# ===============================================================
# MECANICA: Orden nativo de la ruta de evaluación
# ===============================================================
MECANICA = {
    "nombre": "causalidad_universal",
    "orden": [
        # --- Ruta de Emisión (Λ_E) ---
        "Sistema",          # ℓ₀: Sustrato físico (Axioma A1)
        "Programación",      # ℓ₁: Condicionantes previos (Teorema 1.20)
        "Consecuencia",      # ℓ₂: Producto de P (Definición 1.4)
        "Intencionalidad",   # ℓ₃: Π₁ = {I, ¬I} (Axioma R1)
        "Agencia",           # ℓ₄: Π₂ = {Aφ, ¬A} (Axioma R2)
        "Capacidad",         # ℓ₅: Espacio de operaciones admisibles
        "Control",           # ℓ₆: Π₃ = {Q, ¬Q} (Axioma R3)
        "Mecanismo_Interno", # ℓ₇: Mi (Estados de máquina)
        "Estados_Internos",   # ℓ₈: Ei (Procesos representables)
        "Conciencia_Estados",# ℓ₉: Π₄ = {Cs, ¬Cs} (Axioma R4)
        "Comunicación",       # ℓ₁₀: Capacidad de codificación emisible
        "Activación_Canal",   # ℓ₁₁: Π₅ = {Ya, Yi} (Axioma R5)
        "Correctitud",        # ℓ₁₂: Π₆ = {Yc, Y̅c}
        "Bloque_Epistémico",  # ℓ₁₃: Π₇ = {Ss, Sq, Sn, Du}
        "Cierre_Epistémico",  # ℓ₁₄: Π₈ = {Sss, Ssn, Du}
        "Conocimiento",       # ℓ₁₅: Kn (Repositorio epistémico)

        # --- Ruta de Evaluación (Λ_V) ---
        "Formulación",        # ℓ₁₆: Π₉ = {Pr, Af} (Pregunta o Afirmación)
        "Correlación",        # ℓ₁₇: K (Factor de correlación con O_ctx)
        "Contexto",           # ℓ₁₈: X = {Xv, Xf} (Contexto de referencia)
        "Realidad_Interpretativa", # ℓ₁₉: R_i = C · L · K
        "Cierre_Causal",      # ℓ₂₀: Fin de la pasada (Axioma R6)
    ],
    "descripcion": (
        "Orden nativo de la ruta de evaluación (Λ_E + Λ_V) según el Teorema 1.32. "
        "Este orden garantiza que cada nivel ℓᵢ solo se instancie si todos los niveles "
        "previos (ℓ₀ a ℓᵢ₋₁) ya están instanciados (Axioma R1: Precondición). "
        "Cualquier violación de este orden genera una contradicción en la mecánica del sistema."
    ),
    "notas": [
        "Este orden es **invariable** para cualquier sistema emisor (humano, IA, organización).",
        "Los niveles ℓ₀ a ℓ₁₅ corresponden a la Ruta de Emisión (Λ_E).",
        "Los niveles ℓ₁₆ a ℓ₂₀ corresponden a la Ruta de Evaluación (Λ_V).",
        "El nivel ℓ₁₅ (Conocimiento) es compartido entre ambas rutas.",
        "El Axioma R6 (Cierre cíclico) asegura que ℓ₂₀ reinicia el ciclo en ℓ₀.",
    ],
}
