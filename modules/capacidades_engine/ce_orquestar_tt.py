# modules/capacidades_engine/ce_mandato_catalogo.py
# -*- coding: utf-8 -*-
"""
Skill CE — exclusivo Engine.

Mandato de sincronización: lectura del catálogo de escalas.
Engine exige conocer las categorías disponibles.
CE no calcula.
"""

SKILL = {
    "id": "ce_mandato_catalogo",
    "nombre": "Mandato: leer inventario del catálogo TT",
    "enunciado": (
        "Mandato del Engine para descubrir las escalas de verdad declaradas. "
        "El módulo TT expone sus IDs de categoría y CA las registra para el ciclo. "
        "CE no calcula ni inventa escalas."
    ),
    "version": "1.0",
    "modulos_objetivo": [
        "tru_totales",
        "calculator",
    ],
    "requiere_roles": ["TT", "CA"],
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
        "Sin este mandato, Engine no sabe qué escalas puede exigir a CA."
    ),
}
