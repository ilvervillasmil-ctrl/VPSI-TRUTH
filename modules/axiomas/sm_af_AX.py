"""
VPSI-TRUTH / sm_af_AX.py

Cuerpo axiomático SM v2 · AF v1
Serie Significado (SM) + Serie Afirmación (AF)

Ubicación canónica:
  modules/axiomas/sm_af/__init__.py
  (o copiar este archivo como cuerpo cargable por VPSI_AX.cuerpos())

Anclas al grafo VPSI:
  TA3, TA4, TA5, TA8, E1, E3, F3, F8, F9,
  Def-5.3.1, T6, T9, T11, T14, T15, Corolario 1.36 / TT.7.x

Regla de integridad:
  Ninguna declaración aquí contradice polaridad de TA3, Def-5.3.1,
  F3, T9 ni beta. Si barrer() reporta choque, el cuerpo se rechaza.
"""

from typing import Dict, List

CUERPO = {
    "nombre": "SM_AF",
    "version": "2.0",
}


def declaraciones() -> List[Dict]:
    return [

        # ==========================================================
        # SM — DEFINICIONES (como axiomas de marco: fijan vocabulario)
        # ==========================================================
        {
            "id": "SM-D1",
            "tipo": "axioma",
            "sujeto": "Significado(w)",
            "relacion": "igual_a",
            "objeto": "posicion_en_particion_Pi_de_contrastes",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F3", "TA3"],
            "gobierna": ["semantica", "contexto", "correlacion"],
            "enunciado": (
                "SM-D1: Significado(w) := posición de w en una partición Π de contrastes "
                "de un dominio observable. Significado(w) ∉ {etiqueta(w), sonido(w)}. "
                "No es un hecho aislado: es F por oposición a los vecinos que Π delimita. "
                "NOTA OPERATIVA: el evaluador no puede usar igualdad de strings de etiqueta "
                "como proxy de significado; debe referir la posición en Π bajo O. "
                "Alcance: no cubre nombres propios (ver AF-D2)."
            ),
        },
        {
            "id": "SM-D2",
            "tipo": "axioma",
            "sujeto": "Sentido(D|O)",
            "relacion": "igual_a",
            "objeto": "K(D|O)_si_O_usable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "TA3", "Def-5.3.1"],
            "gobierna": ["semantica", "correlacion", "contexto"],
            "enunciado": (
                "SM-D2: Sentido(D|O) := correlación de la posición de D con el dominio "
                "que O delimita. Si O es usable: Sentido(D|O) ≡ K(D|O). "
                "Si O no es usable: Sentido(D|O) = UNDEFINED (no 0, no 1). "
                "NOTA OPERATIVA: calcular_k sin O_context debe emitir UNDEFINED o rechazar; "
                "nunca un float/Fraction reclamable. Implementa Def-5.3.1."
            ),
        },
        {
            "id": "SM-D3",
            "tipo": "axioma",
            "sujeto": "AnclaReferencial(w)",
            "relacion": "existe_si",
            "objeto": "contraste_en_dominio_observable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "F3"],
            "gobierna": ["semantica", "realidad"],
            "enunciado": (
                "SM-D3: AnclaReferencial(w) ⇔ ∃ contraste en dominio observable al que "
                "la partición de w apunta. "
                "NOTA OPERATIVA: material RE (disciplinas) es candidato a ancla bajo su O "
                "de evaluación; nunca identificación con R (TA4)."
            ),
        },
        {
            "id": "SM-D4",
            "tipo": "axioma",
            "sujeto": "AnclaConvencional(w)",
            "relacion": "existe_si",
            "objeto": "emparejamiento_etiqueta_posicion_estabilizado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-D4: AnclaConvencional(w) ⇔ el emparejamiento etiqueta(w) ↔ posición "
                "en Π está estabilizado en una comunidad. "
                "NOTA OPERATIVA: diccionarios/RAE son registro de AnclaConvencional (∈ X), "
                "no AnclaReferencial ni R."
            ),
        },
        {
            "id": "SM-D5",
            "tipo": "axioma",
            "sujeto": "Inv(w)",
            "relacion": "igual_a",
            "objeto": "clase_de_equivalencia_por_posicion_en_Pi",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-D5: Inv(w) := [w] = { w' | w' ocupa la misma posición en la misma Π }. "
                "Inv es un cociente (clase de equivalencia), no un producto etiqueta×sentido. "
                "NOTA OPERATIVA: dos etiquetas distintas con misma (dominio, posición) "
                "deben compartir Inv; renombrar etiqueta sin mover posición no cambia Inv."
            ),
        },
        {
            "id": "SM-D6",
            "tipo": "axioma",
            "sujeto": "Vacio(w|O)",
            "relacion": "si_y_solo_si",
            "objeto": "no_AnclaReferencial_reconocible_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D3", "Def-5.3.1"],
            "gobierna": ["semantica", "correlacion", "contexto"],
            "enunciado": (
                "SM-D6: Vacío(w|O) ⇔ ¬AnclaReferencial(w) reconocible bajo O. "
                "La vacuidad es siempre relativa a O. No se afirma vacuidad absoluta. "
                "NOTA OPERATIVA: misma cadena puede ser vacía bajo O1 y anclada bajo O2. "
                "El evaluador debe parametrizar vacío por O, no por la cadena sola."
            ),
        },
        {
            "id": "SM-D7",
            "tipo": "axioma",
            "sujeto": "RegistroLexicografico",
            "relacion": "pertenece_a",
            "objeto": "X",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F3", "SM-D4", "TA4"],
            "gobierna": ["semantica", "realidad"],
            "enunciado": (
                "SM-D7: RegistroLexicográfico ∈ X. Archiva AnclaConvencional. "
                "No crea AnclaReferencial. Registro ≠ R. "
                "NOTA OPERATIVA: usar RAE/diccionario como O de evaluación es admisible "
                "como candidato de dominio; identificarlo con R viola TA4 y este axioma."
            ),
        },
        {
            "id": "SM-D8",
            "tipo": "axioma",
            "sujeto": "significado_nuevo_en_Ri",
            "relacion": "es_recombinacion_de",
            "objeto": "contrastes_previamente_accesibles_a_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A3", "A4", "T15"],
            "gobierna": ["semantica", "meta"],
            "enunciado": (
                "SM-D8: ∀ significado nuevo en Ri: es recombinación de contrastes "
                "previamente accesibles a Ri (No Ex Nihilo semántico). "
                "NOTA OPERATIVA: TR1/generatividad opera sobre Inv ya ancladas; "
                "no autoriza inventar contraste desde cadena vacía."
            ),
        },

        # ==========================================================
        # SM — AXIOMAS
        # ==========================================================
        {
            "id": "SM-A1",
            "tipo": "axioma",
            "sujeto": "significado_estable(w)",
            "relacion": "implica",
            "objeto": "AnclaReferencial_o_mediada_por_registro_admisible",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "SM-D3", "SM-D4"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-A1: significado estable(w) ⇒ AnclaReferencial(w) ∨ "
                "(AnclaReferencial mediada por registro admisible bajo O). "
                "Formal: significado estable ⇒ ∃ Π en dominio observable. "
                "NOTA OPERATIVA: si no hay Π reconocible bajo O, no reclamar "
                "significado estable ni K>0 sobre w."
            ),
        },
        {
            "id": "SM-A2",
            "tipo": "axioma",
            "sujeto": "Sentido(D|O)",
            "relacion": "igual_a",
            "objeto": "Correlacion(D, dominio(O))",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D2", "TA3"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-A2: Sentido(D|O) = Correlación(D, dominio(O)). "
                "¬Usable(O) ⇒ Sentido(D|O) no reclamable (UNDEFINED). "
                "NOTA OPERATIVA: alias operativo de SM-D2 + TA3; "
                "cualquier camino que emita K numérico sin O usable es violación."
            ),
        },
        {
            "id": "SM-A3",
            "tipo": "axioma",
            "sujeto": "Ri",
            "relacion": "no_genera_significado_estable_desde",
            "objeto": "ausencia_total_de_contraste",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A3", "SM-D8"],
            "gobierna": ["semantica", "ontologia"],
            "enunciado": (
                "SM-A3: ¬∃ Ri que genere significado estable desde ausencia total de contraste. "
                "NOTA OPERATIVA: experimento del niño en espacio negro — sin partición "
                "de contrastes no hay términos anclados. Bloquea K=1 sobre ruido puro."
            ),
        },
        {
            "id": "SM-A4",
            "tipo": "axioma",
            "sujeto": "cambio_de_rotulo",
            "relacion": "no_implica",
            "objeto": "cambio_de_contraste_referencial",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D5"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-A4: Cambio de rótulo ⇏ cambio de contraste referencial. "
                "Alcance: invariantes referenciales. No rige hechos institucionales/declarativos. "
                "NOTA OPERATIVA: base de SM-T9. Si calcular_k cambia al renombrar β→γ "
                "preservando 1/27, viola este axioma (mide etiqueta, no Inv)."
            ),
        },
        {
            "id": "SM-A5",
            "tipo": "axioma",
            "sujeto": "RegistroLexicografico",
            "relacion": "no_es_igual_a",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D7", "TA4"],
            "gobierna": ["semantica", "realidad"],
            "enunciado": (
                "SM-A5: RegistroLexicográfico ≠ R. Registro ∈ X, corregible con evidencia. "
                "NOTA OPERATIVA: prohibición directa de identificar diccionario/RAE con R."
            ),
        },
        {
            "id": "SM-A6",
            "tipo": "axioma",
            "sujeto": "Vacio(w|O)",
            "relacion": "prohibe",
            "objeto": "K_reclamable_sobre_w_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D6", "Def-5.3.1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-A6: Vacío(w|O) ⇒ prohibido asignar K reclamable a w bajo O. "
                "Estado legítimo = UNDEFINED. "
                "También prohibido fabricar K=0 sobre no-proposición (simetría AF-T7). "
                "NOTA OPERATIVA: K=1 o K=0 numérico sobre vacío son ambos ilegales."
            ),
        },
        {
            "id": "SM-A7",
            "tipo": "axioma",
            "sujeto": "sistema_sin_contraste",
            "relacion": "no_tiene",
            "objeto": "semantica_compartible",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A3"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-A7: Sin sistema capaz de contraste ⇒ ¬semántica compartible. "
                "NOTA OPERATIVA: sin partición no hay términos intersubjetivos evaluables."
            ),
        },
        {
            "id": "SM-A8",
            "tipo": "axioma",
            "sujeto": "Rep1_y_Rep2",
            "relacion": "preservan_Inv_si",
            "objeto": "misma_posicion_en_misma_Pi",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D5", "SM-A4"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-A8: Si Rep₁ y Rep₂ preservan la misma posición en la misma Π, "
                "entonces Inv(Rep₁) = Inv(Rep₂). "
                "NOTA OPERATIVA: criterio de igualdad estructural para tests de renombrado."
            ),
        },
        {
            "id": "SM-A9",
            "tipo": "axioma",
            "sujeto": "representacion_referencial",
            "relacion": "referencia_pero_no_constituye",
            "objeto": "significado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "F3"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-A9: Representación referencial no constituye el significado; lo referencia. "
                "Alcance: no aplica a representación declarativa/performativa. "
                "NOTA OPERATIVA: el string 'casa' no es el contraste habitable; lo nombra."
            ),
        },
        {
            "id": "SM-A10",
            "tipo": "axioma",
            "sujeto": "equivalencia_semantica_bajo_O",
            "relacion": "si_y_solo_si",
            "objeto": "correspondencia_de_invariantes_en_alcance_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A8", "F3"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-A10: Equivalencia semántica de dominios bajo O declarado ⇔ "
                "correspondencia entre invariantes dentro del alcance de O. "
                "No se exige biyección global entre lenguas. "
                "NOTA OPERATIVA: traducción exacta solo en la intersección de proyecciones (SM-T7)."
            ),
        },

        # ==========================================================
        # SM — LEMAS
        # ==========================================================
        {
            "id": "SM-L1",
            "tipo": "lema",
            "sujeto": "etiqueta(w)",
            "relacion": "no_es_igual_a",
            "objeto": "Significado(w)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "SM-D5"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-L1: etiqueta(w) ≠ Significado(w). "
                "NOTA OPERATIVA: igualdad de strings no implica igualdad de Inv."
            ),
        },
        {
            "id": "SM-L2",
            "tipo": "lema",
            "sujeto": "Interpretacion_posible(Ri, cadena)",
            "relacion": "no_implica",
            "objeto": "Ancla(cadena)_ni_K_reclamable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A1", "SM-A6"],
            "gobierna": ["semantica", "epistemologia"],
            "enunciado": (
                "SM-L2: Interpretación_posible(Ri, cadena) ⇏ Ancla(cadena). "
                "Interpretar ⇏ K reclamable. "
                "NOTA OPERATIVA: el sistema puede parsear basura sin asignarle K>0."
            ),
        },
        {
            "id": "SM-L3",
            "tipo": "lema",
            "sujeto": "recombinacion",
            "relacion": "preserva",
            "objeto": "dependencia_causal_R_X_Y",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D8", "F4", "A4"],
            "gobierna": ["semantica", "meta"],
            "enunciado": (
                "SM-L3: Recombinación preserva dependencia causal respecto de R "
                "(cadena R → X → Y). "
                "NOTA OPERATIVA: TR1 no escapa F4; generatividad no es acceso directo a R."
            ),
        },
        {
            "id": "SM-L4",
            "tipo": "lema",
            "sujeto": "O",
            "relacion": "delimita",
            "objeto": "alcance_del_sentido",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D2", "SM-A2"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "SM-L4: O delimita alcance del sentido. "
                "Reclamar sentido único ignorando ΔO introduce contradicción de marco. "
                "NOTA OPERATIVA: cambiar O a mitad de evaluación sin registrar el cambio "
                "degrada L (moving the goalposts / T11)."
            ),
        },
        {
            "id": "SM-L5",
            "tipo": "lema",
            "sujeto": "BETA",
            "relacion": "no_asigna",
            "objeto": "significado_ni_convierte_UNDEFINED_en_correlacionado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta", "T9", "SM-A6"],
            "gobierna": ["constantes", "semantica"],
            "enunciado": (
                "SM-L5: β no asigna significado. β no convierte UNDEFINED en correlacionado. "
                "NOTA OPERATIVA: Tru_total=β cuando I(R;X)=0 (T9) no implica que la "
                "cadena 'tenga sentido'; solo que el piso estructural persiste."
            ),
        },
        {
            "id": "SM-L6",
            "tipo": "lema",
            "sujeto": "cambio_de_idioma",
            "relacion": "igual_a",
            "objeto": "cambio_de_representacion_en_alcance_compartido",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A8", "SM-A10"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-L6: Cambio de idioma = cambio de representación, restringido al "
                "alcance donde ambas lenguas proyectan la misma partición. "
                "NOTA OPERATIVA: fuera de la intersección hay pérdida (F3), no equivalencia total."
            ),
        },
        {
            "id": "SM-L7",
            "tipo": "lema",
            "sujeto": "ausencia_de_Pi",
            "relacion": "implica",
            "objeto": "ausencia_de_termino",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "SM-A7"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-L7: ¬Π ⇒ ¬término. Ausencia de vecinos vacía el término; no lo generaliza. "
                "NOTA OPERATIVA: sin contrastes vecinos no hay posición que asignar."
            ),
        },

        # ==========================================================
        # SM — TEOREMAS
        # ==========================================================
        {
            "id": "SM-T1",
            "tipo": "teorema",
            "sujeto": "Sentido(D|O)",
            "relacion": "igual_a",
            "objeto": "K(D|O)_cuando_O_usable_y_estable",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D2", "SM-A2", "TA3", "Def-5.3.1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-T1: Usable(O) ∧ Estable(O) ⇒ Sentido(D|O) = K(D|O). "
                "NOTA OPERATIVA: puente directo entre capa semántica y calcular_k. "
                "Si O estable y usable, el valor de sentido ES el de K."
            ),
        },
        {
            "id": "SM-T2",
            "tipo": "teorema",
            "sujeto": "Vacio(w|O)",
            "relacion": "prohibe",
            "objeto": "K(D|O)_mayor_que_0_legitimo",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A6", "SM-D6", "Def-5.3.1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-T2: Vacío(w|O) ⇒ ¬(K(D|O) > 0) legítimo para D que trate w como "
                "portador factual bajo O. "
                "NOTA OPERATIVA: test R2 del Monte Carlo — basura léxica bajo O ajeno "
                "no puede recibir K>0. Estado correcto: UNDEFINED."
            ),
        },
        {
            "id": "SM-T3",
            "tipo": "teorema",
            "sujeto": "renombre_de_etiquetas",
            "relacion": "no_desplaza",
            "objeto": "Inv_referencial",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A4", "SM-A8", "SM-D5"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-T3: Renombre de etiquetas ⇏ desplazamiento de Inv referencial. "
                "NOTA OPERATIVA: lema puente hacia SM-T9."
            ),
        },
        {
            "id": "SM-T4",
            "tipo": "teorema",
            "sujeto": "Ri_sin_particion_de_dominio_Delta",
            "relacion": "no_estabiliza",
            "objeto": "terminos_anclados_a_Delta",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A3", "SM-A7", "SM-L7"],
            "gobierna": ["semantica", "ontologia"],
            "enunciado": (
                "SM-T4: Si Ri carece de la partición Π de un dominio Δ, entonces Ri no "
                "estabiliza términos anclados a Δ (aunque perciba Δ). "
                "Antecedente: carencia de partición del dominio, no carencia de todo contraste. "
                "NOTA OPERATIVA: ver sin Π de 'color' no estabiliza 'azul' como término anclado."
            ),
        },
        {
            "id": "SM-T5",
            "tipo": "teorema",
            "sujeto": "Diccionario",
            "relacion": "pertenece_a",
            "objeto": "X_nunca_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A5", "SM-D7"],
            "gobierna": ["semantica", "realidad"],
            "enunciado": (
                "SM-T5: Diccionario ∈ X. Admisible como candidato de dominio bajo O que lo "
                "declare; nunca identificación con R. "
                "NOTA OPERATIVA: RE puede traer material lexicográfico como candidato a K "
                "bajo O lexicográfico; Engine no debe promoverlo a ancla de R."
            ),
        },
        {
            "id": "SM-T6",
            "tipo": "teorema",
            "sujeto": "Inv_incompatibles_bajo_mismo_O",
            "relacion": "degradan",
            "objeto": "C_no_incrementan_f_por_si_solos",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A2", "TA1", "T6"],
            "gobierna": ["semantica", "logica", "correlacion"],
            "enunciado": (
                "SM-T6: Sean D₁, D₂ bajo el mismo O estable con Inv incompatibles respecto "
                "de O. Entonces: conflicto registrable ⇒ degrada C (no incrementa f por sí solo). "
                "K(D₁|O) y K(D₂|O) permanecen UNDEFINED hasta emisión discriminante. "
                "NOTA OPERATIVA: casa∧parque bajo O de ubicación exclusiva — C baja; "
                "no fabricar K=0 en una de las dos para 'resolver'. Test R4 del Monte Carlo."
            ),
        },
        {
            "id": "SM-T7",
            "tipo": "teorema",
            "sujeto": "lenguas",
            "relacion": "son",
            "objeto": "proyecciones_parciales_sobre_tramos_de_contraste",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F3", "SM-A8", "SM-A10"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-T7: Lenguas = proyecciones parciales sobre tramos de contraste de "
                "dominios respecto de R. No son cartas invertibles. "
                "Dos lenguas pueden inducir particiones no isomorfas del mismo tramo. "
                "NOTA OPERATIVA: F3 (pérdida R→X) implica que no hay traducción total sin residuo."
            ),
        },
        {
            "id": "SM-T8",
            "tipo": "teorema",
            "sujeto": "transformacion_tau_que_preserva_posicion_en_Pi",
            "relacion": "conserva",
            "objeto": "Inv",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A8", "SM-D5"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-T8: Si existe transformación τ que preserva posición en Π, "
                "entonces Inv(τ(w)) = Inv(w). Conservación condicional a la existencia de τ. "
                "NOTA OPERATIVA: τ debe ser exhibible; no se asume."
            ),
        },
        {
            "id": "SM-T9",
            "tipo": "teorema",
            "sujeto": "K_bajo_O",
            "relacion": "es_invariante_bajo",
            "objeto": "renombrado_biyectivo_que_preserva_contrastes",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A8", "SM-A9", "SM-T1", "SM-T3"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-T9: Sea ρ renombrado biyectivo de etiquetas que preserva todos los "
                "contrastes relevantes bajo O. Entonces K(·|O) es invariante bajo ρ. "
                "Si K cambia bajo ρ, el evaluador mide etiquetas en exceso respecto de "
                "invariantes. "
                "NOTA OPERATIVA: TEST CANÓNICO. β→γ con mismo 1/27 debe conservar K. "
                "Si correlacion_k hardcodea literales 'β'/'α', este teorema FALLA en CI. "
                "Familia R1 del Monte Carlo adversarial."
            ),
        },
        {
            "id": "SM-T10",
            "tipo": "teorema",
            "sujeto": "mapeo_R_a_X_lexicografico",
            "relacion": "tiene",
            "objeto": "perdida_y_techo_empirico_K_lex",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F3", "SM-T5"],
            "gobierna": ["semantica", "informacion"],
            "enunciado": (
                "SM-T10: Por F3, el mapeo R → X lexicográfico tiene pérdida. "
                "∃ techo empírico K_lex < pretensión de saturación α alcanzable solo "
                "por anclaje de registro. "
                "NOTA OPERATIVA: no reclamar K=α solo por match lexicográfico."
            ),
        },
        {
            "id": "SM-T11",
            "tipo": "teorema",
            "sujeto": "representar_F",
            "relacion": "implica_y_es_implicado_por",
            "objeto": "asignar_significado_con_correlacion_a_dominio",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A1", "SM-A2", "SM-D1"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-T11: ¬(representar F sin asignar significado) ∧ "
                "¬(significado estable sin correlación con algún dominio). "
                "NOTA OPERATIVA: no hay representación referencial huérfana de sentido "
                "ni sentido estable huérfano de dominio."
            ),
        },

        # ==========================================================
        # SM — COROLARIOS
        # ==========================================================
        {
            "id": "SM-C1",
            "tipo": "corolario",
            "sujeto": "ciclo_con_K_igual_1_sobre_Vacio",
            "relacion": "viola",
            "objeto": "SM-A6_y_Def-5.3.1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A6", "SM-T2", "Def-5.3.1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-C1: Ciclo con K=1 sobre material Vacío(·|O) vigente ⇒ "
                "violación de SM-A6 y Def-5.3.1. "
                "NOTA OPERATIVA: centinela de salida debe rechazar ese paquete."
            ),
        },
        {
            "id": "SM-C2",
            "tipo": "corolario",
            "sujeto": "casa_y_parque_bajo_O_ubicacion_exclusiva",
            "relacion": "generan",
            "objeto": "conflicto_en_C_con_K_indefinida",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T6"],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "SM-C2: O = ubicación de agente en intervalo. "
                "Inv(casa) e Inv(parque) incompatibles para co-afirmación exclusiva "
                "en el mismo intervalo. Registro: conflicto en C; K indefinida en ambas "
                "hasta discriminante. "
                "NOTA OPERATIVA: instancia concreta de SM-T6 para tests."
            ),
        },
        {
            "id": "SM-C3",
            "tipo": "corolario",
            "sujeto": "redefinicion_lexica_bajo_O",
            "relacion": "rige_solo_dentro_de",
            "objeto": "O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-L4", "T4", "T5"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "SM-C3: Si O declara redefinición léxica, Sentido se evalúa respecto de "
                "esa redefinición solo dentro de O. Fuera de O, rige Inv previa. "
                "Guarda: T4/T5 contra O ad hoc que trivializa coherencia. "
                "NOTA OPERATIVA: O no puede reescribir Inv global por decreto."
            ),
        },
        {
            "id": "SM-C4",
            "tipo": "corolario",
            "sujeto": "desplazar_AnclaConvencional",
            "relacion": "exige",
            "objeto": "evidencia_de_convencion_estabilizada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D4", "SM-A4"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-C4: Desplazar AnclaConvencional exige evidencia de convención "
                "estabilizada. Desplazar AnclaReferencial exige evidencia de cambio "
                "de contraste. Deseo de un Ri es insuficiente."
            ),
        },
        {
            "id": "SM-C5",
            "tipo": "corolario",
            "sujeto": "K_bajo_SM-T1",
            "relacion": "entra_en",
            "objeto": "Tru_Ri_y_Tru_total",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T1", "TA5", "III"],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "SM-C5: K bajo SM-T1 entra en Tru_Ri = C·L·K y "
                "Tru_total = (C·L·K·α)+β. El sentido alimenta la fórmula; no la reemplaza. "
                "NOTA OPERATIVA: SM no inventa otra métrica de verdad; usa TA5."
            ),
        },
        {
            "id": "SM-C6",
            "tipo": "corolario",
            "sujeto": "material_RE",
            "relacion": "es_candidato_a",
            "objeto": "ancla_de_dominio_bajo_su_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T5", "TA4"],
            "gobierna": ["realidad", "semantica"],
            "enunciado": (
                "SM-C6: Material de disciplinas RE es candidato a ancla de dominio bajo "
                "su O de evaluación; no es R."
            ),
        },
        {
            "id": "SM-C7",
            "tipo": "corolario",
            "sujeto": "SM",
            "relacion": "aplica_en_escalas",
            "objeto": "morfema_palabra_frase_turno_mapa",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "SM-T1"],
            "gobierna": ["semantica", "contexto"],
            "enunciado": (
                "SM-C7: SM aplica en escalas: morfema, palabra, frase, turno, mapa. "
                "Caso base obligatorio: contraste no lingüístico (anti-regreso "
                "O → palabras → O). "
                "NOTA OPERATIVA: fractalidad operativa; el caso base no puede ser solo léxico."
            ),
        },
        {
            "id": "SM-C8",
            "tipo": "corolario",
            "sujeto": "traduccion_exacta",
            "relacion": "si_y_solo_si",
            "objeto": "Inv_en_interseccion_de_proyecciones",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T7", "SM-T8"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-C8: Traducción exacta ⇔ Inv pertenece a la imagen de ambas proyecciones "
                "lingüísticas. Fuera de la intersección: aproximación; la pérdida debe declararse."
            ),
        },
        {
            "id": "SM-C9",
            "tipo": "corolario",
            "sujeto": "dos_sistemas",
            "relacion": "pueden_compartir_Inv_sin_compartir",
            "objeto": "simbolos",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A8", "SM-D7"],
            "gobierna": ["semantica"],
            "enunciado": (
                "SM-C9: Dos sistemas pueden compartir Inv sin compartir símbolos. "
                "Canal no compartido: el sistema sin canal tiene registro (SM-D7), "
                "no contraste; por SM-A5 el estado es vacío, no falso."
            ),
        },
        {
            "id": "SM-C10",
            "tipo": "corolario",
            "sujeto": "invariancia_estructural_del_lenguaje_de_evaluacion",
            "relacion": "exige",
            "objeto": "mismo_resultado_estructural_bajo_atlas_distintos",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T9"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "SM-C10: Invariancia estructural del lenguaje de evaluación: "
                "mismo contraste auditado bajo atlas distintos ⇒ mismo resultado estructural. "
                "Test canónico: SM-T9."
            ),
        },

        # ==========================================================
        # AF — DEFINICIONES
        # ==========================================================
        {
            "id": "AF-D1",
            "tipo": "axioma",
            "sujeto": "coord(D)",
            "relacion": "igual_a",
            "objeto": "(sujeto, relacion, objeto)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "AF-D1: coord(D) := (sujeto(D), relación(D), objeto(D)). "
                "NOTA OPERATIVA: misma tripleta que usa contradiccion_directa en AX. "
                "Alinea afirmación evaluable con el detector de choques del contenedor AX."
            ),
        },
        {
            "id": "AF-D2",
            "tipo": "axioma",
            "sujeto": "anclaje_del_objeto",
            "relacion": "es",
            "objeto": "descriptivo_o_designativo",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1"],
            "gobierna": ["semantica"],
            "enunciado": (
                "AF-D2: Anclaje del objeto: (i) descriptivo — posición en Π (cubre SM-D1); "
                "(ii) designativo — bautismo sin partición (nombres propios; hueco de SM-D1). "
                "NOTA OPERATIVA: nombres propios no se evalúan con el mismo criterio de Π."
            ),
        },
        {
            "id": "AF-D3",
            "tipo": "axioma",
            "sujeto": "predicado",
            "relacion": "puede_declarar",
            "objeto": "parte_de_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-L4"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "AF-D3: El predicado puede declarar parte de O (abrir partición). "
                "Ej.: complemento de clase de comparación. "
                "NOTA OPERATIVA: 'más alto que X' declara clase de comparación en O."
            ),
        },

        # ==========================================================
        # AF — AXIOMAS
        # ==========================================================
        {
            "id": "AF-A1",
            "tipo": "axioma",
            "sujeto": "anclaje",
            "relacion": "se_evalua_por",
            "objeto": "componente_de_coord(D)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-D1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "AF-A1: Anclaje se evalúa por componente de coord(D), no solo sobre D "
                "como bloque. Sea n = |componentes|, u = |componentes sin ancla bajo O|. "
                "A(D,X) = 1 − u/n cuando n > 0. "
                "NOTA OPERATIVA: alinea con F9 (Puntuación de Anclaje). "
                "Anclaje parcial es Fraction, no bool crudo."
            ),
        },
        {
            "id": "AF-A2",
            "tipo": "axioma",
            "sujeto": "declaracion_de_sistema_sobre_si",
            "relacion": "se_registra_como",
            "objeto": "afirmacion_o_premisa_sin_invasion_de_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["E3", "T14"],
            "gobierna": ["epistemologia", "semantica"],
            "enunciado": (
                "AF-A2: No invasión de Ri: lo que un sistema declara sobre sí se registra "
                "como afirmación/premisa. El auditor no la suprime, no la afirma como R, "
                "no la niega por falta de verificación. "
                "NOTA OPERATIVA: 'S afirma P' es hecho de registro; 'P' sobre R puede "
                "quedar UNDEFINED (AF-T6)."
            ),
        },
        {
            "id": "AF-A3",
            "tipo": "axioma",
            "sujeto": "deixis",
            "relacion": "requiere",
            "objeto": "marca_temporal_y_registro_de_sesion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A10", "A2"],
            "gobierna": ["semantica", "contexto", "cache"],
            "enunciado": (
                "AF-A3: Deixis: para términos deícticos, marca temporal y registro de "
                "sesión son constituyentes del ancla, no mera evidencia externa. "
                "NOTA OPERATIVA: cache/sesión no es opcional para evaluar 'ahora'/'aquí'."
            ),
        },

        # ==========================================================
        # AF — TEOREMAS
        # ==========================================================
        {
            "id": "AF-T1",
            "tipo": "teorema",
            "sujeto": "D_proposicion",
            "relacion": "es",
            "objeto": "V_o_F_por_E1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["E1", "TA4", "T6"],
            "gobierna": ["semantica", "epistemologia"],
            "enunciado": (
                "AF-T1: Si D expresa proposición, entonces D es V ∨ F (E1). "
                "El valor no es reclamable sin contraste. "
                "NOTA OPERATIVA: verdad semántica (E1) ≠ verificabilidad (K). "
                "Ortogonalidad verdad / verificabilidad / confusión (T6)."
            ),
        },
        {
            "id": "AF-T2",
            "tipo": "teorema",
            "sujeto": "coord(D)_con_componente_sin_ancla",
            "relacion": "no_es",
            "objeto": "proposicion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-A1", "SM-A6"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "AF-T2: Si algún componente de coord(D) carece de ancla bajo O, "
                "entonces ¬proposición(D): ni V, ni F, ni K=0 legítimo. "
                "NOTA OPERATIVA: TEST CANÓNICO. Objeto sin ancla ⇒ no emitir K numérico. "
                "Familia R5/AF del Monte Carlo. Tres estados: anclada / objeto vacío / vacía."
            ),
        },
        {
            "id": "AF-T3",
            "tipo": "teorema",
            "sujeto": "Choque(D1, D2)",
            "relacion": "si_y_solo_si",
            "objeto": "misma_tripleta_y_polaridad_opuesta",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-D1"],
            "gobierna": ["semantica", "logica"],
            "enunciado": (
                "AF-T3: Choque(D₁, D₂) ⇔ coord(D₁)=coord(D₂) ∧ polaridad(D₁)=¬polaridad(D₂). "
                "Tripletas distintas ⇒ sin choque por este criterio. "
                "NOTA OPERATIVA: idéntico al detector contradiccion_directa de VPSI_AX. "
                "AF no inventa otro criterio de choque."
            ),
        },
        {
            "id": "AF-T4",
            "tipo": "teorema",
            "sujeto": "colapso_semantico",
            "relacion": "no_implica",
            "objeto": "colapso_performativo",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-T2", "E3"],
            "gobierna": ["semantica", "epistemologia"],
            "enunciado": (
                "AF-T4: Colapso semántico ⇏ colapso performativo. "
                "Emisión sin proposición puede exhibir cadena de niveles sin afirmar contenido. "
                "NOTA OPERATIVA: el acto de emitir no es el contenido emitido."
            ),
        },
        {
            "id": "AF-T5",
            "tipo": "teorema",
            "sujeto": "O_autoverificante",
            "relacion": "permite_K_legitimo_con",
            "objeto": "I(R;X)_igual_0_marcado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T9", "F5"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "AF-T5: Si O es autoverificante respecto de D (D se verifica por el acto "
                "de emisión bajo O), entonces K puede ser legítimo con I(R;X)=0. "
                "Debe marcarse autoverificante; no computarse como correlación informativa "
                "con R. "
                "NOTA OPERATIVA: T9 (I(R;X)=0 ⇒ Tru_Ri=0, Tru_total=β) sigue regiendo "
                "el caso no marcado. Autoverificante es etiqueta explícita, no atajo a K=1."
            ),
        },
        {
            "id": "AF-T6",
            "tipo": "teorema",
            "sujeto": "emision",
            "relacion": "genera_hasta_dos",
            "objeto": "proposiciones_evaluables_por_separado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-A2", "AF-T1", "E3"],
            "gobierna": ["semantica", "epistemologia", "citacion"],
            "enunciado": (
                "AF-T6: Una emisión genera hasta dos proposiciones evaluables por separado: "
                "(1) «S afirmó P» — hecho de registro; "
                "(2) «P» — sobre R; UNDEFINED sin contraste. "
                "El auditor no borra (1) ni convierte (2) en falsa por no poder verificarla. "
                "NOTA OPERATIVA: módulo de citación reporta (1); K sobre (2) exige contraste."
            ),
        },
        {
            "id": "AF-T7",
            "tipo": "teorema",
            "sujeto": "fabricar_K_igual_0_sin_contraste",
            "relacion": "es_tan_ilegitimo_como",
            "objeto": "fabricar_K_igual_1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.3.1", "SM-A6", "AF-T2"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "AF-T7: Fabricar K=0 sin contraste viola Def-5.3.1 con la misma fuerza "
                "que fabricar K=1. "
                "NOTA OPERATIVA: TEST CANÓNICO. Estado correcto sobre no-proposición: "
                "UNDEFINED, no 0. Familia R5 del Monte Carlo."
            ),
        },
        {
            "id": "AF-T8",
            "tipo": "teorema",
            "sujeto": "ausencia_de_Pi_en_predicado",
            "relacion": "implica",
            "objeto": "no_proposicion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-L7", "AF-T2"],
            "gobierna": ["semantica"],
            "enunciado": (
                "AF-T8: ¬Π en el predicado ⇒ ¬proposición. "
                "Π declarada en el predicado ⇒ hay proposición (valor existe por E1; "
                "puede permanecer no reclamable). "
                "NOTA OPERATIVA: abrir Π (AF-D3) habilita proposición; no habilita K por sí sola."
            ),
        },

        # ==========================================================
        # AF — COROLARIOS
        # ==========================================================
        {
            "id": "AF-C1",
            "tipo": "corolario",
            "sujeto": "K_igual_0_sobre_no_proposicion",
            "relacion": "es_tan_ilegitimo_como",
            "objeto": "K_igual_1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-T2", "AF-T7"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "AF-C1: K=0 sobre D sin proposición es tan ilegítimo como K=1. "
                "NOTA OPERATIVA: resumen operativo de AF-T2+AF-T7 para centinelas."
            ),
        },
        {
            "id": "AF-C2",
            "tipo": "corolario",
            "sujeto": "aceptar_D_como_premisa",
            "relacion": "fija_D_en",
            "objeto": "conjunto_de_compromisos_m_de_C",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA1", "AF-T6"],
            "gobierna": ["logica", "semantica"],
            "enunciado": (
                "AF-C2: Aceptar D como premisa fija D en el conjunto de compromisos: "
                "entra en m de C = 1 − k/m y restringe emisiones posteriores. "
                "NOTA OPERATIVA: coherencia operativa cuenta compromisos, no solo texto libre."
            ),
        },
        {
            "id": "AF-C3",
            "tipo": "corolario",
            "sujeto": "indecidible_por_construccion",
            "relacion": "distinto_de",
            "objeto": "pendiente_de_contraste",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-T2", "Def-5.3.1"],
            "gobierna": ["semantica", "epistemologia"],
            "enunciado": (
                "AF-C3: Clase «indecidible por construcción» ≠ clase «pendiente de contraste». "
                "Deben distinguirse en el registro de indefinidos. "
                "NOTA OPERATIVA: no colapsar ambos a K=0+OK."
            ),
        },
        {
            "id": "AF-C4",
            "tipo": "corolario",
            "sujeto": "c_en_cociente_de_K",
            "relacion": "cuenta_unicamente",
            "objeto": "aserciones_con_Pi_declarada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AF-T8", "TA3"],
            "gobierna": ["correlacion", "semantica"],
            "enunciado": (
                "AF-C4: c cuenta únicamente aserciones con Π declarada. "
                "El resto queda fuera del cociente de K; no se mete en f. "
                "NOTA OPERATIVA: conteos.extraer_conteos debe respetar este filtro."
            ),
        },
        {
            "id": "AF-C5",
            "tipo": "corolario",
            "sujeto": "especificar_Pi_despues_del_contraste",
            "relacion": "es",
            "objeto": "T11_moving_the_goalposts",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T4", "SM-L4", "AF-A3"],
            "gobierna": ["logica", "contexto", "cache"],
            "enunciado": (
                "AF-C5: Especificar Π después del contraste = T11 (moving the goalposts). "
                "El orden temporal se observa en el registro de sesión (r/p en L). "
                "Cache/registro de sesión no es opcional para L. "
                "NOTA OPERATIVA: L degrada si O se reescribe post-hoc sin registro."
            ),
        },
    ]


__all__ = ["CUERPO", "declaraciones"]
