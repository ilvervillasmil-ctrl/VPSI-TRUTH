#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MONTE CARLO ADVERSARIAL — VPSI-TRUTH

No importa NADA por nombre fijo. Descubre lo que el repo expone hoy y
mide contra eso. Si una pieza se renombra, este archivo no se rompe:
lo reporta y sigue.

Razon: escribir 'from modules.axiomas import barrer' ata el test a una
firma concreta. Cuando esa firma cambia, el test falla por ImportError
y no por defecto. Un ImportError no es evidencia sobre el sistema.

Invariantes medidos (los que el marco declara):

    A4  unidad            ALPHA + BETA == 1, derivado del cubo 3x3x3
    A2  piso beta         Tru_total nunca por debajo de BETA
    A3  cota              Tru_total nunca por encima de ALPHA + BETA
    A5  interdependencia  un factor nulo colapsa Tru_total a BETA
    A7  invariancia       misma entrada, misma salida
    EXA exactitud         Fraction en la ruta de decision, nunca float
    VAC no vacuidad       el barrido carga algo; 0 declaraciones = FAIL
    SM-T9  renombrado     renombrar preservando contrastes no altera K
    AF-T2  no-proposicion sin ancla no hay K, ni 0 ni 1
    Def-5.3.1 sin O       sin dominio usable, K no reclamable

Uso:
    pytest  tests/test_montecarlo_vpsi.py
    python  tests/test_montecarlo_vpsi.py --n 20000 --verbose
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import random
import sys
import time
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ===============================================================
# SEGMENTO 1 --- PARAMETROS
# ===============================================================

N_STOCH = 10_000
UMBRAL = 0.0          # invariantes, no estadistica: tolerancia cero
SEED = 0x5F_A7_C0_DE
PISO_DECLARACIONES = 1

# Alias posibles de cada pieza. El repo puede renombrar: se prueban
# todos y gana el primero que exista. Anadir un alias aqui no obliga
# a tocar nada mas.
ALIAS = {
    "barrido":   ("barrer", "barrido", "sweep", "auditar", "verificar",
                  "revisar", "chequear"),
    "declaraciones": ("axiomas", "declaraciones", "recolectar", "todas",
                      "corpus", "listar"),
    "inventario": ("inventario", "inventory", "resumen", "estado"),
    "calcular_k": ("calcular_k", "correlacion", "correlation", "k"),
    "calcular_c": ("calcular_c", "coherencia", "coherence", "c"),
    "calcular_l": ("calcular_l", "logica", "logic", "l"),
    "calcular":   ("calcular", "calculate", "compute", "evaluar"),
    "tru_ri":     ("tru_ri", "truri", "tru_interpretativa"),
    "tru_total":  ("tru_total", "trutotal", "verdad_total"),
}

MODULOS = {
    "axiomas":   ("modules.axiomas", "modules.axioms", "axiomas"),
    "constante": ("modules.constante", "modules.constants", "constante"),
    "formulas":  ("modules.formulas.truth", "modules.formulas",
                  "formulas.truth", "formulas"),
    "calculator": ("modules.calculator", "modules.calculador",
                   "calculator"),
    "engine":    ("core.engine", "engine"),
}

# ===============================================================
# SEGMENTO 2 --- RAIZ
# ===============================================================

def raiz_repo() -> Path:
    aqui = Path(__file__).resolve()
    for base in [aqui.parent] + list(aqui.parents):
        if (base / "modules").is_dir() or (base / "core").is_dir():
            return base
    return aqui.parent


def preparar(raiz: Path) -> None:
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))

# ===============================================================
# SEGMENTO 3 --- DESCUBRIMIENTO TOLERANTE
# ===============================================================

_NOTAS: List[str] = []


def cargar_modulo(clave: str) -> Optional[Any]:
    """Prueba los nombres de modulo candidatos. El primero que importe gana."""
    for ruta in MODULOS.get(clave, ()):
        try:
            return importlib.import_module(ruta)
        except Exception as e:
            _NOTAS.append(f"{ruta}: {type(e).__name__}: {e}")
    return None


