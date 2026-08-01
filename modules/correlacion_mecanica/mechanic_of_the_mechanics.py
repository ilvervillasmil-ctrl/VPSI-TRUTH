"""
VPSI-TRUTH --- modules/correlacion_mecanica/mechanic_of_the_mechanics.py

MECÁNICA DE LA MECÁNICA (Mechanic of the Mechanics).

Directrices del oficio MC: cómo se declara, ordena, valida y usa
cualquier cuerpo de correlación mecánica en esta carpeta.

No es sub-ruta de contexto ni de Λ_E/Λ_V.
Es el manual operativo del mecanismo mismo, en la misma forma
contractual (MECANICA.orden) para que el barrido lo audite y
para que, en conversaciones largas, el archivo recuerde el método.

Principios:
  - R1 (precondición): ningún paso sin los anteriores del orden nativo.
  - No contradicción cruzada entre archivos (CORR_SEQ_02).
  - Un solo sentido de precedencia; sin ciclos.
  - Extensión por archivos nuevos coherentes, no por reescritura opaca.
  - K de dominio solo tras la sub-ruta de anclaje de ese dominio.

Nodos con prefijo MMC_ (Mechanic of the MeChanics) para no colisionar
con causalidad_universal, contexto_MC ni contexto_fractal_MC.
"""

# ===============================================================
# MECANICA: Orden nativo del oficio de correlación mecánica
# ===============================================================
MECANICA = {
    "nombre": "mechanic_of_the_mechanics",
    "version": "1.0",
    "orden": [
        # --- Identidad del oficio ---
        "MMC_Identidad_Carpeta_MC",       # m₀: este directorio es el filtro de coherencia mecánica
        "MMC_Contrato_MECANICA",          # m₁: todo cuerpo expone dict MECANICA con orden legible
        "MMC_Nodos_Nombrados",            # m₂: cada paso del orden es un nodo estable e identificable

        # --- Construcción de un cuerpo ---
        "MMC_Declarar_Cuerpo",            # m₃: nombre, version, descripcion, notas
        "MMC_Orden_Nativo",               # m₄: secuencia causal del dominio (lista ordenada)
        "MMC_Precondicion_R1",            # m₅: paso i exige 0..i-1 del mismo orden
        "MMC_Transiciones_Prohibidas",    # m₆: saltos y confusiones explícitamente vedadas
        "MMC_Anclas_Corpus",              # m₇: ids CX/AX/TA/Def que fundamentan el cuerpo

        # --- Convivencia entre archivos ---
        "MMC_Lectura_Todos_Los_Cuerpos",  # m₈: el init lee todos los *.py con MECANICA
        "MMC_Precedencias_Por_Archivo",   # m₉: de cada orden se derivan pares (a≺b)
        "MMC_Deteccion_Inversion",        # m₁₀: (a≺b) y (b≺a) entre archivos = choque
        "MMC_Deteccion_Ciclo",            # m₁₁: secuencia que se muerde la cola = choque
        "MMC_Union_Orden_Global",         # m₁₂: si no hay choque, existe mecánica global coherente

        # --- Uso legítimo tras el barrido ---
        "MMC_Barrido_Coherente",          # m₁₃: barrer() APROBADO / coherente=True
        "MMC_Permisos_De_Dominio",        # m₁₄: permite_k / permite_* solo según sub-ruta de dominio
        "MMC_No_Saltar_Anclaje",          # m₁₅: prohibido invocar K numérico sin ancla de su dominio
        "MMC_Registro_Y_Extensión",       # m₁₆: evidencia del barrido; archivos futuros bajo las mismas reglas
        "MMC_Cierre_Oficio",              # m₁₇: fin de pasada del mecanismo; el método queda fijado
    ],
    "descripcion": (
        "Mechanic of the Mechanics — mecánica del mecanismo. "
        "Orden nativo de cómo se construye, valida y aplica la correlación "
        "mecánica en modules/correlacion_mecanica. "
        "Garantiza que cada cuerpo nuevo respete R1, no invierta precedencias "
        "ajenas y no habilite permisos de dominio sin barrido coherente. "
        "Es la memoria operativa del método cuando el contexto conversacional se alarga."
    ),
    "notas": [
        "Este archivo no calcula Tru ni clasifica O_context.",
        "No sustituye causalidad_universal (Λ) ni sub-rutas de dominio (contexto_MC, contexto_fractal_MC).",
        "Prefijo MMC_ evita colisión de nodos con el resto del corpus MC.",
        "CORR_SEQ_01: los objetos de la carpeta se leen en orden nativo.",
        "CORR_SEQ_02: colisión sobre un nodo (órdenes invertidos) bloquea el paso.",
        "Añadir un archivo dentro de 4 años = declarar MECANICA.orden coherente; si no cuadra, barrer lo reporta.",
        "MMC_Permisos_De_Dominio no inventa K: delega en permite_k del cuerpo de dominio.",
        "MMC_No_Saltar_Anclaje alinea CX-T16 / Def-5.3.1 a nivel de oficio: sin ancla, sin correlación numérica.",
        "El cierre del oficio no anula β ni redefine α.",
    ],
    "transiciones_prohibidas": [
        {
            "desde": "MMC_Identidad_Carpeta_MC",
            "hacia": "MMC_Barrido_Coherente",
            "motivo": "Sin contrato, orden, lectura de cuerpos y detección de choques no hay barrido válido.",
        },
        {
            "desde": "MMC_Declarar_Cuerpo",
            "hacia": "MMC_Permisos_De_Dominio",
            "motivo": "Declarar un cuerpo no habilita permisos hasta Orden_Nativo + Barrido_Coherente.",
        },
        {
            "desde": "MMC_Precedencias_Por_Archivo",
            "hacia": "MMC_Union_Orden_Global",
            "motivo": "Si hay inversión o ciclo, no existe unión global; estado RECHAZADO.",
        },
        {
            "desde": "cualquier_cuerpo_sin_MECANICA",
            "hacia": "MMC_Lectura_Todos_Los_Cuerpos",
            "motivo": "Contrato: solo dict MECANICA con orden legible participa del grafo.",
        },
        {
            "desde": "MMC_Barrido_Coherente=False",
            "hacia": "MMC_Permisos_De_Dominio",
            "motivo": "Oficio bloqueado: no se usan permite_* con mecánica incoherente.",
        },
        {
            "desde": "sub_ruta_dominio_incompleta",
            "hacia": "K_numerico",
            "motivo": "MMC_No_Saltar_Anclaje: K sin ancla de dominio es mal formado.",
        },
    ],
    "principios": {
        "R1_precondicion": (
            "Instanciar el paso i implica haber instanciado los pasos 0..i-1 "
            "del orden nativo del mismo cuerpo."
        ),
        "no_contradiccion_cruzada": (
            "Si el archivo A declara a≺b y el archivo B declara b≺a, "
            "el barrido rechaza la carpeta y reporta ambos."
        ),
        "un_sentido": (
            "La precedencia es estricta dentro de cada orden; "
            "la unión global solo existe sin ciclos ni inversiones."
        ),
        "extension_por_archivo": (
            "La evolución del método es agregar cuerpos MECANICA coherentes, "
            "no reinterpretar en silencio los ya aprobados."
        ),
        "permiso_tras_anclaje": (
            "Los permite_* de dominio son posteriores al anclaje de ese dominio "
            "y al barrido coherente de la carpeta."
        ),
        "memoria_operativa": (
            "orden + notas + transiciones_prohibidas son la memoria del método; "
            "no dependen de que la conversación humana recuerde el hilo."
        ),
    },
    "relacion_con_corpus": {
        "causalidad_universal": "Orden Λ_E+Λ_V del emisor/evaluador; este archivo no lo reordena.",
        "contexto_MC": "Sub-ruta O→K de contexto; este archivo exige que sus permisos respeten anclaje.",
        "contexto_fractal_MC": "Sub-ruta entrada natural/multi-O; misma regla de no inversión.",
        "init_barrer": "Policía: lee MECANICA, detecta choques, emite APROBADO|RECHAZADO.",
    },
    "anclas": [
        "CORR_SEQ_01",
        "CORR_SEQ_02",
        "R1",
        "Def-5.3.1",
        "CX-T16",
    ],
}


