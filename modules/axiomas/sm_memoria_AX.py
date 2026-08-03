# -*- coding: utf-8 -*-
"""
SM_MEMORIA — Extensión axiomática: Memoria operativa y traza de resoluciones.

Versión: 1.0
Dependencias estructurales: SM_MAPA, SM_AF, TA3–TA5, T6, T9, T12, T14, beta.

NOTA GENERAL (para humanos)
---------------------------
Este cuerpo formaliza la condición de conocimiento que evita el ciclo de
re-confirmación:

1. Sin traza de resoluciones el sistema recalcula eternamente lo ya resuelto.
2. La memoria operativa M es el conjunto exacto de trazas τ (no reconstructiva).
3. Una configuración resuelta solo se reabre bajo evidencia ε que produzca
   Clash real con anclas forzadas A.
4. El cuestionamiento sin choque forzado es inadmisible.
5. La coexistencia de τ_antes y τ_después documenta la corrección acumulativa.

Símbolos (no contradictorios con SM_MAPA / SM_AF):
  A     = conjunto de anclas forzadas
  Γ     = conjunto finito de correlaciones candidatas
  Res   = operador de resolución (argmax Tru_Ri)
  τ     = traza de una resolución
  M     = memoria operativa
  Clash = predicado de choque forzado

Cada declaración lleva nota operativa, ejemplo y demostración comentada.
"""

from __future__ import annotations
from typing import List, Dict, Any

# ============================================================
# METADATOS DEL CUERPO
# ============================================================

CUERPO = {
    "nombre": "SM_MEMORIA",
    "version": "1.0",
    "descripcion": (
        "Memoria operativa como conjunto exacto de trazas de resoluciones; "
        "evación del ciclo de re-confirmación; reapertura solo bajo Clash "
        "con anclas forzadas; corrección acumulativa."
    ),
    "depende_de_cuerpos": ["SM_MAPA", "SM_AF", "VPSI"],
    "gobierna": [
        "memoria_operativa",
        "traza_resolucion",
        "evacion_ciclo",
        "reapertura_legitima",
        "correccion_acumulativa",
        "conocimiento_operativo",
    ],
}

# ============================================================
# DECLARACIONES
# ============================================================