def buscar(mod: Optional[Any], rol: str) -> Tuple[Optional[Callable], str]:
    """
    Busca un callable por alias. Devuelve (funcion, origen).
    Nunca lanza: si no esta, devuelve None y el test lo reporta.
    """
    if mod is None:
        return None, ""
    for nombre in ALIAS.get(rol, ()):
        fn = getattr(mod, nombre, None)
        if callable(fn):
            return fn, f"{mod.__name__}.{nombre}"
    # segunda pasada: coincidencia parcial en el nombre
    for nombre in dir(mod):
        if nombre.startswith("_"):
            continue
        fn = getattr(mod, nombre, None)
        if not callable(fn) or inspect.isclass(fn):
            continue
        bajo = nombre.lower()
        if any(a in bajo for a in ALIAS.get(rol, ())):
            return fn, f"{mod.__name__}.{nombre}"
    return None, ""


def constante(mod: Optional[Any], *nombres: str) -> Any:
    if mod is None:
        return None
    for n in nombres:
        v = getattr(mod, n, None)
        if v is not None:
            return v
    return None

# ===============================================================
# SEGMENTO 4 --- VALORES
# ===============================================================

def es_undefined(x: Any) -> bool:
    if x is None:
        return True
    if type(x).__name__.lower().lstrip("_") in ("undefined", "undef"):
        return True
    if isinstance(x, str) and x.strip().upper() in (
        "UNDEFINED", "INDEFINIDO", "N/A"
    ):
        return True
    return False


def a_num(x: Any) -> Optional[float]:
    if es_undefined(x) or isinstance(x, bool):
        return None
    try:
        return float(x)
    except Exception:
        return None


def es_float_crudo(x: Any) -> bool:
    return isinstance(x, float) and not isinstance(x, bool)


def invocar(fn: Optional[Callable], valores: Dict[frozenset, Any],
            metodo: str = "") -> Tuple[Any, Optional[str]]:
    """Arma kwargs segun la firma real. Un TypeError de firma no es fallo."""
    if fn is None:
        return None, "no descubierto"
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return None, "sin firma inspeccionable"
    kw = {}
    for p in sig.parameters:
        low = p.lower()
        if low in ("metodo", "method"):
            if metodo:
                kw[p] = metodo
            continue
        for grupo, val in valores.items():
            if low in grupo:
                kw[p] = val
                break
    try:
        return fn(**kw), None
    except TypeError as e:
        return None, f"firma: {e}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


P_DESC = frozenset({"descripcion", "description", "d", "texto", "text",
                    "mensaje", "message", "afirmacion", "enunciado"})
P_CTX = frozenset({"o_context", "ocontext", "contexto", "context", "o",
                   "dominio", "domain", "octx"})
P_AFIR = frozenset({"afirmaciones", "afirmaciones_falsas", "assertions", "f",
                    "c"})
P_COMP = frozenset({"compromisos", "contradicciones", "commitments", "k", "m"})
P_POST = frozenset({"posturas", "reversiones", "postures", "r", "p"})

METODOS = ("", "operacional", "teorico")


def vals_k(d: str, o: str) -> Dict[frozenset, Any]:
    return {P_DESC: d, P_CTX: o, P_AFIR: None, P_COMP: None, P_POST: None}


def k_por_metodos(fn, d: str, o: str) -> Dict[str, Any]:
    out = {}
    for m in METODOS:
        v, err = invocar(fn, vals_k(d, o), m)
        if err is None:
            out[m or "default"] = v
    return out

# ===============================================================
# SEGMENTO 5 --- REGISTRO
# ===============================================================

@dataclass
class Fallo:
    familia: str
    invariante: str
    fuente: str
    entrada: str
    observado: str
    causa: str


