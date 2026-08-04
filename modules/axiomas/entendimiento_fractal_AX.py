# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- modules/axiomas/entendimiento_fractal_AX.py

Cuerpo axiomático: Entendimiento y Fractalidad (EF)
Familia EF · Versión 1.1

QUÉ ES:
  Formaliza el proceso de estabilización operativa bajo O: el significado
  evaluable no es átomo, sino estructura de correlaciones parciales que
  se expanden y se cortan cuando el material bajo O deja de crecer.
  Ancla el lenguaje de "entendimiento" al entendimiento operativo ya
  definido en SM-D10 / SM-T13 (organización de X; sin posesión de R).

QUÉ NO ES:
  No calcula Tru, C, L, K ni E numérico.
  No introduce constantes geométricas nuevas (no existe 25/27 en AX ni
  en Omega Engine; α=26/27 y β=1/27 permanecen solos).
  No redefine τ (reservado a traza SM-D13).
  No promedia multi-O en silencio (CX-A25 / CX-T15).
  No convierte estado interno en evidencia X de R (RE-A8, TA4).

CARGA:
  Automática por modules/axiomas/__init__.py vía CUERPO + declaraciones().
  Si barrer() reporta choque, el cuerpo se rechaza.

ANCLAS (depende_de apunta a ids existentes; no los reescribe):
  Def-5.3.1, TA3, TA4, TA5, T9, T14, T16, T17, beta,
  CX-A1, CX-A2, CX-A3, CX-A7, CX-A8, CX-A9, CX-A11, CX-A23, CX-A25,
  CX-T4, CX-T6, CX-T15, CX-T17,
  SM-D1, SM-D10, SM-D12, SM-A2, SM-A6, SM-A11, SM-A13,
  SM-T12, SM-T13, SM-A16, SM-T17, SM-T18,
  SE-A3, SE-A6, SE-T3, SE-T7,
  IND-A1, IND-A4, IND-C3,
  SF-T1, RE-A2, RE-A3, RE-A7, RE-A8, RE-A11, RE-T10.
