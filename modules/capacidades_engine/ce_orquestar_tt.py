# -*- coding: utf-8 -*-
"""
Skill CE (exclusivo Engine): orquestar catálogo TT.

Un skill del repertorio del Engine.
No calcula. Los oficios siguen en TT / CA / FO / CX.
"""

SKILL = {
    "id": "ce_orquestar_tt",
    "nombre": "Orquestar catálogo Tru totales",
    "enunciado": (
        "Skill: consultar tru_totales (ids de escala) y pedir a CA/FO "
        "el cálculo de la escala indicada; depositar Tru_Ri / Tru_total "
        "y, si aplica escala tru_sujeto, la lista por sujeto."
    ),
    "version": "1.0",
    "modulos_objetivo": ["tru_totales", "calculator", "formulas", "contexto"],
    "requiere_roles": ["TT", "CA", "FO", "CX"],
    "entrada": ["categoria_tru", "O_id", "enunciado_O", "material_segmentable"],
    "salida_esperada": ["tru_ri", "tru_total", "sujetos", "categoria_tru"],
    "sincroniza_con": ["ce_depositar_sujetos"],
    "prioridad": 10,
    "notas": "Complementa TT (catálogo pasivo). Solo Engine usa este skill.",
}
