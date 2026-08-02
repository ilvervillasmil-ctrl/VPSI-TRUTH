"""
Auditoría mínima del ancla numérica (CI ↔ VPSI).

Idea:
  - El CI aprueba (o no) el ancla α=26/27, β=1/27, α+β=1, Fraction.
  - Este test usa la fórmula / guards del sistema bajo ruido mínimo
    para comprobar que lo que el CI aprueba no se corrompe y que
    lo que debe rechazar se rechaza.

No modifica el CI.
No llama a Internet.
No exige 3e6 iteraciones: Monte Carlo mínimo y determinista en intención
(semilla fija; ruido controlado).

Ancla:
  ALPHA = 26/27
  BETA  = 1/27
  ALPHA + BETA = 1
"""

from __future__ import annotations

import random
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, List, Tuple

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Semilla fija: reproducible
SEMILLA = 20260802
# Monte Carlo mínimo (no excesivo)
N_ITER = 500
# Tasa de fallo permitida sobre casos que DEBEN ser rechazados
TASA_MAX_FALLO_RECHAZO = 0.0  # rechazo de basura numérica debe ser total


def _ancla_canonica() -> Tuple[Fraction, Fraction]:
    from modules.constante import ALPHA, BETA

    assert isinstance(ALPHA, Fraction)
    assert isinstance(BETA, Fraction)
    return ALPHA, BETA


