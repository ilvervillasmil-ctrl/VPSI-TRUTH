"""
VPSI-TRUTH --- modules/correlacion_mecanica/contexto_MC.py

CONTEXTO (MC): Orden nativo de instanciación del armazón O_context.

Este archivo define la estructura causal mínima para declarar, escalar,
expandir o cambiar un contexto, y solo entonces permitir K.

Fundamento:
  - Def-5.3.1 / CX-A1: K indefinido sin O_context explícito.
  - CX-A7, CX-A8, CX-T4, CX-T5, CX-T6: unidad, cambio, pertenencia,
    expansión coherente, ruptura.
  - CX-A11, CX-T7: escalas (fractalidad operativa).
  - CX-A13, CX-T10: ningún O anula β ni el techo α.

Relación con causalidad_universal.MECANICA:
  Esta es la sub-ruta que debe cumplirse al tocar los niveles
  "Correlación" y "Contexto" de Λ_V. No sustituye Λ_E+Λ_V;
  precodiciona K respecto de O (Axioma R1 de precondición aplicado a CX).

Cualquier desviación (medir K sin O, o tratar un cambio de O como
expansión) rompe la cadena causal del ciclo.
"""

# ===============================================================
# MECANICA: Orden nativo de la ruta de contexto
# ===============================================================
MECANICA = {
    "nombre": "contexto_mecanico",
    "version": "0.2",
    "orden": [
        # --- Precondiciones de ciclo ---
        "Ciclo_Id",              # c₀: Identidad del ciclo (paquete Engine)
        "Declaracion_O",         # c₁: O_context explícito (CX-A1, Def-5.3.1)
        "Escala_O",              # c₂: Resolución del armazón (CX-A11)
        "Regla_Significado",      # c₃: Organización coherente de O (CX-A4)

        # --- Integridad del armazón ---
        "Criterio_Pertenencia",  # c₄: e ∈ O ⇔ no redefine la regla (CX-T4)
        "Clasificacion_Evento",  # c₅: {mismo_O | expansion | cambio | indefinido}
                                 #     (CX-A7, CX-A8, CX-A9, CX-T5, CX-T6)

        # --- Solo si O es estable ---
        "Factores_CLK",          # c₆: C, L disponibles; K aún no forzado
        "Correlacion_K",         # c₇: K(D|O) con O ya fijado (CX-A1, CX-T2)
        "Ri_Local",              # c₈: R_i = C·L·K bajo ese O (no es R)

        # --- Cierre de la sub-ruta ---
        "Registro_Secuencia_O",  # c₉: evidencia de O / cambios / ∅ (CX-C8)
        "Cierre_Contexto",       # c₁₀: fin de pasada de contexto; no anula β (CX-A13)
    ],
    "descripcion": (
        "Orden nativo de instanciación de contexto según el cuerpo CX (axiomas). "
        "Garantiza que cada paso c_i solo se instancia si c_0…c_{i-1} ya están "
        "instanciados (precondición R1 aplicada a O_context). "
        "K no se calcula antes de Declaracion_O + Escala_O + Regla_Significado. "
        "Un cambio de contexto no se confunde con expansión coherente."
    ),
    "notas": [
        "Orden invariable dentro de la sub-ruta de contexto.",
        "No redefine α ni β (CX-T10, CX-A13).",
        "Si Declaracion_O falla → K permanece indefinido (∅), no 0 (CX-A10, CX-L2).",
        "Clasificacion_Evento distingue: mismo O, expansión (CX-T5), cambio (CX-T6), deriva.",
        "Registro_Secuencia_O alimenta CACHE; Centinela puede auditar la secuencia.",
        "Compatible con Λ_V de causalidad_universal: esta sub-ruta debe completarse "
        "antes de tratar Correlación (K) como valor numérico del ciclo.",
        "Multiplicidad de O (CX-A3) no implica varios K simultáneos sin declarar "
        "cuál O gobierna el ciclo actual.",
    ],
    "transiciones_prohibidas": [
        {
            "desde": "Ciclo_Id",
            "hacia": "Correlacion_K",
            "motivo": "CX-A1 / Def-5.3.1: K sin O explícito es mal formado.",
        },
        {
            "desde": "Declaracion_O",
            "hacia": "Correlacion_K",
            "motivo": "Falta Escala_O y Regla_Significado (CX-A11, CX-A4).",
        },
        {
            "desde": "Clasificacion_Evento=cambio",
            "hacia": "Expansion",
            "motivo": "CX-T6: e* ∉ O obliga a nuevo O' o K indefinido; no es expansión.",
        },
        {
            "desde": "cualquier",
            "hacia": "anular_BETA",
            "motivo": "CX-A13 / T17: ningún O anula β.",
        },
    ],
    "clasificacion_evento": {
        "mismo_O": (
            "Elementos nuevos satisfacen CX-T4 respecto del O vigente; "
            "no hay redefinición de la regla global."
        ),
        "expansion": (
            "e_1..e_n ∈ O (CX-T4); crece cobertura, no identidad (CX-T5, CX-A9)."
        ),
        "cambio": (
            "e* ∉ O; se declara O' o el tramo queda con K indefinido (CX-A8, CX-T6)."
        ),
        "indefinido": (
            "No hay O estable recuperable en el tramo (CX-A10, CX-D7 deriva)."
        ),
    },
    "escalas_admitidas": [
        "morfologica",
        "lexica",
        "combinatoria",
        "discursiva",
        "dominio",
        "codigo_lengua",
    ],
    "anclas_cx": [
        "CX-A1", "CX-A4", "CX-A7", "CX-A8", "CX-A9", "CX-A10", "CX-A11", "CX-A13",
        "CX-T4", "CX-T5", "CX-T6", "CX-T7", "CX-T10",
        "CX-C4", "CX-C8",
        "Def-5.3.1", "TA3", "TA4", "T16", "T17",
    ],
}


def orden() -> list:
    """Lista ordenada de pasos de la sub-ruta de contexto."""
    return list(MECANICA["orden"])


def indice(paso: str) -> int:
    """Índice del paso en el orden; KeyError si no existe."""
    return MECANICA["orden"].index(paso)


def precondiciones(paso: str) -> list:
    """Pasos que deben estar instanciados antes de `paso`."""
    i = indice(paso)
    return list(MECANICA["orden"][:i])


def permite_k(instanciados: set) -> bool:
    """
    True solo si la sub-ruta mínima para K está completa:
    Declaracion_O + Escala_O + Regla_Significado (+ ciclo).
    """
    requeridos = {
        "Ciclo_Id",
        "Declaracion_O",
        "Escala_O",
        "Regla_Significado",
    }
    return requeridos.issubset(set(instanciados))


def clasificar_evento(pertenece_a_o: bool, o_estable: bool) -> str:
    """
    Clasificación operativa mínima (CX-T4 / T5 / T6 / A10).
    No calcula Tru; solo etiqueta el evento de contexto.
    """
    if not o_estable:
        return "indefinido"
    if pertenece_a_o:
        return "expansion"  # o mismo_O si no hay elemento nuevo; el caller puede refinar
    return "cambio"


__all__ = [
    "MECANICA",
    "orden",
    "indice",
    "precondiciones",
    "permite_k",
    "clasificar_evento",
]
