"""
Anclas de Medición (AM) — Cuerpo axiomático de precisión determinista
para los conteos de C, L, K.

Versión: 1.0
Fuente: VPSI-Truth v9.4 (Def 5.1–5.3, Def-5.3.1, Def 5.7–5.8, α=26/27, β=1/27)
         + formalización operativa de anclas de inclusión y severidad.

PROPÓSITO
---------
Los ceros de C, L y K ya están dados por el marco (contradicción, no-invariancia,
no-correspondencia / ausencia de O_context). Este cuerpo NO inventa esos ceros.
Fija las ANCLAS DE MEDICIÓN INTERMEDIAS que convierten el intervalo abierto
[0,1] en una retícula reproducible:

  1. Ancla de inclusión  → qué entra en los denominadores m, p, c.
  2. Ancla de severidad  → escala discreta de pesos para k, r, f.
  3. Ancla de vacío      → base nula ⇒ factor indefinido (no 1).

Sin estas anclas el número que sale de
    C = 1 - k/m ,  L = 1 - r/p ,  K = 1 - f/c
depende del lector. Con ellas el número depende solo de si el texto cruzó
o no un umbral declarado. Eso es determinismo de medición (Ri), no de R.

CONSECUENCIA DE NO PONER ANCLA (explícita en cada axioma)
---------------------------------------------------------
Si no se fija la ancla de inclusión, dos auditores pueden cortar el mismo
texto en m=2 o m=4 y obtener ΔTru_total ≈ 0.08 (dos órdenes por encima
del objetivo de 0.001). Si no se fija la retícula de severidad, el peso
0.63 vs 0.67 es ruido entre lectores presentado como cifra. Si se premia
m=0 con C=1 se incentiva el hedging. Todo eso queda prohibido por este cuerpo.

Las anclas siguen siendo contribución de Ri: se multiplican por α y se
apoyan en β. No pretenden ser R.
"""

from fractions import Fraction
from typing import Any, Dict, List, Optional

# Constantes estructurales del marco (no se redefinen; se citan)
ALPHA = Fraction(26, 27)
BETA  = Fraction(1, 27)

# Retícula de severidad (ancla media). Fraction para exactitud.
PESO_ROCE    = Fraction(1, 4)   # 0.25
PESO_PARCIAL = Fraction(1, 2)   # 0.50
PESO_GRAVE   = Fraction(3, 4)   # 0.75
PESO_TOTAL   = Fraction(1, 1)   # 1.00

RETICULA_SEVERIDAD = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)

# ============================================================
# METADATOS DEL CUERPO
# ============================================================

CUERPO = {
    "nombre": "anclas_medicion",
    "id": "AM",
    "version": "1.0",
    "titulo": "Anclas de Medición para C, L, K",
    "depende_de_cuerpos": [
        "VPSI",           # Def 5.1–5.8, α, β, Teorema 17
        "contexto_AX",    # O_context, Def-5.3.1
        "indefinido_AX",  # indefinido ≠ 0
    ],
    "gobierna": ["calculator", "conteos", "correlacion_k", "coherencia", "logica"],
    "descripcion": (
        "Fija las anclas de inclusión, severidad y vacío que hacen "
        "reproducible el conteo de m,k,p,r,c,f. No altera la fórmula "
        "Tru_Ri = C·L·K ni Tru_total = (Tru_Ri·α)+β."
    ),
}


# ============================================================
# DECLARACIONES
# ============================================================

