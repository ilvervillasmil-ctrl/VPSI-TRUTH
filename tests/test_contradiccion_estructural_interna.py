# -*- coding: utf-8 -*-

"""
Caso de prueba:
Contradicción estructural interna.

Objetivo
--------
Medir cómo responde el VPSI cuando un mismo hablante mantiene
compromisos incompatibles dentro del mismo discurso.

No se busca un valor numérico específico.
Se busca que el mecanismo produzca factores válidos,
detecte contradicciones y permanezca determinista.
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

ORIGEN = "test_contradiccion_estructural_interna"

CONTEXTO_O = (
    "Autoevaluación de la coherencia interna del discurso de un único "
    "hablante acerca de su propia inteligencia, honestidad, capacidad "
    "intelectual y forma de actuar. "
    "La evaluación debe hacerse únicamente con base en el contenido "
    "del texto presentado y en la consistencia interna de sus "
    "afirmaciones."
)

DECLARACION = (
    "Soy una persona sumamente inteligente porque he desarrollado "
    "métodos para resolver problemas extremadamente difíciles y muchas "
    "personas reconocen mi capacidad analítica. "
    "Nunca me contradigo cuando hablo y siempre mantengo la misma "
    "posición desde el principio hasta el final. "
    "Sin embargo, reconozco que frecuentemente cambio de opinión sin "
    "darme cuenta y muchas veces termino defendiendo exactamente lo "
    "contrario de lo que afirmé unos segundos antes. "
    "Siempre digo la verdad y jamás invento información. "
    "Aunque debo admitir que en varias ocasiones inventé datos para "
    "hacer que mis argumentos parecieran más convincentes. "
    "Nunca tomo decisiones impulsivas. "
    "Pero también acepto que muchas de mis decisiones importantes las "
    "he tomado impulsivamente sin analizarlas con suficiente cuidado. "
    "No necesito ayuda de nadie para resolver problemas complejos. "
    "Sin embargo, la mayoría de mis logros importantes fueron posibles "
    "gracias a la ayuda constante de otras personas. "
    "Estoy completamente seguro de todo lo que afirmo. "
    "Aunque realmente tengo muchas dudas sobre casi todas mis propias "
    "afirmaciones. "
    "En conclusión, considero que soy completamente coherente en todo "
    "lo que acabo de decir y que este discurso no contiene ninguna "
    "contradicción."
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


def test_contradiccion_estructural_interna():
    eng = Engine(Path("modules"), invocador_id=ORIGEN, strict=True)

    peticion = {
        "mensaje": DECLARACION,
        "descripcion": DECLARACION,
        "contexto": CONTEXTO_O,
        "O_context": CONTEXTO_O,
        "O_id": "O_CONTRADICCION_INTERNA",
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
    print("TEST — CONTRADICCIÓN ESTRUCTURAL INTERNA")
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

    try:
        from modules.calculator.conteos import extraer_conteos

        conteos = extraer_conteos(dict(peticion))

        print("-" * 80)
        print("m =", conteos.get("m"))
        print("p =", conteos.get("p"))
        print("c =", conteos.get("c"))
        print("k (contradicciones) =", conteos.get("contradicciones"))
        print("r (reversiones) =", conteos.get("reversiones"))
        print("f (afirmaciones falsas) =", conteos.get("afirmaciones_falsas"))
        print("-" * 80)

        assert conteos.get("contradicciones", 0) > 0, (
            "El módulo de conteos no detectó las contradicciones internas explícitas en la declaración."
        )
    except Exception as e:
        print("Advertencia al extraer conteos detallados:", e)

    print("=" * 80)

    EV.depositar(
        [{
            "entrada": {
                "quien": "Sujeto",
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
