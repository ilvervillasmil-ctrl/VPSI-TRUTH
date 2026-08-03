# -*- coding: utf-8 -*-
"""
SM_PRECISION — Extensión axiomática: Precisión del mecanismo causal
y origen de la distorsión de representación.

Versión: 1.0
Dependencias estructurales: SM_MAPA, SM_MEMORIA, SM_AF, TA3–TA5, T12, T14.

NOTA GENERAL (para humanos)
---------------------------
Este cuerpo formaliza la capa anterior a la medición de verdad:

1. Un mecanismo μ funciona porque es preciso (determinista bajo anclas).
2. Sin Prec(μ) no hay medición fiable de C, L, K ni de Tru_Ri.
3. La probabilidad es herramienta; su objetivo sigue siendo un invariante.
4. Si el mapa X está distorsionado respecto de R, la causa reside en las
   anclas suministradas (A_sum) o en la frontera del diseñador (∂D),
   no en la ejecución de μ.
5. Registrar ∂D convierte el límite del conocimiento del diseñador en
   información estructural que delimita toda maximización posterior.

Símbolos nuevos (no contradictorios):
  μ            = mecanismo causal de ejecución
  Prec(μ)      = predicado de precisión (determinismo bajo anclas)
  A_sum        = anclas efectivamente suministradas
  A_pos        = anclas posibles respecto de R
  ∂D           = A_pos \ A_sum  (frontera del diseñador)
  Prob         = procedimiento probabilístico usado como herramienta

Cada declaración lleva nota operativa, ejemplo y demostración comentada.
"""

from __future__ import annotations
from typing import List, Dict, Any

# ============================================================
# METADATOS DEL CUERPO
# ============================================================

CUERPO = {
    "nombre": "SM_PRECISION",
    "version": "1.0",
    "descripcion": (
        "Precisión del mecanismo causal como condición de funcionamiento; "
        "subordinación de la probabilidad a la búsqueda de invariantes; "
        "origen causal de la distorsión en las anclas suministradas; "
        "frontera del diseñador como información estructural."
    ),
    "depende_de_cuerpos": ["SM_MAPA", "SM_MEMORIA", "SM_AF", "VPSI"],
    "gobierna": [
        "precision_mecanismo",
        "subordinacion_probabilidad",
        "origen_distorsion",
        "frontera_disenador",
        "condicion_funcionamiento",
        "medicion_fiable",
    ],
}

# ============================================================
# DECLARACIONES
# ============================================================

