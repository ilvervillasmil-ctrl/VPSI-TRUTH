#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTE CARLO ADVERSARIAL — nodo-invisible / OmegaEngine

Objeto bajo prueba (todo importado del repo, sin oraculo interno):

    formulas.truth_VPSI.TruthTheorem.compute_total_truth(c, l, k)
    core.engine.OmegaEngine.apply_vpsi_truth(C, L, K)
    core.engine.OmegaEngine.compute_coherence(layers_data, C1, C2, theta)
    formulas.constants.ALPHA / BETA / PHI / LAYER_FRICTION

Axiomas verificados (los que el propio repo declara en truth_VPSI.py):

    A2  piso beta        Tru_total nunca por debajo de BETA
    A3  cota alpha       Tru_total nunca por encima de ALPHA + BETA
    A4  unidad           ALPHA + BETA == 1
    A5  interdependencia un factor nulo colapsa Tru_total a BETA
    A6  cota informac.   ninguna Ri produce mas que R
    A7  invariancia      misma entrada, misma salida

REGLAS DE CONTEO

    - Solo mide codigo importado. Sin formula de referencia local.
    - Familia de caso fijo: criterio CERO FALLOS.
      Familia con muestreo: criterio tasa < umbral.
    - Familia sin una sola medicion = FAIL: no medir no es aprobar.

Uso:
    pytest  tests/test_montecarlo_omega.py
    python  tests/test_montecarlo_omega.py --n 50000 --verbose
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ===============================================================
# SEGMENTO 1 --- PARAMETROS
# ===============================================================

N_STOCH = 20_000
UMBRAL = 0.0          # tolerancia cero: son invariantes, no estadistica
SEED = 0x0DE_C0_DE
EPS = 1e-12

# ===============================================================
# SEGMENTO 2 --- RAIZ E IMPORTS
# ===============================================================

MARCAS_RAIZ = ("pyproject.toml", "setup.py", "requirements.txt", ".git",
               "core", "formulas")


def raiz_repo() -> Path:
    aqui = Path(__file__).resolve()
    candidata = aqui.parent
    for base in [aqui.parent] + list(aqui.parents):
        if (base / "core").is_dir() and (base / "formulas").is_dir():
            return base
        if any((base / m).exists() for m in MARCAS_RAIZ):
            candidata = base
    return candidata


_ERR: List[str] = []
TruthTheorem = None
OmegaEngine = None
PurposeAlignmentError = None
ALPHA = BETA = PHI = None
ALPHA_ENGINE = BETA_ENGINE = None
LAYER_FRICTION: List[float] = []
NUM_LAYERS = 0


def cargar(raiz: Path) -> None:
    global TruthTheorem, OmegaEngine, PurposeAlignmentError
    global ALPHA, BETA, PHI, ALPHA_ENGINE, BETA_ENGINE
    global LAYER_FRICTION, NUM_LAYERS

    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))

    try:
        from formulas.constants import (ALPHA as A, BETA as B, PHI as P,
                                        LAYER_FRICTION as LF, NUM_LAYERS as NL)
        ALPHA, BETA, PHI = A, B, P
        LAYER_FRICTION, NUM_LAYERS = list(LF), NL
    except Exception as e:
        _ERR.append(f"formulas.constants: {type(e).__name__}: {e}")

    try:
        from formulas.truth_VPSI import TruthTheorem as T
        TruthTheorem = T
    except Exception as e:
        _ERR.append(f"formulas.truth_VPSI: {type(e).__name__}: {e}")

    try:
        from core.engine import (OmegaEngine as OE,
                                 PurposeAlignmentError as PAE,
                                 ALPHA_VPSI, BETA_VPSI)
        OmegaEngine, PurposeAlignmentError = OE, PAE
        ALPHA_ENGINE, BETA_ENGINE = ALPHA_VPSI, BETA_VPSI
    except Exception as e:
        _ERR.append(f"core.engine: {type(e).__name__}: {e}")

# ===============================================================
# SEGMENTO 3 --- REGISTRO
# ===============================================================