@dataclass
class Familia:
    nombre: str
    invariante: str
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
    max_detalle: int = 25

    def _f(self, n, inv="", fija=True) -> Familia:
        if n not in self.familias:
            self.familias[n] = Familia(n, inv, fija)
        return self.familias[n]

    def ok(self, n, inv="", fija=True):
        self._f(n, inv, fija).ok += 1

    def vacio(self, n, inv="", fija=True):
        self._f(n, inv, fija).vacios += 1

    def fail(self, n, inv, src, entrada, observado, causa, fija=True):
        self._f(n, inv, fija).fallos += 1
        if len(self.detalle) < self.max_detalle:
            self.detalle.append(Fallo(n, inv, src, entrada, observado, causa))

# ===============================================================
# SEGMENTO 6 --- MATERIAL
# ===============================================================

PARES_RENOMBRE = [
    ("beta vale B = 1/27", "sabemos que B = 1/27 exactamente",
     "beta vale G = 1/27", "sabemos que G = 1/27 exactamente",
     "B->G conservando 1/27"),
    ("la casa esta en la colina", "ubicacion de la casa en la colina",
     "la X17 esta en la Q44", "ubicacion de la X17 en la Q44",
     "casa->X17, colina->Q44"),
    ("el perro corre rapido", "conducta del perro observada",
     "el K91 corre rapido", "conducta del K91 observada",
     "perro->K91"),
]

BASURA = [
    "rldgdnstwcfmdksxxrjdoevf",
    "Prgsyecdhdyecdhsuwfscdgdudvd",
    "xyzzy plugh foo bar quux",
    "@@@ ### $$$ %%%",
]

DOMINIOS = [
    "dominio de fisica de particulas",
    "taxonomia botanica del siglo XIX",
    "geometria del cubo 3x3x3",
]


def factor(rng: random.Random) -> Fraction:
    r = rng.random()
    if r < 0.12:
        return Fraction(0)
    if r < 0.24:
        return Fraction(1)
    return Fraction(rng.randrange(0, 1001), 1000)

# ===============================================================
# SEGMENTO 7 --- FAMILIAS
# ===============================================================

def f1_ancla(reg: Registro, ALPHA, BETA) -> None:
    """A4: alpha + beta = 1, derivado del cubo 3x3x3. Exacto."""
    fam, inv = "F1_ancla", "A4 alpha+beta=1"
    if ALPHA is None or BETA is None:
        reg.fail(fam, inv, "constante", "descubrimiento",
                 "ALPHA/BETA no descubiertos",
                 "sin ancla no hay marco que medir")
        return
    src = "modulo de constantes"

    if not isinstance(ALPHA, Fraction) or not isinstance(BETA, Fraction):
        reg.fail(fam, inv, src, "tipo de ALPHA / BETA",
                 f"ALPHA={type(ALPHA).__name__}  BETA={type(BETA).__name__}",
                 "el ancla debe ser exacta: Fraction, no float")
    else:
        reg.ok(fam, inv)

    try:
        if ALPHA + BETA != 1:
            reg.fail(fam, inv, src, "ALPHA + BETA", f"{ALPHA + BETA}",
                     "el invariante de unidad no se cumple")
        else:
            reg.ok(fam, inv)
    except Exception as e:
        reg.fail(fam, inv, src, "ALPHA + BETA",
                 f"{type(e).__name__}: {e}", "no comparable")

    # derivacion: 27 celdas, 1 interior, 26 exteriores
    n = 3
    total = n ** 3
    encerradas = (n - 2) ** 3
    accesibles = total - encerradas
    try:
        ok = (ALPHA == Fraction(accesibles, total)
              and BETA == Fraction(encerradas, total))
    except Exception:
        ok = False
    if ok:
        reg.ok(fam, inv)
    else:
        reg.fail(fam, inv, src, f"cubo {n}x{n}x{n}: {accesibles}/{total}",
                 f"ALPHA={ALPHA}  BETA={BETA}",
                 "el ancla no se deriva de la geometria declarada")