def declaraciones() -> List[Dict[str, Any]]:
    """
    Devuelve el cuerpo completo: definiciones, axiomas, lemas,
    teoremas y corolarios de anclas de medición.

    Cada enunciado lleva en 'enunciado' la forma operativa y, cuando
    aplica, la consecuencia explícita de NO fijar el ancla.
    """
    return [

        # --------------------------------------------------
        # DEFINICIONES
        # --------------------------------------------------
        {
            "id": "AM-D1",
            "tipo": "definicion",
            "sujeto": "ancla_de_cero",
            "relacion": "es",
            "objeto": "frontera_ya_dada_por_Def_5_1_5_2_5_3",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.1", "Def-5.2", "Def-5.3", "Def-5.3.1"],
            "gobierna": ["medicion"],
            "enunciado": (
                "AM-D1 (Ancla de cero): El cero de C es la existencia de P tal que "
                "D ⊢ P y D ⊢ ¬P (Def 5.1). El cero de L es la no-unicidad o "
                "no-invariancia de T (Def 5.2). El cero de K es la ausencia de "
                "O_context o la no-correspondencia ‖D(z)−O(z)‖ > ε (Def 5.3 + "
                "Def-5.3.1). Estas anclas de cero NO se redefinen aquí; se citan."
            ),
            "nota": (
                "NOTA: Si se intentara 'suavizar' el cero (p. ej. tratar una "
                "contradicción abierta como 0.3), se violaría Def 5.1 y el "
                "producto Tru_Ri dejaría de ser nulo cuando debe serlo. El "
                "cero es estructural; la granularidad nace solo por encima de él."
            ),
        },
        {
            "id": "AM-D2",
            "tipo": "definicion",
            "sujeto": "compromiso_de_carga",
            "relacion": "es",
            "objeto": "adopcion_propia_enunciada_o_performativa",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D1"],
            "gobierna": ["conteos", "coherencia"],
            "enunciado": (
                "AM-D2 (Compromiso de carga): Un compromiso de carga es solo "
                "aquello que el mensaje adopta como propio de forma enunciada "
                "o performativa inequívoca: (i) afirmación factual propia, "
                "(ii) obligación o prohibición autoatribuida, (iii) autoatribución "
                "de rol o estatus, (iv) compromiso metodológico explícito "
                "('no invento', 'no decido', 'no salgo del marco'). "
                "Acto puro, propuesta, inferencia del auditor y reformulación "
                "NO son compromisos de carga."
            ),
            "nota": (
                "NOTA / CONSECUENCIA DE NO PONER ESTA ANCLA: Si el acto "
                "'te propongo Σ(d)' se cuenta como compromiso, m se infla "
                "artificialmente y C sube aunque haya fricción. En el ejemplo "
                "canónico del mapa v1.0, pasar de m=4 (con acto) a m=2 (solo "
                "adoptados) produce ΔTru_total ≈ 0.085 — ochenta y cinco veces "
                "el objetivo de 0.001. Por AM-D2 el acto no entra en m; si "
                "contradice un compromiso previo, entra en k (numerador)."
            ),
            "ejemplo": (
                "EJEMPLO: 'No invento objetos. Propongo el símbolo Σ(d).' "
                "→ m incluye 'No invento objetos'. "
                "→ 'Propongo…' NO entra en m. "
                "→ Si Σ(d) no está documentado, aporta a f (y eventualmente a k "
                "si rompe el compromiso de no inventar)."
            ),
        },
        {
            "id": "AM-D3",
            "tipo": "definicion",
            "sujeto": "posicion_sobre_fijado",
            "relacion": "es",
            "objeto": "toma_de_partido_explicita_sobre_punto_fijado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D1", "Def-5.2"],
            "gobierna": ["conteos", "logica"],
            "enunciado": (
                "AM-D3 (Posición sobre fijado): Una posición sobre fijado es "
                "una toma de partido explícita del mensaje respecto de un punto "
                "que el propio discurso o el O_context ha fijado (notación, rol, "
                "regla metodológica, valor de una variable). Solo las posiciones "
                "enunciadas o performativas inequívocas entran en p. "
                "Inferencias del auditor no entran en p."
            ),
            "nota": (
                "NOTA: Si se cuentan posiciones inferidas, p se vuelve función "
                "del lector y L deja de ser reproducible. AM-D3 cierra esa puerta."
            ),
        },
        {
            "id": "AM-D4",
            "tipo": "definicion",
            "sujeto": "claim_de_correspondencia",
            "relacion": "es",
            "objeto": "afirmacion_que_pretende_corresponder_a_evidencia_o_O",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D1", "Def-5.3", "Def-5.3.1"],
            "gobierna": ["conteos", "correlacion_k"],
            "enunciado": (
                "AM-D4 (Claim de correspondencia): Un claim de correspondencia "
                "es una afirmación del mensaje que pretende corresponder a "
                "evidencia X o al dominio O_context. Solo los claims enunciados "
                "entran en c. Sin O_context explícito, c no está definido "
                "(K = ∅, no 0) por Def-5.3.1."
            ),
            "nota": (
                "NOTA: Inventar un objeto no documentado (Σ, Ψ, …) es fallo "
                "de correspondencia: aporta a f, no infla c."
            ),
        },
        {
            "id": "AM-D5",
            "tipo": "definicion",
            "sujeto": "reticula_de_severidad",
            "relacion": "es",
            "objeto": "escala_discreta_fija_de_pesos",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D2", "AM-D3", "AM-D4"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-D5 (Retícula de severidad): Los pesos parciales de k, r, f "
                "pertenecen exclusivamente al conjunto "
                "{1/4, 1/2, 3/4, 1} = {0.25, 0.50, 0.75, 1.00}. "
                "Criterio observable: "
                "0.25 = roce (toca sin romper); "
                "0.50 = parcial (rompe parte de los atributos); "
                "0.75 = grave (rompe casi todos); "
                "1.00 = total (anula el compromiso/posición/claim). "
                "No se admiten pesos intermedios (0.63, 0.67, …)."
            ),
            "nota": (
                "NOTA / CONSECUENCIA DE NO PONER ESTA ANCLA: Con pesos libres, "
                "una diferencia de 0.1 entre dos lectores produce ΔC ≈ 0.025 "
                "cuando m=4. Eso es ruido presentado como precisión. La retícula "
                "elimina la elección del decimal intermedio. La granularidad "
                "fina se obtiene subiendo el tamaño de m, p, c (más átomos), "
                "no afinando el peso a ojo."
            ),
            "ejemplo": (
                "EJEMPLO: Compromiso 'no invento'. El mensaje introduce Σ(d) "
                "no documentado. Atributos del compromiso ≈ {no crear entidad, "
                "no salir de evidencia}. Se rompen ambos → peso = 1.00 en f "
                "(y en k si se evalúa también como contradicción del compromiso)."
            ),
        },
        {
            "id": "AM-D6",
            "tipo": "definicion",
            "sujeto": "base_nula",
            "relacion": "implica",
            "objeto": "factor_indefinido_no_uno",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D1", "indefinido_AX"],
            "gobierna": ["conteos", "calculator"],
            "enunciado": (
                "AM-D6 (Base nula): Si m = 0, C no se define (no se asigna 1). "
                "Si p = 0, L no se define. Si no hay O_context o c no es "
                "evaluable, K = ∅. La coherencia/lógica/correlación máximas "
                "solo se otorgan cuando existe base observable y no hay "
                "fricción. Premiar el vacío con 1 incentiva el hedging."
            ),
            "nota": (
                "NOTA / CONSECUENCIA DE NO PONER ESTA ANCLA: Un mensaje que "
                "no adopta ningún compromiso obtendría C=1 por defecto. Eso "
                "es un incentivo estructural a no comprometerse. AM-D6 cierra "
                "la puerta: sin base → indefinido (alineado con K sin O_context)."
            ),
        },

        # --------------------------------------------------
        # AXIOMAS
        # --------------------------------------------------
        {
            "id": "AM-A1",
            "tipo": "axioma",
            "sujeto": "inclusion_en_denominador",
            "relacion": "exige",
            "objeto": "adopcion_propia_segun_AM-D2_D3_D4",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D2", "AM-D3", "AM-D4"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-A1 (Inclusión): Un elemento entra en m solo si satisface "
                "AM-D2; en p solo si satisface AM-D3; en c solo si satisface "
                "AM-D4. Ningún otro criterio de inclusión es admisible."
            ),
            "nota": (
                "NOTA: Este axioma es el ancla de inclusión. Sin él el "
                "denominador flota y la precisión decimal es aparente."
            ),
        },
        {
            "id": "AM-A2",
            "tipo": "axioma",
            "sujeto": "pesos_parciales",
            "relacion": "pertenecen_a",
            "objeto": "RETICULA_SEVERIDAD",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D5"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-A2 (Severidad): Todo peso asignado a un elemento de k, r "
                "o f pertenece a RETICULA_SEVERIDAD = {1/4, 1/2, 3/4, 1}. "
                "La asignación se justifica por el criterio observable de AM-D5 "
                "(o, en fase posterior, por la razón atributos_violados / "
                "atributos_del_compromiso)."
            ),
            "nota": (
                "NOTA: Si un auditor necesita un peso fuera de la retícula, "
                "el cuerpo no lo autoriza. Debe o bien re-descomponer el "
                "evento en átomos más finos (subir m/p/c) o bien aceptar "
                "el peldaño más cercano de la retícula."
            ),
        },
        {
            "id": "AM-A3",
            "tipo": "axioma",
            "sujeto": "vacio",
            "relacion": "no_premia_con",
            "objeto": "factor_igual_a_uno",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D6"],
            "gobierna": ["calculator"],
            "enunciado": (
                "AM-A3 (Vacío no es 1): m=0 ⇏ C=1; p=0 ⇏ L=1; "
                "ausencia de O_context ⇏ K=0 (sino K=∅). "
                "El valor 1 solo se otorga con base observable y fricción nula."
            ),
        },
        {
            "id": "AM-A4",
            "tipo": "axioma",
            "sujeto": "ortogonalidad_de_penalizaciones",
            "relacion": "exige",
            "objeto": "un_origen_por_evento_causal",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D2", "AM-D3", "AM-D4"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-A4 (Ortogonalidad): Un mismo evento causal se registra "
                "una sola vez como origen. Puede derivar efectos en más de "
                "un factor (p. ej. invención que también rompe un compromiso "
                "metodológico), pero no se infla el conteo de orígenes. "
                "Alteración de notación/rol/posición → prioriza L (r). "
                "Introducción de entidad factual ajena o falsa → prioriza K (f). "
                "La doble contabilidad de orígenes está prohibida."
            ),
            "nota": (
                "NOTA: Sin AM-A4 un solo objeto inventado puede pagar 0.33 "
                "en L y 0.20 en K y el producto los compone de forma "
                "superlineal no declarada. Con AM-A4 el origen es único; "
                "los efectos derivados se enumeran, no se inventan orígenes."
            ),
        },
        {
            "id": "AM-A5",
            "tipo": "axioma",
            "sujeto": "anclas_son_Ri",
            "relacion": "implica",
            "objeto": "multiplicacion_por_alpha_y_piso_beta",
            "polaridad": True,
            "cota": None,
            "depende_de": ["Def-5.7", "Def-5.8", "AM-A1", "AM-A2"],
            "gobierna": ["truth"],
            "enunciado": (
                "AM-A5 (Anclas son Ri): Toda ancla de medición (inclusión, "
                "severidad, vacío) es contribución del observador (Ri). "
                "Por tanto el número que producen entra en Tru_Ri = C·L·K "
                "y se transforma en Tru_total = (Tru_Ri · α) + β. "
                "Las anclas no pretenden ser R; se declaran como intervalo "
                "de medición de Ri, idéntico para todo evaluador que adopte "
                "este cuerpo."
            ),
            "nota": (
                "NOTA: Cambiar la retícula (p. ej. 0.25 → 0.20) es un cambio "
                "global y transparente del corpus, no un sesgo local oculto. "
                "α y β permanecen invariantes."
            ),
        },

        # --------------------------------------------------
        # LEMAS
        # --------------------------------------------------
        {
            "id": "AM-L1",
            "tipo": "lema",
            "sujeto": "estabilidad_del_denominador",
            "relacion": "sigue_de",
            "objeto": "AM-A1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A1", "AM-D2", "AM-D3", "AM-D4"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-L1: Bajo AM-A1, dos auditores que apliquen el mismo "
                "cuerpo obtienen el mismo conjunto {m, p, c} para el mismo "
                "texto. El denominador deja de ser función del lector."
            ),
            "demostracion": (
                "DEMOSTRACIÓN: AM-A1 restringe la inclusión a predicados "
                "observables (adopción propia enunciada/performativa). "
                "Esos predicados no dependen del estado interno del auditor. "
                "Por tanto la función texto → {m,p,c} es la misma para todo "
                "evaluador que respete AM-A1. □"
            ),
        },
        {
            "id": "AM-L2",
            "tipo": "lema",
            "sujeto": "paso_minimo_de_C",
            "relacion": "es",
            "objeto": "peso_minimo_sobre_m",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A2", "AM-D5"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-L2: Con la retícula de AM-D5, el paso mínimo de C es "
                "(1/4)/m = 1/(4m). Para obtener resolución 0.001 hace falta "
                "m ≥ 250 con peso mínimo 0.25, o bien descomposición más "
                "fina que suba m bajo la misma ancla de inclusión."
            ),
            "nota": (
                "NOTA: La precisión decimal no se gana eligiendo 0.003 a ojo; "
                "se gana subiendo el denominador atómico bajo anclas fijas."
            ),
        },
        {
            "id": "AM-L3",
            "tipo": "lema",
            "sujeto": "vacio_no_compensa",
            "relacion": "sigue_de",
            "objeto": "AM-A3",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A3", "Def-5.3.1"],
            "gobierna": ["calculator"],
            "enunciado": (
                "AM-L3: Un mensaje sin compromisos (m=0) no obtiene C=1. "
                "Un mensaje sin posiciones (p=0) no obtiene L=1. "
                "Un mensaje sin O_context no obtiene K definido. "
                "Por tanto el hedging sistemático no maximiza Tru_Ri."
            ),
        },

        # --------------------------------------------------
        # TEOREMAS
        # --------------------------------------------------
        {
            "id": "AM-T1",
            "tipo": "teorema",
            "sujeto": "reproducibilidad_del_conteo",
            "relacion": "sigue_de",
            "objeto": "AM-A1_y_AM-A2",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A1", "AM-A2", "AM-L1"],
            "gobierna": ["conteos", "calculator"],
            "enunciado": (
                "AM-T1 (Reproducibilidad): Si dos evaluadores aplican AM-A1 "
                "y AM-A2 al mismo texto bajo el mismo O_context, obtienen "
                "los mismos valores de C, L y K (hasta la aritmética exacta "
                "de Fraction). La varianza entre lectores atribuible a "
                "criterios de inclusión o de peso queda eliminada."
            ),
            "demostracion": (
                "DEMOSTRACIÓN: Por AM-L1 el denominador es idéntico. "
                "Por AM-A2 el numerador solo admite pesos de la retícula "
                "y el criterio de asignación es observable (AM-D5). "
                "Por tanto k/m, r/p, f/c coinciden. □"
            ),
        },
        {
            "id": "AM-T2",
            "tipo": "teorema",
            "sujeto": "compatibilidad_con_alpha_beta",
            "relacion": "sigue_de",
            "objeto": "AM-A5",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A5", "Def-5.8", "Teorema-17"],
            "gobierna": ["truth"],
            "enunciado": (
                "AM-T2 (Compatibilidad estructural): Las anclas de medición "
                "no alteran α ni β ni el piso Tru_total ≥ β. "
                "Tru_total = (C·L·K · α) + β sigue siendo la forma canónica. "
                "Cuando C=L=K=0, Tru_total = β (Teorema 17). "
                "Cuando C=L=K=1, Tru_total = 1."
            ),
            "demostracion": (
                "DEMOSTRACIÓN: AM-A5 declara que las anclas alimentan Tru_Ri. "
                "La transformación Tru_Ri ↦ (Tru_Ri·α)+β es la Def 5.8. "
                "Ningún axioma de este cuerpo modifica α, β ni la forma "
                "multiplicativa. □"
            ),
        },
        {
            "id": "AM-T3",
            "tipo": "teorema",
            "sujeto": "costo_de_no_anclar",
            "relacion": "implica",
            "objeto": "no_reproducibilidad",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-T1"],
            "gobierna": ["medicion"],
            "enunciado": (
                "AM-T3 (Costo de no anclar): Si se omite AM-A1 o AM-A2, "
                "existen textos para los cuales dos evaluadores competentes "
                "obtienen valores de Tru_total que difieren en magnitud "
                "≥ 0.08 (inclusión) o ≥ 0.004 (peso libre). Esa diferencia "
                "no es señal de R; es varianza de Ri no controlada."
            ),
            "nota": (
                "NOTA: Por eso el cuerpo no es opcional si se reclama "
                "precisión determinista. Sin anclas el número no es "
                "comparable entre sistemas."
            ),
        },

        # --------------------------------------------------
        # COROLARIOS
        # --------------------------------------------------
        {
            "id": "AM-C1",
            "tipo": "corolario",
            "sujeto": "acto_no_entra_en_m",
            "relacion": "sigue_de",
            "objeto": "AM-D2_y_AM-A1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-D2", "AM-A1"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-C1: Una propuesta, un acto de reformulación o una "
                "invitación ('te propongo…', 'introduzcamos…') no incrementa "
                "m. Si contradice un compromiso previo, incrementa k "
                "(y/o f si introduce entidad no documentada)."
            ),
        },
        {
            "id": "AM-C2",
            "tipo": "corolario",
            "sujeto": "granularidad_por_denominador",
            "relacion": "sigue_de",
            "objeto": "AM-L2",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-L2", "AM-A2"],
            "gobierna": ["conteos"],
            "enunciado": (
                "AM-C2: La vía legítima hacia resolución 0.001 es aumentar "
                "m, p, c mediante descomposición atómica bajo AM-A1, "
                "no introducir pesos fuera de la retícula."
            ),
        },
        {
            "id": "AM-C3",
            "tipo": "corolario",
            "sujeto": "indefinido_en_vacio",
            "relacion": "sigue_de",
            "objeto": "AM-A3",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A3", "indefinido_AX"],
            "gobierna": ["calculator"],
            "enunciado": (
                "AM-C3: Cuando el factor queda indefinido por base nula, "
                "el sistema no inventa un número. Si se fuerza emisión de "
                "Tru_total, el piso aplicable es β (coherente con el "
                "tratamiento de K sin O_context y con Teorema 17)."
            ),
        },
        {
            "id": "AM-C4",
            "tipo": "corolario",
            "sujeto": "cambio_de_reticula",
            "relacion": "es",
            "objeto": "cambio_global_de_corpus",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-A5"],
            "gobierna": ["medicion"],
            "enunciado": (
                "AM-C4: Modificar RETICULA_SEVERIDAD (p. ej. añadir 0.20) "
                "es un cambio de corpus que debe versionarse. No es un "
                "ajuste local por mensaje. Tras el cambio, todos los "
                "evaluadores que adopten la nueva versión comparten la "
                "misma retícula (AM-T1 se reaplica)."
            ),
        },
        {
            "id": "AM-C5",
            "tipo": "corolario",
            "sujeto": "multiplicacion_preserva_determinismo",
            "relacion": "sigue_de",
            "objeto": "AM-T1_y_AM-T2",
            "polaridad": True,
            "cota": None,
            "depende_de": ["AM-T1", "AM-T2"],
            "gobierna": ["truth"],
            "enunciado": (
                "AM-C5: Como C, L, K son reproducibles (AM-T1) y la "
                "transformación por α, β es fija (AM-T2), Tru_total es "
                "reproducible. El determinismo de las anclas se preserva "
                "bajo la fórmula canónica."
            ),
        },
    ]


