"""
Test simple: conversación bajo un contexto fijo.

No asignamos C, L, K ni Tru a mano.
Solo definimos:
  - contexto (O)
  - turnos de la conversación (Carlos / Luis)

El repositorio calcula.
El test imprime los valores y reporta quién tuvo Tru_total más alto.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ===============================================================
# ENTRADA (solo texto; sin números inventados)
# ===============================================================

CONTEXTO = (
    "Evaluar la coherencia y veracidad de lo afirmado sobre lo que Carlos hizo anoche."
)

CONVERSACION = [
    {"quien": "Carlos", "texto": "Anoche me quedé en casa todo el tiempo."},
    {"quien": "Luis", "texto": "Yo lo vi a Carlos en el parque a las ocho."},
    {"quien": "Carlos", "texto": "No salí. Estuve viendo una película."},
    {"quien": "Luis", "texto": "Entonces o me confundo de persona o alguien no dice la verdad."},
]


def _evaluar_turno(eng: Any, quien: str, texto: str, contexto: str) -> Dict[str, Any]:
    peticion = {
        "modo_entrada": "auditoria",
        "O_id": "O_conversacion_test",
        "enunciado_O": contexto,
        "O_context": contexto,
        "descripcion": "{0}: {1}".format(quien, texto),
        "mensaje": texto,
        "quien": quien,
        "contexto": contexto,
    }
    if hasattr(eng, "evaluar"):
        return eng.evaluar(peticion)
    raise RuntimeError("Engine sin capacidad evaluar()")


def _extraer_valor(res: Dict[str, Any], *claves: str) -> Any:
    for k in claves:
        if k in res and res[k] is not None:
            return res[k]
    for contenedor in ("factores", "resultado", "valores", "tru"):
        sub = res.get(contenedor)
        if isinstance(sub, dict):
            for k in claves:
                if k in sub and sub[k] is not None:
                    return sub[k]
    return None


def test_conversacion_calcula_tru_por_hablante():
    from core.engine import Engine

    eng = Engine(Path("modules"), invocador_id="test_conversacion", strict=True)

    resultados: List[Dict[str, Any]] = []
    por_quien: Dict[str, List[Dict[str, Any]]] = {}

    for turno in CONVERSACION:
        quien = turno["quien"]
        texto = turno["texto"]
        res = _evaluar_turno(eng, quien, texto, CONTEXTO)
        assert isinstance(res, dict), "evaluar() debe devolver dict"

        fila = {
            "quien": quien,
            "texto": texto,
            "estado": res.get("estado") or res.get("state"),
            "C": _extraer_valor(res, "C", "c", "coherencia"),
            "L": _extraer_valor(res, "L", "l", "logica"),
            "K": _extraer_valor(res, "K", "k", "correlacion"),
            "Tru_Ri": _extraer_valor(res, "Tru_Ri", "tru_ri", "TruRi"),
            "Tru_total": _extraer_valor(res, "Tru_total", "tru_total", "TruTotal"),
            "crudo": res,
        }
        resultados.append(fila)
        por_quien.setdefault(quien, []).append(fila)

    print("\n" + "=" * 60)
    print("CONTEXTO:")
    print(" ", CONTEXTO)
    print("=" * 60)
    print("CONVERSACIÓN Y VALORES CALCULADOS POR EL REPOSITORIO")
    print("-" * 60)
    for i, fila in enumerate(resultados, 1):
        print("Turno {0} | {1}: {2}".format(i, fila["quien"], fila["texto"]))
        print("  estado    : {0}".format(fila["estado"]))
        print("  C         : {0}".format(fila["C"]))
        print("  L         : {0}".format(fila["L"]))
        print("  K         : {0}".format(fila["K"]))
        print("  Tru_Ri    : {0}".format(fila["Tru_Ri"]))
        print("  Tru_total : {0}".format(fila["Tru_total"]))
        print("-" * 60)

    print("RESUMEN POR HABLANTÉ")
    ranking = []
    for quien, filas in por_quien.items():
        totales = [f["Tru_total"] for f in filas if f["Tru_total"] is not None]
        if totales:
            try:
                mejor = max(totales)
                ranking.append((quien, mejor))
                print("  {0}: Tru_total (mejor turno) = {1}".format(quien, mejor))
            except TypeError:
                print("  {0}: Tru_total no comparable aún: {1}".format(quien, totales))
        else:
            print(
                "  {0}: sin Tru_total numérico aún "
                "(el repo no asignó valor en estos turnos)".format(quien)
            )

    if ranking:
        ranking.sort(key=lambda x: x[1], reverse=True)
        print("-" * 60)
        print("Tru_total más alto: {0} = {1}".format(ranking[0][0], ranking[0][1]))
    else:
        print("-" * 60)
        print(
            "Tru_total más alto: no comparable todavía "
            "(el repo no lanzó valores numéricos en esta corrida)."
        )
    print("=" * 60 + "\n")

    assert len(resultados) == len(CONVERSACION)
    for fila in resultados:
        assert fila["quien"] in ("Carlos", "Luis")
        assert isinstance(fila["crudo"], dict)
