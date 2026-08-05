# modules/capacidades_engine/mandato_escala_tt.py
# -*- coding: utf-8 -*-
"""
Skill CE — exclusivo Engine.
Mandato de sincronización: escala Tru (catálogo TT).
Engine emite el mandato; cada módulo ejecuta su contrato. CE no calcula.
"""

SKILL = {
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
    "requiere_roles": ["TT", "CX", "MC", "CA", "FO", "CIT", "CH", "TX", "AX"],
    "entrada": [
        "categoria_tru",
        "O_id",
        "enunciado_O",
        "material",
    ],
    "salida_esperada": [
        "C",
        "L",
        "K",
        "tru_ri",
        "tru_total",
        "categoria_tru",
        "citacion",
    ],
    "sincroniza_con": [
        "ce_mandato_sujetos",
        "ce_mandato_aplicar_escala",
    ],
    "prioridad": 10,
    "notas": (
        "Engine lanza el mandato. "
        "TT aporta la casilla; CX el O; MC la correlación; "
        "CA los factores; FO la fórmula; CIT/CH/TX/AX su oficio. "
        "El Engine deposita la salida esperada en el ciclo."
    )
}