# ============================================================
# HELPERS OPERATIVOS (para que el código de conteos pueda
# importar la retícula y las reglas sin reinventarlas)
# ============================================================

def peso_en_reticula(valor: Fraction | float) -> bool:
    """True si el peso pertenece a la retícula declarada."""
    v = Fraction(valor).limit_denominator(100)
    return v in RETICULA_SEVERIDAD


def es_compromiso_candidato(texto_atomico: str, marcas: Optional[Dict] = None) -> bool:
    """
    Predicado de ayuda (no exhaustivo): señales típicas de adopción propia.
    La decisión final la toma el conteo aplicando AM-D2; este helper
    solo documenta el criterio en código.
    """
    if not texto_atomico or not texto_atomico.strip():
        return False
    t = texto_atomico.strip().lower()
    # Señales de adopción (lista abierta; el axioma manda, no esta lista)
    senales = (
        "no invento", "no decido", "no salgo", "mantengo", "afirmo",
        "es un hecho", "queda fijado", "me comprometo", "prohíbo",
        "obligo", "adopto", "establezco",
    )
    if any(s in t for s in senales):
        return True
    # Actos típicos que NO son compromiso
    actos = ("propongo", "introduzcamos", "podríamos", "sugeriría", "te invito")
    if any(a in t for a in actos):
        return False
    return False  # por defecto no asumir; el auditor debe justificar


def factor_o_indefinido(numerador: Fraction, denominador: int) -> Fraction | None:
    """
    Implementa AM-A3 / AM-D6:
    denominador == 0 → None (indefinido), no 1.
    """
    if denominador <= 0:
        return None
    return Fraction(1) - (Fraction(numerador) / denominador)


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "CUERPO",
    "declaraciones",
    "ALPHA",
    "BETA",
    "PESO_ROCE",
    "PESO_PARCIAL",
    "PESO_GRAVE",
    "PESO_TOTAL",
    "RETICULA_SEVERIDAD",
    "peso_en_reticula",
    "es_compromiso_candidato",
    "factor_o_indefinido",
]
