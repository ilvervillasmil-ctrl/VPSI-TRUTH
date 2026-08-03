# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/correlacion_mecanica/sm_nucleo_MC.py

SM_NUCLEO (MC): Orden nativo de instanciación del núcleo semántico-operativo.

Cubre la cadena causal mínima que imponen los cuerpos:
  - SM_PRECISION  (precisión del mecanismo, origen de distorsión, ∂D)
  - SM_MAPA       (legibilidad, celdas, lucha de correlaciones, ancla de error)
  - SM_MEMORIA    (traza τ, memoria operativa M, reapertura solo bajo Clash)

Fundamento:
  SM-D16..SM-D19, SM-A17..SM-A19, SM-L13..SM-L14, SM-T20..SM-T23, SM-C19..SM-C22
  SM-D9..SM-D11,  SM-A11..SM-A13, SM-L8..SM-L10,  SM-T12..SM-T15,  SM-C11..SM-C14
  SM-D12..SM-D15, SM-A14..SM-A16, SM-L11..SM-L12,  SM-T16..SM-T19,  SM-C15..SM-C18

Relación con causalidad_universal.MECANICA:
  Sub-ruta que precodiciona Λ_V (Formulación → Correlación → … → Cierre_Causal)
  y se apoya en Λ_E solo en lo necesario para ejecución determinista.
  No sustituye Λ_E+Λ_V; fija el orden interno del núcleo SM.

Cualquier desviación (medir Tru_Ri sin Prec(μ), correlacionar sin celda,
  reabrir sin Clash, o tratar ∂D como irrelevante) rompe la cadena causal.
