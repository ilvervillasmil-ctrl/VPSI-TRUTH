# modules/tru_totales/categorias/atomo.py
# -*- coding: utf-8 -*-
"""
modules/tru_totales/categorias/atomo.py

Casilla de catálogo — escala átomo.
Solo declara el alcance. No calcula. No cita axiomas. No interpreta.
"""

CATEGORIA = {
    "id": "tru_atomo",
    "nombre": "Tru de átomo",
    "unidad": "atomo",
    "enunciado": (
        "Casilla de catálogo para el Tru_Ri y el Tru_total "
        "a escala de átomo (unidad mínima evaluable)."
    ),
    "version": "1.0",
    "nivel_fractal": 1,
    "jurisdiccion": "palabra",
    "requiere": [
        "segmento_atomo",
        "O_id",
        "enunciado_O",
    ],
    "factores_evaluables": [
        "Tru_Ri",
        "Tru_total",
    ],
    "agrega_desde": [],
    "notas": "Escala mínima del catálogo TT."
}