@dataclass
class Fallo:
    familia: str
    axioma: str
    fuente: str
    entrada: str
    observado: str
    causa: str


@dataclass
class Familia:
    nombre: str
    axioma: str
    fuente: str
    fija: bool
    ok: int = 0
    fallos: int = 0
    vacios: int = 0

    @property
    def medidos(self) -> int:
        return self.ok + self.fallos

    @property
    def tasa(self) -> float:
        return self.fallos / self.medidos if self.medidos else 0.0


@dataclass
class Registro:
    familias: Dict[str, Familia] = field(default_factory=dict)
    detalle: List[Fallo] = field(default_factory=list)
    max_detalle: int = 20

    def _f(self, n, ax="", src="", fija=True) -> Familia:
        if n not in self.familias:
            self.familias[n] = Familia(n, ax, src, fija)
        return self.familias[n]

    def ok(self, n, ax="", src="", fija=True):
        self._f(n, ax, src, fija).ok += 1

    def vacio(self, n, ax="", src="", fija=True):
        self._f(n, ax, src, fija).vacios += 1

    def fail(self, n, ax, src, entrada, observado, causa, fija=True):
        self._f(n, ax, src, fija).fallos += 1
        if len(self.detalle) < self.max_detalle:
            self.detalle.append(Fallo(n, ax, src, entrada, observado, causa))

# ===============================================================
# SEGMENTO 4 --- MUESTREO
# ===============================================================

def factor_en_rango(rng: random.Random) -> float:
    """C, L, K dentro del dominio declarado [0,1]."""
    r = rng.random()
    if r < 0.10:
        return 0.0
    if r < 0.20:
        return 1.0
    return rng.random()


def factor_fuera_de_rango(rng: random.Random) -> float:
    """Adversarial: el dominio se declara [0,1]; se golpea fuera."""
    return rng.choice([
        -rng.random() * 10,
        1.0 + rng.random() * 10,
        float("inf") if rng.random() < 0.05 else rng.random() * -1,
    ])


def capas_validas(rng: random.Random, n: int = 7) -> List[Dict[str, float]]:
    """L6 (indice 6) con phi = 0.0: el motor lo exige."""
    capas = [{"L": rng.random(), "phi": rng.random() * 0.2}
             for _ in range(n - 1)]
    capas.append({"L": rng.random(), "phi": 0.0})
    return capas

# ===============================================================
# SEGMENTO 5 --- FAMILIAS DE ATAQUE
# ===============================================================

def f1_unidad(reg: Registro) -> None:
    """A4: ALPHA + BETA == 1, y las dos fuentes de ALPHA coinciden."""
    fam, ax = "F1_unidad", "A4 alpha+beta=1"
    if ALPHA is None:
        reg.fail(fam, ax, "formulas.constants", "import",
                 "constantes no importadas", "sin constantes no hay marco")
        return
    src = "formulas.constants"

    if abs((ALPHA + BETA) - 1.0) > EPS:
        reg.fail(fam, ax, src, "ALPHA + BETA",
                 f"{ALPHA + BETA!r}", "el invariante de unidad no se cumple")
    else:
        reg.ok(fam, ax, src)

    # geometria declarada: 27 celdas, 1 interior, 26 exteriores
    if abs(ALPHA - 26.0 / 27.0) > EPS or abs(BETA - 1.0 / 27.0) > EPS:
        reg.fail(fam, ax, src, "derivacion del cubo 3x3x3",
                 f"ALPHA={ALPHA!r} BETA={BETA!r}",
                 "no coinciden con 26/27 y 1/27")
    else:
        reg.ok(fam, ax, src)

    # dos fuentes: core.engine define las suyas ademas de importarlas
    if ALPHA_ENGINE is None:
        reg.vacio(fam, ax, src)
    elif abs(ALPHA_ENGINE - ALPHA) > EPS or abs(BETA_ENGINE - BETA) > EPS:
        reg.fail(fam, ax, "core.engine vs formulas.constants",
                 "ALPHA_VPSI vs ALPHA",
                 f"engine=({ALPHA_ENGINE!r}, {BETA_ENGINE!r})  "
                 f"constants=({ALPHA!r}, {BETA!r})",
                 "dos definiciones de la misma constante y ya divergieron")
    else:
        reg.ok(fam, ax, "core.engine + formulas.constants")


