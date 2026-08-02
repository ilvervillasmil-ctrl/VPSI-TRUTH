"""
VPSI-TRUTH --- modules/correlacion_mecanica/citacion_MC.py

CITACIÓN (MC): Orden nativo de instanciación del anuncio auditable.

Este archivo define la estructura causal mínima para registrar, anunciar
y responder peticiones de cadena (normas + evidencia + O + límites)
sin calcular Tru ni fijar O.

Fundamento:
  - PA-D1..PA-D3, PA-A1..PA-A5, PA-T1..PA-T4, PA-C1..PA-C3
    (modules/axiomas/peticion_anuncio_AX.py)
  - Def-5.3.1 / CX-A1: K indefinido sin O_context explícito.
  - T7: el verificador no crea la verdad.
  - T9: imposibilidad de verdad sin evidencia.
  - T14: pertenencia del contenido vs acto de enunciar.
  - T16 / T17: techo α / piso β citables como límite.
  - Contrato CIT: solo forma de anuncio.

Relación con causalidad_universal.MECANICA:
  Sub-ruta en Λ_V (Formulación → … → Cierre_Causal) y en Comunicación /
  Cierre_Epistémico de Λ_E. No sustituye Λ_E+Λ_V; precodiciona el anuncio
  respecto del ciclo (Axioma R1 aplicado a CIT).

Relación con contexto_MC:
  La petición de anuncio / "citar todo" entra por Declaracion_O / modo
  de entrada (CX). CIT no declara O; documenta y empaqueta.

Cualquier desviación (anunciar Tru inventado, negar petición por tipo
de Ri, o usar ausencia de cadena para elevar Tru) rompe la cadena causal.
"""

# ===============================================================
# MECANICA: Orden nativo de la ruta de citación
# ===============================================================
MECANICA = {
    "nombre": "citacion_mecanica",
    "version": "0.1",
    "orden": [
        # --- Precondiciones de ciclo ---
        "Ciclo_Id",                 # t₀: Identidad del ciclo (paquete Engine)
        "Precondicion_Entrada",     # t₁: O y/o resultado y/o petición (PA-A1, R1)
        "Modo_Peticion",            # t₂: tipo de petición o emisión automática

        # --- Forma y registro ---
        "Validacion_Forma",         # t₃: esquema cita (id, enunciado, evidencia_ref…)
        "Registro_Ciclo",           # t₄: acumular citas de proceso (no verdad persistida)

        # --- Contenido anunciable (ya producido por otros) ---
        "Resolucion_Normas",        # t₅: ids AX/PA/TX… sin inventar enunciados
        "Resolucion_Evidencia",     # t₆: evidencia_ref / cache / diagnostics
        "Resolucion_O",             # t₇: O del ciclo si existe (no fijar O nuevo)
        "Resolucion_Factores",      # t₈: C,L,K o Tru solo si el ciclo los aportó

        # --- Límites estructurales ---
        "Clasificacion_Limite",     # t₉: K_SIN_O | SIN_FACTORES | O_INDEFINIDO | α | β
        "Anuncio_Limite",           # t₁₀: emitir código de límite (PA-T3, PA-T4)

        # --- Empaquetado y respuesta ---
        "Empaquetado_Anuncio",      # t₁₁: maqueta enunciado + descripción
        "Respuesta_Peticion",       # t₁₂: cadena según PA-A2
        "Cierre_Auditable",         # t₁₃: cadena entregable o defecto instrumento (PA-A3)
    ],
    "descripcion": (
        "Orden nativo de instanciación de citación según PA (petición de anuncio) "
        "y contrato CIT. Garantiza que cada paso t_i solo se instancia si "
        "t_0…t_{i-1} ya están instanciados (precondición R1 aplicada al anuncio). "
        "No se calcula Tru en esta sub-ruta. No se inventan factores. "
        "Cualquier Ri puede peticionar (PA-T1 / TA4)."
    ),
    "notas": [
        "Orden invariable dentro de la sub-ruta de citación.",
        "No redefine α ni β; solo puede anunciarlos como límite (T16, T17).",
        "Si Precondicion_Entrada falla → no hay emisión de cadena (T1.22).",
        "Si K se interroga sin O → Clasificacion_Limite = K_SIN_O (Def-5.3.1, PA-T3).",
        "Ausencia de cadena no eleva Tru (PA-A3, PA-C3).",
        "Compatible con Λ_V: el anuncio cierra comunicación del resultado, "
        "no sustituye Correlacion_K ni Declaracion_O de contexto_MC.",
        "Engine orquesta; CIT no dirige CA/FO/CX.",
        "Omega filtra presentación; no reduce el universo citable (PA-C1).",
    ],
    "transiciones_prohibidas": [
        {
            "desde": "Ciclo_Id",
            "hacia": "Respuesta_Peticion",
            "motivo": "PA-A1 / R1: sin precondición de entrada no hay cadena emitible.",
        },
        {
            "desde": "cualquier",
            "hacia": "calcular_Tru",
            "motivo": "PA-C2 / contrato CIT: citación no calcula Tru.",
        },
        {
            "desde": "cualquier",
            "hacia": "inventar_factores_CLK",
            "motivo": "T9 / PA-A2: sin evidencia de CA no se rellenan C,L,K.",
        },
        {
            "desde": "Resolucion_O_vacia",
            "hacia": "anunciar_K_numerico",
            "motivo": "Def-5.3.1 / PA-T3: K sin O es ∅, no un número.",
        },
        {
            "desde": "ausencia_de_cadena",
            "hacia": "elevar_Tru",
            "motivo": "PA-A3: defecto de auditabilidad no prueba D.",
        },
        {
            "desde": "peticion_estado_mental",
            "hacia": "atribuir_intencion",
            "motivo": "PA-A4: no es oficio del sistema.",
        },
        {
            "desde": "cualquier",
            "hacia": "negar_peticion_por_tipo_Ri",
            "motivo": "PA-T1 / TA4: sin lista blanca de peticionario.",
        },
    ],
    "tipos_peticion": {
        "por_que_valor": (
            "Exige normas + evidencia + factores reportados o límite "
            "si no hubo factores."
        ),
        "dame_O": (
            "Exige O_context del ciclo o anuncio de O indefinido."
        ),
        "dame_evidencia": (
            "Exige evidencia_ref / artefactos de proceso del ciclo."
        ),
        "dame_normas": (
            "Exige ids AX/PA/TX/MC citables usados en el ciclo."
        ),
        "dame_limites": (
            "Exige códigos de límite estructurales aplicables."
        ),
        "dame_cadena_completa": (
            "Une normas + evidencia + O + factores reportados + límites."
        ),
    },
    "clasificacion_limite": {
        "K_SIN_O": "K=∅ sin O_context (Def-5.3.1, PA-T3).",
        "SIN_FACTORES": "CA no aportó C,L,K en el ciclo.",
        "O_INDEFINIDO": "O inestable o no recuperable (CX-A10).",
        "TECHO_ALPHA": "T16: contribución verificable desde Ri ≤ α.",
        "PISO_BETA": "T17: Tru_total ≥ β siempre.",
        "EVIDENCIA_INSUFICIENTE": "T9: sin base causal suficiente para precisar.",
    },
    "respuesta_minima_PA_A2": [
        "ids_normativos",
        "evidencia_ref",
        "O_context_si_existe",
        "limites_si_aplican",
    ],
    "anclas_pa_cx": [
        "PA-D1", "PA-D2", "PA-D3",
        "PA-A1", "PA-A2", "PA-A3", "PA-A4", "PA-A5",
        "PA-T1", "PA-T2", "PA-T3", "PA-T4",
        "PA-C1", "PA-C2", "PA-C3",
        "CX-A1", "CX-A10", "Def-5.3.1",
        "T7", "T9", "T14", "T16", "T17", "TA4",
    ],
}


