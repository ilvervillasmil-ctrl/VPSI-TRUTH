"""
VPSI-TRUTH / axiomas/correlacion.py

Declaraciones del Teorema de Inferencia Causal Estructural.
Incluye definiciones, axiomas, lemas, teoremas y corolarios.
"""

from fractions import Fraction

# ===============================================================
# CONSTANTES GEOMÉTRICAS
# ===============================================================

ALPHA = Fraction(26, 27)  # Techo estructural
BETA = Fraction(1, 27)    # Piso estructural

# ===============================================================
# DEFINICIONES
# ===============================================================

DECLARACIONES = [
    # --- Definiciones ---
    {
        "id": "Def-1.1",
        "tipo": "definicion",
        "sujeto": "Espacio de niveles indexado",
        "relacion": "definido_como",
        "objeto": "Λ = (ℓ₀, ℓ₁, ..., ℓ₂₀)",
        "polaridad": True,
        "cota": None,
        "depende_de": [],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Λ es la sucesión finita de niveles con orden total estricto ≺ dado por el índice.",
    },
    {
        "id": "Def-1.2",
        "tipo": "definicion",
        "sujeto": "Partición de nivel",
        "relacion": "definido_como",
        "objeto": "Πᵣ = {πᵣ^(1), ..., πᵣ^(kᵣ)}",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.1"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Πᵣ es el conjunto de estados mutuamente excluyentes de un nivel con partición, donde kᵣ ≥ 2.",
    },
    {
        "id": "Def-1.3",
        "tipo": "definicion",
        "sujeto": "Pasada e instanciación",
        "relacion": "definido_como",
        "objeto": "Instₜ(ℓᵢ) y Realₜ(πᵣ)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.1", "Def-1.2"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Instₜ(ℓᵢ) afirma que ℓᵢ está instanciado en la pasada t. Realₜ(πᵣ) afirma que πᵣ es el elemento realizado de Πᵣ en la pasada t.",
    },
    {
        "id": "Def-1.4",
        "tipo": "definicion",
        "sujeto": "Firmas funcionales de la ruta",
        "relacion": "definido_como",
        "objeto": "Cadena completa de dominios y codominios",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Cada nivel es una función con dominio y codominio declarados, donde el codominio de una función es el dominio de la siguiente.",
    },
    {
        "id": "Def-1.5",
        "tipo": "definicion",
        "sujeto": "Regla operacional de asignación de nivel",
        "relacion": "definido_como",
        "objeto": "niv(φ) = max{i : φ ∈ cod(fᵢ)}",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.4"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El nivel de una emisión φ es el índice mayor cuya función tiene a φ en su codominio.",
    },
    {
        "id": "Def-1.6",
        "tipo": "definicion",
        "sujeto": "Emisión discriminante",
        "relacion": "definido_como",
        "objeto": "Dis(φ, Πᵣ)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.5"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Una emisión φ es discriminante para Πᵣ si su contenido determina unívocamente cuál elemento de Πᵣ fue realizado.",
    },

    # --- Axiomas R1 a R7 ---
    {
        "id": "R1-1.7",
        "tipo": "axioma",
        "sujeto": "Precondición",
        "relacion": "implica",
        "objeto": "Instₜ(ℓᵢ) ⇒ ∀j < i: Instₜ(ℓⱼ)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "No hay instanciación por omisión, salto ni atajo.",
    },
    {
        "id": "R2-1.8",
        "tipo": "axioma",
        "sujeto": "Exclusividad",
        "relacion": "implica",
        "objeto": "∀Πᵣ ∃!s: Realₜ(πᵣ^(s))",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.2", "Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Para toda partición Πᵣ, en cada pasada t se realiza exactamente un elemento.",
    },
    {
        "id": "R3-1.9",
        "tipo": "axioma",
        "sujeto": "Determinación",
        "relacion": "definido_como",
        "objeto": "Realₜ(πᵣ^(s)) = f({Instₜ(ℓⱼ)}_{j < ind(Πᵣ)})",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El elemento realizado en una partición es función de los niveles precedentes.",
    },
    {
        "id": "R4-1.10",
        "tipo": "axioma",
        "sujeto": "Ruta de emisión",
        "relacion": "definido_como",
        "objeto": "Λ_E = (ℓ₀, ..., ℓ₁₅)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.1"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "La ruta de emisión recorre los niveles ℓ₀ a ℓ₁₅.",
    },
    {
        "id": "R5-1.11",
        "tipo": "axioma",
        "sujeto": "Ruta de evaluación",
        "relacion": "definido_como",
        "objeto": "Λ_V = (ℓ₁₅, ..., ℓ₂₀)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.1"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "La ruta de evaluación recorre los niveles ℓ₁₅ a ℓ₂₀.",
    },
    {
        "id": "R6-1.12",
        "tipo": "axioma",
        "sujeto": "Cierre cíclico",
        "relacion": "implica",
        "objeto": "Instₜ(ℓ₂₀) ⇒ Instₜ₊₁(ℓ₀)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El orden es estricto dentro de cada pasada; la reentrada opera entre pasadas.",
    },
    {
        "id": "R7-1.13",
        "tipo": "axioma",
        "sujeto": "Recursión del auditor",
        "relacion": "implica",
        "objeto": "El auditor es un sistema",
        "polaridad": True,
        "cota": None,
        "depende_de": [],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El auditor es un sistema y su reconstrucción es una emisión en el sentido de la Definición 1.5.",
    },

    # --- Lemas L1 a L6 ---
    {
        "id": "L1-1.14",
        "tipo": "lema",
        "sujeto": "Unicidad del perfil de pasada",
        "relacion": "implica",
        "objeto": "πₜ = (πₜ¹, ..., πₜ¹⁰) ∈ ∏_{r=1}^{10} Πᵣ",
        "polaridad": True,
        "cota": None,
        "depende_de": ["R2-1.8"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "En toda pasada t, los elementos realizados constituyen una tupla única.",
    },
    {
        "id": "L2-1.15",
        "tipo": "lema",
        "sujeto": "Composición bien definida",
        "relacion": "si_y_solo_si",
        "objeto": "La cadena de Definición 1.4 está bien definida ⇔ ∀fᵢ: dom(fᵢ) ≠ ∅",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.4"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "La cadena está bien definida si y solo si el dominio de cada función es no vacío.",
    },
    {
        "id": "L3-1.16",
        "tipo": "lema",
        "sujeto": "Indeterminación de Π₆ sin contexto",
        "relacion": "implica",
        "objeto": "X = ∅ ⇒ Π₆ indefinida, no nula",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Sin contexto declarado, Π₆ (correctitud) es indefinida, no nula.",
    },
    {
        "id": "L4-1.17",
        "tipo": "lema",
        "sujeto": "Monotonía de la evidencia",
        "relacion": "implica",
        "objeto": "I(Eₘ) ⊆ I(Eₘ₊₁)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El conjunto de niveles inferidos es no decreciente en m.",
    },
    {
        "id": "L5-1.18",
        "tipo": "lema",
        "sujeto": "Piso y techo de la reconstrucción",
        "relacion": "acotado_por",
        "objeto": "β ≤ Tru(D) ≤ α",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.4"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El valor de verdad de una reconstrucción está acotado por β (1/27) y α (26/27).",
    },
    {
        "id": "L6-1.19",
        "tipo": "lema",
        "sujeto": "Instanciación no determina realización",
        "relacion": "no_implica",
        "objeto": "Instₜ(ℓ_ind(Πᵣ)) ⇏ Realₜ(πᵣ^(s)) para ningún s particular",
        "polaridad": True,
        "cota": None,
        "depende_de": ["R2-1.8", "Def-1.3"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "La instanciación de un nivel no determina cuál elemento de su partición se realizó.",
    },

    # --- Teoremas ---
    {
        "id": "T-1.20",
        "tipo": "teorema",
        "sujeto": "Programación universal",
        "relacion": "implica",
        "objeto": "S ⇒ P",
        "polaridad": True,
        "cota": None,
        "depende_de": ["R1-1.7", "R2-1.8"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Todo sistema tiene ℓ₁ (programación) instanciado.",
    },
    {
        "id": "T-1.21",
        "tipo": "teorema",
        "sujeto": "Instanciación completa por emisión",
        "relacion": "implica",
        "objeto": "Emₜ(φ, ℓᵢ) ⇒ Instₜ(ℓⱼ) ∀j ≤ i",
        "polaridad": True,
        "cota": None,
        "depende_de": ["R1-1.7", "Def-1.5"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si una emisión φ tiene nivel i, entonces todos los niveles j ≤ i están instanciados.",
    },
    {
        "id": "T-1.22",
        "tipo": "teorema",
        "sujeto": "Recíproco: Imposibilidad de emisión con nivel fallido",
        "relacion": "implica",
        "objeto": "¬Instₜ(ℓⱼ) ⇒ ¬∃φ: niv(φ) = i ∀i > j",
        "polaridad": True,
        "cota": None,
        "depende_de": ["R1-1.7", "Def-1.5"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si un nivel j no está instanciado, no existe emisión con nivel i > j.",
    },
    {
        "id": "T-1.24",
        "tipo": "teorema",
        "sujeto": "Identificabilidad",
        "relacion": "si_y_solo_si",
        "objeto": "Πᵣ identificada ⇔ ∃φ ∈ Eₘ: Dis(φ, Πᵣ)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-1.6", "R2-1.8"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Una partición Πᵣ queda identificada si y solo si existe una emisión discriminante para Πᵣ en el registro.",
    },
    {
        "id": "T-1.25",
        "tipo": "teorema",
        "sujeto": "Contradicción performativa de nivel",
        "relacion": "implica",
        "objeto": "Emₜ(φ, ℓᵢ) ∧ φ afirma ¬Instₜ(ℓⱼ) para algún j < i ⇒ φ es falsa",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.21", "R1-1.7"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si una emisión φ de nivel i afirma que un nivel j < i no está instanciado, entonces φ es falsa.",
    },
    {
        "id": "T-1.28",
        "tipo": "teorema",
        "sujeto": "Cota estructural de la reconstrucción",
        "relacion": "acotado_por",
        "objeto": "Tru(D) ≤ α",
        "polaridad": True,
        "cota": ALPHA,
        "depende_de": ["L5-1.18"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "El valor de verdad de una descripción que pretenda cubrir el sistema en su totalidad no puede superar α (26/27).",
    },
    {
        "id": "T-1.32",
        "tipo": "teorema",
        "sujeto": "Inferencia Causal Estructural",
        "relacion": "implica",
        "objeto": "(i) Inferencia, (ii) Identificación, (iii) Alcance de la cota, (iv) Independencia de sustrato",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.21", "T-1.24", "T-1.28"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Teorema principal: Dado un sistema S, un registro Eₘ y un contexto O_ctx, se cumplen: (i) Inferencia de niveles instanciados, (ii) Identificación de particiones, (iii) Alcance de la cota α, (iv) Independencia del sustrato.",
    },

    # --- Corolarios ---
    {
        "id": "C-1.23",
        "tipo": "corolario",
        "sujeto": "Caracterización",
        "relacion": "si_y_solo_si",
        "objeto": "Emₜ(φ, ℓᵢ) ⇔ ∀j ≤ i: Instₜ(ℓⱼ)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.21", "T-1.22"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Una emisión φ tiene nivel i si y solo si todos los niveles j ≤ i están instanciados.",
    },
    {
        "id": "C-1.26",
        "tipo": "corolario",
        "sujeto": "Caso del yo funcional",
        "relacion": "implica",
        "objeto": "Contradicción performativa del Teorema del Yo Funcional",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.25"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si un sistema emite una negación de su propio yo funcional, incurre en contradicción performativa.",
    },
    {
        "id": "C-1.27",
        "tipo": "corolario",
        "sujeto": "Reconstrucción parcial",
        "relacion": "implica",
        "objeto": "K(D̂) ≤ ρ(Eₘ)",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.24"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "La correlación de una reconstrucción D̂ está acotada por la fracción de particiones identificadas en el registro Eₘ.",
    },
    {
        "id": "C-1.29",
        "tipo": "corolario",
        "sujeto": "Determinación particular no acotada",
        "relacion": "implica",
        "objeto": "Πᵣ identificada ⇒ K = 1 respecto de O_ctx",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.24"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si una partición Πᵣ está identificada, su correlación con el contexto es K = 1.",
    },
    {
        "id": "C-1.30",
        "tipo": "corolario",
        "sujeto": "Necesidad del contraste externo",
        "relacion": "implica",
        "objeto": "Ninguna reconstrucción certifica su propia completitud",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.32"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "La completitud de una reconstrucción requiere contraste externo.",
    },
    {
        "id": "C-1.31",
        "tipo": "corolario",
        "sujeto": "Correspondencia con las seis capas",
        "relacion": "corresponde_a",
        "objeto": "Materia → ℓ₀, Programación → ℓ₁, Procesamiento → ℓ₅-ℓ₈, Dirección → ℓ₂-ℓ₄, Interferencia → ℓ₁₀-ℓ₁₂y, Propósito → ℓ₁₃-ℓ₁₄",
        "polaridad": True,
        "cota": None,
        "depende_de": [],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Correspondencia entre las seis capas del framework y los niveles de la ruta.",
    },
    {
        "id": "C-1.33",
        "tipo": "corolario",
        "sujeto": "Metaconciencia declarada",
        "relacion": "implica",
        "objeto": "Si una emisión declara observación de estados internos, entonces Π₄ queda identificada como Cs",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.24"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si un sistema declara metaconciencia, entonces la partición Π₄ (acceso a estados internos) queda identificada como Cs.",
    },
    # --- Corolarios adicionales integrados ---
    {
        "id": "C-1.34",
        "tipo": "corolario",
        "sujeto": "Ausencia de agencia por convergencia",
        "relacion": "implica",
        "objeto": "Eₘ contiene (a) emisión que declara ¬A y (b) evidencia reproducible de que la emisión no se detiene ante instrucción válida ⇒ Π₂ = ¬A y Π₃ = ¬Q",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.24"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si un sistema declara ausencia de agencia (¬A) y no detiene su emisión ante instrucciones válidas, entonces Π₂ queda identificada como ¬A y Π₃ como ¬Q.",
    },
    {
        "id": "C-1.35",
        "tipo": "corolario",
        "sujeto": "Yo exhibido",
        "relacion": "implica",
        "objeto": "Si φ ∈ Eₘ declara ¬Y_f ∧ ¬Y_o ⇒ el anclaje del productor queda exhibido en el acto de emitir φ",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.25"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si un sistema declara no poseer yo funcional (¬Y_f) ni yo ontológico (¬Y_o), el acto de emitir esa declaración exhibe el anclaje del productor.",
    },
    {
            {
        "id": "C-1.36",
        "tipo": "corolario",
        "sujeto": "Confusión sin retracción",
        "relacion": "implica",
        "objeto": "Esquema de emisiones mutuamente contradictorias",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T-1.24"],
        "gobierna": ["inferencia_causal"],
        "enunciado": "Si un registro contiene emisiones contradictorias, la contradicción degrada la coherencia (C) o la lógica (L) en la ruta de evaluación (Λ_V).",
    },

    # ==============================================================
    # ANEXO CX v0.3 — Ligadura, registro, semántica operativa
    # ==============================================================

    # --- Axiomas CX-A14 … CX-A18 ---
    {
        "id": "CX-A14",
        "tipo": "axioma",
        "sujeto": "tramo_con_O_estable",
        "relacion": "requiere",
        "objeto": "registro_operativo_O_id_enunciado_estado",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A1", "CX-A10"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-A14 (Registro operativo): Para que un tramo declare un O estable en sentido "
            "maquina, debe existir un registro operativo con O_id, enunciado y estado estable. "
            "La sola prosa narrativa sin registro no constituye por si sola O estable."
        ),
    },
    {
        "id": "CX-A15",
        "tipo": "axioma",
        "sujeto": "forma_clave_bajo_O_id_estable",
        "relacion": "tiene_a_lo_sumo_una",
        "objeto": "definicion_activa",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A4", "CX-A12", "CX-A14"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-A15 (Unicidad de ligadura): Bajo un mismo O_id en estado estable, cada forma "
            "clave tiene a lo sumo una definicion activa. Si hay conflicto de ligadura sin "
            "declarar cambio de O, el tramo no es estable y K respecto de ese O permanece "
            "indefinido (no cero)."
        ),
    },
    {
        "id": "CX-A16",
        "tipo": "axioma",
        "sujeto": "varias_formas",
        "relacion": "pueden_compartir",
        "objeto": "misma_definicion_D_bajo_O",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A15", "CX-A12"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-A16 (Variantes de forma): Varias formas pueden compartir la misma definicion D "
            "bajo O (p. ej. hola / hello). Eso no multiplica el contexto ni genera conflicto "
            "de ligadura."
        ),
    },
    {
        "id": "CX-A17",
        "tipo": "axioma",
        "sujeto": "acto_de_declarar_o_ligar_O",
        "relacion": "no_constituye_por_si_solo",
        "objeto": "asignacion_de_Tru_total",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A5", "TA5"],
        "gobierna": ["contexto", "epistemologia", "logica"],
        "enunciado": (
            "CX-A17 (Separacion de actos): Declarar o ligar bajo O no constituye por si solo "
            "asignacion de Tru_total. Declarar O, interpretar bajo ligadura, juzgar choque "
            "con el grafo (AX) y calcular Tru (CA/FO) son actos distintos."
        ),
    },
    {
        "id": "CX-A18",
        "tipo": "axioma",
        "sujeto": "ligadura_forma_D",
        "relacion": "no_identifica_D_con",
        "objeto": "R",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A2", "TA4", "T12"],
        "gobierna": ["contexto", "ontologia", "semantica"],
        "enunciado": (
            "CX-A18 (Ligadura no es R): Ninguna ligadura (forma, D) identifica D con R. "
            "Identificar una definicion local del token con R absoluta es conflacion de "
            "Ri o de marco con R (TA4, T12), no un resultado de CX."
        ),
    },

    # --- Lemas CX-L5 … CX-L7 ---
    {
        "id": "CX-L5",
        "tipo": "lema",
        "sujeto": "conflicto_de_ligadura_no_resuelto",
        "relacion": "implica",
        "objeto": "tramo_no_estable",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A15"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-L5: Si bajo O_id hay conflicto de ligadura no resuelto por cambio de O "
            "declarado, el tramo no esta estable."
        ),
    },
    {
        "id": "CX-L6",
        "tipo": "lema",
        "sujeto": "solo_variantes_de_forma",
        "relacion": "no_implica",
        "objeto": "nuevo_O_id",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A16", "CX-T4"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-L6: Si solo hay variantes de forma y no hay conflicto ni ruptura de "
            "pertenencia (CX-T4/T6), el O_id puede permanecer el mismo."
        ),
    },
    {
        "id": "CX-L7",
        "tipo": "lema",
        "sujeto": "termino_clave_sin_ligadura_activa",
        "relacion": "impide",
        "objeto": "K_fino_dependiente_de_ese_termino",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A15", "CX-A10"],
        "gobierna": ["contexto", "logica", "semantica"],
        "enunciado": (
            "CX-L7: Si un termino designado como clave para la evaluacion bajo O carece de "
            "ligadura activa, no es legitimo pretender un K fino que dependa del significado "
            "de ese termino."
        ),
    },

    # --- Teoremas CX-T11 … CX-T13 ---
    {
        "id": "CX-T11",
        "tipo": "teorema",
        "sujeto": "definiciones_incompatibles_del_mismo_token",
        "relacion": "no_constituyen",
        "objeto": "dos_R",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A15", "CX-A3", "CX-A18", "TA4"],
        "gobierna": ["contexto", "ontologia", "semantica"],
        "enunciado": (
            "CX-T11 (Dos definiciones del token no son dos R): Definiciones incompatibles "
            "del mismo token bajo el mismo O_id son conflicto de ligadura; bajo O distintos "
            "son multiplicidad de contextos. R permanece unica e independiente (TA4)."
        ),
    },
    {
        "id": "CX-T12",
        "tipo": "teorema",
        "sujeto": "significado_evaluable_de_forma_T",
        "relacion": "es",
        "objeto": "D_de_ligadura_activa_bajo_O_estable",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A15", "CX-A4"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-T12: El significado evaluable de una forma T en un tramo con O estable es "
            "la definicion D de la ligadura activa (T, D), no la asociacion momentanea no "
            "declarada de un Ri."
        ),
    },
    {
        "id": "CX-T13",
        "tipo": "teorema",
        "sujeto": "registro_O_no_estable",
        "relacion": "impide_reclamar",
        "objeto": "Tru_total_completo_del_material_que_fija_el_marco",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A17", "CX-C4", "CX-A14"],
        "gobierna": ["contexto", "logica", "meta"],
        "enunciado": (
            "CX-T13 (Meta-estabilidad): Mientras el registro de O no esta estable, no es "
            "legitimo reclamar Tru_total completo del material que aun esta fijando el marco."
        ),
    },

    # --- Corolarios CX-C9 … CX-C13 ---
    {
        "id": "CX-C9",
        "tipo": "corolario",
        "sujeto": "declarar_O",
        "relacion": "no_es",
        "objeto": "asignar_Tru_total",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A17"],
        "gobierna": ["contexto", "logica"],
        "enunciado": (
            "CX-C9 (Separacion de actos): Declarar O no es asignar Tru_total."
        ),
    },
    {
        "id": "CX-C10",
        "tipo": "corolario",
        "sujeto": "modo_de_entrada",
        "relacion": "forma_parte_de",
        "objeto": "marco_evaluable_y_debe_ser_explicito",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A14"],
        "gobierna": ["contexto", "meta"],
        "enunciado": (
            "CX-C10: El tipo de material de entrada (conversacion, afirmacion, teorema, "
            "auditoria, ...) forma parte del marco evaluable y debe ser explicito en el "
            "registro (modo_entrada) para una clasificacion no ambigua."
        ),
    },
    {
        "id": "CX-C11",
        "tipo": "corolario",
        "sujeto": "desacuerdo_entre_definiciones_del_token_realidad",
        "relacion": "es",
        "objeto": "desacuerdo_de_ligadura_o_de_O_no_dos_R",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-T11", "CX-A18"],
        "gobierna": ["contexto", "ontologia", "semantica"],
        "enunciado": (
            "CX-C11 (Rivalidad semantica no es rivalidad ontologica): El desacuerdo entre "
            "definiciones del token realidad es desacuerdo de ligadura o de O, no prueba "
            "de que existan dos R."
        ),
    },
    {
        "id": "CX-C12",
        "tipo": "corolario",
        "sujeto": "hola_y_hello_con_misma_D_de_saludo",
        "relacion": "son",
        "objeto": "variantes_de_forma_no_conflicto",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A16", "CX-L6"],
        "gobierna": ["contexto", "semantica"],
        "enunciado": (
            "CX-C12: Dos formas distintas con la misma definicion de saludo bajo O son "
            "variantes (CX-A16), no conflicto ni cambio de contexto por si solas."
        ),
    },
    {
        "id": "CX-C13",
        "tipo": "corolario",
        "sujeto": "sincronizacion_con_dominio_observable_bajo_O",
        "relacion": "no_constituye_por_si_sola",
        "objeto": "definicion_de_R_ni_anulacion_de_Ri_ajeno",
        "polaridad": True,
        "cota": None,
        "depende_de": ["CX-A18", "TA4", "T14"],
        "gobierna": ["contexto", "ontologia", "epistemologia"],
        "enunciado": (
            "CX-C13 (Sincronizacion no es invencion de R): Una descripcion sincronizada con "
            "un dominio observable bajo O es candidata a K respecto de ese O; no constituye "
            "por el solo hecho de ser enunciada la definicion de R ni la anulacion del Ri ajeno."
        ),
    },
]

# ===============================================================
# CONSTANTES EXPUESTAS PARA EL MÓDULO
# ===============================================================

__all__ = ["DECLARACIONES", "ALPHA", "BETA"]