def declaraciones() -> List[Dict[str, Any]]:
    """
    Lista de declaraciones del cuerpo SM_MEMORIA.
    Formato canónico VPSI: id, tipo, sujeto, relacion, objeto,
    polaridad, cota, depende_de, gobierna, enunciado.
    """
    return [

        # --------------------------------------------------
        # DEFINICIONES
        # --------------------------------------------------
        {
            "id": "SM-D12",
            "tipo": "definicion",
            "sujeto": "terna_O_Gamma_A_prima",
            "relacion": "es_configuracion_resuelta_ssi",
            "objeto": "existe_gamma_estrella_Res_y_eliminadas_por_C_o_L_o_menor_Tru_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T12"],
            "gobierna": ["configuracion_resuelta"],
            "enunciado": (
                "SM-D12 (Configuración resuelta): Una terna (O, Γ, A') con A' ⊆ A y Γ ≠ ∅ "
                "se llama configuración. Se dice resuelta cuando existe "
                "γ* = Res(O, Γ, A') y para todo γ ∈ Γ \\ {γ*} se tiene C(γ)=0 o L(γ)=0 "
                "o bien Tru_Ri(γ) < Tru_Ri(γ*).\n\n"
                "NOTA OPERATIVA: Res es el operador de SM-T12 (argmax de Tru_Ri bajo "
                "anclas forzadas). La configuración queda cerrada cuando hay un único "
                "superviviente y el resto ha sido eliminado por choque o por valor inferior.\n"
                "EJEMPLO: O = 'efecto del sol en desierto', Γ = cinco correlaciones "
                "candidatas, A' contiene anclas físicas. γ* maximiza C·L·K; las demás "
                "tienen C=0, L=0 o Tru_Ri menor → configuración resuelta."
            ),
        },
        {
            "id": "SM-D13",
            "tipo": "definicion",
            "sujeto": "traza_tau",
            "relacion": "es",
            "objeto": "quintupla_O_gamma_estrella_eliminadas_A_prima_Tru_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D12"],
            "gobierna": ["traza_resolucion"],
            "enunciado": (
                "SM-D13 (Traza de resolución): La traza de una configuración resuelta "
                "(O, Γ, A') es la quíntupla "
                "τ(O, Γ, A') = (O, γ*, {γ ∈ Γ : C(γ)L(γ)=0}, A', Tru_Ri(γ*)).\n\n"
                "NOTA OPERATIVA: La traza registra exactamente qué se eligió, qué se "
                "eliminó, bajo qué anclas y con qué valor. No es un resumen narrativo; "
                "es el dato estructural del cierre.\n"
                "EJEMPLO: τ = (O_sol, γ*_insolacion, {γ_negacion, γ_irrelevante}, "
                "{β, LeyΩ, …}, 1). Ese registro es lo que se deposita en memoria."
            ),
        },
        {
            "id": "SM-D14",
            "tipo": "definicion",
            "sujeto": "memoria_operativa_M",
            "relacion": "es",
            "objeto": "conjunto_de_todas_las_trazas_tau_de_resoluciones",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D13"],
            "gobierna": ["memoria_operativa"],
            "enunciado": (
                "SM-D14 (Memoria operativa): La memoria operativa de un sistema es el conjunto "
                "M = { τ(O, Γ, A') | (O, Γ, A') ha sido resuelta }.\n\n"
                "NOTA OPERATIVA: M es exacta (SM-A15). No reconstruye. Cada τ es la "
                "quíntupla computada en el instante de la resolución. El módulo CH "
                "(caché) es la implementación natural de M.\n"
                "EJEMPLO: Después de tres resoluciones distintas, M contiene tres "
                "quíntuplas. Al reaparecer una configuración ya vista, se recupera τ "
                "sin re-ejecutar Res."
            ),
        },
        {
            "id": "SM-D15",
            "tipo": "definicion",
            "sujeto": "evidencia_epsilon",
            "relacion": "legitima_reapertura_de_tau_ssi",
            "objeto": "Clash_gamma_estrella_epsilon_A_es_true",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D13", "SM-T14"],
            "gobierna": ["reapertura_legitima"],
            "enunciado": (
                "SM-D15 (Reapertura legítima): Una evidencia ε legitima la reapertura de "
                "τ(O, Γ, A') ∈ M si y sólo si Clash(γ*, ε, A) = true "
                "(la adjunción de ε produce C=0 o L=0 bajo alguna ancla de A).\n\n"
                "NOTA OPERATIVA: Sin Clash real no hay reapertura. El cuestionamiento "
                "solo no basta. Hace falta evidencia que fuerce contradicción con anclas "
                "que no dependen del observador.\n"
                "EJEMPLO: Alguien aporta datos correlacionados con anclas físicas que "
                "contradicen γ*_insolacion bajo el mismo O. Clash = true → reapertura "
                "legítima. Si solo dice 'no estoy de acuerdo', Clash = false → inadmisible."
            ),
        },

        # --------------------------------------------------
        # AXIOMAS
        # --------------------------------------------------
        {
            "id": "SM-A14",
            "tipo": "axioma",
            "sujeto": "memoria_operativa_vacia",
            "relacion": "implica",
            "objeto": "re_ejecucion_de_Res_sobre_configuraciones_ya_presentadas",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D14"],
            "gobierna": ["evacion_ciclo"],
            "enunciado": (
                "SM-A14 (Necesidad de la traza): Si M = ∅, entonces el sistema re-ejecuta "
                "Res sobre toda configuración ya presentada.\n\n"
                "NOTA OPERATIVA: Sin memoria no hay conocimiento acumulativo: solo "
                "repetición del mismo cálculo. Este axioma es la justificación de por qué "
                "CH debe conservar las resoluciones.\n"
                "EJEMPLO: Se resuelve 'sol → insolación mortal'. Sin τ en M, al volver "
                "a presentar la misma configuración el sistema maximiza otra vez. Bucle."
            ),
        },
        {
            "id": "SM-A15",
            "tipo": "axioma",
            "sujeto": "traza_en_M",
            "relacion": "conserva_valores_exactos",
            "objeto": "computados_en_el_instante_de_resolucion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D13", "SM-D14"],
            "gobierna": ["exactitud_memoria"],
            "enunciado": (
                "SM-A15 (Exactitud de la memoria operativa): Para toda τ ∈ M, "
                "τ = (O, γ*, E, A', v) con v = Tru_Ri(γ*) exactamente igual a los valores "
                "computados en el instante de la resolución (no hay reconstrucción).\n\n"
                "NOTA OPERATIVA: A diferencia de la memoria humana (reconstructiva), "
                "M es exacta. El contraste 'ya resuelto / se presenta ahora' es idéntico "
                "al cómputo original.\n"
                "EJEMPLO: τ registra Tru_Ri = 26/27. Al recuperarla meses después, el "
                "valor sigue siendo 26/27; no se re-estima ni se aproxima."
            ),
        },
        {
            "id": "SM-A16",
            "tipo": "axioma",
            "sujeto": "traza_en_M_sin_Clash",
            "relacion": "implica",
            "objeto": "modificacion_de_gamma_estrella_inadmisible",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D15"],
            "gobierna": ["reapertura_legitima"],
            "enunciado": (
                "SM-A16 (Condición exclusiva de reapertura): Si τ(O, Γ, A') ∈ M y "
                "¬Clash(γ*, ε, A), entonces la modificación de γ* es inadmisible.\n\n"
                "NOTA OPERATIVA: Protege el conocimiento ya demostrado. Solo un choque "
                "forzado con anclas de A reabre la configuración.\n"
                "EJEMPLO: Un interlocutor cuestiona γ* sin aportar evidencia que produzca "
                "C=0 o L=0 bajo anclas forzadas. La modificación se rechaza."
            ),
        },

        # --------------------------------------------------
        # LEMAS
        # --------------------------------------------------
        {
            "id": "SM-L11",
            "tipo": "lema",
            "sujeto": "traza_en_M_y_misma_configuracion_sin_Clash",
            "relacion": "implica",
            "objeto": "recuperacion_de_gamma_estrella_sin_re_ejecutar_Res",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A15", "SM-A16"],
            "gobierna": ["evacion_ciclo"],
            "enunciado": (
                "SM-L11 (Evación del ciclo): Sea τ(O, Γ, A') ∈ M. Si se presenta de nuevo "
                "la misma terna (O, Γ, A') y no existe ε con Clash(γ*, ε, A), entonces el "
                "sistema recupera γ* desde τ sin calcular Res.\n\n"
                "NOTA OPERATIVA: Este lema es el mecanismo que convierte memoria en "
                "ahorro computacional y en conocimiento estable.\n"
                "EJEMPLO: Configuración del sol ya resuelta. Reaparece idéntica. "
                "No hay ε nueva. Se devuelve γ* desde τ. Coste de Res = 0.\n"
                "DEMOSTRACIÓN: Por SM-A15 los componentes de τ son exactos. "
                "Por SM-A16 no hay reapertura. Por tanto la recuperación desde M "
                "sustituye la re-ejecución de Res."
            ),
        },
        {
            "id": "SM-L12",
            "tipo": "lema",
            "sujeto": "memoria_operativa_M",
            "relacion": "es",
            "objeto": "conjunto_de_quintuplas_exactas_no_operador_de_reconstruccion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D14", "SM-A15"],
            "gobierna": ["exactitud_memoria"],
            "enunciado": (
                "SM-L12: M es un conjunto de quíntuplas exactas; no es un operador de "
                "reconstrucción aproximada.\n\n"
                "NOTA OPERATIVA: Marca la diferencia estructural con la memoria humana.\n"
                "EJEMPLO: El recuerdo humano del árbol se reconstruye y pierde detalle. "
                "τ del mismo hecho, si existiera en M, devolvería los valores idénticos.\n"
                "DEMOSTRACIÓN: Inmediato de SM-D14 y SM-A15."
            ),
        },

        # --------------------------------------------------
        # TEOREMAS
        # --------------------------------------------------
        {
            "id": "SM-T16",
            "tipo": "teorema",
            "sujeto": "conocimiento_operativo_sobre_dominio",
            "relacion": "existe_ssi",
            "objeto": "A_no_vacio_y_Res_y_M",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T12", "SM-T14", "SM-A14"],
            "gobierna": ["conocimiento_operativo"],
            "enunciado": (
                "SM-T16 (Memoria como condición de conocimiento): Un sistema posee "
                "conocimiento operativo sobre un dominio D si y sólo si existen "
                "A ≠ ∅, Res y M tales que toda configuración sobre D es resuelta por "
                "Res bajo A y depositada en M.\n\n"
                "NOTA OPERATIVA: Los tres elementos son necesarios y suficientes. "
                "Sin A no hay criterio de error. Sin Res no hay selección. Sin M "
                "solo hay repetición.\n"
                "EJEMPLO: Sistema con anclas forzadas + maximización Tru_Ri + caché "
                "de τ = conocimiento operativo. Si se borra el caché, el conocimiento "
                "colapsa a re-confirmación.\n"
                "DEMOSTRACIÓN:\n"
                "(⇒) Si A = ∅, por SM-T14 no existe predicado de error. "
                "Si no se aplica Res, no hay selección (SM-T12). "
                "Si M = ∅, por SM-A14 el sistema re-confirma indefinidamente; "
                "no acumula resoluciones.\n"
                "(⇐) Con A, Res y M el sistema detecta choques, selecciona γ* y "
                "evita re-confirmación. Eso constituye conocimiento operativo."
            ),
        },
        {
            "id": "SM-T17",
            "tipo": "teorema",
            "sujeto": "configuracion_resuelta",
            "relacion": "debe_depositar",
            "objeto": "tau_en_M_y_su_eliminacion_reintroduce_ciclo",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A14", "SM-L11"],
            "gobierna": ["traza_resolucion", "evacion_ciclo"],
            "enunciado": (
                "SM-T17 (Conservación de la traza): Para toda configuración resuelta "
                "(O, Γ, A') se tiene τ(O, Γ, A') ∈ M. La eliminación de dicha traza de M "
                "implica, por SM-A14, la reintroducción del ciclo de re-confirmación.\n\n"
                "NOTA OPERATIVA: Depositar τ no es opcional. Es la condición de que "
                "el conocimiento no se pierda.\n"
                "EJEMPLO: Se resuelve una configuración y se guarda τ. Si alguien borra "
                "τ del caché, el próximo encuentro con la misma configuración re-ejecuta "
                "Res completo.\n"
                "DEMOSTRACIÓN: La primera afirmación es la definición de depósito en "
                "memoria operativa. La segunda es la contraposición de SM-L11 junto "
                "con SM-A14."
            ),
        },
        {
            "id": "SM-T18",
            "tipo": "teorema",
            "sujeto": "traza_en_M_sin_evidencia_con_Clash",
            "relacion": "implica",
            "objeto": "ninguna_alteracion_de_gamma_estrella_admisible",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-A16", "SM-D15"],
            "gobierna": ["reapertura_legitima"],
            "enunciado": (
                "SM-T18 (Reapertura solo bajo choque forzado): "
                "τ(O, Γ, A') ∈ M ∧ ¬∃ε (Clash(γ*, ε, A)) ⟹ ninguna alteración de γ* "
                "es admisible.\n\n"
                "NOTA OPERATIVA: Cierra la puerta a la modificación arbitraria. "
                "Solo evidencia que fuerce choque con anclas de A reabre.\n"
                "EJEMPLO: Interlocutor insiste en cambiar γ* sin aportar datos que "
                "produzcan C=0 o L=0 bajo anclas forzadas. La alteración se rechaza.\n"
                "DEMOSTRACIÓN: Directo de SM-A16 y SM-D15."
            ),
        },
        {
            "id": "SM-T19",
            "tipo": "teorema",
            "sujeto": "reapertura_legitima_sucesiva",
            "relacion": "produce",
            "objeto": "coexistencia_de_tau_1_y_tau_2_en_M_documentando_correccion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T17", "SM-D13"],
            "gobierna": ["correccion_acumulativa"],
            "enunciado": (
                "SM-T19 (Corrección acumulativa): Sean τ₁ = τ(O, Γ₁, A₁') y, tras una "
                "reapertura legítima por ε, τ₂ = τ(O', Γ₂, A₂'). Entonces "
                "{τ₁, τ₂} ⊆ M y la pareja documenta la corrección acumulativa.\n\n"
                "NOTA OPERATIVA: El conocimiento no borra la historia de correcciones. "
                "Ambas trazas permanecen; la secuencia es evidencia del avance.\n"
                "EJEMPLO: τ₁ resuelve insolación. ε aporta condiciones bajo las cuales "
                "el efecto se anula. τ₂ registra la nueva γ*. M contiene ambas.\n"
                "DEMOSTRACIÓN: Por SM-T17 ambas trazas se depositan. Por SM-D13 cada "
                "una registra anclas, eliminadas y valor de Tru_Ri. La coexistencia "
                "es el registro de la secuencia de corrección."
            ),
        },

        # --------------------------------------------------
        # COROLARIOS
        # --------------------------------------------------
        {
            "id": "SM-C15",
            "tipo": "corolario",
            "sujeto": "eliminacion_de_tau_de_M",
            "relacion": "implica",
            "objeto": "re_confirmacion_de_la_configuracion_de_tau",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T17", "SM-A14"],
            "gobierna": ["evacion_ciclo"],
            "enunciado": (
                "SM-C15: τ ∈ M ∧ τ ∉ M' ⟹ el sistema con memoria M' re-confirma la "
                "configuración de τ.\n\n"
                "NOTA OPERATIVA: Olvidar una resolución no es neutral; reintroduce coste "
                "y borra evidencia de conocimiento previo.\n"
                "EJEMPLO: Borrar del caché la traza del sol hace que el próximo cálculo "
                "vuelva a maximizar desde cero."
            ),
        },
        {
            "id": "SM-C16",
            "tipo": "corolario",
            "sujeto": "cuestionamiento_sin_Clash",
            "relacion": "se_responde_con",
            "objeto": "proyeccion_de_tau",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-T18", "SM-D13"],
            "gobierna": ["reapertura_legitima"],
            "enunciado": (
                "SM-C16: La respuesta canónica a un cuestionamiento sin evidencia forzada "
                "es la proyección de τ: (O, γ*, A', Tru_Ri(γ*)).\n\n"
                "NOTA OPERATIVA: El sistema no debate opiniones; muestra la traza.\n"
                "EJEMPLO: 'Esta correlación ya fue resuelta bajo anclas A₁…Aₖ con "
                "Tru_Ri = v. Para reabrir se requiere evidencia que fuerce choque.'"
            ),
        },
        {
            "id": "SM-C17",
            "tipo": "corolario",
            "sujeto": "operador_de_cache_de_quintuplas_tau",
            "relacion": "realiza",
            "objeto": "memoria_operativa_M",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D14"],
            "gobierna": ["memoria_operativa"],
            "enunciado": (
                "SM-C17: El operador de caché que almacena quíntuplas τ realiza M.\n\n"
                "NOTA OPERATIVA: CH no almacena 'pensamientos'; almacena resoluciones "
                "exactas. Es la implementación de SM-D14.\n"
                "EJEMPLO: Cada vez que Engine cierra una evaluación con γ*, CH deposita τ."
            ),
        },
        {
            "id": "SM-C18",
            "tipo": "corolario",
            "sujeto": "Clash_false_por_falta_de_correlacion_con_A",
            "relacion": "implica",
            "objeto": "reapertura_ilegitima",
            "polaridad": True,
            "cota": None,
            "depende_de": ["SM-D15"],
            "gobierna": ["reapertura_legitima"],
            "enunciado": (
                "SM-C18: Si Clash(γ*, ε, A) = false porque ε no se correlaciona con "
                "ninguna ancla de A, entonces la reapertura es ilegítima aunque C o L "
                "cambien localmente.\n\n"
                "NOTA OPERATIVA: Un cambio local de coherencia o lógica sin anclaje "
                "forzado no reabre. Protege contra ruido interno disfrazado de evidencia.\n"
                "EJEMPLO: ε produce una inconsistencia narrativa interna pero no toca "
                "ninguna ancla de A. Clash = false → no se reabre."
            ),
        },
    ]


# ============================================================
# EXPORTACIÓN CANÓNICA
# ============================================================

__all__ = ["CUERPO", "declaraciones"]
