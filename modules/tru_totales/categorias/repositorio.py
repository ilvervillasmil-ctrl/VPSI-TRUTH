# -*- coding: utf-8 -*-
"""
modules/tru_totales/categorias/repositorio.py

Casilla de catálogo — escala repositorio / sistema.
Solo declara el alcance. No calcula. No cita axiomas. No interpreta.
"""

CATEGORIA = {
    "id": "tru_repositorio",
    "nombre": "Tru de repositorio",
    "unidad": "repositorio",
    "enunciado": (
        "Casilla de catálogo para el Tru_Ri y el Tru_total "
        "a escala de repositorio o sistema."
    ),
    "version": "1.0",
    "nivel_fractal": 5,
    "jurisdiccion": "sistema",
    "requiere": [
        "O_id",
        "enunciado_O",
    ],
    "factores_evaluables": [
        "Tru_Ri",
        "Tru_total",
    ],
    "agrega_desde": [],
    "notas": "Escala repositorio del catálogo TT.",
}
