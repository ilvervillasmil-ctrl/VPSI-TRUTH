"""
Cuerpo axiomático: realidad_AX
VPSI-TRUTH / UCF — Familia RE (Ω, modalidad, anuncio, refutación)

Carga automática por modules/axiomas/__init__.py vía CUERPO + declaraciones().
No reescribe TA4, T14, Def-5.3.1, beta, T7, T9, T11, T16, T17, F3, F8, etc.
Solo aporta lo que el grafo base no nombra; depende_de apunta a ids existentes.
"""

from typing import List, Dict, Any

CUERPO = {
    "nombre": "realidad_AX",
    "version": "1.1",
}


def declaraciones() -> List[Dict[str, Any]]:
    return [
        # ==========================================================
        # DEFINICIONES / AXIOMAS DE Ω Y CAPAS
        # ==========================================================
        {
            "id": "RE-A0",
            "tipo": "axioma",
            "sujeto": "Omega",
            "relacion": "es_condicion_de",
            "objeto": "existencia_distincion_concepcion_posibilidad",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-A0 (Ω / ICP): Omega es el contenedor irreducible de posibilidad: "
                "condicion minima para existencia, distincion, concepcion y posibilidad. "
                "No es materia, energia ni geometria. Todo x que existe, se concibe, "
                "se distingue o es posible presupone Omega."
            ),
        },
        {
            "id": "RE-A1",
            "tipo": "axioma",
            "sujeto": "Omega",
            "relacion": "no_es_eliminable_por",
            "objeto": "operador_a_nada_absoluta",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A0"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-A1: No existe operador verificable Phi tal que Phi(Omega) = nada absoluta. "
                "La negacion significativa de Omega la presupone (irreducibilidad)."
            ),
        },
        {
            "id": "RE-A2",
            "tipo": "axioma",
            "sujeto": "R",
            "relacion": "no_anuncia",
            "objeto": "verdad",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "T14"],
            "gobierna": ["realidad", "ontologia", "epistemologia"],
            "enunciado": (
                "RE-A2: R no produce el enunciado de verdad. Todo anuncio "
                "'D es verdadero' es acto de un R_i. Contenido (si verdadero) pertenece a R; "
                "acto pertenece a S (Belonging / Def 5.13). Sin R_i no hay concepto de verdad; "
                "sin R no hay ancla del contenido."
            ),
        },
        {
            "id": "RE-A3",
            "tipo": "axioma",
            "sujeto": "representacion",
            "relacion": "no_es_identica_a",
            "objeto": "R_ni_Omega",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "RE-A0"],
            "gobierna": ["realidad", "ontologia", "semantica"],
            "enunciado": (
                "RE-A3: Ningun marco, constante escrita (incluidos alpha y beta como simbolos), "
                "diccionario, sensor ni modulo RE es identico a R ni a Omega. "
                "Son representaciones o canales hacia X."
            ),
        },
        {
            "id": "RE-A4",
            "tipo": "axioma",
            "sujeto": "observador",
            "relacion": "necesita_para_representar",
            "objeto": "Omega_y_anclaje_en_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A0", "TA4"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-A4 (Asimetria): El observador necesita Omega y anclaje en R para representar. "
                "R no necesita al observador para ser. El concepto de verdad necesita R_i; R no."
            ),
        },

        # ==========================================================
        # MODALIDAD TEMPORAL
        # ==========================================================
        {
            "id": "RE-A5",
            "tipo": "axioma",
            "sujeto": "afirmacion_de_hecho",
            "relacion": "exige",
            "objeto": "modalidad_temporal_explicita",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.3.1"],
            "gobierna": ["realidad", "contexto", "epistemologia"],
            "enunciado": (
                "RE-A5: Toda afirmacion que reclame K de hecho debe declarar modalidad "
                "(pasado | presente | futuro) o quedar como modalidad indefinida. "
                "Sin modalidad adecuada no se reclama K pleno de hecho consumado."
            ),
        },
        {
            "id": "RE-A6",
            "tipo": "axioma",
            "sujeto": "enunciado_de_futuro",
            "relacion": "no_es",
            "objeto": "hecho_consumado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A5", "F7", "F8"],
            "gobierna": ["realidad", "contexto", "epistemologia"],
            "enunciado": (
                "RE-A6: Un enunciado de futuro es hipotesis o prediccion hasta evidencia "
                "de realizacion. No se trata como R consumado en el presente."
            ),
        },
        {
            "id": "RE-A7",
            "tipo": "axioma",
            "sujeto": "anclaje_de_emision",
            "relacion": "se_evalua_en",
            "objeto": "sello_de_emision",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A5", "A10"],
            "gobierna": ["realidad", "contexto", "cache"],
            "enunciado": (
                "RE-A7: El anclaje de una emision se evalua contra el estado de contexto "
                "y de evidencia en el turno/sello en que se emitio, no mediante "
                "reescritura retroactiva de K."
            ),
        },

        # ==========================================================
        # EVIDENCIA Y REFUTACIÓN
        # ==========================================================
        {
            "id": "RE-A8",
            "tipo": "axioma",
            "sujeto": "reclamo_de_sincronizacion_con_R",
            "relacion": "exige",
            "objeto": "X_o_limite_explicito_del_cono",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F3", "T9", "Def-5.3.1"],
            "gobierna": ["realidad", "informacion", "epistemologia"],
            "enunciado": (
                "RE-A8: Afirmar sincronizacion con R exige evidencia X "
                "(o limite explicito del cono causal). Sin ello, K de realidad no es pleno."
            ),
        },
        {
            "id": "RE-A9",
            "tipo": "axioma",
            "sujeto": "ancla_representacional",
            "relacion": "es_refutable_bajo_O_mediante",
            "objeto": "refutacion_estructurada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T14", "T7", "RE-A3"],
            "gobierna": ["realidad", "epistemologia", "meta"],
            "enunciado": (
                "RE-A9: Toda fuente de RE y el propio marco VPSI son refutables bajo O "
                "mediante refutacion estructurada: (a) contraejemplo ejecutable, "
                "(b) X bajo O que rompe teorema/axioma aplicado, o "
                "(c) marco alternativo coherente. Ninguna fuente tiene veto."
            ),
        },
        {
            "id": "RE-A10",
            "tipo": "axioma",
            "sujeto": "negacion_vacia",
            "relacion": "no_constituye",
            "objeto": "refutacion_estructurada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A9", "F8"],
            "gobierna": ["realidad", "epistemologia", "meta"],
            "enunciado": (
                "RE-A10 (Carga de la refutacion): Quien afirma que el marco o cualquier D "
                "es falso o inutil debe aportar refutacion estructurada. "
                "La negacion sin contraejemplo, sin X y sin alternativa coherente "
                "no altera la evaluacion de D; clasifica el acto del negador."
            ),
        },
        {
            "id": "RE-A11",
            "tipo": "axioma",
            "sujeto": "sistema_de_calculo",
            "relacion": "no_asigna",
            "objeto": "R_igual_a_0",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T11", "T17", "TA4"],
            "gobierna": ["realidad", "logica", "constantes"],
            "enunciado": (
                "RE-A11: El sistema no asigna 'R = 0'. Puede asignar colapso de R_i "
                "(Tru_Ri → 0) y entonces Tru_total = beta."
            ),
        },
        {
            "id": "RE-A12",
            "tipo": "axioma",
            "sujeto": "invariantes_estables",
            "relacion": "son_condicion_de",
            "objeto": "deteccion_reproducible_de_error_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA2", "A10"],
            "gobierna": ["realidad", "meta", "logica"],
            "enunciado": (
                "RE-A12 (Estabilidad): Sin invariantes estables (dominio de calculo, "
                "contratos, sellos), el error de R_i no es distinguible de la deriva "
                "y la correccion deja de ser reproducible."
            ),
        },

        # ==========================================================
        # LEMAS
        # ==========================================================
        {
            "id": "RE-L1",
            "tipo": "lema",
            "sujeto": "proposicion_significativa",
            "relacion": "presupone",
            "objeto": "Omega",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A0"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-L1: Toda proposicion significativa distingue al menos un estado de otro. "
                "Toda distincion presupone Omega. Por tanto 'Omega no existe', "
                "si es significativa, presupone Omega."
            ),
        },
        {
            "id": "RE-L2",
            "tipo": "lema",
            "sujeto": "negacion_mental_del_espacio",
            "relacion": "presupone",
            "objeto": "Omega",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-L1", "RE-A0"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-L2: La representacion 'no hay espacio' sigue siendo representacion: "
                "requiere distincion y presupone Omega. No elimina R^3 ni R."
            ),
        },
        {
            "id": "RE-L3",
            "tipo": "lema",
            "sujeto": "alpha_beta_escritos",
            "relacion": "pertenecen_al_orden_de",
            "objeto": "representacion_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A3", "beta"],
            "gobierna": ["realidad", "constantes", "semantica"],
            "enunciado": (
                "RE-L3: alpha y beta, como simbolos escritos y como uso en Tru_total, "
                "existen en el orden de la representacion porque hay R_i que deriva y aplica. "
                "Eso no los convierte en R ni en Omega."
            ),
        },
        {
            "id": "RE-L4",
            "tipo": "lema",
            "sujeto": "eliminacion_de_Ri",
            "relacion": "elimina",
            "objeto": "concepto_de_verdad_no_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A2", "T14", "TA4"],
            "gobierna": ["realidad", "epistemologia"],
            "enunciado": (
                "RE-L4: Eliminar todo observador elimina el acto y el concepto de verdad. "
                "No elimina el contenido de R ni Omega."
            ),
        },
        {
            "id": "RE-L5",
            "tipo": "lema",
            "sujeto": "autoaplicacion_del_marco",
            "relacion": "es",
            "objeto": "evaluacion_legitima",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A9", "T14"],
            "gobierna": ["realidad", "meta", "epistemologia"],
            "enunciado": (
                "RE-L5: Evaluar una descripcion del propio marco con las reglas del marco "
                "es instancia valida de evaluacion. No es circularidad viciosa ni identifica "
                "el marco con R."
            ),
        },

        # ==========================================================
        # TEOREMAS
        # ==========================================================
        {
            "id": "RE-T1",
            "tipo": "teorema",
            "sujeto": "Omega",
            "relacion": "es_irreducible",
            "objeto": "respecto_de_nada_absoluta",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A0", "RE-A1", "RE-L1"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-T1 (Irreducibilidad de Omega): No existe operador verificable Phi "
                "tal que Phi(Omega) = nada absoluta. Si hubiera transicion de Omega a la nada, "
                "deberia existir distincion entre estados; esa distincion presupone Omega."
            ),
        },
        {
            "id": "RE-T2",
            "tipo": "teorema",
            "sujeto": "nada_absoluta",
            "relacion": "no_es",
            "objeto": "estado_coherente",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-T1", "A3"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-T2: La nada absoluta no es estado coherente: si fuera concebible "
                "o definible, presupondria Omega y dejaria de ser absoluta."
            ),
        },
        {
            "id": "RE-T3",
            "tipo": "teorema",
            "sujeto": "secuencia_ontologica",
            "relacion": "es",
            "objeto": "Omega_distincion_relacion_geometria_materia",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A0", "A1"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-T3: La derivacion es Omega → distincion → relacion → geometria → materia "
                "(y no al reves). Cada nivel presupone el anterior."
            ),
        },
        {
            "id": "RE-T4",
            "tipo": "teorema",
            "sujeto": "R3",
            "relacion": "presupone_y_no_es_identico_a",
            "objeto": "Omega",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-T3", "RE-A0"],
            "gobierna": ["realidad", "ontologia", "constantes"],
            "enunciado": (
                "RE-T4: Toda geometria G_n (en particular R^3) presupone Omega. "
                "Omega no tiene dimension: las dimensiones son estructuras derivadas. "
                "Preguntar cuantas dimensiones tiene Omega es error de categoria."
            ),
        },
        {
            "id": "RE-T5",
            "tipo": "teorema",
            "sujeto": "marco_VPSI",
            "relacion": "es_mapa_no",
            "objeto": "territorio_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A3", "T14", "TA4"],
            "gobierna": ["realidad", "meta", "epistemologia"],
            "enunciado": (
                "RE-T5 (Mapa ≠ territorio): El marco VPSI, Tru_total, alpha y beta son "
                "representaciones estructuradas. Si una descripcion del marco falla bajo "
                "refutacion estructurada, se corrige o delimita el mapa. "
                "R y Omega no se reescriben por el fallo del mapa."
            ),
        },
        {
            "id": "RE-T6",
            "tipo": "teorema",
            "sujeto": "BETA_como_simbolo_del_mapa",
            "relacion": "no_es_identico_a",
            "objeto": "R_ni_Omega",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-L3", "beta", "T11"],
            "gobierna": ["realidad", "constantes", "meta"],
            "enunciado": (
                "RE-T6: beta = 1/27 garantiza en el formalismo que Tru_total no cae a 0. "
                "Es ancla geometrica del mapa en R^3, no identidad con R ni con Omega. "
                "Quien la refute debe atacar derivacion o uso con refutacion estructurada."
            ),
        },
        {
            "id": "RE-T7",
            "tipo": "teorema",
            "sujeto": "todo_observador",
            "relacion": "tiene_derecho_simetrico_a",
            "objeto": "refutacion_estructurada_del_marco",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A9", "RE-A10", "T14"],
            "gobierna": ["realidad", "epistemologia", "meta"],
            "enunciado": (
                "RE-T7: Ningun observador (autor, consenso, Engine, CI) esta exento "
                "de RE-A9 y RE-A10. El derecho igual a refutar se sigue de que el marco "
                "es representacion, no R."
            ),
        },
        {
            "id": "RE-T8",
            "tipo": "teorema",
            "sujeto": "enunciado_de_catastrofe_futura",
            "relacion": "no_equivale_a",
            "objeto": "dominio_inexistente_en_presente",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A5", "RE-A6"],
            "gobierna": ["realidad", "contexto", "logica"],
            "enunciado": (
                "RE-T8 (Modalidad de catastrofe): 'Puede destruirse el dominio local' (futuro) "
                "no equivale a 'el dominio no existe / ya no es' (presente). "
                "Identificarlos es error de modalidad y degrada L y/o C."
            ),
        },
        {
            "id": "RE-T9",
            "tipo": "teorema",
            "sujeto": "cese_de_S_o_dominio_local",
            "relacion": "no_implica",
            "objeto": "cese_de_R_ni_Omega",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "RE-A0", "T10"],
            "gobierna": ["realidad", "ontologia"],
            "enunciado": (
                "RE-T9 (Persistencia asimetricas): Del cese de S o de un dominio local "
                "no se sigue el cese de R ni de Omega."
            ),
        },
        {
            "id": "RE-T10",
            "tipo": "teorema",
            "sujeto": "error_de_Ri",
            "relacion": "no_altera",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA8", "T10", "T14"],
            "gobierna": ["realidad", "epistemologia"],
            "enunciado": (
                "RE-T10: La equivocacion en la representacion obliga a adaptar R_i "
                "a la evidencia. No autoriza a afirmar que R se equivoco."
            ),
        },
        {
            "id": "RE-T11",
            "tipo": "teorema",
            "sujeto": "uso_del_marco_contra_el_marco",
            "relacion": "no_anula",
            "objeto": "Omega_ni_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-L5", "RE-T5", "T14"],
            "gobierna": ["realidad", "meta", "epistemologia"],
            "enunciado": (
                "RE-T11: Emplear C, L, K, O y evidencia para mostrar que una descripcion "
                "del propio marco no alcanza Tru = 1 es legitimo. El resultado, si procede, "
                "es Tru(D_marco) < 1 o delimitacion de alcance; no la anulacion de Omega ni de R."
            ),
        },
        {
            "id": "RE-T12",
            "tipo": "teorema",
            "sujeto": "R",
            "relacion": "no_se_auto_declara",
            "objeto": "como_verdad",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A2", "T14", "T7"],
            "gobierna": ["realidad", "epistemologia", "semantica"],
            "enunciado": (
                "RE-T12: No existe emision de R del tipo 'esto es verdad'. "
                "Toda verdad anunciada es acto de R_i sobre un contenido que, "
                "si es verdadero, esta en R."
            ),
        },
        {
            "id": "RE-T13",
            "tipo": "teorema",
            "sujeto": "capacidad_de_formalizar_Tru",
            "relacion": "pertenece_a",
            "objeto": "Ri_no_a_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A2", "RE-T12", "T14"],
            "gobierna": ["realidad", "epistemologia", "meta"],
            "enunciado": (
                "RE-T13: La capacidad de formalizar y medir Tru(D) pertenece a R_i "
                "(acto + capacidad C·L·K). Ese poder no convierte al formalizador en R. "
                "El contenido al que Tru apunta, cuando Tru_total = 1, no es propiedad "
                "del formalizador."
            ),
        },

        # ==========================================================
        # COROLARIOS
        # ==========================================================
        {
            "id": "RE-C1",
            "tipo": "corolario",
            "sujeto": "referente_futuro_o_sin_X_como_hecho_presente",
            "relacion": "no_permite",
            "objeto": "K_de_realidad_pleno",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A6", "RE-A8", "F8"],
            "gobierna": ["realidad", "contexto", "epistemologia"],
            "enunciado": (
                "RE-C1 (Invencion de objeto): Introducir un referente futuro o no evidenciado "
                "como hecho presente sin sello ni X no permite K de realidad pleno; "
                "se clasifica como hipotesis, modalidad indefinida o invencion de objeto."
            ),
        },
        {
            "id": "RE-C2",
            "tipo": "corolario",
            "sujeto": "evidencia_sin_fuente_y_tiempo",
            "relacion": "no_sostiene",
            "objeto": "auditoria_por_terceros",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A7", "RE-A8"],
            "gobierna": ["realidad", "cache", "meta"],
            "enunciado": (
                "RE-C2 (Instantanea): Evidencia de contraste sin fuente y tiempo "
                "no sostiene verificacion por terceros ni reconstruccion del calculo."
            ),
        },
        {
            "id": "RE-C3",
            "tipo": "corolario",
            "sujeto": "negacion_vacia_de_alpha_beta_o_Tru",
            "relacion": "no_modifica",
            "objeto": "evaluacion_del_marco",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A10", "RE-T7"],
            "gobierna": ["realidad", "meta", "epistemologia"],
            "enunciado": (
                "RE-C3: Negar alpha, beta o Tru sin refutacion estructurada no modifica "
                "la evaluacion del marco; clasifica el acto como rechazo no estructurado."
            ),
        },
        {
            "id": "RE-C4",
            "tipo": "corolario",
            "sujeto": "modulo_RE",
            "relacion": "no_es",
            "objeto": "arbitro_de_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A3", "RE-A9", "T7"],
            "gobierna": ["realidad"],
            "enunciado": (
                "RE-C4: El modulo RE aporta candidatos a X bajo O. "
                "No tiene veto sobre C, L, K ni Tru. Sus fuentes estan sujetas a RE-A9."
            ),
        },
        {
            "id": "RE-C5",
            "tipo": "corolario",
            "sujeto": "confusion_Ri_con_R_o_Omega",
            "relacion": "invalida",
            "objeto": "reclamo_de_K_pleno_de_realidad",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A3", "T12", "TA4"],
            "gobierna": ["realidad", "semantica", "logica"],
            "enunciado": (
                "RE-C5: Tratar una representacion (marco, diccionario, salida de RE, "
                "simbolo beta, enunciado de Tru) como si fuera R u Omega invalida "
                "el reclamo de K pleno de realidad."
            ),
        },
        {
            "id": "RE-C6",
            "tipo": "corolario",
            "sujeto": "acto_D_es_verdadero",
            "relacion": "pertenece_a",
            "objeto": "S_contenido_a_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A2", "RE-T12", "T14"],
            "gobierna": ["realidad", "epistemologia"],
            "enunciado": (
                "RE-C6 (R no anuncia; R_i anuncia): El acto 'D es verdadero' pertenece a S. "
                "El contenido, si es verdadero, pertenece a R. "
                "Omega es condicion de que el acto y la distincion sean posibles."
            ),
        },
        {
            "id": "RE-C7",
            "tipo": "corolario",
            "sujeto": "correccion_ante_evidencia",
            "relacion": "es_adaptacion_de",
            "objeto": "Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-T10", "RE-A12", "T14"],
            "gobierna": ["realidad", "meta"],
            "enunciado": (
                "RE-C7: Cuando el codigo, el test o la evidencia muestran error, "
                "quien se adapta es R_i. Esa adaptacion es el modo legitimo de crecimiento "
                "del mapa; no es negociacion con R."
            ),
        },
        {
            "id": "RE-C8",
            "tipo": "corolario",
            "sujeto": "discurso_sobre_verdad_sin_medida",
            "relacion": "permanece_en",
            "objeto": "orden_del_concepto_sin_cierre_ejecutable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-T13", "RE-A2"],
            "gobierna": ["realidad", "epistemologia", "meta"],
            "enunciado": (
                "RE-C8: Un discurso sobre la verdad que no produce valor comparable "
                "ni admite contraejemplo numerico permanece en el orden del concepto (R_i) "
                "sin cerrar el contenido; puede extenderse indefinidamente sin resolucion ejecutable."
            ),
        },
    ]


__all__ = ["CUERPO", "declaraciones"]
