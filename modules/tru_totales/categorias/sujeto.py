# -*- coding: utf-8 -*-
"""
modules/tru_totales/categorias/sujeto.py

Casilla de catálogo — escala sujeto.
Solo declara el alcance. No calcula. No cita axiomas. No interpreta.
"""

CATEGORIA = {
    "id": "tru_sujeto",
    "nombre": "Tru de sujeto",
    "unidad": "sujeto",
    "enunciado": (
        "Casilla de catálogo para el Tru_Ri y el Tru_total "
        "a escala de sujeto (S_i, i = 1…N según lo que haya en el material)."
    ),
    "version": "1.0",
    "nivel_fractal": 3,
    "jurisdiccion": "sujeto",
    "requiere": [
        "segmentos_del_sujeto",
        "sujeto_indice",
        "O_id",
        "enunciado_O",
    ],
    "factores_evaluables": [
        "Tru_Ri",
        "Tru_total",
    ],
    "agrega_desde": [
        "tru_frase",
    ],
    "notas": (
        "Escala sujeto del catálogo TT. "
        "N y la identidad de cada S_i los aporta quien segmenta el material; "
        "TT solo declara la casilla."
    ),
}