def orden() -> list:
    """Lista ordenada de pasos del oficio MC."""
    return list(MECANICA["orden"])


def indice(paso: str) -> int:
    """Índice del paso; KeyError si no existe."""
    return MECANICA["orden"].index(paso)


def precondiciones(paso: str) -> list:
    """Pasos que deben estar instanciados antes de `paso`."""
    i = indice(paso)
    return list(MECANICA["orden"][:i])


def ruta_minima_barrido() -> list:
    """Hasta poder declarar barrido coherente (sin extensión futura)."""
    return [
        "MMC_Identidad_Carpeta_MC",
        "MMC_Contrato_MECANICA",
        "MMC_Nodos_Nombrados",
        "MMC_Declarar_Cuerpo",
        "MMC_Orden_Nativo",
        "MMC_Precondicion_R1",
        "MMC_Lectura_Todos_Los_Cuerpos",
        "MMC_Precedencias_Por_Archivo",
        "MMC_Deteccion_Inversion",
        "MMC_Deteccion_Ciclo",
        "MMC_Union_Orden_Global",
        "MMC_Barrido_Coherente",
    ]


def oficio_permite_uso_dominio(instanciados: set) -> bool:
    """
    True solo si el oficio llegó a barrido coherente y no-saltar-anclaje.
    No sustituye permite_k de contexto_MC / fractal.
    """
    requeridos = {
        "MMC_Barrido_Coherente",
        "MMC_Permisos_De_Dominio",
        "MMC_No_Saltar_Anclaje",
    }
    return requeridos.issubset(set(instanciados))


__all__ = [
    "MECANICA",
    "orden",
    "indice",
    "precondiciones",
    "ruta_minima_barrido",
    "oficio_permite_uso_dominio",
]
