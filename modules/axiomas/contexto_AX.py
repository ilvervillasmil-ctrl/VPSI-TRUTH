"""
Cuerpo axiomático: CONTEXTO (CX)
================================
Armazón evaluable O_context. Compatible con VPSI 9.4
(Def-5.3.1, TA3, TA4, T16, T17).

No redefine α/β ni Tru. Formaliza el dominio sin el cual K = ∅.

Ubicación: modules/axiomas/contexto_AX.py
(Sin CONTENEDOR: lo carga el único __init__.py del módulo AX.)
"""

from __future__ import annotations

CUERPO = {
    "nombre": "contexto",
    "version": "0.2",
}


def declaraciones():
    return [
        # ----------------------------------------------------------
        # AXIOMAS CX-A1 … CX-A13
        # ----------------------------------------------------------
        {
            "id": "CX-A1",
            "tipo": "axioma",
            "sujeto": "K(D)",
            "relacion": "requiere_para_ser_definible",
            "objeto": "O_context_explicito",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA3", "Def-5.3.1"],
            "gobierna": ["contexto", "logica", "epistemologia"],
            "enunciado": (
                "CX-A1 (Existencia evaluativa): K(D) es definible si y solo si existe "
                "al menos un O_context explícito respecto del cual se mide."
            ),
        },
        {
            "id": "CX-A2",
            "tipo": "axioma",
            "sujeto": "O_context",
            "relacion": "no_es_identico_a",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4"],
            "gobierna": ["contexto", "ontologia"],
            "enunciado": (
                "CX-A2 (No-identidad con R): O_context no es identico a R. "
                "El contexto es marco de lectura, no la realidad absoluta (TA4)."
            ),
        },
        {
            "id": "CX-A3",
            "tipo": "axioma",
            "sujeto": "D",
            "relacion": "admite_conjunto_de",
            "objeto": "contextos_O_i",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.3.1"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-A3 (Multiplicidad): Una misma descripcion D puede admitir un conjunto "
                "de contextos O_i. K(D|O_i) y K(D|O_j) pueden diferir sin "
                "contradiccion del framework."
            ),
        },
        {
            "id": "CX-A4",
            "tipo": "axioma",
            "sujeto": "significado_evaluable_de_D",
            "relacion": "es_fijado_por",
            "objeto": "organizacion_coherente_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A1"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-A4 (Determinacion del significado evaluable): El significado evaluable "
                "de D relativo a O queda fijado por la organizacion coherente de O, no por "
                "la sola secuencia de tokens de D aislada de todo marco."
            ),
        },
        {
            "id": "CX-A5",
            "tipo": "axioma",
            "sujeto": "intencion_del_evaluador",
            "relacion": "selecciona_pero_no_asigna",
            "objeto": "Tru_total(D)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5"],
            "gobierna": ["contexto", "epistemologia"],
            "enunciado": (
                "CX-A5 (Intencion como selector): La intencion del evaluador puede elegir "
                "o declarar O; no asigna por si misma Tru_total(D)."
            ),
        },
        {
            "id": "CX-A6",
            "tipo": "axioma",
            "sujeto": "S",
            "relacion": "no_enumera_en_tiempo_finito_todos_los",
            "objeto": "O_admisibles_de_D_no_trivial",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A3"],
            "gobierna": ["contexto", "meta"],
            "enunciado": (
                "CX-A6 (Incompletitud operativa): Ningun sistema S enumera en tiempo finito "
                "todos los O admisibles de un D no trivial."
            ),
        },
        {
            "id": "CX-A7",
            "tipo": "axioma",
            "sujeto": "O",
            "relacion": "permanece_el_mismo_mientras",
            "objeto": "elementos_integrables_en_su_armazon",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A4"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A7 (Unidad del armazon): O permanece el mismo mientras los elementos "
                "introducidos sean evaluables bajo la misma organizacion coherente que define O."
            ),
        },
        {
            "id": "CX-A8",
            "tipo": "axioma",
            "sujeto": "cambio_de_contexto",
            "relacion": "ocurre_cuando",
            "objeto": "material_no_integrable_sin_redefinir_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A7"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-A8 (Cambio de contexto): Hay cambio de contexto cuando el nuevo material "
                "no es integrable en el armazon vigente sin redefinir el significado global "
                "de la evaluacion."
            ),
        },
        {
            "id": "CX-A9",
            "tipo": "axioma",
            "sujeto": "cardinalidad_de_topicos_bajo_O",
            "relacion": "no_implica_por_si_sola",
            "objeto": "nuevo_contexto",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A7"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A9 (Amplitud no implica multiplicidad): El crecimiento del numero de "
                "topicos bajo O no implica por si solo un nuevo contexto. La condicion es "
                "pertenencia, no cardinalidad."
            ),
        },
        {
            "id": "CX-A10",
            "tipo": "axioma",
            "sujeto": "K_en_tramo_sin_O_estable",
            "relacion": "permanece",
            "objeto": "indefinido",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A1", "Def-5.3.1"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-A10 (Indefinicion operativa): Si en un tramo no es posible declarar ni "
                "recuperar un O estable, entonces K en ese tramo permanece indefinido, no cero."
            ),
        },
        {
            "id": "CX-A11",
            "tipo": "axioma",
            "sujeto": "O",
            "relacion": "puede_definirse_a",
            "objeto": "distinta_resolucion_de_escala",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A1"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-A11 (Escalas): Un contexto puede definirse a distinta resolucion "
                "(morfologica, lexica, combinatoria, discursiva, de dominio, de codigo). "
                "Cada escala usada para K debe declararse explicitamente."
            ),
        },
        {
            "id": "CX-A12",
            "tipo": "axioma",
            "sujeto": "asociacion_forma_uso_bajo_O_lengua",
            "relacion": "es_regla_de",
            "objeto": "ese_armazon_de_codigo",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A4", "CX-A2"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-A12 (Invariante linguistico): Dentro de un O_lengua fijado, la asociacion "
                "forma-uso convencional es la regla de ese armazon. Cambiar de codigo es "
                "cambio de O, no matiz del mismo O."
            ),
        },
        {
            "id": "CX-A13",
            "tipo": "axioma",
            "sujeto": "O_context",
            "relacion": "no_anula",
            "objeto": "BETA",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta", "T17", "TA4"],
            "gobierna": ["contexto", "constantes", "ontologia"],
            "enunciado": (
                "CX-A13 (No potestad sobre beta): Ningun O anula beta. R persiste bajo "
                "cualquier marco de lectura (Tru_total >= beta)."
            ),
        },

        # ----------------------------------------------------------
        # LEMAS CX-L1 … CX-L4
        # ----------------------------------------------------------
        {
            "id": "CX-L1",
            "tipo": "lema",
            "sujeto": "sucesion_sin_O_estable",
            "relacion": "no_garantiza",
            "objeto": "Tru_global_unico_del_discurso",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A10", "CX-A1"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-L1 (Deriva conversacional): Una sucesion de turnos sin O estable no "
                "garantiza convergencia de un unico Tru bien formado sobre el discurso agregado."
            ),
        },
        {
            "id": "CX-L2",
            "tipo": "lema",
            "sujeto": "asignacion_K_sin_O",
            "relacion": "no_es_legitima_como",
            "objeto": "K_igual_0_ni_K_igual_1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.3.1", "CX-A1"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-L2: Si el evaluador no declara O, no es legitimo asignar K=0 ni K=1; "
                "solo indefinido (Def-5.3.1)."
            ),
        },
        {
            "id": "CX-L3",
            "tipo": "lema",
            "sujeto": "K_en_escala_i",
            "relacion": "no_implica",
            "objeto": "K_en_escala_j",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A11"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-L3 (Transferencia de escala): K(D|O a escala i)=1 no implica "
                "K(D|O a escala j)=1 para i distinto de j."
            ),
        },
        {
            "id": "CX-L4",
            "tipo": "lema",
            "sujeto": "C_y_L_locales_de_dos_observadores",
            "relacion": "no_implican",
            "objeto": "O_compartido",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A3"],
            "gobierna": ["contexto", "epistemologia"],
            "enunciado": (
                "CX-L4: Dos observadores pueden tener C=1 y L=1 en descripciones locales "
                "y aun asi no compartir O; entonces no hay un unico K de pareja."
            ),
        },

        # ----------------------------------------------------------
        # TEOREMAS CX-T1 … CX-T10
        # ----------------------------------------------------------
        {
            "id": "CX-T1",
            "tipo": "teorema",
            "sujeto": "K(D|O_1)",
            "relacion": "puede_diferir_de",
            "objeto": "K(D|O_2)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A3", "Def-5.3.1"],
            "gobierna": ["contexto", "logica", "semantica"],
            "enunciado": (
                "CX-T1 (Independencia parcial de lecturas): Existen D, O_1, O_2 tales que "
                "K(D|O_1)=1 y K(D|O_2)<1."
            ),
        },
        {
            "id": "CX-T2",
            "tipo": "teorema",
            "sujeto": "K(D|O_1)=1",
            "relacion": "no_implica",
            "objeto": "K(D|O_2)=1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T1"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-T2 (No transferencia automatica): K(D|O_1)=1 no implica K(D|O_2)=1."
            ),
        },
        {
            "id": "CX-T3",
            "tipo": "teorema",
            "sujeto": "orden_de_evaluacion_MC",
            "relacion": "utiliza_y_no_crea_ex_nihilo",
            "objeto": "O_context",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A3", "CX-A1"],
            "gobierna": ["contexto", "meta"],
            "enunciado": (
                "CX-T3: El orden de evaluacion (correlacion mecanica) utiliza contextos "
                "declarados; no crea O ex nihilo."
            ),
        },
        {
            "id": "CX-T4",
            "tipo": "teorema",
            "sujeto": "e",
            "relacion": "pertenece_a_O_si",
            "objeto": "inclusion_no_redefine_regla_global_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A7", "CX-A4"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-T4 (Criterio de pertenencia): e pertenece a O si y solo si la inclusion "
                "de e no obliga a redefinir la regla de significado global de O."
            ),
        },
        {
            "id": "CX-T5",
            "tipo": "teorema",
            "sujeto": "elementos_e_i_en_O",
            "relacion": "preservan",
            "objeto": "identidad_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T4", "CX-A9"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-T5 (Expansion legitima): Si e_1,...,e_n pertenecen a O (CX-T4), el "
                "contexto sigue siendo O (expansion coherente), no una familia de contextos."
            ),
        },
        {
            "id": "CX-T6",
            "tipo": "teorema",
            "sujeto": "e_estrella_no_en_O",
            "relacion": "obliga_a",
            "objeto": "nuevo_O_o_K_indefinido",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T4", "CX-A8", "CX-A10"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-T6 (Ruptura): Si aparece e* que no pertenece a O, entonces o se declara "
                "un nuevo O', o el tramo queda con K indefinido respecto de O."
            ),
        },
        {
            "id": "CX-T7",
            "tipo": "teorema",
            "sujeto": "operacion_declarar_O_y_medir_K",
            "relacion": "es_aplicable_en",
            "objeto": "cada_escala_sin_transferencia_automatica",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A11", "CX-L3"],
            "gobierna": ["contexto", "semantica", "meta"],
            "enunciado": (
                "CX-T7 (Fractalidad operativa): Declarar O y medir K es aplicable en cada "
                "escala; la validez en una escala no se transfiere automaticamente a otra."
            ),
        },
        {
            "id": "CX-T8",
            "tipo": "teorema",
            "sujeto": "dos_O_lengua_incompatibles_sobre_misma_forma",
            "relacion": "implican",
            "objeto": "cambio_de_contexto_o_K_de_pareja_no_unitario",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A12", "CX-A8", "CX-L4"],
            "gobierna": ["contexto", "semantica", "epistemologia"],
            "enunciado": (
                "CX-T8 (Choque de invariantes de codigo): Si dos O linguisticos asignan a la "
                "misma forma usos no co-satisfacibles en un mismo acto, hay cambio de contexto "
                "declarado o el acto conjunto degrada coherencia de dialogo / K de pareja."
            ),
        },
        {
            "id": "CX-T9",
            "tipo": "teorema",
            "sujeto": "discurso_en_deriva",
            "relacion": "no_admite",
            "objeto": "Tru_total_unico_del_discurso_entero",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-L1", "CX-A10"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-T9: Si el discurso esta en deriva, no existe un unico Tru_total bien formado "
                "del discurso entero; solo, a lo sumo, valores locales por fragmentos con O_i propios."
            ),
        },
        {
            "id": "CX-T10",
            "tipo": "teorema",
            "sujeto": "Tru_total_bajo_cualquier_O",
            "relacion": "respeta",
            "objeto": "BETA_y_techo_ALPHA",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T16", "T17", "CX-A13"],
            "gobierna": ["contexto", "constantes", "logica"],
            "enunciado": (
                "CX-T10: Para cualquier O y D con factores definidos, beta <= Tru_total(D) <= 1 "
                "y la contribucion de R_i no supera alpha. El cuerpo CX no modifica alpha ni beta."
            ),
        },

        # ----------------------------------------------------------
        # COROLARIOS CX-C1 … CX-C8
        # ----------------------------------------------------------
        {
            "id": "CX-C1",
            "tipo": "corolario",
            "sujeto": "afirmacion_K_sin_O",
            "relacion": "es",
            "objeto": "mal_formada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-L2", "Def-5.3.1"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-C1: La afirmacion K(D)=1 o K(D)=0 sin O declarado es mal formada."
            ),
        },
        {
            "id": "CX-C2",
            "tipo": "corolario",
            "sujeto": "dos_observadores_con_C_L_igual_1",
            "relacion": "pueden_obtener",
            "objeto": "K_distintos_si_O_distintos",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T1", "CX-L4"],
            "gobierna": ["contexto", "epistemologia"],
            "enunciado": (
                "CX-C2: Dos observadores con C=L=1 pueden obtener K distintos si O_1 distinto "
                "de O_2. No implica por si solo posesion de R; implica dominios distintos."
            ),
        },
        {
            "id": "CX-C3",
            "tipo": "corolario",
            "sujeto": "multiplicidad_de_contextos",
            "relacion": "no_anula",
            "objeto": "BETA",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A13", "T17"],
            "gobierna": ["contexto", "constantes"],
            "enunciado": (
                "CX-C3: La multiplicidad de contextos no anula beta: R no depende de cuantos "
                "O se declaren."
            ),
        },
        {
            "id": "CX-C4",
            "tipo": "corolario",
            "sujeto": "paquete_de_ciclo_sin_O_context",
            "relacion": "no_puede_reclamar",
            "objeto": "Tru_numerico_completo",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A1", "CX-A10"],
            "gobierna": ["contexto", "logica", "meta"],
            "enunciado": (
                "CX-C4 (Maquina): Un paquete de evaluacion sin O_context explicito no puede "
                "reclamar Tru numerico completo; estado PARCIAL o UNDEFINED, no invencion de K."
            ),
        },
        {
            "id": "CX-C5",
            "tipo": "corolario",
            "sujeto": "conclusion_global_bajo_contexto_indefinido",
            "relacion": "no_es",
            "objeto": "Tru_total_del_discurso_entero",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T9"],
            "gobierna": ["contexto", "logica"],
            "enunciado": (
                "CX-C5: Si el contexto es indefinido a lo largo de la cadena, la conclusion "
                "global no es un Tru_total del discurso entero."
            ),
        },
        {
            "id": "CX-C6",
            "tipo": "corolario",
            "sujeto": "desacuerdo_inter_codigo",
            "relacion": "prueba",
            "objeto": "no_comparticion_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T8", "CX-A12"],
            "gobierna": ["contexto", "semantica", "epistemologia"],
            "enunciado": (
                "CX-C6: Si S_1 evalua bajo O_1 y S_2 bajo O_2 con reglas incompatibles para "
                "la misma forma, el desacuerdo prueba no comparticion de O, no necesariamente "
                "Tru=0 respecto de R."
            ),
        },
        {
            "id": "CX-C7",
            "tipo": "corolario",
            "sujeto": "trabajo_formal",
            "relacion": "exige",
            "objeto": "O_de_dominio_estable_y_expansiones_CX-T4",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T4", "CX-T5", "CX-A10"],
            "gobierna": ["contexto", "meta"],
            "enunciado": (
                "CX-C7: En trabajo formal se exige O de dominio estable y solo expansiones "
                "que cumplan CX-T4/T5; la deriva es propia de conversacion trivial no controlada."
            ),
        },
        {
            "id": "CX-C8",
            "tipo": "corolario",
            "sujeto": "secuencia_de_contextos_del_ciclo",
            "relacion": "es_parte_de",
            "objeto": "evidencia_en_CACHE",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-C4", "CX-A8"],
            "gobierna": ["contexto", "meta"],
            "enunciado": (
                "CX-C8: La secuencia de contextos de un ciclo (mismos O, cambios, indefinido) "
                "es parte de la evidencia depositable en CACHE para auditoria del filtro Centinela."
            ),
        },
    ]
