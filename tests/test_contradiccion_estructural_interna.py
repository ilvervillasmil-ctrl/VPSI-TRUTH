# -*- coding: utf-8 -*-
"""
Dictamen VPSI de una declaración completa.
Un emisor, un texto, un O declarado.
"""

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.engine import Engine
from modules.calculator.conteos import extraer_conteos

CONTEXTO_O = (
    "Coherencia interna del discurso del emisor: si el emisor se "
    "contradice a sí mismo dentro de esta misma declaración."
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


def test_dictamen_declaracion():
    eng = Engine("modules", invocador_id="core")

    peticion = {
        "mensaje": DECLARACION,
        "descripcion": DECLARACION,
        "contexto": CONTEXTO_O,
        "O_context": CONTEXTO_O,
        "O_id": "O_COHERENCIA_DISCURSO",
        "enunciado_O": CONTEXTO_O,
        "modo_entrada": "auditoria",
    }

    r = eng.evaluar(dict(peticion))
    cts = extraer_conteos(dict(peticion))
    fac = r.get("factores") or {}

    print("=" * 72)
    print("DICTAMEN VPSI — declaración completa")
    print("=" * 72)
    print("O:", CONTEXTO_O)
    print()
    print("D:", DECLARACION)
    print("-" * 72)
    print("  estado    :", r.get("estado"))
    print("  C         :", fac.get("C"))
    print("  L         :", fac.get("L"))
    print("  K         :", fac.get("K"))
    print("  Tru_Ri    :", r.get("tru_ri"))
    print("  Tru_total :", r.get("tru_total"), end="")

    tt = r.get("tru_total")
    if tt is not None and str(tt).upper() != "UNDEFINED":
        try:
            print("   =", "{0:.6f}".format(float(Fraction(str(tt)))))
        except Exception:
            print()
    else:
        print()

    print("-" * 72)
    print("  m / p / c :", cts.get("m"), "/", cts.get("p"), "/", cts.get("c"))
    print("  k / r / f :", cts.get("contradicciones"), "/",
          cts.get("reversiones"), "/", cts.get("afirmaciones_falsas"))
    print("  resolución:", cts.get("resolucion_C"), "/",
          cts.get("resolucion_L"), "/", cts.get("resolucion_K"))
    print("  procedencia:", cts.get("procedencia_texto"),
          " texto_es_o:", cts.get("texto_es_o"))
    print("  stoplist  : restó", cts.get("tokens_restados"),
          "de", cts.get("tokens_brutos"), "tokens")

    print()
    print("  unidades:")
    for i, u in enumerate(cts.get("unidades") or [], 1):
        print("    ", i, ".", u)

    print()
    print("  k_detalle:")
    if cts.get("k_detalle"):
        for u, w in cts["k_detalle"]:
            print("     ", w, "|", u)
    else:
        print("      ninguna")

    print()
    print("  f_detalle:")
    if cts.get("f_detalle"):
        for u, w in cts["f_detalle"]:
            print("     ", w, "|", u)
    else:
        print("      ninguna")

    print("=" * 72)

    assert isinstance(r, dict)


if __name__ == "__main__":
    test_dictamen_declaracion()
