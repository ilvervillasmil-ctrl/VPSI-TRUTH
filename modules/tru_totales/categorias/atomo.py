# -*- coding: utf-8 -*-
"""
modules/tru_totales/categorias/atomo.py
=======================================

Entrada de catálogo — escala átomo.

Declara el alcance del Tru a la unidad mínima evaluable.
No calcula. No orquesta. No interpreta pedidos.

Engine consulta este descriptor por id (tru_atomo) y aplica
el ciclo de cálculo (CX → conteos → CA → FO) sobre el segmento
que corresponda a esta unidad, bajo el O que ya esté fijado.
"""

CATEGORIA = {
    "id": "tru_atomo",
    "nombre": "Tru de átomo",
    "unidad": "atomo",
    "enunciado": (
        "Alcance de Tru_Ri y Tru_total aplicado a la unidad mínima "
        "evaluable del material (átomo / token / palabra), bajo un O "
        "usable. "
        "Si el átomo no es proposición evaluable bajo ese O, K puede "
        "no ser reclamable; no se fabrica Tru. "
        "La fórmula y los factores los aplican CA y FO; este archivo "
        "solo declara la escala."
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
    "senales": [
        "tru de la palabra",
        "tru del atomo",
        "tru del átomo",
        "total de la palabra",
        "tru_atomo",
    ],
    "anclas": [
        "TA5",
        "Def-5.3.1",
        "CX-A14",
        "SM-A6",
        "AF-T2",
    ],
    "notas": (
        "Primera escala del catálogo TT. "
        "Sin agregación inferior (agrega_desde vacío). "
        "Engine segmenta el átomo; TT no segmenta."
    ),
}
