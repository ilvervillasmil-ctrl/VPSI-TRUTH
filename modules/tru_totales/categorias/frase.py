# -*- coding: utf-8 -*-
"""
modules/tru_totales/categorias/frase.py

Casilla de catálogo — escala frase / afirmación.
Solo declara el alcance. No calcula. No cita axiomas. No interpreta.
"""

CATEGORIA = {
    "id": "tru_frase",
    "nombre": "Tru de frase",
    "unidad": "frase",
    "enunciado": (
        "Casilla de catálogo para el Tru_Ri y el Tru_total "
        "a escala de frase o afirmación unitaria."
    ),
    "version": "1.0",
    "nivel_fractal": 2,
    "jurisdiccion": "afirmacion",
    "requiere": [
        "segmento_frase",
        "O_id",
        "enunciado_O",
    ],
    "factores_evaluables": [
        "Tru_Ri",
        "Tru_total",
    ],
    "agrega_desde": [
        "tru_atomo",
    ],
    "notas": "Escala frase del catálogo TT.",
}
