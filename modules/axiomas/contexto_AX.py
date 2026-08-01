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

        # ==============================================================
        # ANEXO CX v0.3 — Ligadura, registro, semántica operativa
        # ==============================================================

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
        # ===========================================================
        # ANEXO CX v0.4 — Fractalidad, entrada natural, multi-O, generacion
        # ===========================================================
        {
            "id": "CX-D16",
            "tipo": "corolario",
            "sujeto": "grano_contextual",
            "relacion": "es",
            "objeto": "nivel_de_resolucion_del_material_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-D16 (Grano contextual): Nivel de resolucion del material bajo el cual se "
                "declara O: grafema/forma, palabra, frase, turno, conversacion, sesion, meta."
            ),
        },
        {
            "id": "CX-D17",
            "tipo": "corolario",
            "sujeto": "O_micro_y_O_global",
            "relacion": "distinguen",
            "objeto": "marco_de_tramo_versus_mapa_de_secuencia",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A14", "CX-C8"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-D17 (O micro / O global): O micro es el marco de un tramo, frase o criterio; "
                "O global es el marco que describe el mapa de varios O micro. O global no sustituye "
                "los micro ni agrega K sin regla de agregacion explicita."
            ),
        },
        {
            "id": "CX-D18",
            "tipo": "corolario",
            "sujeto": "entrada_natural",
            "relacion": "es",
            "objeto": "material_de_casilla_sin_campos_tecnicos_obligatorios",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-D18 (Entrada natural): Material de casilla en prosa, lista, etiqueta o "
                "conversacion sin exigir al emisor campos tecnicos (O_id, escala, ...). "
                "El sistema eleva ese material a registro operativo."
            ),
        },
        {
            "id": "CX-D19",
            "tipo": "corolario",
            "sujeto": "generacion_de_contexto",
            "relacion": "es",
            "objeto": "proponer_y_fijar_enunciado_O_explicito",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A14", "Def-5.3.1"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-D19 (Generacion de contexto): Acto de proponer y fijar un enunciado_O "
                "(y registro) cuando la peticion lo ordena. Generar = declarar O explicito, "
                "no ocultar un marco implicito."
            ),
        },
        {
            "id": "CX-D20",
            "tipo": "corolario",
            "sujeto": "modalidad_de_emision",
            "relacion": "es",
            "objeto": "canal_o_lengua_del_material",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A15", "CX-A16"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-D20 (Modalidad de emision): Canal o lengua del material (ES, EN, mezcla, "
                "codigo, prosa). La modalidad es atributo del tramo; no es por si sola un cambio "
                "de O, salvo que cambie el marco tematico evaluable."
            ),
        },
        {
            "id": "CX-D21",
            "tipo": "corolario",
            "sujeto": "criterios_bajo_un_O",
            "relacion": "son",
            "objeto": "lista_de_condiciones_de_un_mismo_O_de_sesion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-D21 (Criterios bajo un O): Lista de condiciones (1, 2, 3, ...) que precisan "
                "un mismo O de sesion, no una familia de O distintos, salvo declaracion de cambio."
            ),
        },
        {
            "id": "CX-A19",
            "tipo": "axioma",
            "sujeto": "forma_de_registro_operativo",
            "relacion": "es_invariante_en",
            "objeto": "todo_grano_contextual",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D16", "CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A19 (Fractalidad de la forma de marco): La estructura de registro operativo "
                "(O_id, enunciado, estado, evento, ligaduras) es la misma en todo grano. "
                "Cambia el grano, no la forma de la regla."
            ),
        },
        {
            "id": "CX-A20",
            "tipo": "axioma",
            "sujeto": "casilla_con_texto_usable",
            "relacion": "constituye",
            "objeto": "declaracion_de_marco_via_entrada_natural",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D18", "CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A20 (Entrada natural admisible): Una casilla con texto usable constituye "
                "declaracion de marco via entrada natural. La ausencia de vocabulario tecnico "
                "del emisor no anula la declaracion si el enunciado es recuperable."
            ),
        },
        {
            "id": "CX-A21",
            "tipo": "axioma",
            "sujeto": "casilla_vacia_o_enunciado_no_recuperable",
            "relacion": "implica",
            "objeto": "estado_indefinido_y_K_no_reclamable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A10", "Def-5.3.1"],
            "gobierna": ["contexto", "evaluacion"],
            "enunciado": (
                "CX-A21 (Vacio implica indefinido): Casilla vacia o enunciado no recuperable "
                "implica estado indefinido; K no es reclamable en ese tramo."
            ),
        },
        {
            "id": "CX-A22",
            "tipo": "axioma",
            "sujeto": "lista_numerada_de_criterios_sin_cambio_declarado",
            "relacion": "arma",
            "objeto": "un_solo_O_con_criterios",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D21", "CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A22 (Un O por lista de criterios): Una lista numerada de criterios bajo una "
                "misma casilla, sin declaracion de cambio, arma un O con criterios, no N O "
                "independientes por defecto."
            ),
        },
        {
            "id": "CX-A23",
            "tipo": "axioma",
            "sujeto": "cambio_de_O_en_conversacion",
            "relacion": "requiere",
            "objeto": "declaracion_o_frontera_explicita_o_cierre_de_sesion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A8", "CX-T6"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A23 (Cambio solo por declaracion o frontera explicita): El cambio de O en "
                "una conversacion se reconoce por declaracion de cambio, por frontera de tramo "
                "con nuevo marco, o por cierre de sesion — no por inferencia silenciosa del auditor."
            ),
        },
        {
            "id": "CX-A24",
            "tipo": "axioma",
            "sujeto": "contexto_generado_por_peticion",
            "relacion": "debe_fijarse_por_escrito_antes_de",
            "objeto": "reclamo_de_K_o_Tru",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D19", "Def-5.3.1"],
            "gobierna": ["contexto", "evaluacion"],
            "enunciado": (
                "CX-A24 (Generacion es declaracion): Si la peticion ordena crear un contexto, "
                "el O propuesto debe quedar fijado por escrito en el registro antes de cualquier "
                "reclamo de K o Tru sobre ese marco."
            ),
        },
        {
            "id": "CX-A25",
            "tipo": "axioma",
            "sujeto": "O_global_de_mapa",
            "relacion": "no_borra_ni_promedia_en_silencio",
            "objeto": "O_micro_de_la_secuencia",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D17"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-A25 (O global no colapsa micro): Un O global de mapa conversacional no borra "
                "ni promedia en silencio los O micro; cada micro conserva su estado y su derecho "
                "a K local."
            ),
        },
        {
            "id": "CX-A26",
            "tipo": "axioma",
            "sujeto": "cambio_de_lengua_o_canal",
            "relacion": "no_implica_por_si_solo",
            "objeto": "evento_cambio_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D20", "CX-A15"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-A26 (Modalidad no es O): Cambio de lengua o de canal no implica por si solo "
                "evento=cambio de O; implica reevaluacion de ligaduras o escala si el significado "
                "evaluable depende de la modalidad."
            ),
        },
        {
            "id": "CX-A27",
            "tipo": "axioma",
            "sujeto": "mismo_material_bajo_N_O_distintos",
            "relacion": "admite",
            "objeto": "N_evaluaciones_locales_sin_identificar_O_con_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "CX-A18"],
            "gobierna": ["contexto", "epistemologia"],
            "enunciado": (
                "CX-A27 (Multi-marco de evaluacion): Es admisible evaluar el mismo material bajo "
                "N O distintos. Cada uno produce evaluacion local; la comparacion es entre "
                "descripciones, no la identificacion de un O con R."
            ),
        },
        {
            "id": "CX-L8",
            "tipo": "lema",
            "sujeto": "texto_usable_sin_estado_indefinido_ni_cambio",
            "relacion": "permite_construir",
            "objeto": "registro_con_estado_estable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A20", "CX-A14"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-L8 (Elevacion): Si existe texto usable en casilla y no hay estado declarado "
                "indefinido ni cambio, puede construirse registro con estado=estable y "
                "enunciado_O derivado del texto (entrada natural)."
            ),
        },
        {
            "id": "CX-L9",
            "tipo": "lema",
            "sujeto": "una_casilla_con_varios_items_numerados",
            "relacion": "no_implica_por_defecto",
            "objeto": "varios_O_id",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A22", "CX-D21"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-L9 (No multi-O por defecto): De una sola casilla con varios items numerados "
                "no se sigue la existencia de varios O_id salvo regla o declaracion explicita "
                "de particion."
            ),
        },
        {
            "id": "CX-L10",
            "tipo": "lema",
            "sujeto": "secuencia_de_tramos_con_O_micro",
            "relacion": "admite",
            "objeto": "O_global_adicional_de_mapa",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-D17", "CX-A25"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-L10 (Mapa conversacional): Dada una secuencia de tramos con O micro "
                "clasificados, existe la posibilidad de un O global cuyo enunciado describe "
                "esa secuencia; ese O global es un marco adicional, no el sustituto de los micro."
            ),
        },
        {
            "id": "CX-L11",
            "tipo": "lema",
            "sujeto": "material_multiinterpretable_sin_O_declarado",
            "relacion": "deja",
            "objeto": "K_indefinida_o_fuerza_O_no_dicho",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A10", "CX-A21", "Def-5.3.1"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-L11 (Ambiguedad sin O fijo): Material poetico, metaforico o multiinterpretable "
                "sin O declarado deja K indefinida o fuerza al auditor a instalar un O no dicho; "
                "lo segundo viola la exigencia de marco explicito."
            ),
        },
        {
            "id": "CX-T14",
            "tipo": "teorema",
            "sujeto": "reclamo_de_K_en_cualquier_grano",
            "relacion": "exige",
            "objeto": "registro_estable_en_ese_grano",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A19", "CX-A14", "CX-A1"],
            "gobierna": ["contexto", "evaluacion"],
            "enunciado": (
                "CX-T14 (Invariancia de forma bajo fractalidad): Para todo grano contextual, "
                "las condiciones de estabilidad de registro (O_id + enunciado recuperable) son "
                "necesarias para reclamar K en ese grano."
            ),
        },
        {
            "id": "CX-T15",
            "tipo": "teorema",
            "sujeto": "conversacion_con_cambios_de_marco",
            "relacion": "se_evalua_como",
            "objeto": "familia_de_resultados_por_tramo_no_un_solo_Tru_sin_agregacion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A23", "CX-A25", "CX-L1", "CX-C5"],
            "gobierna": ["contexto", "evaluacion"],
            "enunciado": (
                "CX-T15 (Conversacion multi-O): En una conversacion con cambios de marco, "
                "la evaluacion correcta es la familia de resultados por tramo (y opcionalmente "
                "el O global de mapa), no un unico Tru_total del discurso entero sin regla de "
                "agregacion declarada."
            ),
        },
        {
            "id": "CX-T16",
            "tipo": "teorema",
            "sujeto": "reclamo_de_K_sobre_marco_generado",
            "relacion": "exige_previa",
            "objeto": "fijacion_de_enunciado_O_en_registro",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A24", "Def-5.3.1"],
            "gobierna": ["contexto", "evaluacion", "inferencia_causal"],
            "enunciado": (
                "CX-T16 (Generacion antes de correlacion): Ningun reclamo de K sobre un marco "
                "generado es valido si el enunciado_O generado no fue fijado en registro antes "
                "del computo."
            ),
        },
        {
            "id": "CX-T17",
            "tipo": "teorema",
            "sujeto": "mismo_material_bajo_O_1_a_O_n",
            "relacion": "admite",
            "objeto": "hasta_n_valores_locales_de_K_y_Tru",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A27", "TA4"],
            "gobierna": ["contexto", "epistemologia"],
            "enunciado": (
                "CX-T17 (N marcos, N correlaciones): Si el mismo material se evalua bajo "
                "O_1 ... O_n declarados, existen hasta n valores de K (y Tru) locales; la "
                "divergencia entre ellos no es contradiccion del material sino diferencia de marcos."
            ),
        },
        {
            "id": "CX-C14",
            "tipo": "corolario",
            "sujeto": "interfaz_en_prosa_o_lista",
            "relacion": "no_implica_indefinido_por_ausencia_de",
            "objeto": "O_id_tipado_por_el_usuario",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A20", "CX-L8"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-C14: La interfaz puede limitarse a prosa o lista; la ausencia de O_id "
                "tipado por el usuario no implica indefinido si el texto es usable."
            ),
        },
        {
            "id": "CX-C15",
            "tipo": "corolario",
            "sujeto": "casilla_con_contenido_contexto_indefinido",
            "relacion": "es",
            "objeto": "declaracion_meta_no_autorizacion_de_K_arbitraria",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A21", "CX-A10"],
            "gobierna": ["contexto", "evaluacion"],
            "enunciado": (
                "CX-C15: 'Contexto indefinido' como contenido de la casilla es declaracion meta: "
                "clasifica el tramo objeto como indefinido o abre O meta de auditoria; no autoriza "
                "asignar K en {0,1} al agujero."
            ),
        },
        {
            "id": "CX-C16",
            "tipo": "corolario",
            "sujeto": "mezcla_de_lenguas_en_un_turno",
            "relacion": "no_genera_por_si_sola",
            "objeto": "choque_axiomatico",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A26"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "CX-C16: Mezcla ES/EN/otro en un turno no genera por si sola un choque "
                "axiomatico; genera, si acaso, trabajo de ligadura y de escala bajo el O vigente."
            ),
        },
        {
            "id": "CX-C17",
            "tipo": "corolario",
            "sujeto": "reporte_con_Tru_distintos_bajo_O_distintos",
            "relacion": "es_coherente_con",
            "objeto": "CX-T17_sin_exigir_veredicto_unico",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T17"],
            "gobierna": ["contexto", "epistemologia"],
            "enunciado": (
                "CX-C17: Un reporte que muestre 'bajo O_logica alto; bajo O_metaforico al piso beta' "
                "es coherente con CX-T17 y no exige un unico veredicto."
            ),
        },
        {
            "id": "CX-C18",
            "tipo": "corolario",
            "sujeto": "O_global_de_mapa_conversacional",
            "relacion": "mide",
            "objeto": "el_mapa_no_cada_micro",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-L10", "CX-A25"],
            "gobierna": ["contexto"],
            "enunciado": (
                "CX-C18: El O global de 'que se dedico la conversacion' es admisible como producto "
                "de clasificacion de secuencia; su K mide el mapa, no cada micro."
            ),
        },
    ]


__all__ = ["CUERPO", "declaraciones"]
