# -*- coding: utf-8 -*-
"""
Caso de prueba:
Conversación multi-hablante entre Carlos y María sobre la existencia
de galaxias, estrellas y planetas.

Objetivo
--------
Evaluar una secuencia conversacional donde Carlos emite una afirmación fáctica
y María la valida, midiendo la propagación de coherencia y correlación (K)
por hablante dentro del motor VPSI utilizando el dominio astronómico.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.engine import Engine
from diagnostics import evidencia as EV

ORIGEN = "test_conversacion_estrellas"

CONTEXTO_O = (
    "Dominio cosmológico y astronómico: verificación de la existencia "
    "física de galaxias, sistemas estelares y planetarios."
)

# Secuencia de turnos conversacionales entre Carlos y María
SECUENCIA_CONVERSACION = [
    {
        "hablante": "Carlos",
        "mensaje": "Las galaxias, las estrellas y los planetas existen.",
        "enunciado_O": CONTEXTO_O,
    },
    {
        "hablante": "María",
        "mensaje": "Sí, es verdad, Carlos, las galaxias y los planetas y las estrellas sí existen.",
        "enunciado_O": CONTEXTO_O,
    }
]


def test_conversacion_estrellas():
    eng = Engine(Path("modules"), invocador_id=ORIGEN, strict=True)

    peticion = {
        "secuencia": SECUENCIA_CONVERSACION,
        "contexto": CONTEXTO_O,
        "O_context": CONTEXTO_O,
        "O_id": "O_CONVERSACION_COSMOLOGICA",
        "modo_entrada": "secuencia",
    }

    resultado = eng.evaluar(dict(peticion))
    assert isinstance(resultado, dict), "evaluar() debe devolver un diccionario"

    print("\n" + "=" * 80)
    print("TEST — CONVERSACIÓN COSMOLÓGICA (CARLOS Y MARÍA)")
    print("=" * 80)
    print("Resultado global:", resultado)
    print("=" * 80)

    # Depósito de evidencia para el reporte Omega
    EV.depositar(
        [{
            "entrada": {"secuencia": SECUENCIA_CONVERSACION},
            "resultado": resultado,
            "estado": resultado.get("estado") or resultado.get("state"),
        }],
        origen=ORIGEN,
        invocador_id=ORIGEN,
    )

    assert len(EV.resultados_de(ORIGEN)) > 0, "La evidencia debe quedar depositada."
