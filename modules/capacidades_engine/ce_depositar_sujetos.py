# -*- coding: utf-8 -*-
"""
Skill CE (exclusivo Engine): depositar Tru por sujeto S_1…S_N.

Un skill del repertorio del Engine.
No segmenta hablantes. No calcula. Declara la salida del ciclo.
"""

SKILL = {
    "id": "ce_depositar_sujetos",
    "nombre": "Depositar Tru por sujeto",
    "enunciado": (
        "Skill: dejar en el resultado del ciclo "
        "resultado.sujetos = [{indice, nombre, C, L, K, Tru_Ri, Tru_total}, …] "
        "cuando haya varios hablantes y la escala sea tru_sujeto."
    ),
    "version": "1.0",
    "modulos_objetivo": ["tru_totales", "calculator", "formulas"],
    "requiere_roles": ["TT", "CA", "FO"],
    "entrada": ["segmentos_por_sujeto", "O_id", "enunciado_O"],
    "salida_esperada": ["sujetos", "n_sujetos"],
    "sincroniza_con": ["ce_orquestar_tt"],
    "prioridad": 20,
    "notas": "Omega 10.1 lee resultado.sujetos. Solo Engine usa este skill.",
}
