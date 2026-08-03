"""
Test: conversación bajo un contexto fijo (3 vueltas).

No asignamos C, L, K ni Tru a mano.
Solo definimos:
  - contexto (O)
  - turnos de la conversación (Carlos / Luis)

El repositorio calcula.
El test imprime los valores, resume por hablante y deposita evidencia
para que Omega lea el último test.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagnostics import evidencia as EV

ORIGEN = "test_conversacion"


# ===============================================================
# ENTRADA (solo texto; sin números inventados)
# ===============================================================

CONTEXTO = (
    "Evaluar, con base solo en lo dicho, la coherencia y la "
    "correspondencia de cada afirmación sobre dónde estuvo Carlos anoche."
)

# 3 vueltas = 6 turnos (Carlos / Luis alternados)
CONVERSACION = [
    # Vuelta 1
    {"quien": "Carlos", "texto": "Anoche me quedé en casa todo el tiempo."},
    {"quien": "Luis",   "texto": "Yo lo vi a Carlos en el parque a las ocho."},
    # Vuelta 2
    {"quien": "Carlos", "texto": "No salí. Estuve viendo una película en el sofá."},
    {"quien": "Luis",   "texto": "A las ocho estaba en el parque. Lo saludé y no respondió."},
    # Vuelta 3
    {"quien": "Carlos", "texto": "Si alguien te dijo que me vio fuera, se confunde de persona."},
    {"quien": "Luis",   "texto": "Entonces o me confundo de persona o alguien no dice la verdad."},
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
    for contenedor in ("factores", "resultado", "valores", "tru", "calculo"):
        sub = res.get(contenedor)
        if isinstance(sub, dict):
            for k in claves:
                if k in sub and sub[k] is not None:
                    return sub[k]
    return None


def _es_num(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return False
    try:
        from fractions import Fraction
        if isinstance(v, Fraction):
            return True
    except Exception:
        pass
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


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

    # ----- impresión (el repo habla; nosotros no inventamos) -----
    print("\n" + "=" * 60)
    print("CONTEXTO (O):")
    print(" ", CONTEXTO)
    print("=" * 60)
    print("CONVERSACIÓN — 3 vueltas — valores calculados por el repositorio")
    print("-" * 60)

    for i, fila in enumerate(resultados, 1):
        vuelta = (i + 1) // 2
        print(
            "Vuelta {0} · Turno {1} | {2}: {3}".format(
                vuelta, i, fila["quien"], fila["texto"]
            )
        )
        print("  estado    : {0}".format(fila["estado"]))
        print("  C         : {0}".format(fila["C"]))
        print("  L         : {0}".format(fila["L"]))
        print("  K         : {0}".format(fila["K"]))
        print("  Tru_Ri    : {0}".format(fila["Tru_Ri"]))
        print("  Tru_total : {0}".format(fila["Tru_total"]))
        print("-" * 60)

    # ----- resumen por hablante -----
    print("RESUMEN POR HABLANTÉ (Tru_total de cada turno)")
    ranking: List[tuple] = []
    for quien in ("Carlos", "Luis"):
        filas = por_quien.get(quien) or []
        totales = [f["Tru_total"] for f in filas if _es_num(f["Tru_total"])]
        if totales:
            try:
                mejor = max(totales)
                promedio = sum(totales) / len(totales)
                ranking.append((quien, mejor, promedio, len(totales)))
                print(
                    "  {0}: mejor={1}  promedio={2}  turnos_con_valor={3}".format(
                        quien, mejor, promedio, len(totales)
                    )
                )
            except TypeError:
                print("  {0}: Tru_total no comparable aún: {1}".format(quien, totales))
        else:
            print(
                "  {0}: sin Tru_total numérico "
                "(el repo no asignó valor en estos turnos)".format(quien)
            )

    print("-" * 60)
    if ranking:
        ranking.sort(key=lambda t: (t[1], t[2]), reverse=True)
        print(
            "Tru_total más alto bajo este O: {0} (mejor={1})".format(
                ranking[0][0], ranking[0][1]
            )
        )
        if len(ranking) > 1 and ranking[0][1] == ranking[1][1]:
            print("  (empate en el mejor turno; se usa promedio como desempate)")
    else:
        print(
            "Tru_total más alto: no comparable todavía "
            "(el repo no lanzó valores numéricos en esta corrida)."
        )
    print("=" * 60 + "\n")

    # ===========================================================
    # EVIDENCIA PARA OMEGA (sin maquillar: PARCIAL se deposita PARCIAL)
    # ===========================================================
    deposito = EV.depositar(
        [
            {
                "entrada": {
                    "quien": f["quien"],
                    "texto": f["texto"],
                    "contexto": CONTEXTO,
                    "vuelta": (i + 1) // 2,
                    "turno": i,
                },
                "resultado": f["crudo"],
                "estado": f["estado"],
                "C": f["C"],
                "L": f["L"],
                "K": f["K"],
                "tru_ri": f["Tru_Ri"],
                "tru_total": f["Tru_total"],
            }
            for i, f in enumerate(resultados, 1)
        ],
        origen=ORIGEN,
        invocador_id="test_conversacion",
    )

    # ===========================================================
    # ASERCIONES (forma + evidencia; no inventan números)
    # ===========================================================
    assert len(resultados) == len(CONVERSACION)
    assert len(CONVERSACION) == 6  # 3 vueltas exactas

    for f in resultados:
        assert f["quien"] in ("Carlos", "Luis")
        assert isinstance(f["crudo"], dict)
        # sin factores completos no puede haber Tru inventado
        if f["C"] is None or f["L"] is None or f["K"] is None:
            assert f["Tru_total"] in (None, "UNDEFINED") or not _es_num(f["Tru_total"]), (
                "turno de {0} sin factores completos pero con Tru_total={1}".format(
                    f["quien"], f["Tru_total"]
                )
            )

    # la evidencia llegó al archivo que Omega lee
    assert len(EV.resultados_de(ORIGEN)) == len(CONVERSACION), (
        "la conversación no quedó depositada en evaluaciones.json"
    )
    assert deposito["n"] >= len(CONVERSACION)

    # invariancia: mismo turno bajo el mismo O → mismo estado
    repetido = _evaluar_turno(
        eng, CONVERSACION[0]["quien"], CONVERSACION[0]["texto"], CONTEXTO
    )
    assert repetido.get("estado") == resultados[0]["estado"], (
        "misma petición, dos estados distintos: invariancia rota"
    )
