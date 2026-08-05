# -*- coding: utf-8 -*-
"""
modules/capacidades_engine/mandato_catalogo.py

ID: ce_mandato_catalogo
CE no calcula.
"""

SKILL = {
    "id": "ce_mandato_catalogo",
    "nombre": "Mandato: consultar catalogo TT",
    "version": "1.0",
    "enunciado": (
        "Mandato del Engine para descubrir las escalas de verdad declaradas. "
        "TT expone sus IDs; CA las registra para el ciclo. "
        "CE no calcula ni inventa escalas."
    ),
    "modulos_objetivo": [
        "tru_totales",
        "calculator",
    ],
    "requiere_roles": [
        "TT", 
        "CA",
    ],
    "entrada": [],
    "salida_esperada": [
        "escalas_disponibles",
        "ids_tt",
    ],
    "sincroniza_con": [
        "ce_mandato_escala_tt",
    ],
    "prioridad": 1,
    "notas": (
        "Es el paso previo a cualquier cálculo de escala. "
        "Sin este mandato declarativo, el Engine no sabría "
        "qué salidas de catálogo exigir a CA y TT."
    )
}
