# -*- coding: utf-8 -*-
"""
modules/tru_totales/categorias/conversacion.py

Casilla de catálogo — escala conversación / diálogo.
Solo declara el alcance. No calcula. No cita axiomas. No interpreta.
"""

CATEGORIA = {
    "id": "tru_conversacion",
    "nombre": "Tru de conversación",
    "unidad": "conversacion",
    "enunciado": (
        "Casilla de catálogo para el Tru_Ri y el Tru_total "
        "a escala de conversación o diálogo completo."
    ),
    "version": "1.0",
    "nivel_fractal": 4,
    "jurisdiccion": "dialogo",
    "requiere": [
        "segmentos_dialogo",
        "O_id",
        "enunciado_O",
    ],
    "factores_evaluables": [
        "Tru_Ri",
        "Tru_total",
    ],
    "agrega_desde": [
        "tru_sujeto",
        "tru_frase",
    ],
    "notas": "Escala conversación del catálogo TT.",
}
