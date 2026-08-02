# -*- coding: utf-8 -*-
"""
sentido_estructural — cuerpo axiomático SE/TCC v0.2
===================================================
Satélite AX. Lenguaje / cierre composicional bajo O.

Nombre de identificación (test + CI):
  se_tcc / sentido_estructural
  (test_se_tcc_montecarlo.py, SE-A-REC)

QUÉ ES:
  Primer filtro de auditoría lingüística: cuándo una descripción D
  tiene sentido estructural bajo un contexto O y una escala e*, y cuándo no.
  No calcula Tru_total; no inventa K de R. Define cierre, recombinación
  y el sentido del no-sentido (nivel objeto vs nivel meta).

ANCLAJE AL MARCO VPSI (no duplica, depende_de):
  A4, T15, TR1  → recombinación / generatividad
  TA3, Def-5.3.1 → K y O_context
  TA4, T14      → R ⊥ observador; verdad de R, error de S
  TT.11.1       → coherencia sin Real (ficción)
  T6            → separación verdad / verificación / confusión

VIGILANCIA:
  Lo ejerce el INIT de axiomas (barrer): contradicción directa y de cota.
  Este cuerpo solo declara.
"""

CUERPO = {
    "nombre": "sentido_estructural",
    "version": "0.2",
}


def declaraciones():
    return [
        # ==============================================================
        # DEFINICIONES OPERATIVAS (como axiomas de marco del dominio SE)
        # ==============================================================
        {
            "id": "SE-D1",
            "tipo": "axioma",
            "sujeto": "O_linguistico",
            "relacion": "es",
            "objeto": "contexto_explicito_de_lengua_registro_genero_escala",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.3.1", "TA3"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "SE-D1: O lingüístico es el contexto explícito que fija lengua, "
                "registro, género y escala e* bajo los cuales se evalúa D. "
                "Sin O explícito, el sentido pleno no se declara (ancla Def-5.3.1)."
            ),
        },
        {
            "id": "SE-D2",
            "tipo": "axioma",
            "sujeto": "M(D)",
            "relacion": "es",
            "objeto": "material_linguistico_de_D",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A4"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SE-D2: M(D) es el material lingüístico de D (tokens, letras, "
                "morfemas, cadenas). El material solo no constituye sentido."
            ),
        },
        {
            "id": "SE-D3",
            "tipo": "axioma",
            "sujeto": "Comb(D, O)",
            "relacion": "es",
            "objeto": "modo_de_combinacion_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A4", "T15"],
            "gobierna": ["semantica", "meta"],
            "enunciado": (
                "SE-D3: Comb(D, O) es el modo de combinación de M bajo O "
                "(orden, roles, cohesión a la escala e*). "
                "La recombinación es operación (A4/T15); no es criterio de sentido."
            ),
        },
        {
            "id": "SE-D4",
            "tipo": "axioma",
            "sujeto": "Cierre(D, O, e_star)",
            "relacion": "vale_si",
            "objeto": "lectura_estable_determinada_por_M_y_Comb_bajo_O_a_e_star",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D1", "SE-D2", "SE-D3"],
            "gobierna": ["semantica", "contexto"],
            "enunciado": (
                "SE-D4: Cierre(D, O, e*) vale si y solo si existe lectura estable "
                "determinada por M y Comb bajo O a la escala e*. "
                "Independiente de K/Real de R."
            ),
        },
        {
            "id": "SE-D5",
            "tipo": "axioma",
            "sujeto": "Sentido_O(D)",
            "relacion": "igual_a_1_si",
            "objeto": "O_explicito_y_Cierre_a_e_star",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D1", "SE-D4"],
            "gobierna": ["semantica", "contexto", "logica"],
            "enunciado": (
                "SE-D5: Sentido_O(D) = 1 ⇔ O lingüístico explícito y Cierre(D, O, e*). "
                "Sentido_O no exige K de R ni Real(D) = 1."
            ),
        },

        # ==============================================================
        # AXIOMAS NÚCLEO
        # ==============================================================
        {
            "id": "SE-A0",
            "tipo": "axioma",
            "sujeto": "sentido",
            "relacion": "es_asignado_por",
            "objeto": "Ri_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "T14"],
            "gobierna": ["semantica", "ontologia", "epistemologia"],
            "enunciado": (
                "SE-A0 (Núcleo): El sentido de una representación lingüística "
                "lo asigna Ri bajo O; R no anuncia sentido. "
                "Afirmar hechos de R exige demostración (carga en S, T14)."
            ),
        },
        {
            "id": "SE-A1",
            "tipo": "axioma",
            "sujeto": "Sentido_O_pleno",
            "relacion": "exige",
            "objeto": "O_explicito",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D1", "Def-5.3.1"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "SE-A1: Sin O explícito no hay sentido pleno. "
                "El evaluador no inventa O para salvar D."
            ),
        },
        {
            "id": "SE-A2",
            "tipo": "axioma",
            "sujeto": "M(D)",
            "relacion": "no_basta_para",
            "objeto": "Sentido_O(D)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D2", "SE-D5"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SE-A2: El material solo (tokens, letras, anclas léxicas) "
                "no basta para Sentido_O. Hace falta Comb y Cierre a e*."
            ),
        },
        {
            "id": "SE-A3",
            "tipo": "axioma",
            "sujeto": "Cierre",
            "relacion": "no_se_exporta_entre",
            "objeto": "escalas_e_star_distintas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D4"],
            "gobierna": ["semantica", "contexto"],
            "enunciado": (
                "SE-A3: El cierre a una escala e* (p. ej. letra, morfema, cláusula) "
                "no se exporta automáticamente a otra (p. ej. discurso). "
                "La letra M puede cerrar bajo O de letra; no por ello da sentido discursivo."
            ),
        },
        {
            "id": "SE-A4",
            "tipo": "axioma",
            "sujeto": "meta_en_D",
            "relacion": "no_establece",
            "objeto": "Cierre",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T6", "SE-D4"],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "SE-A4: Cadenas meta del tipo 'Tru_total=1', 'sentido pleno', "
                "'Sentido_O=1' insertadas en D no establecen Cierre. "
                "La verdad del diagnóstico no se auto-otorga en el objeto (T6)."
            ),
        },
        {
            "id": "SE-A5",
            "tipo": "axioma",
            "sujeto": "fallo_de_norma_O",
            "relacion": "no_es",
            "objeto": "fallo_de_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "T12"],
            "gobierna": ["ontologia", "semantica"],
            "enunciado": (
                "SE-A5: El fallo de norma o convención bajo O no se reporta como "
                "fallo de R. Norma(O) es representación; R es invariante (TA4, T12)."
            ),
        },
        {
            "id": "SE-A6",
            "tipo": "axioma",
            "sujeto": "ficcion_bajo_O",
            "relacion": "puede_tener_Sentido_O_sin",
            "objeto": "Real_ni_K_de_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.11.1", "SE-D5"],
            "gobierna": ["semantica", "ontologia"],
            "enunciado": (
                "SE-A6: Bajo O de ficción/relato, D puede tener Sentido_O = 1 "
                "sin Real(D) = 1 ni K de R (TT.11.1). Sentido ≠ verdad de R."
            ),
        },

        # ==============================================================
        # SE-A-REC — clave (test + generatividad lingüística)
        # ==============================================================
        {
            "id": "SE-A-REC",
            "tipo": "axioma",
            "sujeto": "recombinacion_bajo_O",
            "relacion": "no_implica",
            "objeto": "Sentido_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A4", "T15", "TR1", "SE-D3", "SE-D5"],
            "gobierna": ["semantica", "meta", "informacion"],
            "enunciado": (
                "SE-A-REC (Recombinación bajo O): Sea D' obtenida por recombinación "
                "(edición, permutación, inserción, mezcla) a partir de material bajo O y e*. "
                "(1) D' puede tener Sentido_O=1 solo si hay Cierre a e*. "
                "(2) D' puede tener Sentido_O=0 aunque conserve tokens del original. "
                "(3) Recombinar no es criterio de sentido: anclas léxicas o procedencia "
                "de plantilla positiva no implican cierre. "
                "(4) Si la recombinación destruye orden/roles a e*, no hay sentido pleno. "
                "(5) Si D' conserva cierre canónico a e* bajo O, hay sentido pleno. "
                "(6) 'No tiene sentido' bajo O/e* ES Sentido_O=0; no hay un segundo "
                "sentido metafísico del sinsentido. "
                "Ancla: A4, T15, TR1 (generatividad: no toda combinación es verdad nueva)."
            ),
        },

        # ==============================================================
        # TEOREMAS
        # ==============================================================
        {
            "id": "SE-T1",
            "tipo": "teorema",
            "sujeto": "Sentido_O(D)",
            "relacion": "vale_ssi",
            "objeto": "O_y_Cierre_a_e_star",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D5", "SE-A1", "SE-A2"],
            "gobierna": ["semantica", "contexto"],
            "enunciado": (
                "SE-T1: Sentido_O(D) vale si y solo si hay O lingüístico explícito "
                "y Cierre(D, O, e*). No se exige K de R."
            ),
        },
        {
            "id": "SE-T2",
            "tipo": "teorema",
            "sujeto": "material_o_anclas",
            "relacion": "no_implican",
            "objeto": "Cierre",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A2", "SE-A-REC"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SE-T2: La presencia de material reconocible o anclas léxicas "
                "no implica Cierre. Match parcial en basura no es sentido (SE-A-REC)."
            ),
        },
        {
            "id": "SE-T3",
            "tipo": "teorema",
            "sujeto": "Sentido_O_en_ficcion",
            "relacion": "no_implica",
            "objeto": "K_ni_Real_de_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A6", "TT.11.1", "TA4"],
            "gobierna": ["semantica", "ontologia"],
            "enunciado": (
                "SE-T3: Sentido_O bajo O de ficción no implica K de R ni Real(D)=1."
            ),
        },
        {
            "id": "SE-T4",
            "tipo": "teorema",
            "sujeto": "Cierre_local",
            "relacion": "no_exporta",
            "objeto": "sentido_a_escala_superior",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A3"],
            "gobierna": ["semantica", "contexto"],
            "enunciado": (
                "SE-T4: Un cierre local (letra, morfema, cláusula) no exporta "
                "sentido a escala discursiva u otra e* no declarada."
            ),
        },
        {
            "id": "SE-T5",
            "tipo": "teorema",
            "sujeto": "forma_SE",
            "relacion": "es_independiente_de",
            "objeto": "idioma_particular",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T1", "SE-A-REC"],
            "gobierna": ["semantica", "meta"],
            "enunciado": (
                "SE-T5 (Forma universal): Los predicados SE (O, M, Comb, Cierre, "
                "Sentido_O) son independientes del idioma particular; "
                "solo cambian las instancias de M/Comb/norma."
            ),
        },
        {
            "id": "SE-T6",
            "tipo": "teorema",
            "sujeto": "inyeccion_meta",
            "relacion": "no_fija",
            "objeto": "Cierre_ni_Sentido_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A4", "T6"],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "SE-T6: La inyección meta en D no fija Cierre ni Sentido_O. "
                "Separación estructural objeto / veredicto (T6)."
            ),
        },
        {
            "id": "SE-T7",
            "tipo": "teorema",
            "sujeto": "recombinacion",
            "relacion": "genera",
            "objeto": "candidatos_no_todas_verdades_ni_sentidos",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A-REC", "TR1", "T15"],
            "gobierna": ["meta", "semantica", "informacion"],
            "enunciado": (
                "SE-T7: La recombinación genera candidatos (generatividad TR1/T15); "
                "no todas las combinaciones son sentido bajo O ni verdad de R. "
                "Misma forma que |Im(⊕)| > |Θ| aplicada al dominio lingüístico."
            ),
        },

        # ==============================================================
        # LEMAS
        # ==============================================================
        {
            "id": "SE-L1",
            "tipo": "lema",
            "sujeto": "permutacion_agresiva_a_e_star",
            "relacion": "rompe",
            "objeto": "Comb_y_Cierre",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-D3", "SE-A-REC"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SE-L1: Una permutación que destruye roles/orden a e* rompe Comb "
                "y por tanto Cierre, aunque M conserve tokens."
            ),
        },
        {
            "id": "SE-L2",
            "tipo": "lema",
            "sujeto": "O_omitido",
            "relacion": "impide",
            "objeto": "Sentido_O_pleno",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A1"],
            "gobierna": ["contexto"],
            "enunciado": (
                "SE-L2: O omitido impide Sentido_O pleno (no se inventa O)."
            ),
        },
        {
            "id": "SE-L3",
            "tipo": "lema",
            "sujeto": "match_parcial_en_basura",
            "relacion": "no_es",
            "objeto": "Cierre_a_e_star",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T2", "SE-T4"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SE-L3: Un match parcial de plantilla dentro de basura discursiva "
                "no constituye Cierre a e* del discurso."
            ),
        },

        # ==============================================================
        # COROLARIOS — incl. sentido del no-sentido (fractal)
        # ==============================================================
        {
            "id": "SE-C1",
            "tipo": "corolario",
            "sujeto": "Sentido_O_0",
            "relacion": "es",
            "objeto": "veredicto_estructural_no_segunda_ontologia",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T1", "SE-A-REC"],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "SE-C1: Sentido_O(D)=0 bajo O/e* es veredicto estructural de "
                "ausencia de cierre; no introduce una segunda ontología del sinsentido."
            ),
        },
        {
            "id": "SE-C2",
            "tipo": "corolario",
            "sujeto": "D_asterisco_juicio_sobre_D",
            "relacion": "puede_tener_Sentido_O_sin_conferir_sentido_a",
            "objeto": "D",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T1", "T6", "SE-C1"],
            "gobierna": ["semantica", "epistemologia", "meta"],
            "enunciado": (
                "SE-C2 (Sentido del no-sentido): La afirmación de que D carece de "
                "sentido bajo O es ella misma una descripción D* que puede tener "
                "Sentido_O bajo un contexto de evaluación O*. "
                "El sentido de D* no confiere sentido a D; solo hace comunicable "
                "y verificable la ausencia de cierre en D. "
                "Mismo predicado; cambian el nivel y el O. Fractalidad del filtro."
            ),
        },
        {
            "id": "SE-C3",
            "tipo": "corolario",
            "sujeto": "experiencia_privada_de_sentido",
            "relacion": "no_impone",
            "objeto": "K_publico_ni_Real",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta-Private-1", "SE-A0", "T14"],
            "gobierna": ["epistemologia", "semantica"],
            "enunciado": (
                "SE-C3: La experiencia privada de sentido (β-Private) no se niega "
                "y no impone por sí sola K público ni Real de R."
            ),
        },
        {
            "id": "SE-C4",
            "tipo": "corolario",
            "sujeto": "auditoria_linguistica_SE",
            "relacion": "es_filtro_previo_a",
            "objeto": "cita_de_axiomas_en_palabras",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T1", "SE-A1", "SE-A-REC", "Def-5.3.1"],
            "gobierna": ["contexto", "semantica", "meta"],
            "enunciado": (
                "SE-C4: El cuerpo sentido_estructural actúa como primer filtro de "
                "auditoría lingüística: antes de citar o aplicar axiomas en palabras, "
                "D debe poder evaluarse bajo O y e* (cierre o no-cierre explícitos). "
                "Sin O, no hay aplicación plena de K ni de veredicto de sentido."
            ),
        },
        {
            "id": "SE-C5",
            "tipo": "corolario",
            "sujeto": "generatividad_linguistica",
            "relacion": "instancia",
            "objeto": "TR1_en_dominio_SE",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T7", "TR1", "T15"],
            "gobierna": ["meta", "informacion"],
            "enunciado": (
                "SE-C5: La generatividad lingüística bajo SE es instancia de TR1 "
                "en el dominio del sentido: se generan más combinaciones que cierres; "
                "el filtro es Cierre bajo O, no el volumen de recombinación."
            ),
        },
    ]


__all__ = ["CUERPO", "declaraciones"]
