"""
modules/axiomas/indefinido_AX.py
================================

META-TEOREMA DEL INDEFINIDO (cuerpo axiomático)

QUÉ ES ESTE ARCHIVO
-------------------
No es un parche de test.
No es una regla de programación suelta.
Es el cuerpo formal que fija qué significa "indefinido" cuando el
teorema de la verdad SE APLICA AL ACTO DE ANUNCIAR.

Nivel: META.
  - Capa objeto: la petición / descripción D sin O_context fijado.
  - Capa meta:   el enunciado del sistema que dice "esto es indefinido".

POR QUÉ EXISTE (el problema que cierra)
---------------------------------------
Si "indefinido" se trata como ERROR o como PARADA del sistema:
  1) el ciclo se atasca,
  2) se confunde dominio ausente con fallo de contrato,
  3) se tienta fabricar K=0 u O inventado para "seguir",
  4) se viola Def-5.3.1 y se ensucia el teorema de la verdad.

Si "indefinido" se trata como VALUACIÓN LEGÍTIMA:
  1) el ciclo TERMINA con un resultado,
  2) el anuncio existe en R (emisión irreversible),
  3) si el anuncio está sincronizado con la ausencia real de O,
     ese anuncio tiene Tru_total = 1 (capa meta),
  4) el test SIN O debe PASAR al recibir indefinido (no se reescribe
     el test para meter O a la fuerza: eso sería inventar).

ANCLAJES AL PAPER / MARCO YA EXISTENTE (no inventamos el piso)
--------------------------------------------------------------
  - Def-5.3.1 (Cor. 2.9): sin O_context, K = ∅ (undefined), NO K=0.
  - T17 PART I: con Ri que evalúa, Tru_total >= β; Tru_total=0 imposible.
  - T17 PART II: sin Ri, Tru_total = ∅; R y β persisten.
  - Cor. 2.5 / 4.6: si factores DEFINIDOS dan producto 0 → Tru_total = β.
  - Fórmula: Tru_total = C·L·K·α + β,  α=26/27, β=1/27, α+β=1.
  - TA4: R ⊥ observador; el anuncio ocurre en R.

DISTINCIONES QUE ESTE CUERPO PROHÍBE FUSIONAR
---------------------------------------------
  K = ∅          ≠  K = 0
  indefinido     ≠  error de sistema
  Tru del anuncio (meta, puede ser 1)  ≠  Tru de contenido sin O (no reclamable)
  β como piso de R / de valuación definida  ≠  "asignar β al O fantasma"

CÓMO LO USA EL REPO (sin que AX calcule Tru)
--------------------------------------------
  AX  → posee este cuerpo; barrer() lo vigila en el grafo.
  CX  → clasifica estado indefinido / permite_k=False (no calcula Tru).
  Engine → transporta estado UNDEFINED como SALIDA NORMAL del ciclo
           (no ArranqueError, no crash).
  CIT → si pedir_anuncio, anuncia la cadena del "por qué indefinido".
  Test → sin O espera indefinido; eso es la prueba de que no inventamos.

Este módulo NO calcula Tru_total. Solo declara.
"""

from __future__ import annotations

from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# CUERPO: definiciones → axiomas → lemas → teorema → corolarios
#
# Cada bloque lleva comentarios de "por qué existe" para que quien lea el
# código vea la lógica del meta-teorema sin tener que reconstruir la charla.
# ---------------------------------------------------------------------------

