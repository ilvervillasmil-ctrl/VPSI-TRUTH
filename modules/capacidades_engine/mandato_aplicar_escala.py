# -*- coding: utf-8 -*-
"""
Skill CE — exclusivo Engine.

Mandato de sincronización: aplicar escala de Tru por id
(usando todas las capacidades del sistema).

CE no calcula. Engine emite el mandato; cada módulo ejecuta su contrato.
"""

SKILL = {
    "id": "ce_mandato_aplicar_escala",
    "nombre": "Mandato: aplicar escala Tru por id (sistema completo)",
    "enunciado": (
        "Mandato del Engine a todos los módulos de oficio: "
        "se pide valuación en la escala indicada por id "
        "(escalas_ids / catálogo TT: tru_atomo, tru_frase, tru_sujeto, "
        "tru_conversacion, tru_repositorio u otro id declarado). "
        "El recorte de material sigue el descriptor del id; "
        "cada módulo aporta lo suyo en sincronía; "
        "si repetir_por es por_sujeto (u otro repetidor), "
        "el ciclo se repite por cada recorte y Engine deposita "
        "el resultado (incl. resultado.sujetos cuando aplique). "
        "CE no calcula."
    ),
    "version": "1.0",
    "modulos_objetivo": [
        "capacidades_engine",
        "tru_totales",
        "calculator",
        "formulas",
        "contexto",
        "correlacion_mecanica",
        "citacion",
        "citaciones",
        "cache",
        "taxonomia",
        "axiomas",
        "realidad",
        "verificacion",
        "constante",
        "diccionario",
        "glosario",
        "self",
        "diagnostico",
        "interfaz",
    ],
    "requiere_roles": [
        "CE", "TT", "CA", "FO", "CX", "MC", "CIT", "CC",
        "CH", "TX", "AX", "RE", "VX", "CT", "DI", "GL", "SF", "DG", "UI",
    ],
    "entrada": [
        "escala_id",
        "categoria_tru",
        "texto",
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
        "sujetos",
        "n_sujetos",
        "resultado_ciclo",
    ],
    "sincroniza_con": [
        "ce_mandato_catalogo",
        "ce_mandato_escala_tt",
        "ce_mandato_sujetos",
    ],
    "prioridad": 15,
    "notas": (
        "Utiliza todas las capacidades del sistema en sincronía. "
        "escalas_ids (bajo calculator) describe el recorte; "
        "conteos cuenta; FO formula; el resto su oficio. "
        "Engine deposita; Omega lee. CE solo declara el mandato."
    ),
}