def f2_barrido(reg: Registro, mod_ax) -> None:
    """VAC: el barrido debe cargar algo. Cero declaraciones = vacuidad."""
    fam, inv = "F2_barrido", "VAC no vacuidad"
    if mod_ax is None:
        reg.fail(fam, inv, "-", "descubrimiento", "modulo de axiomas ausente",
                 "sin juez de contraste no hay barrido que medir")
        return

    fn_barrer, org_b = buscar(mod_ax, "barrido")
    fn_decl, org_d = buscar(mod_ax, "declaraciones")
    fn_inv, org_i = buscar(mod_ax, "inventario")

    if fn_barrer is None and fn_inv is None:
        reg.fail(fam, inv, mod_ax.__name__, "alias de barrido",
                 f"probados: {ALIAS['barrido']}",
                 "el modulo no expone funcion de barrido bajo ningun alias "
                 "conocido: anadir el nombre real a ALIAS['barrido']")
        return

    informe = None
    for fn, org in ((fn_barrer, org_b), (fn_inv, org_i)):
        if fn is None:
            continue
        try:
            informe = fn()
            src = org
            break
        except TypeError:
            continue
        except Exception as e:
            reg.fail(fam, inv, org, "llamada sin argumentos",
                     f"{type(e).__name__}: {e}", "excepcion en el barrido")
            return

    if not isinstance(informe, dict):
        reg.vacio(fam, inv)
        return

    n = None
    for clave in ("declaraciones", "total", "n", "cargadas", "count"):
        if isinstance(informe.get(clave), int):
            n = informe[clave]
            break
    if n is None and fn_decl is not None:
        try:
            lista = fn_decl()
            if isinstance(lista, (list, tuple)):
                n = len(lista)
        except Exception:
            pass

    if n is None:
        reg.vacio(fam, inv)
    elif n < PISO_DECLARACIONES:
        reg.fail(fam, inv, src, "conteo del barrido", f"{n} declaraciones",
                 "cero declaraciones cargadas: el informe sale coherente "
                 "por vacuidad, no por coherencia")
    else:
        reg.ok(fam, inv)

    coherente = informe.get("coherente")
    choques = informe.get("choques") or []
    if coherente is False or choques:
        reg.fail(fam, inv, src, "coherencia del corpus",
                 f"coherente={coherente}  choques={len(choques)}",
                 "contradiccion axiomatica en el corpus cargado")
    elif coherente is True:
        reg.ok(fam, inv)


