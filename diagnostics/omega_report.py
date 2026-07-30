#!/usr/bin/env python3
"""
OMEGA REPORT - VPSI-TRUTH
Auditoria de ejecucion real, no de descubrimiento.

Cada compuerta ejecuta el camino que audita y reporta lo que devuelve.
Ninguna compuerta afirma mas de lo que midio.

Estados:
    OK        la compuerta corrio y el resultado es el exigido
    FALLO     la compuerta corrio y el resultado no es el exigido
    PENDIENTE la compuerta no pudo correr por una pieza ausente
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Si STRICT=1, un FALLO devuelve exit code 1 y el CI se pone rojo.
# Si STRICT=0, el reporte informa pero el job pasa.
STRICT = os.getenv("OMEGA_STRICT", "0") == "1"

OK = "OK"
FALLO = "FALLO"
PENDIENTE = "PENDIENTE"


class Compuerta:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.estado = PENDIENTE
        self.detalle: List[str] = []
        self.datos: Dict[str, Any] = {}

    def ok(self, msg: str = ""):
        self.estado = OK
        if msg:
            self.detalle.append(msg)
        return self

    def fallo(self, msg: str):
        self.estado = FALLO
        self.detalle.append(msg)
        return self

    def pendiente(self, msg: str):
        self.estado = PENDIENTE
        self.detalle.append(msg)
        return self

    def nota(self, msg: str):
        self.detalle.append(msg)
        return self


def frac(v) -> str:
    """Representa una Fraction como fraccion exacta y decimal de lectura."""
    if isinstance(v, Fraction):
        return f"{v}  ({float(v):.6f})"
    return str(v)


# =============================================================================
# COMPUERTA 1 - CONSTANTES
# =============================================================================

def compuerta_constantes() -> Tuple[Compuerta, Optional[Fraction], Optional[Fraction]]:
    c = Compuerta("Constantes ALPHA / BETA")
    try:
        from modules.constante import ALPHA, BETA
    except Exception as e:
        c.pendiente(f"no se pudo importar modules.constante: {type(e).__name__}: {e}")
        return c, None, None

    c.datos["alpha"] = str(ALPHA)
    c.datos["beta"] = str(BETA)
    c.datos["tipo_alpha"] = type(ALPHA).__name__
    c.datos["tipo_beta"] = type(BETA).__name__

    if not isinstance(ALPHA, Fraction) or not isinstance(BETA, Fraction):
        c.fallo(
            f"ALPHA y BETA deben ser Fraction. "
            f"ALPHA={type(ALPHA).__name__}, BETA={type(BETA).__name__}"
        )
        return c, None, None

    c.nota(f"ALPHA = {frac(ALPHA)}")
    c.nota(f"BETA  = {frac(BETA)}")

    suma = ALPHA + BETA
    c.datos["suma"] = str(suma)
    if suma != Fraction(1):
        c.fallo(f"invariante roto: ALPHA + BETA = {suma}, se exige 1 exacto")
        return c, ALPHA, BETA

    c.nota("ALPHA + BETA = 1 exacto")
    c.ok()
    return c, ALPHA, BETA


# =============================================================================
# COMPUERTA 2 - MODULOS Y ROLES
# =============================================================================

ROLES_ESPERADOS = {
    "AX": "axiomas: juez de contraste",
    "CT": "constante: ALPHA y BETA",
    "FO": "formulas: tru_ri y tru_total",
    "CA": "calculador: devuelve C, L, K",
    "CX": "contexto: resuelve Octx",
    "TX": "taxonomia: anota tacticas",
}

OBLIGATORIOS = ("AX", "CT", "FO")


def compuerta_modulos(eng) -> Compuerta:
    c = Compuerta("Modulos y roles")
    if eng is None:
        c.pendiente("Engine no disponible")
        return c

    resumen = eng.registro.resumen()
    roles = resumen.get("roles", {})
    vacios = resumen.get("roles_vacios", [])
    rechazados = resumen.get("rechazados", [])

    c.datos["roles"] = roles
    c.datos["roles_vacios"] = vacios
    c.datos["rechazados"] = rechazados

    for rol, desc in ROLES_ESPERADOS.items():
        if rol in roles:
            c.nota(f"  {rol}  CARGADO   {roles[rol]:12s}  {desc}")
        else:
            marca = "AUSENTE" if rol in OBLIGATORIOS else "vacio"
            c.nota(f"  {rol}  {marca:9s} {'-':12s}  {desc}")

    for r in rechazados:
        c.nota(f"  RECHAZADO {r.get('ruta')}: {r.get('razon')}")

    faltan_obl = [r for r in OBLIGATORIOS if r not in roles]
    if faltan_obl:
        c.fallo(f"roles obligatorios ausentes: {faltan_obl}")
        return c

    if vacios:
        c.nota(
            f"roles opcionales vacios: {vacios} "
            "-- sin CA no hay C, L, K y el camino de evaluacion no puede correr"
        )
    c.ok()
    return c


# =============================================================================
# COMPUERTA 3 - BARRIDO AXIOMATICO CON DESGLOSE DE ORIGEN
# =============================================================================

def _cargar_modulo_suelto(nombre: str, ruta: Path, paquete_dir: Optional[Path] = None):
    locs = [str(paquete_dir)] if paquete_dir else None
    spec = importlib.util.spec_from_file_location(
        nombre, ruta, submodule_search_locations=locs
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"no se pudo crear spec para {ruta}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


def compuerta_axiomas(eng) -> Compuerta:
    c = Compuerta("Barrido axiomatico")
    if eng is None:
        c.pendiente("Engine no disponible")
        return c

    informe = eng.informe_axiomas or {}
    total = informe.get("declaraciones", 0)
    choques = informe.get("choques", []) or []
    errores = informe.get("errores", []) or []

    c.datos["total"] = total
    c.datos["choques"] = len(choques)
    c.datos["errores"] = len(errores)

    c.nota(f"total declaraciones que entraron al barrido: {total}")
    c.nota(f"choques: {len(choques)}   errores de forma: {len(errores)}")

    # --- desglose por origen ---
    ax_dir = REPO_ROOT / "modules" / "axiomas"
    por_archivo: Dict[str, int] = {}
    ids_archivo: List[str] = []

    if ax_dir.exists():
        for archivo in sorted(ax_dir.glob("*.py")):
            if archivo.name == "__init__.py" or archivo.name.startswith("_"):
                continue
            try:
                mod = _cargar_modulo_suelto(f"omega_ax_{archivo.stem}", archivo)
            except Exception as e:
                por_archivo[archivo.name] = -1
                c.nota(f"  archivo {archivo.name}: NO CARGA ({type(e).__name__}: {e})")
                continue

            decls = getattr(mod, "DECLARACIONES", None)
            if isinstance(decls, list):
                por_archivo[archivo.name] = len(decls)
                ids_archivo.extend(str(d.get("id")) for d in decls if isinstance(d, dict))
                c.nota(f"  archivo {archivo.name}: {len(decls)} via DECLARACIONES")
            else:
                # busca funciones que devuelvan declaraciones pero no expongan la lista
                alternativas = [
                    n for n in ("declaraciones", "declarations", "axiomas", "axioms")
                    if callable(getattr(mod, n, None))
                ]
                cuenta_alt = 0
                for n in alternativas:
                    try:
                        r = getattr(mod, n)()
                        if isinstance(r, list):
                            cuenta_alt = max(cuenta_alt, len(r))
                    except Exception:
                        pass
                por_archivo[archivo.name] = 0
                if cuenta_alt:
                    c.nota(
                        f"  archivo {archivo.name}: 0 cargadas -- "
                        f"expone {alternativas} con {cuenta_alt} declaraciones "
                        "pero no el atributo DECLARACIONES"
                    )
                else:
                    c.nota(f"  archivo {archivo.name}: 0 cargadas, sin DECLARACIONES")

    total_archivos = sum(v for v in por_archivo.values() if v > 0)
    c.datos["por_archivo"] = por_archivo
    c.datos["total_archivos"] = total_archivos

    # --- externas: lo que cada contenedor declara via axiomas() ---
    externas: Dict[str, int] = {}
    ids_externas: List[str] = []
    for cont in eng.registro.contenedores.values():
        g = cont.fn("axiomas")
        if callable(g):
            try:
                lista = g()
            except Exception as e:
                externas[cont.nombre] = -1
                c.nota(f"  externas de {cont.nombre}: ERROR {type(e).__name__}: {e}")
                continue
            if isinstance(lista, list):
                externas[cont.nombre] = len(lista)
                ids_externas.extend(str(d.get("id")) for d in lista if isinstance(d, dict))
                c.nota(f"  externas de {cont.nombre}: {len(lista)} via axiomas()")

    total_externas = sum(v for v in externas.values() if v > 0)
    c.datos["externas"] = externas
    c.datos["total_externas"] = total_externas

    c.nota(f"suma esperada: archivos {total_archivos} + externas {total_externas} "
           f"= {total_archivos + total_externas}   (barrido reporto {total})")

    # --- duplicados por id ---
    todos = ids_archivo + ids_externas
    vistos: Dict[str, int] = {}
    for i in todos:
        vistos[i] = vistos.get(i, 0) + 1
    duplicados = {k: v for k, v in vistos.items() if v > 1}
    c.datos["ids_unicos"] = len(vistos)
    c.datos["duplicados"] = len(duplicados)

    if duplicados:
        muestra = ", ".join(sorted(duplicados)[:8])
        c.nota(
            f"ids repetidos: {len(duplicados)} de {len(vistos)} unicos "
            f"(ej: {muestra})"
        )
        c.nota(
            "una misma declaracion entra por dos caminos de carga. "
            "hoy no produce choque; si una copia se edita y la otra no, "
            "el choque sera entre una declaracion y su propia copia"
        )

    if errores:
        for e in errores[:10]:
            c.nota(f"  error de forma: {e}")

    if choques:
        c.fallo(f"{len(choques)} contradicciones axiomaticas")
        for ch in choques[:10]:
            c.nota(f"  choque: {ch}")
        return c

    if total == 0:
        c.fallo("0 declaraciones entraron al barrido: coherente por vacuidad, no por coherencia")
        return c

    c.ok()
    return c


# =============================================================================
# COMPUERTA 4 - FORMULAS: EJECUCION REAL DE Tru_ri Y Tru_total
# =============================================================================

VECTORES = [
    # (C, L, K, descripcion)
    (Fraction(1), Fraction(1), Fraction(1),        "sincronizacion total"),
    (Fraction(1), Fraction(1), Fraction(90, 100),  "una particion sin emision discriminante"),
    (Fraction(1), Fraction(1), Fraction(0),        "K colapsada: forma impecable, ancla rota"),
    (Fraction(0), Fraction(1), Fraction(1),        "C colapsada"),
    (Fraction(1), Fraction(0), Fraction(1),        "L colapsada"),
    (Fraction(0), Fraction(0), Fraction(0),        "colapso de los tres factores"),
    (Fraction(85, 100), Fraction(90, 100), Fraction(70, 100), "caso intermedio"),
]


def compuerta_formulas(eng, ALPHA: Optional[Fraction], BETA: Optional[Fraction]) -> Compuerta:
    c = Compuerta("Formulas Tru_ri y Tru_total")

    if ALPHA is None or BETA is None:
        c.pendiente("constantes no disponibles")
        return c

    try:
        from modules.formulas.truth import tru_ri, tru_total
    except Exception as e:
        c.pendiente(f"no se pudo importar modules.formulas.truth: {type(e).__name__}: {e}")
        return c

    c.nota("formula canonica: Tru_total = (C * L * K * ALPHA) + BETA")
    c.nota("")
    c.nota("     C      L      K   |   Tru_Ri            Tru_total          estado")
    c.nota("   " + "-" * 76)

    fallos = 0
    filas = []

    for C, L, K, desc in VECTORES:
        ri = tru_ri(C, L, K)
        tt = tru_total(C, L, K)

        ri_esp = C * L * K
        tt_esp = (C * L * K * ALPHA) + BETA

        problemas = []
        if ri != ri_esp:
            problemas.append(f"Tru_ri esperado {ri_esp}, recibido {ri}")
        if tt != tt_esp:
            problemas.append(f"Tru_total esperado {tt_esp}, recibido {tt}")
        if not isinstance(ri, Fraction) or not isinstance(tt, Fraction):
            problemas.append(
                f"tipo no exacto: Tru_ri={type(ri).__name__}, Tru_total={type(tt).__name__}"
            )
        if not (BETA <= tt <= ALPHA + BETA):
            problemas.append(f"Tru_total fuera de cota [{BETA}, {ALPHA + BETA}]: {tt}")

        # multiplicatividad: un factor nulo colapsa al piso
        if Fraction(0) in (C, L, K) and tt != BETA:
            problemas.append(f"factor nulo pero Tru_total = {tt}, se exige BETA = {BETA}")

        estado = "OK" if not problemas else "FALLO"
        if problemas:
            fallos += 1

        filas.append({
            "C": str(C), "L": str(L), "K": str(K),
            "tru_ri": str(ri), "tru_total": str(tt),
            "estado": estado, "descripcion": desc,
            "problemas": problemas,
        })

        c.nota(
            f"   {float(C):5.2f}  {float(L):5.2f}  {float(K):5.2f}  |  "
            f"{str(ri):16s}  {float(tt):.6f}   {estado}   {desc}"
        )
        for p in problemas:
            c.nota(f"        -> {p}")

    c.datos["vectores"] = filas
    c.nota("")

    # piso y techo declarados
    piso = tru_total(Fraction(0), Fraction(0), Fraction(0))
    techo = tru_total(Fraction(1), Fraction(1), Fraction(1))
    c.datos["piso"] = str(piso)
    c.datos["techo"] = str(techo)
    c.nota(f"piso  Tru_total(0,0,0) = {frac(piso)}   se exige BETA = {frac(BETA)}")
    c.nota(f"techo Tru_total(1,1,1) = {frac(techo)}   se exige ALPHA + BETA = {frac(ALPHA + BETA)}")

    if piso != BETA:
        c.fallo(f"piso incorrecto: {piso} != {BETA}")
        return c
    if techo != ALPHA + BETA:
        c.fallo(f"techo incorrecto: {techo} != {ALPHA + BETA}")
        return c

    if fallos:
        c.fallo(f"{fallos} de {len(VECTORES)} vectores no cumplen la formula declarada")
        return c

    c.ok(f"{len(VECTORES)} vectores verificados con aritmetica exacta")
    return c


# =============================================================================
# COMPUERTA 5 - CAMINO DE EVALUACION: LLAMA A evaluar() DE VERDAD
# =============================================================================

SONDAS = [
    {
        "nombre": "sonda basica",
        "peticion": {
            "mensaje": "prueba de camino de evaluacion",
            "contexto": "Octx declarado",
        },
    },
    {
        "nombre": "sonda con factores provistos",
        "peticion": {
            "mensaje": "prueba con C, L, K inyectados",
            "contexto": "Octx declarado",
            "C": "1", "L": "1", "K": "9/10",
        },
    },
]


def compuerta_evaluacion(eng) -> Compuerta:
    c = Compuerta("Camino de evaluacion (engine.evaluar)")
    if eng is None:
        c.pendiente("Engine no disponible")
        return c

    resultados = []
    hubo_excepcion = False
    hubo_undefined = False

    for sonda in SONDAS:
        c.nota(f"  {sonda['nombre']}: {json.dumps(sonda['peticion'], ensure_ascii=False)}")
        try:
            r = eng.evaluar(sonda["peticion"])
        except Exception as e:
            hubo_excepcion = True
            tb = traceback.extract_tb(sys.exc_info()[2])
            ultimo = tb[-1] if tb else None
            loc = f"{ultimo.filename}:{ultimo.lineno} en {ultimo.name}" if ultimo else "?"
            c.nota(f"    EXCEPCION {type(e).__name__}: {e}")
            c.nota(f"    en {loc}")
            resultados.append({
                "sonda": sonda["nombre"],
                "excepcion": f"{type(e).__name__}: {e}",
                "ubicacion": loc,
            })
            continue

        factores = r.get("factores", {})
        tt = r.get("tru_total")
        c.nota(f"    factores  : {factores}")
        c.nota(f"    Tru_Ri    : {r.get('tru_ri')}")
        c.nota(f"    Tru_total : {tt}")
        c.nota(f"    estado    : {r.get('estado')}")
        c.nota(f"    limitante : {r.get('limitante')}   detenido_en: {r.get('detenido_en')}")
        if r.get("fallos"):
            for f in r["fallos"]:
                c.nota(f"    fallo interno: {f.get('rol')} {f.get('contenedor')}: {f.get('razon')}")
        if r.get("anotaciones"):
            c.nota(f"    anotaciones taxonomia: {r['anotaciones']}")

        if tt == "UNDEFINED" or "UNDEFINED" in str(factores):
            hubo_undefined = True

        resultados.append({
            "sonda": sonda["nombre"],
            "factores": factores,
            "tru_ri": r.get("tru_ri"),
            "tru_total": tt,
            "estado": r.get("estado"),
            "limitante": r.get("limitante"),
            "detenido_en": r.get("detenido_en"),
            "fallos": r.get("fallos", []),
        })

    c.datos["sondas"] = resultados

    if hubo_excepcion:
        c.fallo(
            "evaluar() lanza excepcion: el camino de evaluacion no corre. "
            "sin contenedor CA, C/L/K quedan UNDEFINED y el reporte Omega interno "
            "compara UNDEFINED con Fraction"
        )
        return c

    if hubo_undefined:
        c.fallo(
            "evaluar() devuelve UNDEFINED en factores o Tru_total: "
            "no hay contenedor que calcule C, L, K"
        )
        return c

    c.ok("evaluar() corrio y devolvio factores y Tru_total definidos")
    return c


# =============================================================================
# COMPUERTA 6 - TESTS
# =============================================================================

def compuerta_tests() -> Compuerta:
    c = Compuerta("Tests (pytest / junit xml)")
    xml_path = DIAGNOSTICS_DIR / "test_results.xml"
    if not xml_path.exists():
        c.pendiente(f"no existe {xml_path.name}: corre pytest con --junit-xml antes de este paso")
        return c

    try:
        raiz = ET.parse(xml_path).getroot()
    except Exception as e:
        c.fallo(f"xml ilegible: {type(e).__name__}: {e}")
        return c

    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    total = fallos = errores = omitidos = 0
    nombres: List[str] = []

    for s in suites:
        total += int(s.get("tests", 0))
        fallos += int(s.get("failures", 0))
        errores += int(s.get("errors", 0))
        omitidos += int(s.get("skipped", 0))
        for caso in s.iter("testcase"):
            nombres.append(f"{caso.get('classname','')}::{caso.get('name','')}")

    fallidos = fallos + errores
    pasados = total - fallidos - omitidos
    tasa = (pasados / total * 100) if total else 0.0

    c.datos.update({
        "total": total, "pasados": pasados, "fallidos": fallidos,
        "omitidos": omitidos, "tasa": tasa, "casos": nombres,
    })

    c.nota(f"total {total}   pasados {pasados}   fallidos {fallidos}   omitidos {omitidos}   tasa {tasa:.2f}%")
    for n in nombres:
        c.nota(f"  {n}")

    # que modulos del paquete tocan los tests
    tests_dir = REPO_ROOT / "tests"
    tocados = set()
    if tests_dir.exists():
        for f in tests_dir.glob("*.py"):
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for objetivo in ("core.engine", "modules.constante", "modules.formulas", "modules.axiomas"):
                if objetivo in txt:
                    tocados.add(objetivo)
    c.datos["modulos_cubiertos"] = sorted(tocados)
    c.nota(f"modulos del paquete importados por los tests: {sorted(tocados) or 'ninguno'}")

    if fallidos:
        c.fallo(f"{fallidos} tests fallidos")
        return c
    if not tocados:
        c.fallo("ningun test importa core.engine ni modules.*: la suite no cubre el paquete")
        return c

    c.ok()
    return c


# =============================================================================
# ENSAMBLADO
# =============================================================================

def arrancar_engine() -> Tuple[Any, Optional[str]]:
    try:
        from core.engine import Engine
    except Exception as e:
        return None, f"no se pudo importar core.engine: {type(e).__name__}: {e}"

    try:
        eng = Engine(
            raiz_modulos=str(REPO_ROOT / "modules"),
            invocador_id="core",
            verificar_axiomas=True,
        )
        return eng, None
    except Exception as e:
        return None, f"el Engine no arranca: {type(e).__name__}: {e}"


def bloque(c: Compuerta) -> str:
    marca = {OK: "[OK]", FALLO: "[FALLO]", PENDIENTE: "[PENDIENTE]"}[c.estado]
    out = [f"{marca} {c.nombre}"]
    for d in c.detalle:
        out.append(f"    {d}" if d else "")
    return "\n".join(out)


def main() -> None:
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = os.getenv("GITHUB_SHA", "local")[:7]

    print("=" * 80)
    print("OMEGA REPORT - VPSI-TRUTH")
    print(f"generado: {ahora}    commit: {sha}    python: {sys.version.split()[0]}")
    print(f"modo: {'STRICT (un FALLO pone el CI en rojo)' if STRICT else 'INFORMATIVO'}")
    print("=" * 80)
    print()

    eng, err_engine = arrancar_engine()
    if err_engine:
        print(f"[FALLO] Arranque del Engine")
        print(f"    {err_engine}")
        print()

    c_const, ALPHA, BETA = compuerta_constantes()
    compuertas = [
        c_const,
        compuerta_modulos(eng),
        compuerta_axiomas(eng),
        compuerta_formulas(eng, ALPHA, BETA),
        compuerta_evaluacion(eng),
        compuerta_tests(),
    ]

    for c in compuertas:
        print(bloque(c))
        print()

    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    ancho = max(len(c.nombre) for c in compuertas)
    for c in compuertas:
        marca = {OK: "OK       ", FALLO: "FALLO    ", PENDIENTE: "PENDIENTE"}[c.estado]
        print(f"  {marca}  {c.nombre.ljust(ancho)}")

    n_ok = sum(1 for c in compuertas if c.estado == OK)
    n_fallo = sum(1 for c in compuertas if c.estado == FALLO)
    n_pend = sum(1 for c in compuertas if c.estado == PENDIENTE)
    print()
    print(f"  {n_ok} OK   {n_fallo} FALLO   {n_pend} PENDIENTE")
    print("=" * 80)

    datos = {
        "generado": datetime.now(timezone.utc).isoformat(),
        "commit": sha,
        "strict": STRICT,
        "compuertas": [
            {
                "nombre": c.nombre,
                "estado": c.estado,
                "detalle": [d for d in c.detalle if d],
                "datos": c.datos,
            }
            for c in compuertas
        ],
        "conteo": {"ok": n_ok, "fallo": n_fallo, "pendiente": n_pend},
    }

    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    (DIAGNOSTICS_DIR / "omega_report_data.json").write_text(
        json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nJSON: {DIAGNOSTICS_DIR / 'omega_report_data.json'}")

    if STRICT and (n_fallo or err_engine):
        sys.exit(1)


if __name__ == "__main__":
    main()