def orden() -> list:
    """Lista ordenada de pasos de la sub-ruta de citación."""
    return list(MECANICA["orden"])


def indice(paso: str) -> int:
    """Índice del paso en el orden; KeyError si no existe."""
    return MECANICA["orden"].index(paso)


def precondiciones(paso: str) -> list:
    """Pasos que deben estar instanciados antes de `paso`."""
    i = indice(paso)
    return list(MECANICA["orden"][:i])


def permite_anuncio(instanciados: set) -> bool:
    """
    True solo si la sub-ruta mínima para emitir anuncio está completa:
    Ciclo_Id + Precondicion_Entrada + Validacion_Forma (si hay citas)
    o Clasificacion_Limite (si solo hay límite).
    """
    base = {"Ciclo_Id", "Precondicion_Entrada"}
    if not base.issubset(set(instanciados)):
        return False
    # Emisión por citas formadas o por límite estructural explícito
    return (
        "Validacion_Forma" in instanciados
        or "Clasificacion_Limite" in instanciados
        or "Anuncio_Limite" in instanciados
    )


def clasificar_limite(
    *,
    o_estable: bool,
    permite_k: bool,
    tiene_factores: bool,
) -> list:
    """
    Clasificación operativa de límites estructurales.
    No calcula Tru; solo etiqueta códigos aplicables.
    """
    codigos = []
    if not o_estable:
        codigos.append("O_INDEFINIDO")
    if not permite_k:
        codigos.append("K_SIN_O")
    if not tiene_factores:
        codigos.append("SIN_FACTORES")
    return codigos


def respuesta_minima() -> list:
    """Campos mínimos de una respuesta a petición (PA-A2)."""
    return list(MECANICA["respuesta_minima_PA_A2"])


__all__ = [
    "MECANICA",
    "orden",
    "indice",
    "precondiciones",
    "permite_anuncio",
    "clasificar_limite",
    "respuesta_minima",
]