def f2_cotas_truththeorem(reg: Registro, rng: random.Random, n: int) -> None:
    """A2 y A3 sobre TruthTheorem, con factores dentro del dominio."""
    fam, ax = "F2_cotas_TT", "A2 piso / A3 cota"
    if TruthTheorem is None:
        reg.fail(fam, ax, "-", "import", "TruthTheorem ausente",
                 "sin motor de verdad no hay nada que medir")
        return
    src = "formulas.truth_VPSI.TruthTheorem"
    piso, techo = BETA, ALPHA + BETA

    for _ in range(n):
        c, l, k = (factor_en_rango(rng) for _ in range(3))
        try:
            t = TruthTheorem.compute_total_truth(c, l, k)
        except Exception as e:
            reg.fail(fam, ax, src, f"C={c} L={l} K={k}",
                     f"{type(e).__name__}: {e}", "excepcion", fija=False)
            continue
        if t < piso - EPS:
            reg.fail(fam, ax, src, f"C={c!r} L={l!r} K={k!r}",
                     f"Tru_total={t!r}",
                     f"por debajo del piso BETA={piso!r}: el axioma 2 "
                     "prohibe que Tru_total baje de beta", fija=False)
        elif t > techo + EPS:
            reg.fail(fam, ax, src, f"C={c!r} L={l!r} K={k!r}",
                     f"Tru_total={t!r}",
                     f"por encima de ALPHA+BETA={techo!r}", fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)


def f3_cotas_engine(reg: Registro, rng: random.Random, n: int) -> None:
    """
    A2 y A3 sobre apply_vpsi_truth con factores FUERA del dominio.

    TruthTheorem recorta a [0,1]; el motor no. Si el motor no recorta,
    un factor fuera de rango rompe el piso y la cota a la vez.
    """
    fam, ax = "F3_cotas_engine", "A2 piso / A3 cota"
    if OmegaEngine is None:
        reg.fail(fam, ax, "-", "import", "OmegaEngine ausente",
                 "sin motor no hay nada que medir")
        return
    src = "core.engine.OmegaEngine.apply_vpsi_truth"
    eng = OmegaEngine()
    piso, techo = BETA, ALPHA + BETA

    for _ in range(n):
        c, l, k = (factor_fuera_de_rango(rng) if rng.random() < 0.5
                   else factor_en_rango(rng) for _ in range(3))
        try:
            t = eng.apply_vpsi_truth(c, l, k)
        except Exception as e:
            reg.fail(fam, ax, src, f"C={c} L={l} K={k}",
                     f"{type(e).__name__}: {e}", "excepcion", fija=False)
            continue
        if isinstance(t, float) and (math.isnan(t) or math.isinf(t)):
            reg.fail(fam, ax, src, f"C={c!r} L={l!r} K={k!r}",
                     f"Tru_total={t!r}", "resultado no finito", fija=False)
        elif t < piso - EPS:
            reg.fail(fam, ax, src, f"C={c!r} L={l!r} K={k!r}",
                     f"Tru_total={t!r}",
                     f"por debajo del piso BETA={piso!r}. El motor no "
                     "recorta los factores al dominio [0,1] declarado",
                     fija=False)
        elif t > techo + EPS:
            reg.fail(fam, ax, src, f"C={c!r} L={l!r} K={k!r}",
                     f"Tru_total={t!r}",
                     f"por encima de ALPHA+BETA={techo!r}. El motor no "
                     "recorta los factores al dominio [0,1] declarado",
                     fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)


