# -*- coding: utf-8 -*-
"""
modules/capacidades_engine/mandatos_ce.py

Fuente unica de mandatos CE.

OFICIO
  Declarar los mandatos del Engine.
  Nada mas.

NO HACE
  Calcular C / L / K / Tru_Ri / Tru_total.
  Segmentar hablantes.
  Depositar resultados.
  Orquestar el ciclo.
  Inventar bornes (por_sujeto, ejecutor, regex).

LECTURA
  Este archivo exporta SKILLS (lista).
  El INIT de capacidades_engine lee TODOS los dicts de SKILLS.
  Engine, cuando consulta CE (ids / skills / por_id / barrer / inventario),
  ve el catalogo completo sin huecos.

BORNES DE SALIDA (exactos)
  ce_mandato_catalogo      -> escalas_disponibles, ids_tt
  ce_mandato_escala_tt     -> categoria_tru, escala_id, citacion
  ce_mandato_sujetos       -> sujetos, n_sujetos
  ce_mandato_aplicar_escala -> categoria_tru, escala_id, resultado_ciclo

Quien produce C/L/K: CA.
Quien produce Tru: FO.
Quien segmenta material: orquestacion del ciclo (no este archivo).
Quien deposita: Engine.
Quien lee el deposito: Omega.
"""

from __future__ import annotations

from typing import Any, Dict, List

SKILLS: List[Dict[str, Any]] = [
    {
        "id": "ce_mandato_catalogo",
        "nombre": "Mandato: consultar catalogo TT",
        "version": "1.0",
        "enunciado": (
            "Mandato del Engine: descubrir las escalas de verdad declaradas "
            "en el catalogo TT (y registrables en CA). "
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
            "ce_mandato_aplicar_escala",
        ],
        "prioridad": 1,
        "notas": (
            "Paso previo a valuacion por escala. "
            "TT aporta ids; CA puede registrarlos. CE solo declara."
        ),
    },
    {
        "id": "ce_mandato_escala_tt",
        "nombre": "Mandato: escala TT por id",
        "version": "1.0",
        "enunciado": (
            "Mandato del Engine: valuacion orientada a la escala indicada "
            "por id (tru_atomo, tru_frase, tru_sujeto, tru_conversacion, "
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
            "TT",
            "CX",
            "MC",
            "CA",
            "FO",
            "CIT",
            "CH",
            "TX",
            "AX",
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
            "Fija la escala; el ciclo de oficio aporta el resto."
        ),
    },
    {
        "id": "ce_mandato_sujetos",
        "nombre": "Mandato: Tru por sujeto S_1..S_N",
        "version": "2.0",
        "enunciado": (
            "Mandato del Engine: valuacion por sujeto bajo la escala "
            "tru_sujeto del catalogo TT. "
            "N y la identidad de cada S_i los aporta quien prepara el "
            "material del ciclo; este skill no segmenta. "
            "CE no calcula. Engine deposita sujetos y n_sujetos cuando "
            "el ciclo los produce."
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
            "TT",
            "CX",
            "MC",
            "CA",
            "FO",
            "CIT",
            "CH",
            "TX",
            "AX",
        ],
        "entrada": [
            "categoria_tru",
            "escala_id",
            "O_id",
            "enunciado_O",
            "material",
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
            "Sin C/L/K/Tru como salida de CE."
        ),
    },
    {
        "id": "ce_mandato_aplicar_escala",
        "nombre": "Mandato: aplicar escala Tru por id",
        "version": "2.0",
        "enunciado": (
            "Mandato del Engine: aplicar la escala indicada por id "
            "(mapa escalas_ids / catalogo TT). "
            "El descriptor de recorte lo aporta escalas_ids; "
            "cada modulo de oficio aporta lo suyo. "
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
            "TT",
            "CA",
            "FO",
            "CX",
            "MC",
            "CIT",
            "CH",
            "TX",
            "AX",
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
            "Si la escala es tru_sujeto, el mandato de sujetos orienta "
            "el deposito de sujetos/n_sujetos cuando el ciclo los produce."
        ),
    },
]


def ids() -> List[str]:
    return [str(s["id"]) for s in SKILLS if s.get("id")]


def por_id(skill_id: str):
    key = str(skill_id or "").strip().lower()
    for s in SKILLS:
        if str(s.get("id") or "").strip().lower() == key:
            return dict(s)
    return None


def listar() -> List[Dict[str, Any]]:
    return [dict(s) for s in SKILLS]
