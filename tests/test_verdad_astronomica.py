# -*- coding: utf-8 -*-
"""
Caso de prueba:
Verdad astronómica objetiva (El Sol en la Vía Láctea).

Objetivo
--------
Evaluar una afirmación fáctica verdadera sobre la realidad física
utilizando el dominio de astronomía para medir una alta correlación (K)
y un valor de verdad (Tru_total) elevado respaldado por hechos.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.engine import Engine
from diagnostics import evidencia as EV

ORIGEN = "test_verdad_astronomica"

CONTEXTO_O = (
    "Contraste de material astronómico: observaciones, modelos celestes "
    "y ubicación del Sol dentro del sistema solar y la galaxia Vía Láctea."
)

DECLARACION = (
    "El Sol es una estrella ubicada en el sistema solar, el cual forma parte "
    "de nuestra galaxia, la Vía Láctea."
)


def _extraer_valor(res: Dict[str, Any], *claves: str) -> Any:
    for k in claves:
        if k in res and res[k] is not None:
            return res[k]
    for contenedor in ("factores", "resultado", "valores", "tru", "calculo"):
        sub = res.get(contenedor)
        if isinstance(sub, dict):
            for k in claves:
                if k in sub and sub[k] is not None:
                    return sub[k]
    return None


def test_verdad_astronomica():
    eng = Engine(Path("modules"), invocador_id=ORIGEN, strict=True)

    peticion = {
        "mensaje": DECLARACION,
        "descripcion": DECLARACION,
        "contexto": CONTEXTO_O,
        "O_context": CONTEXTO_O,
        "O_id": "O_ASTRONOMIA_SOL",
        "enunciado_O": CONTEXTO_O,
        "modo_entrada": "auditoria",
    }

    resultado = eng.evaluar(dict(peticion))
    assert isinstance(resultado, dict), "evaluar() debe devolver dict"

    c_val = _extraer_valor(resultado, "C", "c", "coherencia")
    l_val = _extraer_valor(resultado, "L", "l", "logica")
    k_val = _extraer_valor(resultado, "K", "k", "correlacion")
    tru_ri = _extraer_valor(resultado, "Tru_Ri", "tru_ri", "TruRi")
    tru_total = _extraer_valor(resultado, "Tru_total", "tru_total", "TruTotal")

    print("\n" + "=" * 80)
    print("TEST — VERDAD ASTRONÓMICA OBJETIVA")
    print("=" * 80)
    print("C           :", c_val)
    print("L           :", l_val)
    print("K           :", k_val)
    print("Tru_total   :", tru_total)
    print("=" * 80)

    # Verificamos que al tener un contexto físico real y una afirmación alineada,
    # el motor evalúe los factores de manera limpia y sin contradicciones (k = 0).
    from modules.calculator.conteos import extraer_conteos
    conteos = extraer_conteos(dict(peticion))

    print("Contradicciones detectadas (k):", conteos.get("contradicciones"))
    assert conteos.get("contradicciones", 0) == 0, "Una verdad fáctica clara no debe generar contradicciones internas."

    # Depósito de evidencia para Omega
    EV.depositar(
        [{
            "entrada": {
                "quien": "Sistema",
                "texto": DECLARACION,
                "contexto": CONTEXTO_O,
            },
            "resultado": resultado,
            "estado": resultado.get("estado") or resultado.get("state"),
            "C": c_val,
            "L": l_val,
            "K": k_val,
            "tru_ri": tru_ri,
            "tru_total": tru_total,
        }],
        origen=ORIGEN,
        invocador_id=ORIGEN,
    )

    assert len(EV.resultados_de(ORIGEN)) > 0, "La evidencia no quedó depositada."

    # Comprobación de invariancia determinista
    r2 = eng.evaluar(dict(peticion))
    assert _extraer_valor(r2, "Tru_total", "tru_total", "TruTotal") == tru_total, (
        "Invariancia rota: Tru_total cambió en la segunda ejecución."
    )