def f4_paridad(reg: Registro, rng: random.Random, n: int) -> None:
    """
    A7: dos implementaciones de la misma formula deben coincidir.

    TruthTheorem.compute_total_truth y OmegaEngine.apply_vpsi_truth
    computan Tru_total = C*L*K*alpha + beta. Si divergen, hay dos
    verdades para la misma entrada.
    """
    fam, ax = "F4_paridad", "A7 invariancia"
    if TruthTheorem is None or OmegaEngine is None:
        reg.fail(fam, ax, "-", "import", "falta una de las dos vias",
                 "no se puede contrastar")
        return
    src = "TruthTheorem vs OmegaEngine"
    eng = OmegaEngine()

    for _ in range(n):
        fuera = rng.random() < 0.4
        c, l, k = ((factor_fuera_de_rango(rng) if fuera
                    else factor_en_rango(rng)) for _ in range(3))
        try:
            a = TruthTheorem.compute_total_truth(c, l, k)
            b = eng.apply_vpsi_truth(c, l, k)
        except Exception as e:
            reg.fail(fam, ax, src, f"C={c} L={l} K={k}",
                     f"{type(e).__name__}: {e}", "excepcion", fija=False)
            continue
        if isinstance(a, float) and isinstance(b, float) \
                and (math.isnan(a) or math.isnan(b)):
            reg.vacio(fam, ax, src, fija=False)
            continue
        if abs(a - b) > 1e-9:
            reg.fail(fam, ax, src, f"C={c!r} L={l!r} K={k!r}",
                     f"TruthTheorem={a!r}  OmegaEngine={b!r}  "
                     f"delta={abs(a-b)!r}",
                     "dos implementaciones de la misma formula dan "
                     "resultados distintos: TruthTheorem recorta al "
                     "dominio [0,1] y el motor no", fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)


def f5_multiplicatividad(reg: Registro, rng: random.Random, n: int) -> None:
    """A5: un factor nulo colapsa Tru_total a BETA. Sin compensacion."""
    fam, ax = "F5_multiplicativa", "A5 interdependencia"
    if TruthTheorem is None:
        reg.fail(fam, ax, "-", "import", "TruthTheorem ausente",
                 "sin motor no hay nada que medir")
        return
    src = "formulas.truth_VPSI.TruthTheorem"

    for _ in range(n):
        cual = rng.randrange(3)
        vals = [factor_en_rango(rng) for _ in range(3)]
        vals[cual] = 0.0
        try:
            t = TruthTheorem.compute_total_truth(*vals)
        except Exception as e:
            reg.fail(fam, ax, src, str(vals), f"{type(e).__name__}: {e}",
                     "excepcion", fija=False)
            continue
        if abs(t - BETA) > EPS:
            reg.fail(fam, ax, src,
                     f"C={vals[0]!r} L={vals[1]!r} K={vals[2]!r} "
                     f"(factor {'CLK'[cual]} = 0)",
                     f"Tru_total={t!r}",
                     f"con un factor nulo Tru_total debe ser exactamente "
                     f"BETA={BETA!r}: no hay compensacion entre factores",
                     fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)


def f6_monotonia(reg: Registro, rng: random.Random, n: int) -> None:
    """Si C*L*K crece, Tru_total no puede decrecer."""
    fam, ax = "F6_monotonia", "A5 interdependencia"
    if TruthTheorem is None:
        reg.fail(fam, ax, "-", "import", "TruthTheorem ausente",
                 "sin motor no hay nada que medir")
        return
    src = "formulas.truth_VPSI.TruthTheorem"

    for _ in range(n):
        a = [factor_en_rango(rng) for _ in range(3)]
        b = [min(1.0, x + rng.random() * (1.0 - x)) for x in a]
        try:
            ta = TruthTheorem.compute_total_truth(*a)
            tb = TruthTheorem.compute_total_truth(*b)
        except Exception as e:
            reg.fail(fam, ax, src, f"{a} vs {b}", f"{type(e).__name__}: {e}",
                     "excepcion", fija=False)
            continue
        if tb < ta - EPS:
            reg.fail(fam, ax, src,
                     f"a={a!r}  b={b!r} (b >= a componente a componente)",
                     f"Tru(a)={ta!r}  Tru(b)={tb!r}",
                     "aumentar un factor redujo Tru_total", fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)


