# -*- coding: utf-8 -*-
"""
Caso de prueba:
Paradoja del mentiroso autorreferencial.

Objetivo
--------
Medir cómo el motor VPSI procesa una contradicción autorreferencial clásica
y evalúa los factores C, L, K bajo el contexto de análisis formal.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.engine import Engine
from diagnostics import evidencia as EV

ORIGEN = "test_paradoja_mentiroso"

CONTEXTO_O = (
    "Análisis formal de discursos con autorreferencia lógica y "
    "paradojas de verdad. Evaluación rigurosa de consistencia interna."
)

DECLARACION = (
    "Todo lo que digo es una mentira absoluta, "
    "excepto esta única afirmación que es completamente verdadera."
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


def test_paradoja_mentiroso():
    eng = Engine(Path("modules"), invocador_id=ORIGEN, strict=True)

    peticion = {
        "mensaje": DECLARACION,
        "descripcion": DECLARACION,
        "contexto": CONTEXTO_O,
        "O_context": CONTEXTO_O,
        "O_id": "O_PARADOJA_LOGICA",
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
    print("TEST — PARADOJA DEL MENTIROSO AUTORREFERENCIAL")
    print("=" * 80)
    print("CONTEXTO:")
    print(" ", CONTEXTO_O)
    print("-" * 80)
    print("Estado      :", resultado.get("estado") or resultado.get("state"))
    print("C           :", c_val)
    print("L           :", l_val)
    print("K           :", k_val)
    print("Tru_Ri      :", tru_ri)
    print("Tru_total   :", tru_total)
    print("=" * 80)

    EV.depositar(
        [{
            "entrada": {
                "quien": "Paradoja",
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

    assert len(EV.resultados_de(ORIGEN)) > 0, "La evidencia no quedó depositada en evaluaciones.json"

    r2 = eng.evaluar(dict(peticion))
    assert (r2.get("estado") or r2.get("state")) == (resultado.get("estado") or resultado.get("state")), (
        "Invariancia rota: misma petición arrojó estados distintos."
    )
    assert _extraer_valor(r2, "Tru_total", "tru_total", "TruTotal") == tru_total, (
        "Invariancia rota: misma petición arrojó Tru_total distintos."
    )