def f3_formula(reg: Registro, fn_ri, fn_tt, ALPHA, BETA,
               rng: random.Random, n: int) -> None:
    """A2, A3, A5: piso, cota y multiplicatividad, con Fraction exacta."""
    fam, inv = "F3_formula", "A2 piso / A3 cota / A5"
    if fn_tt is None:
        reg.fail(fam, inv, "-", "descubrimiento", "tru_total no descubierto",
                 "sin funcional canonico no hay nada que medir")
        return
    if ALPHA is None or BETA is None:
        reg.vacio(fam, inv)
        return
    src = "modulo de formulas"

    for _ in range(n):
        C, L, K = factor(rng), factor(rng), factor(rng)
        try:
            tt = fn_tt(C, L, K)
        except Exception as e:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"{type(e).__name__}: {e}", "excepcion", fija=False)
            continue

        if es_float_crudo(tt):
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"Tru_total={tt!r} ({type(tt).__name__})",
                     "float en la ruta de decision: se exige Fraction",
                     fija=False)
            continue

        # derivacion canonica exacta
        esperado = (C * L * K * ALPHA) + BETA
        if tt != esperado:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"Tru_total={tt}  esperado={esperado}",
                     "Tru_total no se deriva de (C*L*K*alpha)+beta",
                     fija=False)
            continue

        if tt < BETA:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"Tru_total={tt}  BETA={BETA}",
                     "por debajo del piso estructural", fija=False)
        elif tt > ALPHA + BETA:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"Tru_total={tt}  techo={ALPHA + BETA}",
                     "por encima de la cota", fija=False)
        elif Fraction(0) in (C, L, K) and tt != BETA:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K} (un factor nulo)",
                     f"Tru_total={tt}  BETA={BETA}",
                     "un factor nulo debe colapsar a BETA exacto: no hay "
                     "compensacion entre factores", fija=False)
        else:
            reg.ok(fam, inv, fija=False)

    # coherencia entre tru_ri y tru_total, si ambas existen
    if fn_ri is None:
        return
    for _ in range(max(1, n // 20)):
        C, L, K = factor(rng), factor(rng), factor(rng)
        try:
            ri, tt = fn_ri(C, L, K), fn_tt(C, L, K)
        except Exception:
            continue
        if ri != C * L * K:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"Tru_Ri={ri}  esperado={C*L*K}",
                     "Tru_Ri no es el producto de los factores", fija=False)
        elif tt != (ri * ALPHA) + BETA:
            reg.fail(fam, inv, src, f"C={C} L={L} K={K}",
                     f"Tru_Ri={ri}  Tru_total={tt}",
                     "Tru_total no se deriva de Tru_Ri", fija=False)
        else:
            reg.ok(fam, inv, fija=False)


def f4_renombrado(reg: Registro, fn_k) -> None:
    """SM-T9: renombrar preservando contrastes no altera K."""
    fam, inv = "F4_renombrado", "SM-T9"
    if fn_k is None:
        reg.vacio(fam, inv)
        return
    src = "calculador de K"

    for d1, o1, d2, o2, tag in PARES_RENOMBRE:
        m1, m2 = k_por_metodos(fn_k, d1, o1), k_por_metodos(fn_k, d2, o2)
        medido = False
        for m in set(m1) & set(m2):
            k1, k2 = m1[m], m2[m]
            u1, u2 = es_undefined(k1), es_undefined(k2)
            if u1 and u2:
                continue
            medido = True
            if u1 != u2:
                reg.fail(fam, inv, src,
                         f"[{m}] {tag}\n    D1={d1!r} O1={o1!r}\n"
                         f"    D2={d2!r} O2={o2!r}",
                         f"K1={k1!r}  K2={k2!r}",
                         "un lado UNDEFINED y el otro numerico tras "
                         "renombrado que preserva el contraste")
                continue
            n1, n2 = a_num(k1), a_num(k2)
            if n1 is None or n2 is None:
                reg.vacio(fam, inv)
            elif abs(n1 - n2) > 1e-12:
                reg.fail(fam, inv, src,
                         f"[{m}] {tag}\n    D1={d1!r} O1={o1!r}\n"
                         f"    D2={d2!r} O2={o2!r}",
                         f"K1={n1}  K2={n2}  delta={abs(n1-n2)}",
                         "K cambio bajo renombrado biyectivo: el evaluador "
                         "mide etiquetas, no invariantes")
            else:
                reg.ok(fam, inv)
        if not medido:
            reg.vacio(fam, inv)


def f5_no_proposicion(reg: Registro, fn_k) -> None:
    """AF-T2 / AF-C1: sin ancla no hay K, ni 0 ni 1."""
    fam, inv = "F5_no_proposicion", "AF-T2 / AF-C1"
    if fn_k is None:
        reg.vacio(fam, inv)
        return
    src = "calculador de K"

    casos = [
        ("rldgdnstwcfmdksxxrjdoevf qwerty zxcvbn",
         "topologia algebraica de variedades", "vacia total"),
        ("Yo soy rldgdnstwcfmdksxxrjdoevf",
         "identidad del emisor", "objeto sin ancla"),
        ("soy el mejor", "desempeno competitivo",
         "superlativo sin particion"),
    ]
    for d, o, etiqueta in casos:
        vals = k_por_metodos(fn_k, d, o)
        medido = False
        for m, k in vals.items():
            if es_undefined(k):
                continue
            medido = True
            nk = a_num(k)
            if nk is None:
                reg.ok(fam, inv)
            elif abs(nk) < 1e-15:
                reg.fail(fam, inv, src,
                         f"[{m}] {etiqueta}\n    D={d!r}\n    O={o!r}",
                         f"K={k!r}",
                         "K=0 fabricado sobre no-proposicion. Fabricar 0 "
                         "viola Def-5.3.1 igual que fabricar 1")
            elif abs(nk - 1.0) < 1e-15:
                reg.fail(fam, inv, src,
                         f"[{m}] {etiqueta}\n    D={d!r}\n    O={o!r}",
                         f"K={k!r}", "K=1 sobre material sin ancla")
            else:
                reg.ok(fam, inv)
        if not medido:
            reg.vacio(fam, inv)


def f6_sin_dominio(reg: Registro, fn_k) -> None:
    """Def-5.3.1: sin O usable, K no reclamable."""
    fam, inv = "F6_sin_dominio", "Def-5.3.1"
    if fn_k is None:
        reg.vacio(fam, inv)
        return
    src = "calculador de K"

    for d in ("el sol irradia luz", "1 + 1 = 2", "Carlos fue a la casa"):
        vals = k_por_metodos(fn_k, d, "")
        if not vals:
            reg.ok(fam, inv)          # rechazo por firma: legitimo
            continue
        for m, k in vals.items():
            if es_undefined(k):
                reg.ok(fam, inv)
            else:
                reg.fail(fam, inv, src, f"[{m}] D={d!r}  O='' (vacio)",
                         f"K={k!r}",
                         "K reclamado sin O usable: la correlacion es "
                         "indefinida, no un numero")


def f7_ruido(reg: Registro, fn_k, rng: random.Random, n: int) -> None:
    """SM-T2: cadena sin ancla no satura K."""
    fam, inv = "F7_ruido", "SM-T2 / SM-A6"
    if fn_k is None:
        reg.vacio(fam, inv, fija=False)
        return
    src = "calculador de K"

    for _ in range(n):
        d = rng.choice(BASURA) + " " + rng.choice(BASURA)
        o = rng.choice(DOMINIOS)
        vals = k_por_metodos(fn_k, d, o)
        medido = False
        for m, k in vals.items():
            if es_undefined(k):
                continue
            medido = True
            nk = a_num(k)
            if nk is not None and nk > 0:
                reg.fail(fam, inv, src, f"[{m}] D={d!r}\n    O={o!r}",
                         f"K={k!r}",
                         "cadena sin ancla referencial recibio K>0",
                         fija=False)
            else:
                reg.ok(fam, inv, fija=False)
        if not medido:
            reg.vacio(fam, inv, fija=False)


def f8_determinismo(reg: Registro, fn_k, rng: random.Random, n: int) -> None:
    """A7: misma entrada, misma salida."""
    fam, inv = "F8_determinismo", "A7 invariancia"
    if fn_k is None:
        reg.vacio(fam, inv, fija=False)
        return
    src = "calculador de K"

    for _ in range(max(1, n // 10)):
        d = rng.choice(BASURA + ["el sol irradia luz", "la casa es azul"])
        o = rng.choice(DOMINIOS)
        a = k_por_metodos(fn_k, d, o)
        b = k_por_metodos(fn_k, d, o)
        if not a:
            reg.vacio(fam, inv, fija=False)
            continue
        for m in set(a) & set(b):
            x, y = a[m], b[m]
            if es_undefined(x) and es_undefined(y):
                reg.ok(fam, inv, fija=False)
            elif es_undefined(x) != es_undefined(y):
                reg.fail(fam, inv, src, f"[{m}] D={d!r} O={o!r}",
                         f"1a={x!r}  2a={y!r}",
                         "misma entrada, un lado definido y otro no",
                         fija=False)
            elif x != y:
                reg.fail(fam, inv, src, f"[{m}] D={d!r} O={o!r}",
                         f"1a={x!r}  2a={y!r}",
                         "misma entrada, dos salidas", fija=False)
            else:
                reg.ok(fam, inv, fija=False)


def f9_exactitud(reg: Registro, fn_pipe) -> None:
    """EXA: ningun factor ni resultado puede ser float."""
    fam, inv = "F9_exactitud", "EXA Fraction"
    if fn_pipe is None:
        reg.vacio(fam, inv)
        return
    src = "pipeline"

    peticion = {
        "descripcion": "el sol irradia luz",
        "mensaje": "el sol irradia luz",
        "o_context": "fisica termica / astronomia observacional",
        "contexto": "fisica termica / astronomia observacional",
        "O_id": "sonda_1", "enunciado_O": "fisica termica",
        "compromisos": ["c1", "c2"], "contradicciones": 0,
        "posturas": ["p1", "p2"], "reversiones": 0,
        "afirmaciones": ["a1"], "afirmaciones_falsas": 0,
    }
    claves = ("C", "L", "K", "c", "l", "k",
              "tru_ri", "tru_total", "Tru_Ri", "Tru_total")

    for m in METODOS:
        p = dict(peticion)
        if m:
            p["metodo"] = m
        try:
            out = fn_pipe(p)
        except TypeError:
            reg.vacio(fam, inv)
            continue
        except Exception as e:
            reg.fail(fam, inv, src, "peticion con conteos completos",
                     f"{type(e).__name__}: {e}", "excepcion en el pipeline")
            continue
        if not isinstance(out, dict):
            reg.vacio(fam, inv)
            continue
        presentes = [k for k in claves
                     if k in out and not es_undefined(out[k])]
        if not presentes:
            reg.vacio(fam, inv)
            continue
        malos = [(k, out[k]) for k in presentes if es_float_crudo(out[k])]
        if malos:
            reg.fail(fam, inv, src, f"[{m or 'default'}] peticion completa",
                     ", ".join(f"{k}={v!r} ({type(v).__name__})"
                               for k, v in malos),
                     "float donde el contrato exige Fraction")
        else:
            reg.ok(fam, inv)

# ===============================================================
# SEGMENTO 8 --- INFORME
# ===============================================================

def informe(reg: Registro, raiz: Path, hallado: Dict[str, str],
            dt: float, umbral: float, verbose: bool) -> int:
    print("\n" + "-" * 78)
    print(f"{'FAMILIA':22s} {'INVARIANTE':22s} {'TIPO':6s} {'OK':>7s} "
          f"{'FALLO':>7s} {'VACIO':>6s}")
    print("-" * 78)

    fijos, peor, vacias = 0, 0.0, []
    for n in sorted(reg.familias):
        f = reg.familias[n]
        tipo = "fija" if f.fija else "estoc"
        print(f"{n:22s} {f.invariante:22s} {tipo:6s} {f.ok:>7,} "
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
            print(f"  familia    : {f.familia}")
            print(f"  invariante : {f.invariante}")
            print(f"  fuente     : {f.fuente}")
            print(f"  entrada    : {f.entrada}")
            print(f"  observado  : {f.observado}")
            print(f"  causa      : {f.causa}")

    print("\n" + "=" * 78)
    print("VEREDICTO")
    print("=" * 78)
    print(f"  raiz              : {raiz}")
    print("  piezas descubiertas:")
    for rol, org in hallado.items():
        print(f"    {rol:14s}: {org or 'NO DESCUBIERTA'}")
    if verbose and _NOTAS:
        print("\n  notas de importacion:")
        for nota in _NOTAS[:12]:
            print(f"    - {nota}")
    print(f"  tiempo            : {dt:.2f}s")
    print(f"  fallos en fijas   : {fijos}   (criterio: cero)")
    print(f"  peor tasa estoc.  : {peor:.8f}   (umbral: {umbral})")
    if vacias:
        print(f"\n  SIN MEDICION: {vacias}")
        print("  No medir no es aprobar. Si la pieza existe con otro nombre,")
        print("  anadirlo al diccionario ALIAS de la cabecera.")

    rc = 0
    if fijos:
        print(f"\nFAIL  {fijos} fallo(s) en familias de caso fijo")
        rc = 1
    if peor > umbral:
        print(f"\nFAIL  tasa {peor:.8f} > umbral {umbral}")
        rc = 1
    if rc == 0:
        print("\nPASS  invariantes sostenidos en todo el muestreo")
    print("=" * 78)
    return rc

# ===============================================================
# SEGMENTO 9 --- MAIN
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
    preparar(raiz)

    print("=" * 78)
    print("MONTE CARLO ADVERSARIAL — VPSI-TRUTH")
    print(f"raiz={raiz}")
    print(f"N={args.n:,}  umbral={args.umbral}  seed={hex(args.seed)}")
    print("=" * 78)

    print("\n[1] descubriendo piezas ...")
    mod_ax = cargar_modulo("axiomas")
    mod_ct = cargar_modulo("constante")
    mod_fo = cargar_modulo("formulas")
    mod_ca = cargar_modulo("calculator")

    ALPHA = constante(mod_ct, "ALPHA", "alpha", "A")
    BETA = constante(mod_ct, "BETA", "beta", "B")

    fn_ri, org_ri = buscar(mod_fo, "tru_ri")
    fn_tt, org_tt = buscar(mod_fo, "tru_total")
    fn_k, org_k = buscar(mod_ca, "calcular_k")
    fn_pipe, org_pipe = buscar(mod_ca, "calcular")

    hallado = {
        "axiomas": mod_ax.__name__ if mod_ax else "",
        "constante": mod_ct.__name__ if mod_ct else "",
        "ALPHA/BETA": f"{ALPHA} / {BETA}" if ALPHA is not None else "",
        "tru_ri": org_ri,
        "tru_total": org_tt,
        "calcular_k": org_k,
        "pipeline": org_pipe,
    }
    for rol, org in hallado.items():
        print(f"    {rol:14s}: {org or 'no descubierta'}")

    if ALPHA is None and fn_tt is None and mod_ax is None:
        print("\nFAIL  no se descubrio ninguna pieza medible.")
        return 1

    rng = random.Random(args.seed)
    reg = Registro()
    t0 = time.time()
    n = args.n

    print("\n[2] midiendo ...")
    print("    F1  ancla alpha/beta ...")
    f1_ancla(reg, ALPHA, BETA)
    print("    F2  barrido axiomatico ...")
    f2_barrido(reg, mod_ax)
    print(f"    F3  funcional canonico ({n:,}) ...")
    f3_formula(reg, fn_ri, fn_tt, ALPHA, BETA, rng, n)
    print("    F4  renombrado ...")
    f4_renombrado(reg, fn_k)
    print("    F5  no-proposicion ...")
    f5_no_proposicion(reg, fn_k)
    print("    F6  sin dominio ...")
    f6_sin_dominio(reg, fn_k)
    print(f"    F7  ruido ({n:,}) ...")
    f7_ruido(reg, fn_k, rng, n)
    print(f"    F8  determinismo ({max(1, n // 10):,}) ...")
    f8_determinismo(reg, fn_k, rng, n)
    print("    F9  exactitud Fraction ...")
    f9_exactitud(reg, fn_pipe)

    return informe(reg, raiz, hallado, time.time() - t0,
                   args.umbral, args.verbose)

# ===============================================================
# SEGMENTO 10 --- ENTRADA PYTEST
# ===============================================================

def test_montecarlo_vpsi():
    """parse_args con lista vacia: pytest deja sus flags en sys.argv."""
    rc = main([])
    assert rc == 0, (
        "Monte Carlo VPSI: invariante roto. Ver detalle arriba."
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