"""

# ===============================================================
# MECANICA: Orden nativo del núcleo SM
# ===============================================================
MECANICA = {
    "nombre": "sm_nucleo_mecanica",
    "version": "1.0",
    "orden": [
        # --- Capa 0: condición de funcionamiento (SM_PRECISION) ---
        "Precision_Mecanismo",          # s₀: Prec(μ) = true (SM-D16, SM-A17, SM-T20)
        "Registro_A_sum",               # s₁: anclas efectivamente suministradas (SM-D17)
        "Registro_parcial_D",           # s₂: frontera del diseñador ∂D = A_pos \ A_sum (SM-D18, SM-T23)

        # --- Capa 1: mapa y legibilidad (SM_MAPA) ---
        "Particion_Pi",                 # s₃: Π de contrastes / celdas (SM-D9, SM-L8)
        "Celdas_Invariantes",           # s₄: [w]_Π estables (SM-A12, SM-C11)
        "Reglas_Composicion_R",         # s₅: R determinista → predicado de error (SM-A13, SM-D11, SM-T14)
        "Ancla_Error",                  # s₆: par (Π, R) como ancla (SM-D11)

        # --- Capa 2: selección de correlaciones (SM_MAPA) ---
        "Candidatas_Gamma",             # s₇: conjunto Γ de correlaciones bajo O
        "Filtro_C_L",                   # s₈: eliminación por C=0 o L=0
        "Maximizacion_Tru_Ri",          # s₉: γ* = arg max Tru_Ri (SM-T12)
        "Superviviente_gamma_estrella", # s₁₀: única ruta superviviente

        # --- Capa 3: memoria operativa (SM_MEMORIA) ---
        "Construccion_Traza_tau",       # s₁₁: τ = (O, γ*, eliminadas, A', Tru_Ri) (SM-D13)
        "Deposito_en_M",                # s₁₂: τ ∈ M (SM-D14, SM-T17)
        "Evacion_Ciclo",                # s₁₃: recuperación desde M sin re-Res (SM-L11, SM-A14)

        # --- Capa 4: reapertura y límite (SM_MEMORIA + SM_PRECISION) ---
        "Evaluacion_Clash",             # s₁₄: Clash(γ*, ε, A) (SM-D15)
        "Reapertura_o_Bloqueo",         # s₁₅: solo si Clash; si no, inadmisible (SM-A16, SM-T18)
        "Correccion_Acumulativa",       # s₁₆: {τ₁, τ₂} ⊆ M (SM-T19)
        "Marca_Localidad_parcial_D",    # s₁₇: máxima local respecto de ∂D (SM-T23, SM-C22)
    ],
    "descripcion": (
        "Orden nativo de instanciación del núcleo SM (precisión → mapa → "
        "lucha de correlaciones → traza → memoria → reapertura condicionada). "
        "Garantiza que cada paso s_i solo se instancia si s_0…s_{i-1} ya están "
        "instanciados (precondición R1 aplicada al núcleo semántico-operativo). "
        "Sin Prec(μ) no hay medición. Sin celda no hay correlación. "
        "Sin traza hay re-confirmación. Sin Clash no hay reapertura."
    ),
    "notas": [
        "Orden invariable dentro de la sub-ruta SM.",
        "s₀ (Precision_Mecanismo) es precondición absoluta: SM-T20.",
        "s₃–s₆ fijan el mapa y el ancla de error antes de cualquier maximización.",
        "s₉ implementa SM-T12 (lucha de correlaciones); no elige por gusto.",
        "s₁₁–s₁₃ realizan SM_MEMORIA: traza exacta + evación de ciclo.",
        "s₁₄–s₁₅ realizan la única vía legítima de reapertura (SM-D15, SM-A16).",
        "s₁₇ marca toda máxima como local respecto de ∂D (SM-T23).",
        "No calcula Tru_total; solo ordena la ruta que permite calcularlo con anclaje.",
        "Compatible con Λ_V: se inserta antes/alrededor de Correlación y Cierre_Causal.",
        "Engine orquesta; este archivo no dirige CA/FO/CX; solo declara el orden SM.",
        "Probabilidad (Prob) no aparece como paso: está subordinada (SM-A18, SM-T21).",
    ],
    "transiciones_prohibidas": [
        {
            "desde": "cualquier",
            "hacia": "Maximizacion_Tru_Ri",
            "si_falta": "Precision_Mecanismo",
            "motivo": "SM-T20: sin Prec(μ) el operador Tru_Ri no está definido.",
        },
        {
            "desde": "cualquier",
            "hacia": "Maximizacion_Tru_Ri",
            "si_falta": "Celdas_Invariantes",
            "motivo": "SM-A11 / SM-A12: sin celda definida o con celda flotante, K=0 y no hay correlación admisible.",
        },
        {
            "desde": "cualquier",
            "hacia": "Maximizacion_Tru_Ri",
            "si_falta": "Ancla_Error",
            "motivo": "SM-T14: sin ancla (Π, R) no existe predicado de error.",
        },
        {
            "desde": "Superviviente_gamma_estrella",
            "hacia": "siguiente_ciclo_sin_tau",
            "motivo": "SM-T17 / SM-A14: toda resolución debe depositar τ; si no, re-confirmación.",
        },
        {
            "desde": "Deposito_en_M",
            "hacia": "modificar_gamma_estrella",
            "si_falta": "Evaluacion_Clash_true",
            "motivo": "SM-A16 / SM-T18: sin Clash la modificación es inadmisible.",
        },
        {
            "desde": "cualquier",
            "hacia": "tratar_Prob_como_generador_de_invariante",
            "motivo": "SM-T21 / SM-A18: Prob localiza candidatos; no produce invariantes por sí sola.",
        },
        {
            "desde": "cualquier",
            "hacia": "ignorar_parcial_D",
            "motivo": "SM-T23 / SM-C22: ∂D delimita el dominio; las máximas dentro de A_sum son locales respecto de ∂D.",
        },
        {
            "desde": "Precision_Mecanismo_false",
            "hacia": "reportar_Tru_Ri_numerico",
            "motivo": "SM-C19 / SM-L13: sin precisión no hay medición fiable de C, L, K ni Tru_Ri.",
        },
    ],
    "capas": {
        "0_precision": [
            "Precision_Mecanismo",
            "Registro_A_sum",
            "Registro_parcial_D",
        ],
        "1_mapa": [
            "Particion_Pi",
            "Celdas_Invariantes",
            "Reglas_Composicion_R",
            "Ancla_Error",
        ],
        "2_seleccion": [
            "Candidatas_Gamma",
            "Filtro_C_L",
            "Maximizacion_Tru_Ri",
            "Superviviente_gamma_estrella",
        ],
        "3_memoria": [
            "Construccion_Traza_tau",
            "Deposito_en_M",
            "Evacion_Ciclo",
        ],
        "4_reapertura_limite": [
            "Evaluacion_Clash",
            "Reapertura_o_Bloqueo",
            "Correccion_Acumulativa",
            "Marca_Localidad_parcial_D",
        ],
    },
    "anclas_sm": [
        # SM_PRECISION
        "SM-D16", "SM-D17", "SM-D18", "SM-D19",
        "SM-A17", "SM-A18", "SM-A19",
        "SM-L13", "SM-L14",
        "SM-T20", "SM-T21", "SM-T22", "SM-T23",
        "SM-C19", "SM-C20", "SM-C21", "SM-C22",
        # SM_MAPA
        "SM-D9", "SM-D10", "SM-D11",
        "SM-A11", "SM-A12", "SM-A13",
        "SM-L8", "SM-L9", "SM-L10",
        "SM-T12", "SM-T13", "SM-T14", "SM-T15",
        "SM-C11", "SM-C12", "SM-C13", "SM-C14",
        # SM_MEMORIA
        "SM-D12", "SM-D13", "SM-D14", "SM-D15",
        "SM-A14", "SM-A15", "SM-A16",
        "SM-L11", "SM-L12",
        "SM-T16", "SM-T17", "SM-T18", "SM-T19",
        "SM-C15", "SM-C16", "SM-C17", "SM-C18",
    ],
    "precondiciones_criticas": {
        "Maximizacion_Tru_Ri": [
            "Precision_Mecanismo",
            "Celdas_Invariantes",
            "Ancla_Error",
        ],
        "Deposito_en_M": [
            "Superviviente_gamma_estrella",
            "Construccion_Traza_tau",
        ],
        "Reapertura_o_Bloqueo": [
            "Deposito_en_M",
            "Evaluacion_Clash",
        ],
    },
}


def orden() -> list:
    """Lista ordenada de pasos del núcleo SM."""
    return list(MECANICA["orden"])


def indice(paso: str) -> int:
    """Índice del paso en el orden; KeyError si no existe."""
    return MECANICA["orden"].index(paso)


def precondiciones(paso: str) -> list:
    """Pasos que deben estar instanciados antes de `paso`."""
    i = indice(paso)
    return list(MECANICA["orden"][:i])


def capa_de(paso: str) -> str:
    """Nombre de la capa a la que pertenece el paso."""
    for nombre, pasos in MECANICA["capas"].items():
        if paso in pasos:
            return nombre
    raise KeyError(paso)


def permite_maximizar(instanciados: set) -> bool:
    """
    True solo si la sub-ruta mínima para maximizar Tru_Ri está completa:
    Precision_Mecanismo + Celdas_Invariantes + Ancla_Error.
    """
    req = set(MECANICA["precondiciones_criticas"]["Maximizacion_Tru_Ri"])
    return req.issubset(set(instanciados))


def permite_reabrir(instanciados: set, clash: bool) -> bool:
    """
    True solo si hay traza en M y Clash es true.
    """
    base = {"Deposito_en_M", "Evaluacion_Clash"}
    return base.issubset(set(instanciados)) and bool(clash)


def marca_localidad(parcial_d_registrado: bool) -> str:
    """
    Etiqueta de localidad respecto de ∂D.
    """
    if parcial_d_registrado:
        return "LOCAL_RESPECTO_DE_parcial_D"
    return "parcial_D_NO_REGISTRADO"


__all__ = [
    "MECANICA",
    "orden",
    "indice",
    "precondiciones",
    "capa_de",
    "permite_maximizar",
    "permite_reabrir",
    "marca_localidad",
]