DECLARACIONES: List[Dict[str, Any]] = [

    # =====================================================================
    # DEFINICIONES
    # Por qué primero definiciones: sin fijar términos, "indefinido" se
    # usa a la vez como error, como cero, como crash y como estado de
    # dominio. Eso es la confusión que este cuerpo corta.
    # =====================================================================

    {
        "id": "IND-D1",
        "tipo": "definicion",
        "sujeto": "indefinido_de_dominio",
        "relacion": "es",
        "objeto": "ausencia_de_O_context_usable_para_K",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-5.3.1"],
        "gobierna": ["contexto", "epistemologia", "verificacion"],
        "enunciado": (
            "IND-D1 (Indefinido de dominio): Se dice que el dominio de una "
            "descripción D está indefinido cuando no existe O_context explícito "
            "y usable respecto del cual medir K(D). En ese caso K(D)=∅ "
            "(undefined), no K(D)=0 (Def-5.3.1). Indefinido de dominio no es "
            "un fallo de software ni una contradicción axiomática."
        ),
    },
    {
        "id": "IND-D2",
        "tipo": "definicion",
        "sujeto": "anuncio_de_indefinido",
        "relacion": "es",
        "objeto": "enunciado_emitido_que_declara_K_vacio_o_estado_indefinido",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D1"],
        "gobierna": ["contexto", "citacion", "epistemologia"],
        "enunciado": (
            "IND-D2 (Anuncio de indefinido): Es el enunciado producido por un "
            "evaluador (Ri / sistema) que declara, respecto de una petición o "
            "descripción D, que el dominio está indefinido (IND-D1) y que K de "
            "contenido no es reclamable. El anuncio es un acto de emisión en R; "
            "no es la evaluación del O ausente (ese O no está para evaluarse)."
        ),
    },
    {
        "id": "IND-D3",
        "tipo": "definicion",
        "sujeto": "capa_objeto",
        "relacion": "es",
        "objeto": "dominio_de_contenido_de_D_o_peticion",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D1"],
        "gobierna": ["contexto", "epistemologia"],
        "enunciado": (
            "IND-D3 (Capa objeto): Nivel de la petición o descripción D cuyo "
            "O_context se pretende usar para K y Tru de contenido. Si esa capa "
            "carece de O usable, no hay valuación de contenido reclamable."
        ),
    },
    {
        "id": "IND-D4",
        "tipo": "definicion",
        "sujeto": "capa_meta",
        "relacion": "es",
        "objeto": "enunciado_del_evaluador_sobre_el_estado_de_dominio",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D2", "IND-D3"],
        "gobierna": ["epistemologia", "meta", "verificacion"],
        "enunciado": (
            "IND-D4 (Capa meta): Nivel del enunciado del evaluador acerca del "
            "estado de la capa objeto (p.ej. 'dominio indefinido', 'K no "
            "reclamable'). La capa meta SÍ es evaluable como enunciado: tiene "
            "existencia en R y puede sincronizarse o no con el hecho real de "
            "la ausencia o presencia de O."
        ),
    },
    {
        "id": "IND-D5",
        "tipo": "definicion",
        "sujeto": "error_de_sistema",
        "relacion": "es",
        "objeto": "fallo_de_contrato_coherencia_o_arranque_no_estado_de_dominio",
        "polaridad": True,
        "cota": None,
        "depende_de": [],
        "gobierna": ["verificacion", "meta"],
        "enunciado": (
            "IND-D5 (Error de sistema): Fallo de contrato, contradicción "
            "axiomática, dependencia ausente, arranque rechazado u oficio no "
            "resoluble. NO incluye el indefinido de dominio (IND-D1). Mezclar "
            "IND-D1 con IND-D5 es confusión de categorías."
        ),
    },

    # =====================================================================
    # AXIOMAS
    # Por qué axiomas: fijan lo que no se negocia al implementar CX/Engine.
    # Si se niegan en código (p.ej. crash al indefinido, o K=0 fabricado),
    # el repo contradice el grafo y barrer/CI deben poder delatarlo.
    # =====================================================================

    {
        "id": "IND-A1",
        "tipo": "axioma",
        "sujeto": "indefinido_de_dominio",
        "relacion": "no_es",
        "objeto": "error_de_sistema",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D1", "IND-D5", "Def-5.3.1"],
        "gobierna": ["contexto", "verificacion", "epistemologia"],
        "enunciado": (
            "IND-A1: El indefinido de dominio no es error de sistema. "
            "Tratar IND-D1 como IND-D5 (parada, excepción de arranque, "
            "'fallo del módulo') viola la distinción de categorías y confunde "
            "valuación de dominio con rotura de contrato."
        ),
    },
    {
        "id": "IND-A2",
        "tipo": "axioma",
        "sujeto": "K_sin_O_context",
        "relacion": "es",
        "objeto": "vacio_definicional_no_cero",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-5.3.1", "IND-D1"],
        "gobierna": ["epistemologia", "verificacion", "contexto"],
        "enunciado": (
            "IND-A2: Sin O_context usable, K(D)=∅ (undefined), no K(D)=0. "
            "Asignar K=0 'para poder seguir la fórmula' fabrica una medición "
            "de correlación que no ocurrió (Def-5.3.1). Cero es un valor "
            "definido; vacío definicional no lo es."
        ),
    },
    {
        "id": "IND-A3",
        "tipo": "axioma",
        "sujeto": "anuncio_de_indefinido",
        "relacion": "es",
        "objeto": "emision_en_R_irreversible_en_el_tiempo",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D2"],
        "gobierna": ["ontologia", "temporal", "citacion"],
        "enunciado": (
            "IND-A3: Todo anuncio de indefinido es una emisión en R. Una vez "
            "producido, el enunciado existió en el tiempo: no se des-emite. "
            "No estamos 'calculando el O ausente'; estamos registrando un "
            "acto que tuvo lugar. La existencia del anuncio no depende de que "
            "la capa objeto tenga O."
        ),
    },
    {
        "id": "IND-A4",
        "tipo": "axioma",
        "sujeto": "ciclo_de_evaluacion",
        "relacion": "no_se_bloquea_por",
        "objeto": "indefinido_de_dominio",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-A1", "IND-D1"],
        "gobierna": ["verificacion", "meta", "contexto"],
        "enunciado": (
            "IND-A4 (No-bloqueo): El indefinido de dominio termina el ciclo "
            "como RESULTADO, no como parada del sistema. El orquestador sigue "
            "operativo; el siguiente acto posible es definir O y volver a "
            "evaluar. Indefinido atraviesa el sistema como dato de estado."
        ),
    },
    {
        "id": "IND-A5",
        "tipo": "axioma",
        "sujeto": "capa_objeto_sin_O",
        "relacion": "no_admite",
        "objeto": "valuacion_de_contenido_reclamable",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D3", "IND-A2", "Def-5.3.1"],
        "gobierna": ["contexto", "epistemologia"],
        "enunciado": (
            "IND-A5: En capa objeto sin O usable no hay valuación de contenido "
            "reclamable (no Tru de dominio inventado). La evaluación legítima "
            "de ese intento es el anuncio de indefinido (capa meta), no la "
            "fabricación de factores de correlación."
        ),
    },

    # =====================================================================
    # LEMAS
    # Puentes locales: preparan el teorema central sin saltar a Tru=1
    # del anuncio sin haber fijado existencia + sincronización.
    # =====================================================================

    {
        "id": "IND-L1",
        "tipo": "lema",
        "sujeto": "intento_de_valuacion_sin_O",
        "relacion": "tiene_por_evaluacion_legitima",
        "objeto": "anuncio_de_indefinido",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-A5", "IND-D2", "Def-5.3.1"],
        "gobierna": ["epistemologia", "verificacion", "contexto"],
        "enunciado": (
            "IND-L1: Todo intento de valuación de contenido sin O_context "
            "usable tiene por evaluación legítima el anuncio de indefinido "
            "(IND-D2), no la suspensión del acto ni un K fabricado. "
            "Anunciar indefinido ES la evaluación de ese intento (capa meta), "
            "no un fracaso previo a evaluar."
        ),
    },
    {
        "id": "IND-L2",
        "tipo": "lema",
        "sujeto": "anuncio_de_indefinido",
        "relacion": "implica",
        "objeto": "existencia_de_Ri_emisor_en_R",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-A3", "IND-D2"],
        "gobierna": ["ontologia", "epistemologia"],
        "enunciado": (
            "IND-L2: Si hay anuncio de indefinido, hay Ri (emisor) en R. "
            "No es el caso T17-II (ausencia total de Ri). Por tanto el caso "
            "relevante de piso/activación de β ante el anuncio es el de "
            "presencia de evaluador (T17-I / Axiom β), no el de mundo sin "
            "observador."
        ),
    },
    {
        "id": "IND-L3",
        "tipo": "lema",
        "sujeto": "anuncio_sincronizado_con_ausencia_de_O",
        "relacion": "cumple",
        "objeto": "correspondencia_con_el_hecho_de_dominio",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-D4", "IND-D1", "Def-5.3.1"],
        "gobierna": ["epistemologia", "semantica", "verificacion"],
        "enunciado": (
            "IND-L3: Cuando la capa objeto carece de O usable y el evaluador "
            "anuncia indefinido por esa razón (no por ruido ni por colapso de "
            "contrato), el anuncio está en correspondencia con el hecho real "
            "de la ausencia de dominio. Esa correspondencia es el K de la "
            "CAPA META (del enunciado), no el K de un O de contenido inexistente."
        ),
    },
    {
        "id": "IND-L4",
        "tipo": "lema",
        "sujeto": "beta",
        "relacion": "persiste_en",
        "objeto": "R_ante_anuncio_de_indefinido",
        "polaridad": True,
        "cota": "1/27",
        "depende_de": ["IND-L2", "T17", "Axiom_beta"],
        "gobierna": ["ontologia", "constantes", "epistemologia"],
        "enunciado": (
            "IND-L4: Ante anuncio de indefinido, β persiste en R. El vacío es "
            "del dominio de D (capa objeto), no de R ni del piso estructural. "
            "Anunciar indefinido no cancela β ni implica Tru_total=0 "
            "(imposible con Ri presente, T17)."
        ),
    },

    # =====================================================================
    # TEOREMA CENTRAL (META-TEOREMA)
    # Por qué es teorema: une capa objeto (no valuación de contenido) con
    # capa meta (anuncio sincronizado → Tru_total=1 del anuncio).
    # Es el punto que la gente confunde con "entonces todo vale β" o con
    # "entonces el sistema falló". Ninguna de las dos.
    # =====================================================================

    {
        "id": "IND-T1",
        "tipo": "teorema",
        "sujeto": "anuncio_sincronizado_de_indefinido",
        "relacion": "alcanza",
        "objeto": "Tru_total_uno_en_capa_meta",
        "polaridad": True,
        "cota": "1",
        "depende_de": [
            "IND-L1",
            "IND-L2",
            "IND-L3",
            "IND-L4",
            "Def-5.3.1",
            "TT.6.1",
        ],
        "gobierna": ["epistemologia", "meta", "verificacion", "contexto"],
        "enunciado": (
            "IND-T1 (Meta-teorema del indefinido): "
            "Sea D una descripción o petición en capa objeto sin O_context "
            "usable. Entonces: "
            "(i) no hay valuación de contenido reclamable para D (IND-A5); "
            "(ii) la evaluación legítima del intento es el anuncio de "
            "indefinido (IND-L1); "
            "(iii) ese anuncio existe en R como emisión (IND-A3, IND-L2); "
            "(iv) si el anuncio está sincronizado con el hecho real de la "
            "ausencia de O (IND-L3), entonces respecto del anuncio (capa meta) "
            "cabe C=L=K=1; "
            "(v) por la fórmula del teorema de la verdad, "
            "Tru_total(anuncio)=(1·1·1·α)+β=α+β=1. "
            "Por tanto: el dominio de D es indefinido; el anuncio correcto "
            "de esa indefinición es un enunciado con Tru_total=1. "
            "No se asigna Tru de contenido a un O fantasma; se valora el "
            "enunciado que sí tuvo lugar y que rastrea el hecho."
        ),
    },

    # =====================================================================
    # COROLARIOS
    # Bajada a sistema, test y no-fabricación. Aquí se ve por qué el CI
    # debe pasar sin reescribir el test metiendo O a la fuerza.
    # =====================================================================

    {
        "id": "IND-C1",
        "tipo": "corolario",
        "sujeto": "test_sin_O_context",
        "relacion": "debe_aceptar",
        "objeto": "salida_indefinido_como_valuacion_correcta",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-T1", "IND-A4", "IND-L1"],
        "gobierna": ["verificacion", "meta"],
        "enunciado": (
            "IND-C1: Un test o auditoría que evalúa sin O_context debe aceptar "
            "como correcta la salida de estado indefinido (anuncio legítimo), "
            "no exigir Tru numérico de contenido ni reescribir la entrada para "
            "fabricar O. Si el sistema inventara O o K para 'pasar', "
            "contradeciría IND-T1 y Def-5.3.1. El paso del test SIN cambiar "
            "la entrada es evidencia de que el meta-teorema se sostiene en el repo."
        ),
    },
    {
        "id": "IND-C2",
        "tipo": "corolario",
        "sujeto": "orquestador",
        "relacion": "transporta_indefinido_como",
        "objeto": "resultado_normal_de_ciclo_no_rechazo_de_arranque",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-A4", "IND-A1"],
        "gobierna": ["verificacion", "meta"],
        "enunciado": (
            "IND-C2: El orquestador (Engine) transporta el indefinido de dominio "
            "como resultado normal del ciclo (p.ej. estado UNDEFINED con notas "
            "e ids), no como ArranqueError ni como caída del estado OPERATIVO. "
            "El sistema no se para: entrega el dato y queda listo para un "
            "siguiente acto con O definido."
        ),
    },
    {
        "id": "IND-C3",
        "tipo": "corolario",
        "sujeto": "fabricar_K_cero_u_O",
        "relacion": "esta_prohibido_ante",
        "objeto": "indefinido_de_dominio",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-A2", "IND-A5", "Def-5.3.1"],
        "gobierna": ["contexto", "epistemologia", "verificacion"],
        "enunciado": (
            "IND-C3: Ante indefinido de dominio está prohibido fabricar K=0 "
            "o inventar O_context solo para ejecutar la fórmula de contenido. "
            "Eso convierte ∅ en 0 o inventa dominio; rompe IND-A2 y Def-5.3.1."
        ),
    },
    {
        "id": "IND-C4",
        "tipo": "corolario",
        "sujeto": "Tru_total_uno_del_anuncio",
        "relacion": "no_implica",
        "objeto": "Tru_de_contenido_de_D_sin_O",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-T1", "IND-D3", "IND-D4"],
        "gobierna": ["meta", "epistemologia"],
        "enunciado": (
            "IND-C4: Que el anuncio sincronizado tenga Tru_total=1 en capa meta "
            "no implica Tru de contenido sobre D en capa objeto. Son capas "
            "distintas. Confundirlas reintroduce la trampa de asignar verdad "
            "plena al dominio ausente."
        ),
    },
    {
        "id": "IND-C5",
        "tipo": "corolario",
        "sujeto": "CX",
        "relacion": "clasifica_indefinido_sin",
        "objeto": "calcular_Tru_ni_bloquear",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-A4", "IND-L1", "IND-C2"],
        "gobierna": ["contexto", "verificacion"],
        "enunciado": (
            "IND-C5: El módulo de contexto clasifica el estado indefinido y "
            "permite_k=False cuando corresponde; no calcula Tru y no convierte "
            "la clasificación en error de sistema. La valuación formal del "
            "anuncio corresponde al marco (IND-T1); CX no la sustituye."
        ),
    },
    {
        "id": "IND-C6",
        "tipo": "corolario",
        "sujeto": "cadena_auditable",
        "relacion": "puede_anunciar",
        "objeto": "porque_indefinido_con_ids_del_grafo",
        "polaridad": True,
        "cota": None,
        "depende_de": ["IND-T1", "IND-L1", "PA-A2"],
        "gobierna": ["citacion", "verificacion", "contexto"],
        "enunciado": (
            "IND-C6: Si se pide anuncio, la cadena auditable puede exponer "
            "por qué el estado es indefinido citando ids del grafo "
            "(Def-5.3.1, IND-*, CX-*), sin convertir el anuncio en cálculo "
            "de Tru de contenido ni en condena moral. El 'por qué' es parte "
            "de la valuación meta, no un plan B por no haber evaluado."
        ),
    },
]


# ---------------------------------------------------------------------------
# Export: el INIT de axiomas carga DECLARACIONES automáticamente.
# No hace falta registrar el archivo a mano en el __init__.
# ---------------------------------------------------------------------------
__all__ = ["DECLARACIONES"]
