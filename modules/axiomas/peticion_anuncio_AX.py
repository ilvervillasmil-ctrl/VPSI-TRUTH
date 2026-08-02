"""
VPSI-TRUTH --- modules/axiomas/peticion_anuncio_AX.py

Cuerpo axiomático: derecho de petición de anuncio / auditabilidad del acto.

No calcula Tru.
No fija O.
No juzga personas.
Fija normas sobre el derecho de cualquier Ri a exigir la cadena
(contexto, evidencia, normas, límites) de un resultado emitido.

Anclas del marco (VPSI v9.4):
  TA4   — R ⊥ observador (sin privilegio de rol)
  T7    — el verificador no crea la verdad
  T9    — imposibilidad de verdad sin evidencia
  T14   — pertenencia del contenido vs acto de enunciar
  Def-5.3.1 — K indefinido sin O_context
  T16/T17 — techo α / piso β
  Prefacio — el marco se aplica a sí mismo

Estilo de declaración: id, tipo, sujeto, relacion, objeto,
polaridad, cota, depende_de, gobierna, enunciado.
"""

from __future__ import annotations

from typing import Any, Dict, List

# ===============================================================
# CUERPO
# ===============================================================

DECLARACIONES: List[Dict[str, Any]] = [
    # ---------- Definiciones ----------
    {
        "id": "PA-D1",
        "tipo": "definicion",
        "sujeto": "peticion_de_anuncio",
        "relacion": "es",
        "objeto": "solicitud_de_cadena_auditable",
        "polaridad": True,
        "cota": None,
        "depende_de": [],
        "gobierna": ["citacion", "auditoria", "meta"],
        "enunciado": (
            "PA-D1: Petición de anuncio es la solicitud, por cualquier Ri, "
            "de la cadena auditable de un resultado o descripción D emitida "
            "por el sistema: O_context, evidencia_ref, ids normativos "
            "(axiomas/teoremas/corolarios), factores reportados y límites "
            "estructurales aplicables. No es petición de autoridad ni de "
            "estado mental."
        ),
    },
    {
        "id": "PA-D2",
        "tipo": "definicion",
        "sujeto": "cadena_auditable",
        "relacion": "consta_de",
        "objeto": "citas_con_enunciado_y_evidencia",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-D1"],
        "gobierna": ["citacion", "meta"],
        "enunciado": (
            "PA-D2: Cadena auditable = conjunto de citas {id, tipo, "
            "fuente_modulo, enunciado, descripcion, evidencia_ref} "
            "suficiente para reconstruir por qué se emitió D bajo el O "
            "declarado, sin recalcular Tru en el acto de anunciar."
        ),
    },
    {
        "id": "PA-D3",
        "tipo": "definicion",
        "sujeto": "peticionario",
        "relacion": "es",
        "objeto": "cualquier_Ri_sin_lista_blanca",
        "polaridad": True,
        "cota": None,
        "depende_de": ["TA4"],
        "gobierna": ["citacion", "epistemologia", "meta"],
        "enunciado": (
            "PA-D3: Peticionario es cualquier Ri (persona, sistema, Engine, "
            "CI, otra IA). No existe lista blanca de privilegio: TA4 "
            "(R ⊥ observador) implica igualdad de derecho de petición "
            "respecto del instrumento."
        ),
    },
    # ---------- Axiomas ----------
    {
        "id": "PA-A1",
        "tipo": "axioma",
        "sujeto": "emision_de_resultado",
        "relacion": "genera_derecho_a",
        "objeto": "peticion_de_anuncio",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-D1", "T7", "T14"],
        "gobierna": ["citacion", "engine", "meta"],
        "enunciado": (
            "PA-A1: Si el sistema emite un resultado o descripción D bajo "
            "un ciclo de evaluación, cualquier peticionario tiene derecho "
            "a solicitar la cadena auditable de esa emisión. El verificador "
            "no crea la verdad (T7); el acto de emitir es auditable (T14)."
        ),
    },
    {
        "id": "PA-A2",
        "tipo": "axioma",
        "sujeto": "respuesta_a_peticion",
        "relacion": "debe_constar_de",
        "objeto": "normas_evidencia_contexto_limites",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-A1", "T9", "Def-5.3.1"],
        "gobierna": ["citacion", "contexto", "meta"],
        "enunciado": (
            "PA-A2: La respuesta a una petición de anuncio debe componerse "
            "solo de: (i) normas citadas (ids), (ii) evidencia_ref del ciclo, "
            "(iii) O_context si fue declarado, (iv) límites estructurales "
            "si aplican (p. ej. K sin O). Queda excluido el recurso a "
            "autoridad, intención atribuida o 'porque sí'."
        ),
    },
    {
        "id": "PA-A3",
        "tipo": "axioma",
        "sujeto": "ausencia_de_cadena",
        "relacion": "no_eleva",
        "objeto": "Tru_de_D",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-A1", "T9"],
        "gobierna": ["citacion", "auditoria", "meta"],
        "enunciado": (
            "PA-A3: La imposibilidad de entregar cadena auditable no eleva "
            "Tru(D). Es defecto de auditabilidad del instrumento (se delata "
            "en registro/test), no privilegio del sistema ni prueba de verdad."
        ),
    },
    {
        "id": "PA-A4",
        "tipo": "axioma",
        "sujeto": "peticion_de_estado_mental",
        "relacion": "no_es_oficio_de",
        "objeto": "sistema_VPSI",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-D1"],
        "gobierna": ["citacion", "taxonomia", "meta"],
        "enunciado": (
            "PA-A4: Pedir motivos psicológicos, intenciones ocultas o "
            "calificativos morales de personas no es oficio del sistema. "
            "La respuesta legítima es anunciar el límite de oficio "
            "(evidencia estructural vs. convención humana), no inventar "
            "estados mentales."
        ),
    },
    {
        "id": "PA-A5",
        "tipo": "axioma",
        "sujeto": "autoaplicacion",
        "relacion": "incluye",
        "objeto": "peticion_sobre_el_propio_marco",
        "polaridad": True,
        "cota": None,
        "depende_de": ["TA4", "PA-A1"],
        "gobierna": ["meta", "axiomas"],
        "enunciado": (
            "PA-A5: El derecho de petición se aplica al propio marco y al "
            "propio Engine: cualquier Ri puede exigir la cadena de un "
            "resultado del sistema sobre el sistema. Sin excepción de autor."
        ),
    },
    # ---------- Teoremas ----------
    {
        "id": "PA-T1",
        "tipo": "teorema",
        "sujeto": "derecho_universal_de_peticion",
        "relacion": "sigue_de",
        "objeto": "TA4_y_PA-A1",
        "polaridad": True,
        "cota": None,
        "depende_de": ["TA4", "PA-A1", "PA-D3"],
        "gobierna": ["citacion", "epistemologia"],
        "enunciado": (
            "PA-T1 (Derecho universal de petición): De TA4 y PA-A1 se sigue "
            "que no hay clase de peticionario excluida a priori. Humano, "
            "IA, CI o módulo interno pueden exigir anuncio de la misma forma."
        ),
    },
    {
        "id": "PA-T2",
        "tipo": "teorema",
        "sujeto": "respuesta_sin_evidencia",
        "relacion": "viola",
        "objeto": "T9_y_PA-A2",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T9", "PA-A2"],
        "gobierna": ["citacion", "auditoria"],
        "enunciado": (
            "PA-T2: Una respuesta a petición que no aporta evidencia_ref ni "
            "norma citable ni límite estructural explícito viola T9 y PA-A2. "
            "No cuenta como cadena auditable."
        ),
    },
    {
        "id": "PA-T3",
        "tipo": "teorema",
        "sujeto": "K_sin_O_en_respuesta",
        "relacion": "debe_anunciar",
        "objeto": "limite_Def-5.3.1",
        "polaridad": True,
        "cota": None,
        "depende_de": ["Def-5.3.1", "PA-A2"],
        "gobierna": ["citacion", "contexto"],
        "enunciado": (
            "PA-T3: Si la petición interroga un K (o Tru_Ri) y no hubo "
            "O_context explícito, la respuesta auditable debe anunciar el "
            "límite K=∅ (Def-5.3.1), no un valor numérico inventado."
        ),
    },
    {
        "id": "PA-T4",
        "tipo": "teorema",
        "sujeto": "techo_y_piso_en_anuncio",
        "relacion": "son_citables",
        "objeto": "T16_y_T17",
        "polaridad": True,
        "cota": None,
        "depende_de": ["T16", "T17", "PA-A2"],
        "gobierna": ["citacion", "formulas"],
        "enunciado": (
            "PA-T4: Cuando el ciclo invoca techo α (T16) o piso β (T17), "
            "esos límites son parte legítima de la cadena auditable y "
            "deben poder anunciarse ante petición."
        ),
    },
    # ---------- Corolarios ----------
    {
        "id": "PA-C1",
        "tipo": "corolario",
        "sujeto": "Omega_y_tests",
        "relacion": "pueden_ejercer",
        "objeto": "peticion_de_anuncio",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-T1"],
        "gobierna": ["citacion", "diagnostics"],
        "enunciado": (
            "PA-C1: Omega Report, CI y tests son peticionarios válidos: "
            "pueden exigir cadena auditable sin ser 'usuarios humanos'."
        ),
    },
    {
        "id": "PA-C2",
        "tipo": "corolario",
        "sujeto": "citacion",
        "relacion": "es_instrumento_de",
        "objeto": "PA-A2",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-A2", "PA-D2"],
        "gobierna": ["citacion"],
        "enunciado": (
            "PA-C2: El módulo de citación es el instrumento de forma de "
            "PA-A2: registra y anuncia; no calcula Tru ni sustituye a AX/MC/CX."
        ),
    },
    {
        "id": "PA-C3",
        "tipo": "corolario",
        "sujeto": "falla_de_auditabilidad",
        "relacion": "es_evidencia_contra",
        "objeto": "integridad_del_instrumento",
        "polaridad": True,
        "cota": None,
        "depende_de": ["PA-A3"],
        "gobierna": ["auditoria", "meta"],
        "enunciado": (
            "PA-C3: Si tras emisión no existe cadena entregable, eso es "
            "evidencia de defecto del instrumento (PA-A3), usable en "
            "auditoría del propio sistema, no argumento a favor de D."
        ),
    },
]


def declaraciones() -> List[Dict[str, Any]]:
    return list(DECLARACIONES)


# Compatibilidad con descubridores que buscan CUERPO
CUERPO = DECLARACIONES

__all__ = ["DECLARACIONES", "CUERPO", "declaraciones"]
