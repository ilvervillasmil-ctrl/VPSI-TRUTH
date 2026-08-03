"""
VPSI-TRUTH --- modules/correlacion_mecanica/ciclo_calculo_MC.py

CICLO DE CÁLCULO (MC): Orden nativo del procedimiento de valuación
que Engine orquesta. No calcula Tru. No es CA ni FO ni TX ni CIT.
Declara la secuencia causal mínima para recoger, puntuar y cerrar
un ciclo de evaluación bajo el Protocolo (5 pasos) y calculo_variables.

Fundamento:
  - PROTOCOLO.pdf Abstract + §0.15 (C=1-k/m, L=1-r/p, K=1-f/c)
  - PROTOCOLO 5 pasos: Octx → premisas → registro/puntuación → taxonomía → reconstrucción
  - calculo_variables.MECANICA (O → C → L → K → Tru_Ri → Tru_total)
  - contexto_MC / realidad_MC / citacion_MC (sin invertir nodos)
  - Def-5.3.1, TA5, TA6, T9, T16, T17

Relación:
  - No sustituye calculo_variables: lo precodiciona y lo cierra.
  - CA ejecuta conteos y factores; FO aplica fórmula; TX clasifica;
    CIT anuncia; Engine solo sigue este orden + contratos.
  - Si falta O o conteos, K o Tru no se inventan (límite, no humo).
"""

# ===============================================================
# MECANICA: Orden nativo del ciclo de cálculo
# ===============================================================
MECANICA = {
    "nombre": "ciclo_calculo_MC",
    "version": "1.0",
    "orden": [
        # --- Paso 1 PROTOCOLO: fijar O (sin O no hay K numérico) ---
        "CC_Ciclo_Id",              # v₀: identidad del ciclo (paquete Engine)
        "CC_Declaracion_O",         # v₁: O_context explícito (Def-5.3.1, CX-A1)
        "CC_Estado_O",              # v₂: estable | indefinido | cambio
        "CC_Permite_K",             # v₃: compuerta; si False → K=∅, no 0

        # --- Paso 2 PROTOCOLO: premisas / evidencia estructural ---
        "CC_Premisas_Registro",     # v₄: compromisos y posturas del objeto (m, p base)
        "CC_Evidencia_Estructural", # v₅: lo ya producido (AX/CI/censo/tests) sin reinterpretar
        "CC_Afirmaciones_D",        # v₆: aserciones verificables del run (c base)

        # --- Paso 3 PROTOCOLO: conteos operacionales + factores ---
        "CC_Conteo_C",              # v₇: m, k  → entrada CA (C = 1 - k/m)
        "CC_Conteo_L",              # v₈: p, r  → entrada CA (L = 1 - r/p)
        "CC_Conteo_K",              # v₉: c, f  → entrada CA (K = 1 - f/c) solo si permite_K
        "CC_Factores_CA",           # v₁₀: CA entrega C, L, K (o límite SIN_FACTORES / K_SIN_O)
        "CC_Tru_FO",                # v₁₁: FO: Tru_Ri = C·L·K; Tru_total = (Tru_Ri·α)+β

        # --- Paso 4 PROTOCOLO: taxonomía (TX; none si no hay match) ---
        "CC_Revision_Afirmaciones", # v₁₂: cada afirmación del objeto, una a una
        "CC_Taxonomia_TX",          # v₁₃: código TX o none (firma de factor degradado)

        # --- Paso 5 PROTOCOLO: cierre auditable ---
        "CC_Normas_AX",             # v₁₄: ids que explican o contradicen (sin inventar)
        "CC_Citacion_CIT",          # v₁₅: anuncio cadena norma + evidencia + O + límites
        "CC_Deposito_Evidencia",    # v₁₆: evaluaciones / cache del ciclo
        "CC_Cierre_Ciclo",          # v₁₇: fin de pasada; listo para Omega (solo presenta)
    ],
    "descripcion": (
        "Orden causal del procedimiento de cálculo que Engine orquesta. "
        "Integra los 5 pasos del Protocolo con calculo_variables y las "
        "sub-rutas CX/RE/CIT ya declaradas. "
        "No calcula: fija cuándo CA, FO, TX y CIT pueden actuar. "
        "Sin CC_Declaracion_O no hay K numérico. Sin conteos no hay "
        "factores inventados. TX y CIT no sustituyen FO."
    ),
    "notas": [
        "Prefijo CC_ evita colisión con contexto_MC, realidad_MC, citacion_MC, MMC_.",
        "Alineado a calculo_variables: O_context ≺ C ≺ L ≺ K ≺ Tru_Ri ≺ Tru_total.",
        "Alineado a contexto_MC: Declaracion_O antes de Correlacion_K / factores K.",
        "Alineado a realidad_MC: evaluación numérica solo tras O y admisibilidad.",
        "Alineado a citacion_MC: anuncio tras factores o tras Clasificacion_Limite.",
        "Paso 2 no es 'opinión': son compromisos/posturas/afirmaciones observables del run.",
        "Conteos k,r,f admiten peso en (0,1) según §0.15 (penalización ponderada).",
        "Si CC_Permite_K es falso: se instancia límite K_SIN_O / O_INDEFINIDO; no se fuerza K=0.",
        "Si CA no entrega factores: límite SIN_FACTORES; FO no rellena; CIT puede anunciarlo.",
        "CC_Taxonomia_TX: match estructural a catálogo TX; si no aplica → none.",
        "Engine no inventa m,k,p,r,c,f ni C,L,K ni Tru; solo ordena oficios por contrato.",
        "Omega lee el depósito; no recalcula (presentador).",
        "Violar el orden (p. ej. Tru sin O, o TX como sustituto de C) es choque mecánico MC.",
    ],
    "precondiciones": {
        "reclamar_K_numerico": [
            "CC_Ciclo_Id",
            "CC_Declaracion_O",
            "CC_Estado_O",
            "CC_Permite_K",
        ],
        "ejecutar_CA_factores": [
            "CC_Premisas_Registro",
            "CC_Conteo_C",
            "CC_Conteo_L",
            # CC_Conteo_K solo si permite_K; si no, CA puede omitir K numérico
        ],
        "ejecutar_FO": [
            "CC_Factores_CA",
        ],
        "aplicar_TX": [
            "CC_Afirmaciones_D",
            "CC_Revision_Afirmaciones",
        ],
        "emitir_CIT": [
            "CC_Ciclo_Id",
            # factores reportados O límites estructurales
        ],
        "depositar": [
            "CC_Citacion_CIT",
        ],
    },
    "transiciones_prohibidas": [
        {
            "desde": "CC_Ciclo_Id",
            "hacia": "CC_Tru_FO",
            "motivo": "Sin O, premisas, conteos y factores no hay Tru admisible (T9, Def-5.3.1).",
        },
        {
            "desde": "CC_Declaracion_O",
            "hacia": "CC_Factores_CA",
            "motivo": "Faltan premisas y conteos operacionales (§0.15).",
        },
        {
            "desde": "CC_Permite_K=False",
            "hacia": "CC_Conteo_K_numerico",
            "motivo": "K sin O estable es ∅, no un número (Def-5.3.1, CX-A1).",
        },
        {
            "desde": "cualquier",
            "hacia": "inventar_C_L_K",
            "motivo": "Humo: solo CA a partir de conteos observables.",
        },
        {
            "desde": "cualquier",
            "hacia": "recalcular_Tru_en_Omega_o_CIT",
            "motivo": "FO es el único oficio de la fórmula; CIT/Omega no calculan.",
        },
        {
            "desde": "CC_Taxonomia_TX",
            "hacia": "sustituir_factores",
            "motivo": "TX clasifica desviación; no reemplaza C, L, K ni Tru.",
        },
        {
            "desde": "sin_match_TX",
            "hacia": "forzar_codigo_TX",
            "motivo": "Si no aplica táctica → none; no se inventa etiqueta.",
        },
    ],
    "mapeo_protocolo_5": {
        "1_Octx": ["CC_Ciclo_Id", "CC_Declaracion_O", "CC_Estado_O", "CC_Permite_K"],
        "2_premisas": ["CC_Premisas_Registro", "CC_Evidencia_Estructural", "CC_Afirmaciones_D"],
        "3_registro_puntuacion": [
            "CC_Conteo_C", "CC_Conteo_L", "CC_Conteo_K",
            "CC_Factores_CA", "CC_Tru_FO",
        ],
        "4_taxonomia": ["CC_Revision_Afirmaciones", "CC_Taxonomia_TX"],
        "5_reconstruccion_cierre": [
            "CC_Normas_AX", "CC_Citacion_CIT",
            "CC_Deposito_Evidencia", "CC_Cierre_Ciclo",
        ],
    },
    "formulas_operacionales": {
        "C": "1 - (k / m)",
        "L": "1 - (r / p)",
        "K": "1 - (f / c)  si permite_K; else ∅",
        "Tru_Ri": "C * L * K",
        "Tru_total": "(Tru_Ri * ALPHA) + BETA",
        "fuente": "PROTOCOLO.pdf §0.15; IlverVillasmil TA5/TA6",
    },
    "oficios_por_nodo": {
        "CC_Declaracion_O": "CX",
        "CC_Permite_K": "CX",
        "CC_Factores_CA": "CA",
        "CC_Tru_FO": "FO",
        "CC_Taxonomia_TX": "TX",
        "CC_Citacion_CIT": "CIT",
        "CC_Deposito_Evidencia": "CH/Engine registro",
        "orquestacion": "Engine según contratos + este orden",
    },
    "anclas": [
        "Def-5.3.1", "CX-A1", "CX-A10",
        "TA1", "TA2", "TA3", "TA5", "TA6",
        "T9", "T16", "T17",
        "PROTOCOLO_5_pasos", "PROTOCOLO_0.15",
        "calculo_variables",
        "CORR_SEQ_01", "R1",
    ],
}


