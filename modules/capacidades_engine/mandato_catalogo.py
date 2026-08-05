# -*- coding: utf-8 -*-
"""
modules/capacidades_engine/skills/ce_mandato_catalogo.py

Skill CE — Mandato de catálogo TT.

Oficio
------
Declarar que Engine debe consultar el catálogo de categorías de
Tru totales antes de solicitar un cálculo de escala.

Este skill:
    • no calcula,
    • no interpreta fórmulas,
    • no modifica el catálogo,
    • no decide resultados.

Solo establece el mandato operativo para Engine.
"""

SKILL = {
    "id": "ce_mandato_catalogo",

    "nombre": "Mandato: consultar catálogo TT",

    "version": "1.0",

    "oficio": "mandato",

    "descripcion": (
        "Cuando una petición requiera una escala de Tru, "
        "Engine debe consultar el catálogo de tru_totales "
        "para conocer las categorías disponibles y obtener "
        "el descriptor correspondiente antes de continuar "
        "el ciclo de evaluación."
    ),

    "objetivo": (
        "Poner el catálogo TT a disposición de Engine "
        "como fuente oficial de categorías de escala."
    ),

    "requiere": [
        "tru_totales",
        "escalas_ids",
    ],

    "produce": [
        "descriptor_categoria",
    ],

    "limites": [
        "No calcula Tru_Ri.",
        "No calcula Tru_total.",
        "No aplica C.",
        "No aplica L.",
        "No aplica K.",
        "No aplica alpha.",
        "No aplica beta.",
        "No modifica el catálogo.",
        "No interpreta lenguaje natural.",
    ],

    "delegacion": {
        "Engine": "Consulta el catálogo y orquesta.",
        "Calculator": "Calcula C, L, K, Tru_Ri y Tru_total.",
        "Omega": "Presenta el resultado.",
        "tru_totales": "Expone el catálogo.",
    },
}