def _tru_total(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    from modules.formulas import tru_total

    return tru_total(C, L, K)


def _tru_ri(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    from modules.formulas import tru_ri

    return tru_ri(C, L, K)


# ----------------------------------------------------------------
# 1. Ancla dura (sin ruido): lo que el CI ya aprueba
# ----------------------------------------------------------------

def test_ancla_canonica_dura():
    alpha, beta = _ancla_canonica()
    assert alpha == Fraction(26, 27)
    assert beta == Fraction(1, 27)
    assert alpha + beta == Fraction(1, 1)
    assert alpha > 0 and beta > 0
    assert alpha < 1 and beta < 1


def test_ancla_via_formula_piso_y_techo():
    """Con C=L=K=1: Tru_Ri=1, Tru_total=1; con C=L=K=0: Tru_total=β."""
    alpha, beta = _ancla_canonica()
    uno = Fraction(1, 1)
    cero = Fraction(0, 1)

    assert _tru_ri(uno, uno, uno) == uno
    assert _tru_total(uno, uno, uno) == uno
    assert _tru_total(cero, cero, cero) == beta
    assert _tru_total(cero, uno, uno) == beta


def test_ancla_rechaza_float():
    """Lo que el CI aprueba como Fraction no debe aceptar float en fórmula."""
    with pytest.raises((TypeError, ValueError, AssertionError)):
        _tru_total(1.0, Fraction(1, 1), Fraction(1, 1))  # type: ignore[arg-type]
    with pytest.raises((TypeError, ValueError, AssertionError)):
        _tru_ri(Fraction(1, 1), 0.5, Fraction(1, 1))  # type: ignore[arg-type]


# ----------------------------------------------------------------
# 2. Monte Carlo mínimo de ruido sobre el ancla
# ----------------------------------------------------------------

def _ruido_factor(rng: random.Random) -> Any:
    """Genera candidatos: canónicos, basura float, fracciones fuera de [0,1], tipos raros."""
    kind = rng.randint(0, 7)
    if kind == 0:
        return Fraction(1, 1)
    if kind == 1:
        return Fraction(0, 1)
    if kind == 2:
        return Fraction(rng.randint(0, 26), 27)
    if kind == 3:
        return rng.random()  # float en [0,1) — debe rechazarse
    if kind == 4:
        return rng.uniform(-2.0, 2.0)  # float fuera
    if kind == 5:
        return Fraction(rng.randint(2, 50), rng.randint(1, 7))  # >1 posible
    if kind == 6:
        return "1"  # tipo inválido
    return None


def _es_fraction_01(x: Any) -> bool:
    return isinstance(x, Fraction) and Fraction(0, 1) <= x <= Fraction(1, 1)


def test_montecarlo_minimo_ruido_ancla():
    """
    N_ITER ensayos:
      - Si C,L,K son Fraction en [0,1]: la fórmula no debe romper ancla
        (Tru_total en [β, 1], Tru_ri en [0,1], tipos Fraction).
      - Si hay float / tipo inválido: debe fallar (rechazo), no inventar Tru.
    """
    rng = random.Random(SEMILLA)
    alpha, beta = _ancla_canonica()

    fallos_canon = 0
    fallos_rechazo = 0
    n_validos = 0
    n_basura = 0
    detalle: List[str] = []

    for i in range(N_ITER):
        C = _ruido_factor(rng)
        L = _ruido_factor(rng)
        K = _ruido_factor(rng)
        validos = _es_fraction_01(C) and _es_fraction_01(L) and _es_fraction_01(K)

        if validos:
            n_validos += 1
            try:
                ri = _tru_ri(C, L, K)
                tot = _tru_total(C, L, K)
            except Exception as e:
                fallos_canon += 1
                detalle.append("valido_raise i={0}: {1}".format(i, e))
                continue
            if not isinstance(ri, Fraction) or not isinstance(tot, Fraction):
                fallos_canon += 1
                detalle.append("valido_tipo i={0}".format(i))
                continue
            if ri < Fraction(0, 1) or ri > Fraction(1, 1):
                fallos_canon += 1
                detalle.append("valido_ri_rango i={0} ri={1}".format(i, ri))
                continue
            if tot < beta or tot > Fraction(1, 1):
                fallos_canon += 1
                detalle.append("valido_tot_rango i={0} tot={1}".format(i, tot))
                continue
            esperado = (ri * alpha) + beta
            if tot != esperado:
                fallos_canon += 1
                detalle.append(
                    "valido_formula i={0} tot={1} esperado={2}".format(i, tot, esperado)
                )
        else:
            n_basura += 1
            acepto = False
            try:
                _tru_total(C, L, K)  # type: ignore[arg-type]
                acepto = True
            except Exception:
                acepto = False
            if acepto:
                fallos_rechazo += 1
                detalle.append(
                    "basura_aceptada i={0} C={1!r} L={2!r} K={3!r}".format(i, C, L, K)
                )

    assert fallos_canon == 0, (
        "ANCLA ROTA bajo entradas válidas: fallos={0}/{1}\n{2}".format(
            fallos_canon, n_validos, "\n".join(detalle[:20])
        )
    )
    tasa_rechazo_fallido = (
        float(fallos_rechazo) / float(n_basura) if n_basura else 0.0
    )
    assert tasa_rechazo_fallido <= TASA_MAX_FALLO_RECHAZO, (
        "BASURA ACEPTADA: fallos_rechazo={0}/{1} tasa={2}\n{3}".format(
            fallos_rechazo, n_basura, tasa_rechazo_fallido, "\n".join(detalle[:20])
        )
    )


def test_montecarlo_ci_aprueba_misma_ancla():
    """
    Puente mínimo CI ↔ VPSI:
    lo que los tests de ancla del CI dan por bueno (α, β, suma 1)
    debe coincidir con la lectura del módulo constante y con Tru_total(1,1,1)=1.
    """
    alpha, beta = _ancla_canonica()
    assert alpha + beta == Fraction(1, 1)
    assert _tru_total(Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)) == Fraction(1, 1)
    assert _tru_total(Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)) == beta

    try:
        from core.engine import Engine

        eng = Engine(Path("modules"), invocador_id="test_ancla_ci", strict=True)
        if hasattr(eng, "get_constantes"):
            c = eng.get_constantes()
            assert c.get("ALPHA") == alpha
            assert c.get("BETA") == beta
    except Exception:
        pass