def orden() -> list:
    """Lista ordenada del ciclo de cálculo."""
    return list(MECANICA["orden"])


def indice(paso: str) -> int:
    return MECANICA["orden"].index(paso)


def precondiciones(paso: str) -> list:
    i = indice(paso)
    return list(MECANICA["orden"][:i])


def permite_factores_k(instanciados: set) -> bool:
    """K numérico solo tras O y compuerta permite_K."""
    req = {
        "CC_Ciclo_Id",
        "CC_Declaracion_O",
        "CC_Estado_O",
        "CC_Permite_K",
    }
    return req.issubset(set(instanciados))


def permite_tru(instanciados: set) -> bool:
    """Tru solo tras factores CA (no inventados)."""
    return "CC_Factores_CA" in set(instanciados)


def ruta_minima_valuacion() -> list:
    """Hasta Tru_FO, sin TX/CIT/depósito."""
    return [
        "CC_Ciclo_Id",
        "CC_Declaracion_O",
        "CC_Estado_O",
        "CC_Permite_K",
        "CC_Premisas_Registro",
        "CC_Evidencia_Estructural",
        "CC_Afirmaciones_D",
        "CC_Conteo_C",
        "CC_Conteo_L",
        "CC_Conteo_K",
        "CC_Factores_CA",
        "CC_Tru_FO",
    ]


__all__ = [
    "MECANICA",
    "orden",
    "indice",
    "precondiciones",
    "permite_factores_k",
    "permite_tru",
    "ruta_minima_valuacion",
]
