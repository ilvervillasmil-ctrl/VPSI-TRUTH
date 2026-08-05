# modules/capacidades_engine/ce_mandato_sujetos.py
# -*- coding: utf-8 -*-
"""
Skill CE — exclusivo Engine.

Mandato de sincronización: Tru total por sujeto S_1…S_N.
Engine emite el mandato; cada módulo ejecuta su contrato.
CE no calcula ni segmenta hablantes.
"""

SKILL = {
    "id": "ce_mandato_sujetos",
    "nombre": "Mandato: Tru total por sujeto S_1…S_N",
    "enunciado": (
        "Mandato del Engine a los módulos de oficio: "
        "se pide valuación por sujeto (escala tru_sujeto del catálogo TT) "
        "para cada S_i presente en el material (i = 1…N). "
        "Cada módulo aporta lo suyo en sincronía por sujeto; "
        "Engine deposita resultado.sujetos = "
        "[{indice, nombre, C, L, K, Tru_Ri, Tru_total}, …]. "
        "CE no calcula."
    ),
    "version": "1.0",
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
    "requiere_roles": ["TT", "CX", "MC", "CA", "FO", "CIT", "CH", "TX", "AX"],
    "entrada": [
        "categoria_tru=tru_sujeto",
        "O_id",
        "enunciado_O",
        "material_multi_hablante",
    ],
    "salida_esperada": [
        "sujetos",
        "n_sujetos",
        "por_sujeto",
    ],
    "sincroniza_con": [
        "ce_mandato_escala_tt",
    ],
    "prioridad": 20,
    "notas": (
        "Engine lanza el mandato a todo el conjunto. "
        "No es solo CA+FO: CX, MC, TT, CIT, CH, TX, AX participan "
        "según su contrato. Omega 10.1 lee resultado.sujetos y resultado.por_sujeto. "
        "CE solo declara el mandato."
    ),
}
