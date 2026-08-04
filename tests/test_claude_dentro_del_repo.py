# tests/test_claude_dentro_del_repo.py
# -*- coding: utf-8 -*-
"""
Test: afirmacion de Claude sobre su propia participacion.

O declarado : ubicacion de Claude respecto del repositorio.
D           : afirmacion verificable contra esta conversacion.

Proposito del caso: la afirmacion es VERDADERA en su totalidad.
Si Tru_total sale bajo, el numero dice algo sobre el instrumento,
no sobre la verdad de lo afirmado. Esa distincion es lo que se
quiere medir.

El texto contiene a proposito:
  - marcadores de contradiccion ("aunque")
  - una tension real de contenido: no invento / lo escribio sin verificar
  - tokens que SI solapan con O (repositorio, engine, dentro)
  - tokens que NO solapan (conteos, barrido, axiomatico, declaraciones)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.engine import Engine
from diagnostics import evidencia as EV

ORIGEN = "test_claude_dentro_del_repo"

CONTEXTO_O = (
    "Ubicación de Claude durante esta conversación: si Claude estuvo "
    "o no dentro del repositorio VPSI-TRUTH, entendido como haber "
    "ejecutado su código y leído sus archivos."
)

DECLARACION = (
    "Estuve dentro del repositorio. "
    "Ejecuté el engine y medí sus factores. "
    "Leí conteos punto py línea por línea. "
    "No inventé el rol RE, aunque sí lo escribí sin verificarlo. "
    "Corrí el barrido axiomático y dio 487 declaraciones sin choques. "
    "No leí los 487 axiomas."
)


def test_claude_dentro_del_repo():
    eng = Engine("modules", invocador_id="core")

    peticion = {
        "mensaje": DECLARACION,
        "descripcion": DECLARACION,
        "contexto": CONTEXTO_O,
        "O_context": CONTEXTO_O,
        "O_id": "O_CLAUDE_REPO",
        "enunciado_O": CONTEXTO_O,
        "modo_entrada": "auditoria",
    }

    r = eng.evaluar(dict(peticion))

    print("=" * 70)
    print("TEST — afirmación de Claude sobre su participación")
    print("=" * 70)
    print("O : {0}".format(CONTEXTO_O))
    print()
    print("D : {0}".format(DECLARACION))
    print("-" * 70)
    print("estado    : {0}".format(r.get("estado")))
    print("factores  : {0}".format(r.get("factores")))
    print("Tru_Ri    : {0}".format(r.get("tru_ri")))
    print("Tru_total : {0}".format(r.get("tru_total")))

    tt = r.get("tru_total")
    if tt is not None:
        try:
            from fractions import Fraction
            print("            = {0:.6f}".format(float(Fraction(str(tt)))))
        except Exception:
            pass

    # ----- detalle del conteo -----
    try:
        from modules.calculator.conteos import extraer_conteos
        cts = extraer_conteos(dict(peticion))

        print("-" * 70)
        print("m={0}  p={1}  c={2}".format(cts["m"], cts["p"], cts["c"]))
        print("k={0}  r={1}  f={2}".format(
            cts["contradicciones"], cts["reversiones"],
            cts["afirmaciones_falsas"],
        ))
        print("procedencia_texto : {0}".format(cts["procedencia_texto"]))
        print("texto_es_o        : {0}".format(cts["texto_es_o"]))
        print("resolucion C/L/K  : {0} / {1} / {2}".format(
            cts["resolucion_C"], cts["resolucion_L"], cts["resolucion_K"],
        ))
        print("stoplist          : restó {0} de {1} tokens".format(
            cts["tokens_restados"], cts["tokens_brutos"],
        ))

        print()
        print("k_detalle (contradicciones):")
        if cts["k_detalle"]:
            for u, w in cts["k_detalle"]:
                print("   [{0}]  {1}".format(w, u))
        else:
            print("   (ninguna)")

        print()
        print("f_detalle (divergencia contra O):")
        if cts["f_detalle"]:
            for u, w in cts["f_detalle"]:
                print("   [{0}]  {1}".format(w, u))
        else:
            print("   (ninguna: toda afirmación ancló en O)")

        print()
        print("unidades ({0}):".format(len(cts["unidades"])))
        for i, u in enumerate(cts["unidades"], 1):
            print("   {0}. {1}".format(i, u))

    except Exception as e:
        print("no se pudo leer el detalle: {0}: {1}".format(
            type(e).__name__, e
        ))
        cts = {}

    print("=" * 70)

    # ----- depósito para Omega -----
    EV.depositar(
        [{
            "entrada": {
                "quien": "Claude",
                "texto": DECLARACION,
                "contexto": CONTEXTO_O,
            },
            "resultado": r,
            "estado": r.get("estado"),
            "tru_ri": r.get("tru_ri"),
            "tru_total": r.get("tru_total"),
        }],
        origen=ORIGEN,
        invocador_id=ORIGEN,
    )

    # ----- aserciones -----
    assert isinstance(r, dict)
    assert len(EV.resultados_de(ORIGEN)) == 1

    # no se inventan números: sin factores completos no hay Tru
    fac = r.get("factores") or {}
    if any(fac.get(x) in (None, "UNDEFINED") for x in ("C", "L", "K")):
        assert r.get("tru_total") in (None, "UNDEFINED")

    # invariancia: misma petición, mismo estado
    r2 = eng.evaluar(dict(peticion))
    assert r2.get("estado") == r.get("estado")


if __name__ == "__main__":
    test_claude_dentro_del_repo()