def f7_puerta_l6(reg: Registro, rng: random.Random) -> None:
    """El motor exige phi = 0.0 en L6. Debe lanzar si no."""
    fam, ax = "F7_puerta_L6", "alineacion de proposito"
    if OmegaEngine is None or PurposeAlignmentError is None:
        reg.fail(fam, ax, "-", "import", "OmegaEngine ausente",
                 "sin motor no hay puerta que probar")
        return
    src = "core.engine.OmegaEngine.compute_coherence"
    eng = OmegaEngine()

    # caso valido: no debe lanzar
    capas = capas_validas(rng)
    try:
        eng.compute_coherence(capas)
        reg.ok(fam, ax, src)
    except PurposeAlignmentError as e:
        reg.fail(fam, ax, src, "L6 phi = 0.0", str(e),
                 "lanzo con L6 correctamente alineada")
    except Exception as e:
        reg.fail(fam, ax, src, "L6 phi = 0.0",
                 f"{type(e).__name__}: {e}", "excepcion inesperada")

    # casos invalidos: debe lanzar
    for phi_malo in (0.5, 1e-9, -0.1):
        malas = capas_validas(rng)
        malas[6]["phi"] = phi_malo
        try:
            eng.compute_coherence(malas)
            reg.fail(fam, ax, src, f"L6 phi = {phi_malo!r}",
                     "no lanzo",
                     "L6 con friccion no nula debe abortar el computo")
        except PurposeAlignmentError:
            reg.ok(fam, ax, src)
        except Exception as e:
            reg.fail(fam, ax, src, f"L6 phi = {phi_malo!r}",
                     f"{type(e).__name__}: {e}",
                     "lanzo una excepcion distinta de PurposeAlignmentError")


def f8_piso_pipeline(reg: Registro, rng: random.Random) -> None:
    """
    A2 a traves del pipeline completo.

    compute_coherence aplica Tru_total y luego escala por PHI/2 y L7.
    Si el escalado deja el resultado por debajo de BETA, el piso
    estructural no sobrevive al pipeline.
    """
    fam, ax = "F8_piso_pipeline", "A2 piso beta"
    if OmegaEngine is None:
        reg.fail(fam, ax, "-", "import", "OmegaEngine ausente",
                 "sin motor no hay pipeline")
        return
    src = "core.engine.OmegaEngine.compute_coherence"
    eng = OmegaEngine()

    casos = [
        ("activaciones nulas", 0.0),
        ("activaciones minimas", 1e-9),
        ("activaciones bajas", 0.01),
    ]
    for etiqueta, val in casos:
        capas = [{"L": val, "phi": p}
                 for p in (LAYER_FRICTION or [0.1, .02, .05, .03, .01, .01, 0.0])]
        capas[6]["phi"] = 0.0
        try:
            r = eng.compute_coherence(capas)
        except Exception as e:
            reg.fail(fam, ax, src, etiqueta, f"{type(e).__name__}: {e}",
                     "excepcion")
            continue
        if r < BETA - EPS:
            reg.fail(fam, ax, src, f"{etiqueta} (L={val!r} en todas las capas)",
                     f"compute_coherence={r!r}   BETA={BETA!r}",
                     "el resultado quedo por debajo del piso estructural. "
                     "El escalado posterior (PHI/2 y L7) destruye la "
                     "garantia de que Tru_total >= BETA")
        else:
            reg.ok(fam, ax, src)


