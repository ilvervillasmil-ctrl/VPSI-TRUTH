# -*- coding: utf-8 -*-
"""
Skill CE — exclusivo Engine.

Mandato genérico: usar cualquier id de catálogo (TT / CC / …)
y sincronizar el conjunto de módulos de oficio.
"""

SKILL = {
    "id": "ce_mandato_catalogo",
    "nombre": "Mandato: ejecutar pedido por id de catálogo",
    "enunciado": (
        "Mandato del Engine: el pedido trae uno o más ids de catálogo "
        "(TT, CC u otro catálogo del repo). "
        "Engine comunica a todos los módulos de oficio implicados "
        "qué se pide; cada uno ejecuta su contrato; "
        "la sincronización deposita el resultado del ciclo. "
        "CE no calcula."
    ),
    "version": "1.0",
    "modulos_objetivo": [
        "tru_totales",
        "citaciones",
        "contexto",
        "correlacion_mecanica",
        "calculator",
        "formulas",
        "citacion",
        "cache",
        "taxonomia",
        "axiomas",
        "realidad",
        "verificacion",
    ],
    "requiere_roles": [
        "TT", "CC", "CX", "MC", "CA", "FO", "CIT", "CH", "TX", "AX", "RE", "VX",
    ],
    "entrada": [
        "ids_catalogo",
        "O_id",
        "enunciado_O",
        "material",
    ],
    "salida_esperada": [
        "resultado_ciclo",
        "ids_atendidos",
    ],
    "sincroniza_con": [
        "ce_mandato_escala_tt",
        "ce_mandato_sujetos",
    ],
    "prioridad": 5,
    "notas": (
        "Puerta genérica: cualquier id de catálogo entra aquí como mandato. "
        "Engine no inventa oficios; sincroniza los que ya existen."
    ),
}
