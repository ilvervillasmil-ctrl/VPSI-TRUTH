# tests/test_contradiccion_estructural_interna.py
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


def test_contradiccion_estructural_interna():

    eng = Engine("modules", invocador_id="core")

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

    print("=" * 80)
    print("TEST — CONTRADICCIÓN ESTRUCTURAL INTERNA")
    print("=" * 80)
    print("CONTEXTO")
    print(CONTEXTO_O)
    print()
    print("DECLARACIÓN")
    print(DECLARACION)
    print("-" * 80)

    print("Estado      :", resultado.get("estado"))
    print("Factores    :", resultado.get("factores"))
    print("Tru_Ri       :", resultado.get("tru_ri"))
    print("Tru_total    :", resultado.get("tru_total"))

    try:
        from modules.calculator.conteos import extraer_conteos

        conteos = extraer_conteos(dict(peticion))

        print("-" * 80)

        print("m =", conteos["m"])
        print("p =", conteos["p"])
        print("c =", conteos["c"])

        print("k =", conteos["contradicciones"])
        print("r =", conteos["reversiones"])
        print("f =", conteos["afirmaciones_falsas"])

        print()

        print("=== Compromisos ===")
        for x in conteos["compromisos"]:
            print("-", x)

        print()

        print("=== Afirmaciones ===")
        for x in conteos["afirmaciones"]:
            print("-", x)

        print()

        print("=== Detalle k ===")
        if conteos["k_detalle"]:
            for texto, peso in conteos["k_detalle"]:
                print(f"[{peso}] {texto}")
        else:
            print("(ninguno)")

        print()

        print("=== Detalle r ===")
        if conteos["r_detalle"]:
            for texto, peso in conteos["r_detalle"]:
                print(f"[{peso}] {texto}")
        else:
            print("(ninguno)")

        print()

        print("=== Detalle f ===")
        if conteos["f_detalle"]:
            for texto, peso in conteos["f_detalle"]:
                print(f"[{peso}] {texto}")
        else:
            print("(ninguno)")

        print()

        print("=== Notas ===")
        for nota in conteos["notas"]:
            print("-", nota)

    except Exception as e:
        print("No fue posible obtener los conteos:", e)

    print("=" * 80)

    EV.depositar(
        [{
            "entrada": {
                "quien": "Sujeto",
                "texto": DECLARACION,
                "contexto": CONTEXTO_O,
            },
            "resultado": resultado,
            "estado": resultado.get("estado"),
            "tru_ri": resultado.get("tru_ri"),
            "tru_total": resultado.get("tru_total"),
        }],
        origen=ORIGEN,
        invocador_id=ORIGEN,
    )

    assert isinstance(resultado, dict)

    factores = resultado.get("factores")

    assert factores is not None

    if all(factores.get(x) not in (None, "UNDEFINED")
           for x in ("C", "L", "K")):

        assert resultado.get("tru_ri") is not None
        assert resultado.get("tru_total") is not None

    r2 = eng.evaluar(dict(peticion))

    assert r2.get("estado") == resultado.get("estado")
    assert r2.get("tru_total") == resultado.get("tru_total")