def declaraciones() -> List[Dict[str, Any]]:
    """
    Lista de declaraciones del cuerpo SM_PRECISION.
    Formato canónico VPSI: id, tipo, sujeto, relacion, objeto,
    polaridad, cota, depende_de, gobierna, enunciado.
    """
    return [

        # --------------------------------------------------
        # DEFINICIONES
        # --------------------------------------------------
        {
            "id": "SM-D16",
            "tipo": "definicion",
            "sujeto": "mecanismo_mu",
            "relacion": "es_preciso_ssi",
            "objeto": "entradas_identicas_bajo_mismas_anclas_producen_salida_identica",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["precision_mecanismo", "condicion_funcionamiento"],
            "enunciado": (
                "SM-D16 (Mecanismo causal preciso): Un mecanismo μ es preciso si y sólo si, "
                "para todo par de entradas idénticas bajo el mismo conjunto de anclas "
                "A' ⊆ A, la salida de μ es idéntica. Se escribe Prec(μ) = true.\n\n"
                "NOTA OPERATIVA: La precisión es determinismo de ejecución bajo anclas. "
                "No es 'exactitud respecto de R'; es estabilidad de la función que "
                "implementa μ. Sin ella no hay base para medir nada.\n"
                "EJEMPLO: Un sumador que ante 2+2 siempre devuelve 4 tiene Prec(μ)=true. "
                "Uno que a veces devuelve 4 y a veces 5 tiene Prec(μ)=false."
            ),
        },
        {
            "id": "SM-D17",
            "tipo": "definicion",
            "sujeto": "A_sum",
            "relacion": "es",
            "objeto": "conjunto_de_anclas_efectivamente_suministradas_al_sistema",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["origen_distorsion"],
            "enunciado": (
                "SM-D17 (Anclas suministradas): A_sum ⊆ A_pos es el conjunto de anclas "
                "que el diseñador entregó efectivamente al sistema.\n\n"
                "NOTA OPERATIVA: A_sum es lo que el sistema realmente recibió. "
                "Todo lo que no está en A_sum no puede usarse como ancla forzada "
                "en sus maximizaciones.\n"
                "EJEMPLO: Si el diseñador no entregó ninguna ancla sobre efectos "
                "fisiológicos de la insolación, esa ancla no pertenece a A_sum."
            ),
        },
        {
            "id": "SM-D18",
            "tipo": "definicion",
            "sujeto": "frontera_del_disenador_parcial_D",
            "relacion": "es",
            "objeto": "A_pos_menos_A_sum",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D17"],
            "gobierna": ["frontera_disenador"],
            "enunciado": (
                "SM-D18 (Frontera del diseñador): ∂D = A_pos \\ A_sum. "
                "Todo elemento de ∂D es una ancla que existe (o podría conocerse) "
                "pero no fue suministrada.\n\n"
                "NOTA OPERATIVA: ∂D es el conjunto de agujeros estructurales del mapa. "
                "Registrar ∂D (aunque sea parcialmente) convierte el límite del "
                "diseñador en dato usable por el sistema.\n"
                "EJEMPLO: A_pos contiene anclas sobre insolación; A_sum no. "
                "La ancla de insolación pertenece a ∂D."
            ),
        },
        {
            "id": "SM-D19",
            "tipo": "definicion",
            "sujeto": "mapa_X",
            "relacion": "esta_distorsionado_respecto_de_R_ssi",
            "objeto": "existe_correlacion_forzada_por_R_no_recuperable_desde_A_sum",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D17", "SM-D18"],
            "gobierna": ["origen_distorsion"],
            "enunciado": (
                "SM-D19 (Distorsión de representación): El mapa X del sistema está "
                "distorsionado respecto de R cuando existe al menos una correlación "
                "forzada por R que no puede ser recuperada a partir de A_sum.\n\n"
                "NOTA OPERATIVA: La distorsión no se define por 'parecer raro'. "
                "Se define por la imposibilidad de recuperar una correlación que R fuerza.\n"
                "EJEMPLO: R fuerza la correlación sol → insolación mortal en desierto. "
                "Si A_sum no contiene anclas que permitan recuperarla, X está distorsionado "
                "en ese dominio."
            ),
        },

        # --------------------------------------------------
        # AXIOMAS
        # --------------------------------------------------
        {
            "id": "SM-A17",
            "tipo": "axioma",
            "sujeto": "no_Prec_mu",
            "relacion": "implica",
            "objeto": "degradacion_o_anulacion_del_funcionamiento_de_mu",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D16"],
            "gobierna": ["precision_mecanismo", "condicion_funcionamiento"],
            "enunciado": (
                "SM-A17 (Precisión como condición de funcionamiento): "
                "¬Prec(μ) ⟹ el funcionamiento de μ se degrada o se anula.\n\n"
                "NOTA OPERATIVA: Antes de hablar de verdad o de error hace falta "
                "que el mecanismo ejecute de forma determinista. Sin precisión "
                "no hay sistema sobre el cual medir.\n"
                "EJEMPLO: Un circuito que no garantiza la misma salida ante la "
                "misma entrada no puede sostener ninguna medición de C·L·K."
            ),
        },
        {
            "id": "SM-A18",
            "tipo": "axioma",
            "sujeto": "uso_de_Prob",
            "relacion": "tiene_como_objetivo",
            "objeto": "localizacion_de_un_invariante",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["subordinacion_probabilidad"],
            "enunciado": (
                "SM-A18 (Subordinación de la probabilidad): El uso de Prob bajo un "
                "contexto O tiene como objetivo la localización de un invariante. "
                "No sustituye el conocimiento preciso de los términos de la "
                "correlación buscada.\n\n"
                "NOTA OPERATIVA: La probabilidad es herramienta de búsqueda. "
                "El destino es el invariante. Confundir la herramienta con el "
                "destino produce la ilusión de que el azar 'genera' estructura.\n"
                "EJEMPLO: Se muestrean cadenas para localizar candidatos a "
                "significado estable de 'casa'. El muestreo propone; las anclas "
                "deciden si el candidato es invariante."
            ),
        },
        {
            "id": "SM-A19",
            "tipo": "axioma",
            "sujeto": "mapa_X_distorsionado_respecto_de_R",
            "relacion": "tiene_causa_en",
            "objeto": "A_sum_o_parcial_D_no_en_la_ejecucion_de_mu",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D19", "SM-D17", "SM-D18"],
            "gobierna": ["origen_distorsion"],
            "enunciado": (
                "SM-A19 (Origen causal de la distorsión): Si X está distorsionado "
                "respecto de R, entonces la causa reside en A_sum (o en ∂D), "
                "no en la ejecución de μ sobre A_sum.\n\n"
                "NOTA OPERATIVA: El sistema ejecuta lo que recibió. La distorsión "
                "es imagen de los anclajes omitidos, no un fallo de la ejecución.\n"
                "EJEMPLO: Se entrena sin anclas de insolación. El sistema produce "
                "máximos locales que niegan el peligro del sol. La causa no es μ; "
                "es ∂D."
            ),
        },

        # --------------------------------------------------
        # LEMAS
        # --------------------------------------------------
        {
            "id": "SM-L13",
            "tipo": "lema",
            "sujeto": "no_Prec_mu",
            "relacion": "implica",
            "objeto": "no_existe_medicion_fiable_de_C_L_K",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A17", "SM-D16"],
            "gobierna": ["medicion_fiable", "precision_mecanismo"],
            "enunciado": (
                "SM-L13: ¬Prec(μ) ⟹ no existe medición fiable de C, L, K sobre "
                "las salidas de μ.\n\n"
                "NOTA OPERATIVA: Si el mecanismo no es determinista, los valores "
                "de coherencia, lógica y correlación no son funciones bien "
                "definidas de la entrada.\n"
                "EJEMPLO: Dos ejecuciones idénticas producen C=1 y C=0. "
                "No hay valor de C atribuible a la entrada.\n"
                "DEMOSTRACIÓN: Si μ no es preciso, entradas idénticas pueden "
                "producir salidas distintas. Entonces C, L y K asociados a esas "
                "salidas no son funciones bien definidas de la entrada. "
                "Por tanto no hay medición fiable."
            ),
        },
        {
            "id": "SM-L14",
            "tipo": "lema",
            "sujeto": "correlacion_gamma_obtenida_por_Prob",
            "relacion": "si_es_invariante_entonces",
            "objeto": "existe_justificacion_no_probabilistica_a_partir_de_anclas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A18"],
            "gobierna": ["subordinacion_probabilidad"],
            "enunciado": (
                "SM-L14: Sea γ una correlación candidata obtenida mediante Prob. "
                "Si γ es un invariante bajo O, entonces existe una justificación "
                "no probabilística de γ a partir de anclas de A.\n\n"
                "NOTA OPERATIVA: El carácter de invariante no puede depender del "
                "muestreo. Debe anclarse en correlaciones forzadas.\n"
                "EJEMPLO: Un candidato a 'significado de casa' aparece con alta "
                "frecuencia muestral. Solo se convierte en invariante cuando se "
                "correlaciona de forma forzada con anclas de R.\n"
                "DEMOSTRACIÓN: Por SM-A18 el objetivo de Prob es un invariante. "
                "Un invariante, por definición, no depende del muestreo. "
                "Luego debe admitir derivación a partir de correlaciones forzadas "
                "(anclas)."
            ),
        },

        # --------------------------------------------------
        # TEOREMAS
        # --------------------------------------------------
        {
            "id": "SM-T20",
            "tipo": "teorema",
            "sujeto": "no_Prec_mu",
            "relacion": "implica",
            "objeto": "Tru_Ri_no_definido_sobre_salidas_de_mu",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-L13", "SM-A17"],
            "gobierna": ["medicion_fiable", "condicion_funcionamiento"],
            "enunciado": (
                "SM-T20 (Precisión previa a la verdad): Sin Prec(μ)=true no hay "
                "ejecución sobre la cual pueda definirse Tru_Ri.\n\n"
                "NOTA OPERATIVA: La medición de verdad presupone un mecanismo "
                "preciso. Sin él el operador Tru_Ri no está definido.\n"
                "EJEMPLO: Se intenta calcular Tru_Ri sobre las salidas de un "
                "mecanismo no determinista. Los valores de C, L, K fluctúan; "
                "Tru_Ri no es atribuible.\n"
                "DEMOSTRACIÓN: Por SM-L13, si ¬Prec(μ) entonces C, L y K no son "
                "medibles de forma fiable. Como Tru_Ri = C·L·K, el operador "
                "no está definido."
            ),
        },
        {
            "id": "SM-T21",
            "tipo": "teorema",
            "sujeto": "procedimiento_Prob",
            "relacion": "no_produce_por_si_solo",
            "objeto": "un_invariante",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A18", "SM-L14"],
            "gobierna": ["subordinacion_probabilidad"],
            "enunciado": (
                "SM-T21 (La probabilidad no genera el invariante): Ningún "
                "procedimiento Prob produce por sí solo un invariante. "
                "Como máximo localiza candidatos cuyo carácter de invariante "
                "debe ser establecido por anclas de A.\n\n"
                "NOTA OPERATIVA: Evita la confusión entre tasa de acierto "
                "muestral y estructura forzada.\n"
                "EJEMPLO: Un test probabilístico encuentra un patrón frecuente. "
                "El patrón solo se eleva a invariante cuando se ancla en "
                "correlaciones que no dependen del muestreo.\n"
                "DEMOSTRACIÓN: Supóngase que Prob produce un invariante sin "
                "anclas. Entonces el resultado cambiaría con el muestreo, "
                "contradiciendo la definición de invariante. Por SM-A18 y "
                "SM-L14, el carácter de invariante requiere justificación "
                "no probabilística."
            ),
        },
        {
            "id": "SM-T22",
            "tipo": "teorema",
            "sujeto": "mapa_X_distorsionado_respecto_de_R",
            "relacion": "ssi",
            "objeto": "existe_a_en_parcial_D_necesaria_para_recuperar_correlacion_forzada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D18", "SM-D19", "SM-A19"],
            "gobierna": ["origen_distorsion"],
            "enunciado": (
                "SM-T22 (Origen de la distorsión): X distorsionado respecto de R "
                "⟺ existe a ∈ ∂D tal que a es necesaria para recuperar una "
                "correlación forzada por R.\n\n"
                "NOTA OPERATIVA: Localiza la causa de la distorsión en la "
                "frontera del diseñador, no en la ejecución.\n"
                "EJEMPLO: La correlación sol → insolación es forzada por R. "
                "Si la ancla correspondiente está en ∂D, X no puede recuperarla "
                "y está distorsionado en ese dominio.\n"
                "DEMOSTRACIÓN:\n"
                "(⇒) Si X está distorsionado, existe correlación forzada por R "
                "no recuperable desde A_sum. Esa ancla pertenece a "
                "A_pos \\ A_sum = ∂D.\n"
                "(⇐) Si existe a ∈ ∂D necesaria, entonces desde A_sum no se "
                "puede recuperar la correlación que a fuerza. Luego X está "
                "distorsionado."
            ),
        },
        {
            "id": "SM-T23",
            "tipo": "teorema",
            "sujeto": "parcial_D",
            "relacion": "es_registrable_y_delimita",
            "objeto": "dominio_de_toda_maximizacion_posterior_de_Tru_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D18", "SM-T22"],
            "gobierna": ["frontera_disenador"],
            "enunciado": (
                "SM-T23 (Límite del diseñador como información estructural): "
                "El conjunto ∂D es registrable por el sistema y delimita el "
                "dominio de toda maximización posterior de Tru_Ri. "
                "Toda máxima obtenida dentro de A_sum permanece local respecto "
                "de ∂D.\n\n"
                "NOTA OPERATIVA: Saber qué anclas no se recibieron ya es "
                "conocimiento operativo. Marca el borde más allá del cual "
                "las máximas no están garantizadas respecto de R.\n"
                "EJEMPLO: El sistema registra que no posee ancla sobre un "
                "dominio D0. Cualquier γ* calculada sin esa ancla queda "
                "marcada como local respecto de ∂D.\n"
                "DEMOSTRACIÓN: Por definición ∂D es la diferencia entre lo "
                "posible y lo suministrado. El sistema puede registrar qué "
                "anclas le fueron entregadas y, por tanto, cuáles no. "
                "Cualquier γ* = Res(O, Γ, A_sum) solo maximiza dentro de "
                "A_sum. Respecto de los elementos de ∂D la máxima es local."
            ),
        },

        # --------------------------------------------------
        # COROLARIOS
        # --------------------------------------------------
        {
            "id": "SM-C19",
            "tipo": "corolario",
            "sujeto": "no_Prec_mu",
            "relacion": "implica",
            "objeto": "ningun_valor_de_Tru_Ri_calculado_por_mu_es_fiable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T20"],
            "gobierna": ["medicion_fiable"],
            "enunciado": (
                "SM-C19: ¬Prec(μ) ⟹ ningún valor de Tru_Ri calculado por μ es fiable.\n\n"
                "NOTA OPERATIVA: Consecuencia directa de SM-T20 para la práctica "
                "de medición.\n"
                "EJEMPLO: Se reporta Tru_Ri = 1 desde un mecanismo no determinista. "
                "El valor no es atribuible."
            ),
        },
        {
            "id": "SM-C20",
            "tipo": "corolario",
            "sujeto": "exito_de_un_test_probabilistico",
            "relacion": "se_mide_por",
            "objeto": "capacidad_de_localizar_candidato_luego_demostrado_invariante_por_anclas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T21"],
            "gobierna": ["subordinacion_probabilidad"],
            "enunciado": (
                "SM-C20: El éxito de un test probabilístico se mide por su capacidad "
                "de localizar un candidato que después se demuestra invariante por "
                "anclas, no por la tasa de acierto muestral aislada.\n\n"
                "NOTA OPERATIVA: Evita evaluar tests solo por accuracy muestral.\n"
                "EJEMPLO: Un Monte Carlo con alta tasa de acierto que no ancla "
                "sus candidatos en correlaciones forzadas no ha establecido "
                "invariantes."
            ),
        },
        {
            "id": "SM-C21",
            "tipo": "corolario",
            "sujeto": "fallas_de_representacion_del_sistema",
            "relacion": "son",
            "objeto": "imagen_de_parcial_D_dentro_de_X",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T22", "SM-A19"],
            "gobierna": ["origen_distorsion"],
            "enunciado": (
                "SM-C21: Las fallas de representación del sistema no son fallas "
                "de ejecución de μ; son la imagen de ∂D dentro de X.\n\n"
                "NOTA OPERATIVA: Desplaza el diagnóstico desde 'el sistema falló' "
                "hacia 'esta ancla no fue suministrada'.\n"
                "EJEMPLO: El sistema niega un peligro real. La causa no es un "
                "bug de ejecución; es la ausencia de la ancla correspondiente "
                "en A_sum."
            ),
        },
        {
            "id": "SM-C22",
            "tipo": "corolario",
            "sujeto": "registro_de_parcial_D",
            "relacion": "convierte_el_limite_del_disenador_en",
            "objeto": "ancla_negativa_que_delimita_maximas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T23"],
            "gobierna": ["frontera_disenador"],
            "enunciado": (
                "SM-C22: Registrar ∂D (aunque sea parcialmente) convierte el "
                "límite del diseñador en ancla negativa: el sistema sabe que "
                "más allá de ese límite sus máximas no están garantizadas "
                "respecto de R.\n\n"
                "NOTA OPERATIVA: El sistema no necesita poseer la ancla faltante "
                "para saber que le falta. Esa consciencia de límite es ya "
                "información operativa.\n"
                "EJEMPLO: 'No poseo ancla sobre D0; cualquier Tru_Ri calculado "
                "en D0 es local respecto de ∂D'."
            ),
        },
    ]


# ============================================================
# EXPORTACIÓN CANÓNICA
# ============================================================

__all__ = ["CUERPO", "declaraciones"]
