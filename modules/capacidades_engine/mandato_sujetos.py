# -*- coding: utf-8 -*-
"""
modules/capacidades_engine/mandatos_ce.py

Todos los mandatos CE en un solo archivo.
CE no calcula. CE no segmenta. CE no deposita.
Solo declara id, enunciado, entrada, salida_esperada y roles.

Bornes:
  - sin ejecutor
  - sin regex / recorte de hablantes
  - sin por_sujeto
  - C/L/K/Tru los producen CA y FO; el mandato solo orienta la escala
"""

from __future__ import annotations

from typing import Any, Dict, List

SKILLS: List[Dict[str, Any]] = [
    {
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
            "Paso previo a cualquier valuacion por escala. "
            "CE solo declara; TT y CA aportan los ids."
        ),
    },
    {
        "id": "ce_mandato_escala_tt",
        "nombre": "Mandato: escala TT por id",
        "version": "1.0",
        "enunciado": (
            "Mandato del Engine: valuacion en la escala indicada por id "
            "(tru_atomo, tru_frase, tru_sujeto, tru_conversacion, "
            "tru_repositorio u otro id del catalogo TT). "
            "CE no calcula. CA produce C/L/K; FO Tru; Engine deposita."
        ),
        "modulos_objetivo": [
            "tru_totales",
            "contexto",
            "correlacion_mecanica",
            "calculator",
            "formulas",
            "citacion",
            "cache",
            "taxonomia",
            "axiomas",
        ],
        "requiere_roles": [
            "TT", "CX", "MC", "CA", "FO", "CIT", "CH", "TX", "AX",
        ],
        "entrada": [
            "categoria_tru",
            "escala_id",
            "O_id",
            "enunciado_O",
            "material",
        ],
        "salida_esperada": [
            "categoria_tru",
            "escala_id",
            "citacion",
        ],
        "sincroniza_con": [
            "ce_mandato_catalogo",
            "ce_mandato_sujetos",
            "ce_mandato_aplicar_escala",
        ],
        "prioridad": 10,
        "notas": (
            "No declara C/L/K/Tru como producto de CE. "
            "Esos valores los depositan CA y FO en el ciclo; "
            "este mandato solo fija la escala."
        ),
    },
    {
        "id": "ce_mandato_sujetos",
        "nombre": "Mandato: Tru por sujeto S_1..S_N",
        "version": "2.0",
        "enunciado": (
            "Mandato del Engine: valuacion por sujeto "
            "(escala tru_sujeto del catalogo TT). "
            "N y la identidad de cada S_i los aporta quien segmenta "
            "el material (Engine / preparacion), no este skill. "
            "CE no calcula. Engine deposita resultado.sujetos y n_sujetos."
        ),
        "modulos_objetivo": [
            "tru_totales",
            "contexto",
            "correlacion_mecanica",
            "calculator",
            "formulas",
            "citacion",
            "cache",
            "taxonomia",
            "axiomas",
        ],
        "requiere_roles": [
            "TT", "CX", "MC", "CA", "FO", "CIT", "CH", "TX", "AX",
        ],
        "entrada": [
            "categoria_tru=tru_sujeto",
            "O_id",
            "enunciado_O",
            "material_multi_hablante",
        ],
        "salida_esperada": [
            "sujetos",
            "n_sujetos",
        ],
        "sincroniza_con": [
            "ce_mandato_escala_tt",
            "ce_mandato_aplicar_escala",
        ],
        "prioridad": 20,
        "notas": (
            "Bornes exactos: sujetos, n_sujetos. "
            "Sin por_sujeto. Sin ejecutor. Sin regex. "
            "El recorte Nombre: mensaje es oficio de orquestacion, no de CE."
        ),
    },
    {
        "id": "ce_mandato_aplicar_escala",
        "nombre": "Mandato: aplicar escala Tru por id",
        "version": "2.0",
        "enunciado": (
            "Mandato del Engine a los modulos de oficio: "
            "valuacion en la escala indicada por id "
            "(escalas_ids / catalogo TT). "
            "El descriptor de recorte lo aporta escalas_ids; "
            "cada modulo aporta su oficio en sincronia. "
            "CE no calcula."
        ),
        "modulos_objetivo": [
            "tru_totales",
            "calculator",
            "formulas",
            "contexto",
            "correlacion_mecanica",
            "citacion",
            "cache",
            "taxonomia",
            "axiomas",
        ],
        "requiere_roles": [
            "TT", "CA", "FO", "CX", "MC", "CIT", "CH", "TX", "AX",
        ],
        "entrada": [
            "escala_id",
            "categoria_tru",
            "material",
            "O_id",
            "enunciado_O",
        ],
        "salida_esperada": [
            "categoria_tru",
            "escala_id",
            "resultado_ciclo",
        ],
        "sincroniza_con": [
            "ce_mandato_catalogo",
            "ce_mandato_escala_tt",
            "ce_mandato_sujetos",
        ],
        "prioridad": 15,
        "notas": (
            "No declara C/L/K/Tru ni sujetos como producto de CE. "
            "Si la escala es tru_sujeto, el mandato de sujetos "
            "orienta el deposito sujetos/n_sujetos. "
            "CA y FO siguen siendo dueÃ±os de factores y formula."
        ),
    },
]