"""

from __future__ import annotations

from typing import Any, Dict, List

CUERPO = {
    "nombre": "entendimiento_fractal",
    "version": "1.1",
    "descripcion": (
        "Proceso de estabilización operativa bajo O; recursión semántica "
        "y cognitiva; ruptura por saturación de material; multi-O sin "
        "colapso; interrupción jurisdiccional al Self sin inventar X de R."
    ),
}


def declaraciones() -> List[Dict[str, Any]]:
    return [

        # ==============================================================
        # DEFINICIONES
        # ==============================================================
        {
            "id": "EF-D1",
            "tipo": "definicion",
            "sujeto": "Corr(D)",
            "relacion": "es",
            "objeto": "conjunto_finito_de_componentes_correlacionales_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "CX-A11", "SM-A6"],
            "gobierna": ["semantica", "correlacion", "contexto"],
            "enunciado": (
                "EF-D1 (Ciclo de correlaciones / fractal semántico operativo): "
                "Sea D una descripción bajo O usable. D admite ciclo de correlaciones "
                "si existe un conjunto finito Corr(D) = {e_1, …, e_n} de componentes "
                "evaluables bajo escalas e* declarables (CX-A11), pudiendo cada e_i "
                "admitir a su vez Corr(e_i). El significado evaluable no se trata como "
                "átomo: es la estructura de ese ciclo bajo O. "
                "NOTA OPERATIVA: Sin Π reconocible bajo O rigen SM-A6 y AF-T2 "
                "(no proposición / K no reclamable). EF-D1 no crea proposiciones "
                "donde no las hay. "
                "EJEMPLO: 'casa' bajo O de hábitat puede abrir Corr con "
                "techo, muro, habitación; cada uno puede abrir el suyo a otra escala."
            ),
        },
        {
            "id": "EF-D2",
            "tipo": "definicion",
            "sujeto": "O_micro(e)",
            "relacion": "es",
            "objeto": "sub_armazon_recuperable_de_Corr_e_y_ligaduras_inmediatas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D1", "CX-A2", "RE-A3"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "EF-D2 (Contexto tácito local): O_micro(e) es el sub-armazón recuperable "
                "a partir de Corr(e) y de las ligaduras inmediatas de e bajo la escala "
                "declarada. Es marco de lectura, no R (CX-A2, RE-A3). "
                "NOTA OPERATIVA: no identificar O_micro con R ni con Omega."
            ),
        },
        {
            "id": "EF-D3",
            "tipo": "definicion",
            "sujeto": "B(D,O)",
            "relacion": "es",
            "objeto": "sucesion_finita_de_expansiones_de_material_correlacional_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D1", "SM-D10", "SM-T13", "TA4"],
            "gobierna": ["semantica", "correlacion", "meta"],
            "enunciado": (
                "EF-D3 (Bucle de estabilización operativa): B(D,O) es la sucesión finita "
                "de expansiones Corr^(0)(D) ⊆ Corr^(1) ⊆ … que un evaluador ejecuta al "
                "intentar enriquecer el material usable para correlacionar D con el "
                "dominio de O. Es instancia del proceso que SM-D10 llama entendimiento "
                "operativo (organización bajo Π y reglas deterministas), no posesión "
                "de R (SM-T13, TA4). "
                "NOTA OPERATIVA: 'entendimiento' en este cuerpo = entendimiento operativo; "
                "no estado mental ni contacto con R."
            ),
        },
        {
            "id": "EF-D4",
            "tipo": "definicion",
            "sujeto": "E_p(e|O)",
            "relacion": "es",
            "objeto": "material_parcial_aportado_por_e_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D3", "TA5"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "EF-D4 (Material parcial): E_p(e|O) designa el material parcial aportado "
                "por e al ensamblaje bajo O. Ningún E_p aislado es Tru_Ri(D). "
                "E_p no entra en la fórmula TA5. "
                "NOTA OPERATIVA: sirve para hablar del aporte local; no es un factor "
                "numérico que el cuerpo calcule."
            ),
        },
        {
            "id": "EF-D5",
            "tipo": "definicion",
            "sujeto": "ruptura_de_B",
            "relacion": "es",
            "objeto": "paso_de_St_a_Resuelto_por_cese_de_expansion_admisible",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D3", "IND-A1"],
            "gobierna": ["meta", "correlacion"],
            "enunciado": (
                "EF-D5 (Ruptura de bucle): Ruptura de B(D,O) es el paso de St(B) a "
                "Resuelto cuando cesa la expansión admisible de Corr bajo O (EF-T1). "
                "No es error de sistema (IND-A1). "
                "NOTA OPERATIVA: ruptura ≠ indefinido de dominio (ver EF-L3)."
            ),
        },
        {
            "id": "EF-D6",
            "tipo": "definicion",
            "sujeto": "recursion_estructural",
            "relacion": "es",
            "objeto": "expansion_sobre_material_de_significado_bajo_escalas_e_star",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D1", "CX-A11", "SE-A3"],
            "gobierna": ["semantica"],
            "enunciado": (
                "EF-D6 (Recursión estructural): Expansión sobre material de significado "
                "(componentes definicionales o composicionales) bajo escalas e*. "
                "Es semántica; no es por sí sola inferencia de hechos de R. "
                "EJEMPLO: corazón → órgano → tejido → … a distinta e*."
            ),
        },
        {
            "id": "EF-D7",
            "tipo": "definicion",
            "sujeto": "recursion_cognitiva_operativa",
            "relacion": "es",
            "objeto": "expansion_sobre_demanda_de_correlacion_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D3", "EF-A5"],
            "gobierna": ["semantica", "meta"],
            "enunciado": (
                "EF-D7 (Recursión cognitiva operativa): Expansión sobre demanda de "
                "correlación (pregunta, hipótesis, cadena inferencial) bajo O. "
                "Puede suspenderse por cambio de jurisdicción (EF-A5). "
                "EJEMPLO: ¿qué es X? → abre demanda de correlación; no solo desglose "
                "definicional de la etiqueta X."
            ),
        },
        {
            "id": "EF-D8",
            "tipo": "definicion",
            "sujeto": "St(B)",
            "relacion": "pertenece_a",
            "objeto": "Activo_o_Suspendido_o_Resuelto",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D3", "EF-D5"],
            "gobierna": ["meta"],
            "enunciado": (
                "EF-D8 (Estados del bucle): St(B) ∈ {Activo, Suspendido, Resuelto}. "
                "Exactamente un valor por instante de evaluación (EF-A6)."
            ),
        },

        # ==============================================================
        # AXIOMAS
        # ==============================================================
        {
            "id": "EF-A1",
            "tipo": "axioma",
            "sujeto": "entendimiento_operativo_evaluable",
            "relacion": "exige",
            "objeto": "al_menos_un_acto_de_correlacion_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A11", "SM-A2", "TA3", "SM-D10"],
            "gobierna": ["semantica", "correlacion", "epistemologia"],
            "enunciado": (
                "EF-A1 (Necesidad de correlación): No hay entendimiento operativo "
                "evaluable de D bajo O sin al menos un acto de correlación de D "
                "(o de sus partes) con el dominio que O delimita. "
                "NOTA OPERATIVA: sigue SM-A11 (sin celda en Π no hay medida) y "
                "TA3/SM-A2 (K/sentido = correlación con dominio(O))."
            ),
        },
        {
            "id": "EF-A2",
            "tipo": "axioma",
            "sujeto": "E_p",
            "relacion": "es_parcial_respecto_de",
            "objeto": "configuracion_resuelta_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D4", "SM-D12", "SM-T12"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "EF-A2 (Parcialidad del material): Todo E_p es parcial respecto de una "
                "configuración resuelta (SM-D12). El valor reclamable, si existe, es el "
                "de γ* bajo O (SM-T12), no el de un componente aislado."
            ),
        },
        {
            "id": "EF-A3",
            "tipo": "axioma",
            "sujeto": "B(D,O)",
            "relacion": "es_finito_en",
            "objeto": "evaluacion_efectiva",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D3", "SM-T17", "CX-A6", "IND-A4", "Def-5.3.1"],
            "gobierna": ["meta", "correlacion", "verificacion"],
            "enunciado": (
                "EF-A3 (Finitud efectiva del bucle): En evaluación efectiva, B(D,O) es "
                "finito: o St pasa a Resuelto (EF-T1), o el tramo queda bajo reglas de "
                "indefinido si no hay O usable (IND-A4, Def-5.3.1). No se admite "
                "expansión no terminante dentro de un ciclo de motor. "
                "NOTA OPERATIVA: sin terminación no hay traza depositable (SM-T17)."
            ),
        },
        {
            "id": "EF-A4",
            "tipo": "axioma",
            "sujeto": "O_micro_y_O_global",
            "relacion": "pueden_coexistir_sin",
            "objeto": "borrado_ni_promedio_silencioso_de_micro",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A25", "CX-T15", "CX-A3"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "EF-A4 (Multiplicidad micro/global): Pueden coexistir O_1…O_n micro y, "
                "si se declara, O_global de mapa. El global no borra ni promedia en "
                "silencio los micro (CX-A25, CX-T15)."
            ),
        },
        {
            "id": "EF-A5",
            "tipo": "axioma",
            "sujeto": "desplazamiento_del_objeto_hacia_el_sistema",
            "relacion": "suspende_B_externo_y_exige",
            "objeto": "cambio_de_O_o_frontera_explicita_bajo_SF",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SF-T1", "CX-A23", "RE-A8", "Def-5.3.1", "TA4", "RE-A3"],
            "gobierna": ["meta", "contexto", "epistemologia", "self"],
            "enunciado": (
                "EF-A5 (Interrupción jurisdiccional): Si el material evaluable desplaza "
                "el objeto de evaluación hacia el propio sistema como sistema "
                "(auto-referencia operativa / Self funcional), el bucle externo B(D,O) "
                "pasa a Suspendido y el cambio de marco debe tratarse como cambio de O "
                "o frontera explícita (CX-A23), bajo el cuerpo SF. "
                "Este axioma NO autoriza tratar el estado interno como evidencia X de "
                "hechos de R ni como sustituto de O externo sin declaración "
                "(RE-A8, Def-5.3.1, TA4, RE-A3). "
                "NOTA OPERATIVA: solo suspende el fractal externo; no inventa "
                "correlación con R. "
                "EJEMPLO: una demanda del tipo auto-referencia del motor suspende la "
                "expansión del tema externo; no rellena con material estocástico."
            ),
        },
        {
            "id": "EF-A6",
            "tipo": "axioma",
            "sujeto": "St(B)",
            "relacion": "toma_exactamente_uno_de",
            "objeto": "Activo_Suspendido_Resuelto",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-D8"],
            "gobierna": ["meta"],
            "enunciado": (
                "EF-A6 (Unicidad de estado): En cada instante de evaluación, St(B) toma "
                "exactamente un valor de EF-D8."
            ),
        },
        {
            "id": "EF-A7",
            "tipo": "axioma",
            "sujeto": "entendimiento_operativo",
            "relacion": "se_afirma_de",
            "objeto": "estructura_de_relaciones_bajo_O_no_del_elemento_aislado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D1", "EF-A1"],
            "gobierna": ["semantica", "correlacion"],
            "enunciado": (
                "EF-A7 (Primacía relacional): El entendimiento operativo no se afirma "
                "del elemento aislado sino de la estructura de relaciones bajo O "
                "(coherente con SM-D1: significado = posición en Π)."
            ),
        },
        {
            "id": "EF-A8",
            "tipo": "axioma",
            "sujeto": "proceso_E",
            "relacion": "no_es_factor_de",
            "objeto": "Tru_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5"],
            "gobierna": ["logica", "semantica", "meta"],
            "enunciado": (
                "EF-A8 (E no es factor de Tru_Ri): El proceso E no es un cuarto factor "
                "en Tru_Ri. Tru_Ri(D) = C(D)·L(D)·K(D) (TA5). E organiza y filtra "
                "material correlacional bajo O; no modifica la fórmula. "
                "NOTA OPERATIVA: si se añadiera E∈[0,1] a Tru, o redundaría con C,L,K "
                "o contradiría la multiplicatividad cargada. Por tanto E ∉ {C,L,K}."
            ),
        },

        # ==============================================================
        # LEMAS
        # ==============================================================
        {
            "id": "EF-L1",
            "tipo": "lema",
            "sujeto": "ejecucion_suspension_o_ruptura_de_B",
            "relacion": "no_modifica",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "RE-A2", "RE-T10"],
            "gobierna": ["ontologia", "realidad", "meta"],
            "enunciado": (
                "EF-L1: Ejecución, suspensión o ruptura de B no modifican R; solo "
                "delimitan el mapa de R_i (TA4, RE-A2, RE-T10)."
            ),
        },
        {
            "id": "EF-L2",
            "tipo": "lema",
            "sujeto": "expansion_de_Corr",
            "relacion": "no_autoriza_Tru_total_fuera_de",
            "objeto": "intervalo_beta_1_ni_techo_Ri_sobre_alpha",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T16", "T17", "CX-T10", "EF-A8", "beta"],
            "gobierna": ["logica", "constantes"],
            "enunciado": (
                "EF-L2 (Cotas α y β intactas): Ningún esquema de expansión de Corr "
                "autoriza Tru_total fuera de [β, 1] cuando los factores están definidos, "
                "ni techo de R_i por encima de α (T16, T17, CX-T10). "
                "NOTA OPERATIVA: no existe constante 25/27 en este cuerpo ni en el grafo."
            ),
        },
        {
            "id": "EF-L3",
            "tipo": "lema",
            "sujeto": "ruptura_por_saturacion_bajo_O_usable",
            "relacion": "es_distinta_de",
            "objeto": "dominio_indefinido",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-T1", "IND-D1", "Def-5.3.1"],
            "gobierna": ["contexto", "epistemologia", "verificacion"],
            "enunciado": (
                "EF-L3: St=Resuelto por saturación bajo O usable ≠ dominio indefinido "
                "(IND-D1). El primero presupone O; el segundo, ausencia de O usable "
                "(Def-5.3.1)."
            ),
        },
        {
            "id": "EF-L4",
            "tipo": "lema",
            "sujeto": "St_Suspendido",
            "relacion": "no_borra_Corr_ni_reescribe_gamma_estrella_sin",
            "objeto": "Clash_con_anclas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A16", "SM-T18"],
            "gobierna": ["meta", "memoria_operativa"],
            "enunciado": (
                "EF-L4: St=Suspendido no borra Corr ya obtenido. Reabrir o reescribir "
                "una configuración ya resuelta exige Clash con anclas (SM-A16, SM-T18); "
                "la sola suspensión no basta."
            ),
        },

        # ==============================================================
        # TEOREMAS
        # ==============================================================
        {
            "id": "EF-T1",
            "tipo": "teorema",
            "sujeto": "saturacion_conjuntista_de_Corr_bajo_O",
            "relacion": "permite",
            "objeto": "St_Resuelto",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-A3", "SM-A13", "TA3", "SM-A2", "SM-T17", "IND-C3", "Def-5.3.1"],
            "gobierna": ["correlacion", "meta", "verificacion"],
            "enunciado": (
                "EF-T1 (Saturación conjuntista y ruptura): Sea B(D,O) con O usable. "
                "Si en un paso de expansión el conjunto de material correlacional usable "
                "bajo O no crece (no aparecen componentes nuevos admisibles bajo las "
                "anclas y reglas deterministas vigentes), entonces St(B) puede pasar a "
                "Resuelto. La ruptura es el reconocimiento de que seguir expandiendo Corr "
                "no aporta nuevo material de correlación bajo ese O. "
                "NOTA OPERATIVA: este teorema NO fija umbral numérico ni constante 25/27. "
                "Cualquier criterio numérico de parada del motor es parámetro operativo "
                "anunciable (PA), no cota del grafo AX. "
                "Si el material se agota sin poder reclamar K, rigen IND-C3 / Def-5.3.1."
            ),
        },
        {
            "id": "EF-T2",
            "tipo": "teorema",
            "sujeto": "discurso_con_O_1_a_O_n",
            "relacion": "no_admite_Tru_total_unico_sin",
            "objeto": "regla_de_agregacion_declarada",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-T15", "CX-A25", "CX-T17", "CX-C18"],
            "gobierna": ["contexto", "logica", "epistemologia"],
            "enunciado": (
                "EF-T2 (N contextos sin colapso): Con turnos bajo O_1…O_n posiblemente "
                "distintos, no hay un único Tru_total del discurso entero sin regla de "
                "agregación declarada (CX-T15). Un O_global de mapa, si se declara, "
                "evalúa el mapa sin borrar micro (CX-A25, CX-C18). "
                "NOTA OPERATIVA: cualquier suma ponderada de Tru locales solo es admisible "
                "con O_global declarado y pesos como regla explícita; nunca como promedio oculto."
            ),
        },
        {
            "id": "EF-T3",
            "tipo": "teorema",
            "sujeto": "circularidad_o_ausencia_de_ancla_bajo_O",
            "relacion": "no_hace_caer_Tru_total_bajo",
            "objeto": "beta_con_Ri_presente",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A6", "Def-5.3.1", "T17", "RE-A11", "EF-A3", "beta"],
            "gobierna": ["correlacion", "constantes", "ontologia"],
            "enunciado": (
                "EF-T3 (Circularidad/vacío y piso β): Si B encuentra circularidad o "
                "ausencia de ancla bajo O (SM-A6), el material para K puede ser no "
                "reclamable. Con Ri presente, Tru_total no cae bajo β (T17). "
                "No se asigna R=0 (RE-A11). EF-A3 fuerza terminación del bucle."
            ),
        },
        {
            "id": "EF-T4",
            "tipo": "teorema",
            "sujeto": "proceso_E",
            "relacion": "produce_material_para_K_y_no_se_define_como_funcion_de",
            "objeto": "K_ya_dado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA3", "SM-A2", "EF-A8"],
            "gobierna": ["correlacion", "semantica", "meta"],
            "enunciado": (
                "EF-T4 (Orden E → material de K): El proceso E produce y filtra material "
                "correlacional bajo O. No se define E como función de un K ya dado: sin "
                "proceso correlacional no hay K reclamable (TA3, SM-A2). "
                "NOTA OPERATIVA: E ⇒ candidatos a K; no K ⇒ E."
            ),
        },
        {
            "id": "EF-T5",
            "tipo": "teorema",
            "sujeto": "estabilidad_de_O_global",
            "relacion": "exige",
            "objeto": "integrabilidad_en_el_armazon_no_continuidad_tematica",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A7", "CX-A8", "CX-A9", "CX-T4", "CX-T6"],
            "gobierna": ["contexto", "semantica"],
            "enunciado": (
                "EF-T5 (Continuidad causal del mapa, no temática): La estabilidad de "
                "O_global no exige el mismo tema en todos los turnos, sino integrabilidad "
                "en el armazón (CX-A7–A9). Si el material no es integrable, CX-T6: "
                "nuevo O o K indefinido en el tramo."
            ),
        },
        {
            "id": "EF-T6",
            "tipo": "teorema",
            "sujeto": "evolucion_declarada_de_marco",
            "relacion": "integra_sin",
            "objeto": "reescritura_retroactiva_de_K",
            "polaridad": True,
            "cota": None,
            "depende_de": ["RE-A7", "CX-A23"],
            "gobierna": ["contexto", "cache", "realidad"],
            "enunciado": (
                "EF-T6 (Trayectoria contextual): Cuando se declara evolución de marco, "
                "O(t+1) integra O(t) y el material de T(t+1) en el registro, sin "
                "reescritura retroactiva de K (RE-A7, CX-A23)."
            ),
        },
        {
            "id": "EF-T7",
            "tipo": "teorema",
            "sujeto": "St_Resuelto_con_configuracion_cerrada",
            "relacion": "activa",
            "objeto": "deposito_de_traza_tau_segun_SM-T17",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D12", "SM-T17", "SM-A16", "SM-T18"],
            "gobierna": ["meta", "memoria_operativa"],
            "enunciado": (
                "EF-T7 (Compatibilidad con memoria operativa): Si St(B)=Resuelto y el "
                "ciclo cierra (O, Γ, A') con γ*, aplica SM-T17 (depósito de τ). "
                "EF no redefine τ (SM-D13). Reapertura sin Clash es inadmisible "
                "(SM-A16, SM-T18)."
            ),
        },

        # ==============================================================
        # COROLARIOS
        # ==============================================================
        {
            "id": "EF-C1",
            "tipo": "corolario",
            "sujeto": "agotamiento_de_Corr_sin_K_reclamable",
            "relacion": "impone",
            "objeto": "IND_o_Def-5.3.1_sin_fabricar_material",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-T1", "IND-C3", "Def-5.3.1", "F8"],
            "gobierna": ["epistemologia", "verificacion", "correlacion"],
            "enunciado": (
                "EF-C1 (Sin alucinación por bucle): Si Corr se agota bajo O sin poder "
                "reclamar K, se aplica IND/Def-5.3.1; está prohibido fabricar material "
                "o K (IND-C3, F8)."
            ),
        },
        {
            "id": "EF-C2",
            "tipo": "corolario",
            "sujeto": "usos_no_literales",
            "relacion": "se_evaluan_como",
            "objeto": "D_bajo_O_sin_operador_especial",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-A6", "SE-T3"],
            "gobierna": ["semantica", "ontologia"],
            "enunciado": (
                "EF-C2 (Metáfora sin operador especial): Usos no literales se evalúan "
                "como D bajo O. Puede haber Sentido_O sin Real ni K de R (SE-A6, SE-T3)."
            ),
        },
        {
            "id": "EF-C3",
            "tipo": "corolario",
            "sujeto": "interrupcion_por_EF-A5",
            "relacion": "es",
            "objeto": "cambio_de_jurisdiccion_no_relleno_estocastico",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-A5", "SF-T1"],
            "gobierna": ["meta", "self", "verificacion"],
            "enunciado": (
                "EF-C3: La interrupción por EF-A5 es cambio de jurisdicción bajo SF/CX, "
                "no autorización de componentes estocásticos en la ruta de decisión."
            ),
        },
        {
            "id": "EF-C4",
            "tipo": "corolario",
            "sujeto": "alteracion_de_O_global_por_micro",
            "relacion": "rige_por",
            "objeto": "regla_de_agregacion_declarada_del_mapa",
            "polaridad": True,
            "cota": None,
            "depende_de": ["CX-A25", "EF-T2"],
            "gobierna": ["contexto"],
            "enunciado": (
                "EF-C4: La alteración de O_global por cambios micro se rige por la regla "
                "de agregación declarada del mapa (CX-A25), no por peso oculto del motor."
            ),
        },
        {
            "id": "EF-C5",
            "tipo": "corolario",
            "sujeto": "conteos_y_CA",
            "relacion": "no_implementan",
            "objeto": "proceso_E",
            "polaridad": True,
            "cota": None,
            "depende_de": ["EF-A8", "EF-T4"],
            "gobierna": ["meta", "correlacion"],
            "enunciado": (
                "EF-C5: conteos produce m,k,p,r,c,f. CA calcula factores. E, si se "
                "instrumenta, es política de expansión/cierre en Engine, subordinada a "
                "AX y a CA — nunca al revés. Este cuerpo no calcula."
            ),
        },
        {
            "id": "EF-C6",
            "tipo": "corolario",
            "sujeto": "expansion_de_Corr",
            "relacion": "es_instancia_de",
            "objeto": "generatividad_acotada_por_cierre_bajo_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SE-T7", "TR1"],
            "gobierna": ["meta", "semantica", "informacion"],
            "enunciado": (
                "EF-C6: Expandir Corr es generatividad (TR1 / SE-T7): más combinaciones "
                "que cierres. El filtro sigue siendo cierre bajo O y Tru_Ri, no el "
                "volumen de recursión."
            ),
        },
        {
            "id": "EF-C7",
            "tipo": "corolario",
            "sujeto": "cuerpo_EF",
            "relacion": "no_introduce",
            "objeto": "constante_25_27_ni_tercer_invariante_geometrico",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta", "T16", "T17", "EF-L2"],
            "gobierna": ["constantes", "meta"],
            "enunciado": (
                "EF-C7 (Ninguna constante 25/27): Este cuerpo no introduce 25/27 ni "
                "ningún tercer invariante geométrico entre β y α. Omega Engine y el "
                "grafo AX carecen de esa constante; EF no la crea. α=26/27 y β=1/27 "
                "permanecen solos."
            ),
        },
    ]


__all__ = ["CUERPO", "declaraciones"]