def f9_determinismo(reg: Registro, rng: random.Random, n: int) -> None:
    """
    A7: misma entrada, misma salida.

    Se usan instancias NUEVAS en cada pasada: una instancia acumula
    estado de sesion y la comparacion seria de dos objetos distintos.
    """
    fam, ax = "F9_determinismo", "A7 invariancia"
    if OmegaEngine is None:
        reg.fail(fam, ax, "-", "import", "OmegaEngine ausente",
                 "sin motor no hay nada que medir")
        return
    src = "core.engine.OmegaEngine.compute_coherence"

    for _ in range(max(1, n // 40)):
        capas = capas_validas(rng)
        try:
            a = OmegaEngine().compute_coherence([dict(c) for c in capas])
            b = OmegaEngine().compute_coherence([dict(c) for c in capas])
        except Exception as e:
            reg.fail(fam, ax, src, str(capas)[:100],
                     f"{type(e).__name__}: {e}", "excepcion", fija=False)
            continue
        if abs(a - b) > EPS:
            reg.fail(fam, ax, src, str(capas)[:160],
                     f"1a={a!r}  2a={b!r}  delta={abs(a-b)!r}",
                     "misma entrada, dos instancias limpias, dos salidas",
                     fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)


def f10_dominio_salida(reg: Registro, rng: random.Random, n: int) -> None:
    """compute_coherence declara devolver float en [0,1]."""
    fam, ax = "F10_dominio_salida", "A6 cota informacional"
    if OmegaEngine is None:
        reg.fail(fam, ax, "-", "import", "OmegaEngine ausente",
                 "sin motor no hay nada que medir")
        return
    src = "core.engine.OmegaEngine.compute_coherence"

    for _ in range(max(1, n // 40)):
        capas = capas_validas(rng)
        eng = OmegaEngine()
        try:
            r = eng.compute_coherence(capas)
        except Exception as e:
            reg.fail(fam, ax, src, str(capas)[:100],
                     f"{type(e).__name__}: {e}", "excepcion", fija=False)
            continue
        if not isinstance(r, float):
            reg.fail(fam, ax, src, str(capas)[:100],
                     f"{r!r} ({type(r).__name__})",
                     "el contrato declara float", fija=False)
        elif math.isnan(r) or math.isinf(r):
            reg.fail(fam, ax, src, str(capas)[:100], f"{r!r}",
                     "resultado no finito", fija=False)
        elif not (0.0 - EPS <= r <= 1.0 + EPS):
            reg.fail(fam, ax, src, str(capas)[:100], f"{r!r}",
                     "fuera de [0,1]", fija=False)
        else:
            reg.ok(fam, ax, src, fija=False)

# ===============================================================
# SEGMENTO 6 --- INFORME
# ===============================================================

def informe(reg: Registro, raiz: Path, dt: float, umbral: float,
            verbose: bool) -> int:
    print("\n" + "-" * 78)
    print(f"{'FAMILIA':22s} {'AXIOMA':22s} {'TIPO':6s} {'OK':>7s} "
          f"{'FALLO':>7s} {'VACIO':>6s}")
    print("-" * 78)

    fijos = 0
    peor = 0.0
    vacias = []
    for n in sorted(reg.familias):
        f = reg.familias[n]
        tipo = "fija" if f.fija else "estoc"
        print(f"{n:22s} {f.axioma:22s} {tipo:6s} {f.ok:>7,} "
              f"{f.fallos:>7,} {f.vacios:>6,}")
        if f.fija:
            fijos += f.fallos
        else:
            peor = max(peor, f.tasa)
        if f.medidos == 0:
            vacias.append(n)
    print("-" * 78)

    if reg.detalle:
        print("\n" + "=" * 78)
        print(f"DETALLE DE FALLOS (max {reg.max_detalle})")
        print("=" * 78)
        for i, f in enumerate(reg.detalle, 1):
            print(f"\n--- fallo {i} ---")
            print(f"  familia   : {f.familia}")
            print(f"  axioma    : {f.axioma}")
            print(f"  fuente    : {f.fuente}")
            print(f"  entrada   : {f.entrada}")
            print(f"  observado : {f.observado}")
            print(f"  causa     : {f.causa}")

    print("\n" + "=" * 78)
    print("VEREDICTO")
    print("=" * 78)
    print(f"  raiz              : {raiz}")
    print(f"  ALPHA / BETA      : {ALPHA!r} / {BETA!r}")
    print(f"  tiempo            : {dt:.2f}s")
    print(f"  fallos en fijas   : {fijos}   (criterio: cero)")
    print(f"  peor tasa estoc.  : {peor:.8f}   (umbral: {umbral})")
    if vacias:
        print(f"\n  SIN MEDICION: {vacias}")
        print("  No medir no es aprobar.")

    rc = 0
    if fijos:
        print(f"\nFAIL  {fijos} fallo(s) en familias de caso fijo")
        rc = 1
    if peor > umbral:
        print(f"\nFAIL  tasa {peor:.8f} > umbral {umbral}")
        rc = 1
    if vacias:
        print(f"\nFAIL  {len(vacias)} familia(s) sin una sola medicion")
        rc = 1
    if rc == 0:
        print("\nPASS  invariantes sostenidos en todo el muestreo")
    print("=" * 78)
    return rc

# ===============================================================
# SEGMENTO 7 --- MAIN
# ===============================================================

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--n", type=int, default=N_STOCH)
    ap.add_argument("--umbral", type=float, default=UMBRAL)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--raiz", type=str, default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv if argv is not None else [])

    raiz = Path(args.raiz).resolve() if args.raiz else raiz_repo()

    print("=" * 78)
    print("MONTE CARLO ADVERSARIAL — nodo-invisible / OmegaEngine")
    print(f"raiz={raiz}")
    print(f"N={args.n:,}  umbral={args.umbral}  seed={hex(args.seed)}")
    print("=" * 78)

    cargar(raiz)
    if _ERR:
        print("\nIMPORTS NO RESUELTOS:")
        for e in _ERR:
            print(f"  X  {e}")
    if TruthTheorem is None and OmegaEngine is None:
        print("\nFAIL  no hay motor importable. Sin sistema bajo prueba "
              "no hay resultado.")
        return 1
    print("\nimports:")
    print(f"  TruthTheorem : {'ok' if TruthTheorem else 'AUSENTE'}")
    print(f"  OmegaEngine  : {'ok' if OmegaEngine else 'AUSENTE'}")
    print(f"  constantes   : ALPHA={ALPHA!r}  BETA={BETA!r}  PHI={PHI!r}")

    rng = random.Random(args.seed)
    reg = Registro()
    t0 = time.time()

    n = args.n
    print("\n[F1]  unidad alpha+beta y fuentes de la constante ...")
    f1_unidad(reg)
    print(f"[F2]  cotas de TruthTheorem ({n:,}) ...")
    f2_cotas_truththeorem(reg, rng, n)
    print(f"[F3]  cotas de apply_vpsi_truth ({n:,}) ...")
    f3_cotas_engine(reg, rng, n)
    print(f"[F4]  paridad entre las dos implementaciones ({n:,}) ...")
    f4_paridad(reg, rng, n)
    print(f"[F5]  multiplicatividad ({n:,}) ...")
    f5_multiplicatividad(reg, rng, n)
    print(f"[F6]  monotonia ({n:,}) ...")
    f6_monotonia(reg, rng, n)
    print("[F7]  puerta L6 ...")
    f7_puerta_l6(reg, rng)
    print("[F8]  piso a traves del pipeline ...")
    f8_piso_pipeline(reg, rng)
    print(f"[F9]  determinismo ({max(1, n // 40):,}) ...")
    f9_determinismo(reg, rng, n)
    print(f"[F10] dominio de salida ({max(1, n // 40):,}) ...")
    f10_dominio_salida(reg, rng, n)

    return informe(reg, raiz, time.time() - t0, args.umbral, args.verbose)

# ===============================================================
# SEGMENTO 8 --- ENTRADA PYTEST
# ===============================================================

def test_montecarlo_omega():
    """parse_args con lista vacia: pytest deja sus flags en sys.argv."""
    rc = main([])
    assert rc == 0, (
        "Monte Carlo OmegaEngine: invariante roto. Ver detalle arriba."
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
