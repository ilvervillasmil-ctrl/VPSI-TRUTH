# -*- coding: utf-8 -*-
"""
Skill CE — exclusivo Engine.

Mandato de sincronización: escala Tru (catálogo TT).
Engine emite el mandato; cada módulo ejecuta su contrato.
CE no calcula.
"""

SKILL = {
    "id": "ce_mandato_escala_tt",
    "nombre": "Mandato: calcular escala Tru del catálogo TT",
    "enunciado": (
        "Mandato del Engine a los módulos de oficio: "
        "se pide valuación en la escala indicada por el catálogo TT "
        "(categoria_tru / id de casilla). "
        "Cada módulo aporta lo suyo en sincronía; "
        "Engine deposita el resultado del ciclo. "
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
    ],
    "prioridad": 10,
    "notas": (
        "Engine lanza el mandato. "
        "TT aporta la casilla; CX el O; MC la correlación; "
        "CA los factores; FO la fórmula; CIT/CH/TX/AX su oficio. "
        "El conjunto en sincronía produce el depósito. CE solo declara el mandato."
    ),
}
