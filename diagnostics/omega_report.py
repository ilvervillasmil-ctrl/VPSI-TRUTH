#!/usr/bin/env python3
"""
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.9)
==============================

Orden de presentación (contrato de salida):
  1) AUDITORÍA DEL VPSI  — valuación del repositorio como objeto
  2) ÚLTIMO TEST         — valuación del último ciclo de prueba
  3) Resto del mapa      — salud, intervención, capas, generatividad

Contrato de cálculo (inviolable):
  - C, L, K, Tru_Ri, Tru_total los produce el sistema (CA / FO / Engine).
  - Omega NO inventa Fraction, NO aplica la fórmula, NO rellena huecos.
  - Omega SOLO LEE lo que el ciclo depositó y lo presenta tal cual.
  - 0 es 0. UNDEFINED es UNDEFINED. None es "no depositado".
  - Un chulito marca factor LEÍDO; su ausencia marca factor NO depositado.

Autor: Ilver Villasmil
ORCID: 0009-0009-3413-4270
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ICON_OK = "✅"
ICON_FAIL = "❌"
ICON_PEND = "⚪"
ICON_WARN = "⚠️"
ICON_INFO = "ℹ️"
ICON_DOT = "·"
ICON_MOD = "📦"
ICON_REJ = "🚫"
ICON_CIT = "📎"
ICON_CLK = "📐"
ICON_READ = "📖"

STRICT = os.getenv("OMEGA_STRICT", "0") == "1"
VERSION = "9.9"

CAMPOS_OBLIGATORIOS = (
    "estado_engine",
    "constantes",
    "informe_axiomas",
)

# Petición canónica de auto-auditoría del repositorio (O real)
PETICION_AUDITORIA_VPSI = {
    "contexto": (
        "Auditoría estructural del repositorio VPSI-TRUTH: "
        "coherencia axiomática, contratos, mecánica y correlación "
        "del sistema consigo mismo en este run."
    ),
    "modo_entrada": "auditoria",
    "O_id": "O_VPSI_REPO",
    "enunciado_O": (
        "Estado observable del repositorio VPSI-TRUTH "
        "(axiomas, contratos, módulos, generatividad) en el run actual."
    ),
    "pedir_anuncio": True,
    "tipos_peticion": [
        "dame_cadena_completa",
        "dame_normas",
        "auto_auditoria",
    ],
}


# =============================================================================
# VALIDACIÓN
# =============================================================================
def validar_entrada(datos: Dict[str, Any]) -> List[str]:
    faltas: List[str] = []
    if not isinstance(datos, dict):
        return ["entrada no es dict"]
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos:
            faltas.append("falta campo obligatorio: {0}".format(campo))
    if "constantes" in datos:
        c = datos["constantes"]
        if not isinstance(c, dict) or "ALPHA" not in c or "BETA" not in c:
            faltas.append("constantes debe contener ALPHA y BETA")
    if "informe_axiomas" in datos:
        ia = datos["informe_axiomas"]
        if not isinstance(ia, dict) or "coherente" not in ia:
            faltas.append("informe_axiomas inválido o incompleto")
    if "estado_engine" in datos:
        if datos["estado_engine"] not in ("OPERATIVO", "RECHAZADO", "NO_INICIADO"):
            faltas.append(
                "estado_engine inválido: {0}".format(datos["estado_engine"])
            )
    return faltas


# =============================================================================
# LECTURA FIEL — sin inventar, sin calcular
# =============================================================================
def _es_undefined(v: Any) -> bool:
    """True si el ciclo depositó UNDEFINED (base nula / ancla)."""
    if v is None:
        return False
    if type(v).__name__ in ("_Undefined", "Undefined"):
        return True
    s = str(v).strip().upper()
    return s in ("UNDEFINED", "INDEFINIDO", "<UNDEFINED>")


def _depositado(v: Any) -> bool:
    """True si el ciclo dejó un valor (incluye 0 y UNDEFINED)."""
    if v is None:
        return False
    if isinstance(v, str) and not v.strip():
        return False
    return True


def _fmt(v: Any) -> str:
    """
    Presentación exacta de lo leído.
      None / vacío  →  no depositado
      UNDEFINED      →  UNDEFINED
      0 / Fraction  →  tal cual (0 es 0)
    """
    if v is None:
        return "no depositado"
    if _es_undefined(v):
        return "UNDEFINED"
    s = str(v).strip()
    if not s:
        return "no depositado"
    # normalizar representaciones raras de cero
    if s in ("0", "0/1", "0.0"):
        return "0"
    return s


def _marca_lectura(v: Any) -> str:
    """Chulito si el factor fue leído del ciclo; pendiente si no."""
    if not _depositado(v):
        return ICON_PEND
    if _es_undefined(v):
        return ICON_WARN  # leído, pero base nula
    return ICON_OK


def _pick(d: Dict[str, Any], *keys: str) -> Any:
    if not isinstance(d, dict):
        return None
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    for nest in ("resultado", "truth", "valores", "salida", "factores"):
        sub = d.get(nest)
        if isinstance(sub, dict):
            for k in keys:
                if k in sub and sub[k] is not None:
                    return sub[k]
    return None


def _cuerpo_resultado(r: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(r, dict):
        return {}
    inner = r.get("resultado")
    if isinstance(inner, dict) and (
        "estado" in inner
        or "tru_total" in inner
        or "factores" in inner
        or "Tru_total" in inner
        or "citacion" in inner
        or "C" in inner
        or "L" in inner
        or "K" in inner
    ):
        return inner
    return r


def _factores_de(r: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lee C, L, K del ciclo.
    Prioridad: resultado.factores → cuerpo plano → fila superior.
    No convierte, no rellena.
    """
    body = _cuerpo_resultado(r)
    fac = body.get("factores") if isinstance(body.get("factores"), dict) else {}

    def _uno(*claves: str) -> Any:
        for k in claves:
            if k in fac and fac[k] is not None:
                return fac[k]
        for k in claves:
            if k in body and body[k] is not None:
                return body[k]
        if isinstance(r, dict):
            for k in claves:
                if k in r and r[k] is not None:
                    return r[k]
        return None

    return {
        "C": _uno("C", "c"),
        "L": _uno("L", "l"),
        "K": _uno("K", "k"),
    }


def _extraer_valuacion(r: Any) -> Dict[str, Any]:
    """Normaliza un ciclo Engine → bloque de valuación (solo lectura)."""
    vacio = {
        "estado": None,
        "C": None,
        "L": None,
        "K": None,
        "tru_ri": None,
        "tru_total": None,
        "alpha": None,
        "beta": None,
        "taxonomia": None,
        "citas": [],
        "razon": None,
        "permite_k": None,
        "origen": None,
        "lectura": {
            "C": False,
            "L": False,
            "K": False,
            "tru_ri": False,
            "tru_total": False,
        },
    }
    if not isinstance(r, dict):
        return vacio

    body = _cuerpo_resultado(r)
    fac = _factores_de(r)
    cit = body.get("citacion") if isinstance(body.get("citacion"), dict) else {}
    val = body.get("valuacion") if isinstance(body.get("valuacion"), dict) else {}
    cx = body.get("contexto_cx") if isinstance(body.get("contexto_cx"), dict) else {}

    citas: List[str] = []
    for src in (val.get("ids"), cx.get("ids_cx_relevantes"), body.get("ids")):
        if isinstance(src, list):
            for i in src:
                s = str(i).strip()
                if s and s not in citas:
                    citas.append(s)
    for a in cit.get("anuncios") or []:
        if not isinstance(a, dict):
            continue
        tid = a.get("id") or a.get("titulo")
        if tid:
            s = str(tid).strip()
            if s and s not in citas:
                citas.append(s)

    tax = (
        body.get("taxonomia")
        or body.get("tx")
        or val.get("taxonomia")
        or (
            (cit.get("meta") or {}).get("taxonomia")
            if isinstance(cit.get("meta"), dict)
            else None
        )
    )

    C = fac.get("C")
    L = fac.get("L")
    K = fac.get("K")
    tru_ri = _pick(body, "tru_ri", "Tru_Ri")
    if tru_ri is None and isinstance(r, dict):
        tru_ri = r.get("tru_ri") or r.get("Tru_Ri")
    tru_total = _pick(body, "tru_total", "Tru_total")
    if tru_total is None and isinstance(r, dict):
        tru_total = r.get("tru_total") or r.get("Tru_total")

    return {
        "estado": _pick(body, "estado") or _pick(r, "estado"),
        "C": C,
        "L": L,
        "K": K,
        "tru_ri": tru_ri,
        "tru_total": tru_total,
        "alpha": body.get("alpha") if body.get("alpha") is not None else r.get("alpha"),
        "beta": body.get("beta") if body.get("beta") is not None else r.get("beta"),
        "taxonomia": tax,
        "citas": citas,
        "razon": body.get("razon") or r.get("razon"),
        "permite_k": cx.get("permite_k"),
        "origen": r.get("invocador_id") or body.get("origen") or r.get("origen"),
        "secuencia": r.get("secuencia"),
        "n_citas": cit.get("n_citas"),
        "n_anuncios": cit.get("n_anuncios"),
        "lectura": {
            "C": _depositado(C),
            "L": _depositado(L),
            "K": _depositado(K),
            "tru_ri": _depositado(tru_ri),
            "tru_total": _depositado(tru_total),
        },
    }


def _caja_valuacion(
    titulo: str,
    sub: str,
    v: Dict[str, Any],
    *,
    ancho: int = 78,
) -> List[str]:
    """
    Recuadro de LECTURA (no de cálculo):

        LECTURA DEL CICLO
          ✅ C (coherencia)   = valor exacto
          ✅ L (lógica)      = valor exacto
          ✅ K (correlación) = valor exacto
          …
        0 es 0. UNDEFINED es UNDEFINED. no depositado = no vino del ciclo.
    """
    lineas: List[str] = []
    borde = "═" * ancho
    lineas.append(borde)
    lineas.append("  {0}".format(titulo))
    if sub:
        lineas.append("  {0}".format(sub))
    lineas.append(borde)

    est = _fmt(v.get("estado")) if v.get("estado") is not None else "no depositado"
    if est in ("OK", "OPERATIVO", "COMPLETO"):
        m = ICON_OK
    elif est in ("FALLO", "ERROR", "RECHAZADO"):
        m = ICON_FAIL
    elif est in ("UNDEFINED", "PARCIAL", "no depositado"):
        m = ICON_WARN
    else:
        m = ICON_DOT

    lineas.append("  Estado     : {0} {1}".format(m, est))
    if v.get("razon"):
        lineas.append("  Razón      : {0}".format(str(v.get("razon"))[:70]))
    if v.get("permite_k") is not None:
        lineas.append("  permite_k  : {0}".format(_fmt(v.get("permite_k"))))
    lineas.append("")

    lec = v.get("lectura") or {}
    n_leidos = sum(1 for k in ("C", "L", "K") if lec.get(k))
    lineas.append(
        "  {0}  LECTURA DEL CICLO  (Omega no calcula; solo presenta)".format(ICON_READ)
    )
    lineas.append(
        "  Factores leídos: {0}/3  (C={1} L={2} K={3})".format(
            n_leidos,
            ICON_OK if lec.get("C") else ICON_PEND,
            ICON_OK if lec.get("L") else ICON_PEND,
            ICON_OK if lec.get("K") else ICON_PEND,
        )
    )
    lineas.append("  ┌─────────────────────────────────────────────────────────┐")

    def _fila_factor(nombre: str, etiqueta: str, val: Any) -> str:
        marca = _marca_lectura(val)
        texto = _fmt(val)
        return "  │  {0} {1} ({2}) =  {3}".format(
            marca, nombre.ljust(1), etiqueta, texto.ljust(32)
        ) + "│"

    lineas.append(_fila_factor("C", "coherencia  ", v.get("C")))
    lineas.append(_fila_factor("L", "lógica      ", v.get("L")))
    lineas.append(_fila_factor("K", "correlación ", v.get("K")))
    lineas.append("  │─────────────────────────────────────────────────────────│")

    m_ri = _marca_lectura(v.get("tru_ri"))
    m_tt = _marca_lectura(v.get("tru_total"))
    lineas.append(
        "  │  {0} Tru_Ri     =  {1}".format(
            m_ri, _fmt(v.get("tru_ri")).ljust(40)
        )
        + "│"
    )
    lineas.append(
        "  │  {0} Tru_total  =  {1}".format(
            m_tt, _fmt(v.get("tru_total")).ljust(40)
        )
        + "│"
    )
    if v.get("alpha") is not None or v.get("beta") is not None:
        lineas.append(
            "  │  ancla      α={0}  β={1}".format(
                _fmt(v.get("alpha")), _fmt(v.get("beta"))
            ).ljust(58)
            + "│"
        )
    lineas.append("  └─────────────────────────────────────────────────────────┘")
    lineas.append(
        "  Nota: ✅ leído del ciclo · ⚠️ UNDEFINED (base nula) · ⚪ no depositado"
    )
    lineas.append("        0 es valor real. Omega no rellena ni recalcula.")
    lineas.append("")

    tax = v.get("taxonomia")
    lineas.append(
        "  Taxonomía  : {0}".format(_fmt(tax) if tax is not None else "none")
    )

    citas = list(v.get("citas") or [])
    if citas:
        lineas.append("  {0} Citas (teoremas / axiomas / normas):".format(ICON_CIT))
        for i, c in enumerate(citas[:24], 1):
            lineas.append("      {0:>2}. {1}".format(i, c))
        if len(citas) > 24:
            lineas.append("      … y {0} más".format(len(citas) - 24))
    else:
        lineas.append(
            "  {0} Citas      : — (sin ids/anuncios en el ciclo)".format(ICON_CIT)
        )

    if v.get("n_citas") is not None or v.get("n_anuncios") is not None:
        lineas.append(
            "  CIT resumen: n_citas={0}  n_anuncios={1}".format(
                _fmt(v.get("n_citas")), _fmt(v.get("n_anuncios"))
            )
        )
    if v.get("origen"):
        lineas.append("  Origen     : {0}".format(_fmt(v.get("origen"))))
    if v.get("secuencia") is not None:
        lineas.append("  Secuencia  : {0}".format(_fmt(v.get("secuencia"))))
    lineas.append(borde)
    lineas.append("")
    return lineas


def _tabla(
    headers: List[str],
    rows: List[List[str]],
    anchos: List[int] | None = None,
) -> List[str]:
    if anchos is None:
        anchos = [
            max(len(h), max((len(str(r[i])) for r in rows), default=0))
            for i, h in enumerate(headers)
        ]
    sep = "+" + "+".join("-" * (w + 2) for w in anchos) + "+"

    def fila(vals: List[str]) -> str:
        return (
            "| "
            + " | ".join(str(v).ljust(anchos[i]) for i, v in enumerate(vals))
            + " |"
        )

    out = [sep, fila(headers), sep]
    for r in rows:
        out.append(fila(r))
    out.append(sep)
    return out


def _lineas_generatividad(g: Dict[str, Any] | None) -> List[str]:
    out: List[str] = [
        "=" * 80,
        "{0}  GENERATIVIDAD (TR1 / U1)".format(ICON_INFO),
        "=" * 80,
    ]
    if not g or g.get("estado") == "UNDEFINED":
        out.append(
            "  {0} sin datos — AX.generatividad no disponible".format(ICON_PEND)
        )
        if g and g.get("razon"):
            out.append("  razon: {0}".format(g.get("razon")))
        out.append("")
        return out

    im = g.get("im_vs_theta", "—")
    marca_im = (
        ICON_OK if im == "GENERATIVO" else (ICON_WARN if im == "ESTANCADO" else ICON_PEND)
    )
    out.append("  |Θ| (AX)           : {0}".format(g.get("theta_n", "—")))
    out.append("  pares totales      : {0}".format(g.get("pares_totales", "—")))
    out.append("  pares compatibles  : {0}".format(g.get("pares_compatibles", "—")))
    out.append("  pares novedosos    : {0}".format(g.get("pares_novedosos", "—")))
    out.append("  |Im(⊕)| ? |Θ|      : {0} {1}".format(marca_im, im))
    out.append("  dominios           : {0}".format(g.get("dominios", [])))
    out.append("  U1                 : {0}".format(g.get("u1_estado", "—")))
    can = g.get("canonica") or {}
    if can:
        out.append("  --- capa canónica ---")
        out.append("  |Θ|_can            : {0} / 24".format(can.get("theta_n", "—")))
        out.append("  novedosos_can      : {0}".format(can.get("pares_novedosos", "—")))
        out.append("  |Im| ? |Θ| can     : {0}".format(can.get("im_vs_theta", "—")))
    out.append("")
    return out


# =============================================================================
# MAPA DE INTERVENCIÓN
# =============================================================================
def construir_acciones(datos: Dict[str, Any]) -> List[Dict[str, Any]]:
    acciones: List[Dict[str, Any]] = []
    reg = datos.get("registro_modulos") or {}
    vacios = list(reg.get("roles_vacios") or [])
    rechazados = list(reg.get("rechazados") or [])
    ct = datos.get("contratos")

    if datos.get("estado_engine") != "OPERATIVO":
        acciones.append({
            "prioridad": 1,
            "tipo": "BLOQUEANTE",
            "item": "Engine",
            "detalle": "estado = {0}".format(datos.get("estado_engine")),
            "impacto": "Sin Engine OPERATIVO no hay valuación confiable",
            "accion": "Revisar errores_arranque",
            "errores": list(datos.get("errores_arranque") or []),
        })

    ia = datos.get("informe_axiomas") or {}
    if not ia.get("coherente", False):
        acciones.append({
            "prioridad": 1,
            "tipo": "BLOQUEANTE",
            "item": "Axiomas",
            "detalle": "choques={0} errores={1}".format(
                len(ia.get("choques") or []), len(ia.get("errores") or [])
            ),
            "impacto": "Axiomatización incoherente",
            "accion": "Resolver choques en modules/axiomas",
            "errores": list(ia.get("choques") or [])[:5],
        })

    if isinstance(ct, dict) and ct.get("coherente") is False:
        acciones.append({
            "prioridad": 2,
            "tipo": "CONTRATO",
            "item": "auditoria_contratos",
            "detalle": "coherente=False",
            "impacto": "Fallos de contrato en CI",
            "accion": "Leer diagnostics/contratos_report.json",
            "errores": [
                (e.get("mensaje") if isinstance(e, dict) else str(e))
                for e in (ct.get("errores") or [])[:5]
            ],
        })

    for r in rechazados:
        if not isinstance(r, dict):
            continue
        acciones.append({
            "prioridad": 2,
            "tipo": "RECHAZADO",
            "item": Path(str(r.get("ruta", "?"))).parent.name,
            "detalle": str(r.get("razon", "?")),
            "impacto": "Módulo ignorado",
            "accion": "Corregir CONTENEDOR/ROLES",
            "errores": [],
        })

    for rol in vacios:
        acciones.append({
            "prioridad": 3,
            "tipo": "VACÍO",
            "item": str(rol),
            "detalle": "rol sin módulo",
            "impacto": "Capacidad ausente",
            "accion": "Montar módulo rol={0}".format(rol),
            "errores": [],
        })

    av = datos.get("auditoria_vpsi") or {}
    lec = av.get("lectura") or {}
    if not av or not (lec.get("C") or lec.get("L") or lec.get("K") or av.get("tru_total") is not None):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "auditoria_vpsi",
            "detalle": "Ciclo de auto-auditoría sin factores depositados legibles",
            "impacto": "La caja 1 no muestra C/L/K leídos",
            "accion": "Engine.evaluar(PETICION_AUDITORIA_VPSI) debe depositar resultado",
            "errores": [],
        })

    if not datos.get("tests"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "tests",
            "detalle": "sin test_results.xml",
            "impacto": "Sin tasa pytest",
            "accion": "Generar junit xml en CI",
            "errores": [],
        })

    if not isinstance(ct, dict):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "contratos_report",
            "detalle": "ausente",
            "impacto": "Sin juez CI de contratos",
            "accion": "Correr auditoría estructural antes de Omega",
            "errores": [],
        })

    g = datos.get("generatividad")
    if not g or g.get("estado") == "UNDEFINED":
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "generatividad",
            "detalle": "no disponible",
            "impacto": "Sin TR1/U1",
            "accion": "AX.generatividad / censar_generatividad",
            "errores": [],
        })
    elif g.get("im_vs_theta") == "ESTANCADO":
        acciones.append({
            "prioridad": 5,
            "tipo": "TR1",
            "item": "generatividad",
            "detalle": "ESTANCADO",
            "impacto": "Sin expansión por recombinación",
            "accion": "Revisar gobierna/dominios",
            "errores": [],
        })

    acciones.sort(key=lambda a: a["prioridad"])
    return acciones


# =============================================================================
# PRESENTACIÓN
# =============================================================================
def presentar(datos: Dict[str, Any]) -> str:
    faltas = validar_entrada(datos)
    lineas: List[str] = []
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = os.getenv("GITHUB_SHA", "local")[:12]

    lineas += [
        "=" * 80,
        "{0}  OMEGA REPORT — MAPA DE TRABAJO".format(ICON_INFO),
        "VPSI-TRUTH (Versión {0})".format(VERSION),
        "Generado: {0}    Commit: {1}".format(ahora, sha),
        "Orden: (1) Auditoría VPSI  (2) Último test  (3) Mapa / capas",
        "Contrato: Omega SOLO LEE lo que el ciclo depositó · no calcula · no rellena",
        "=" * 80,
        "",
    ]

    if faltas:
        lineas.append("{0} Entrada incompleta".format(ICON_FAIL))
        for f in faltas:
            lineas.append("    - {0}".format(f))
        return "\n".join(lineas)

    estado = datos["estado_engine"]
    ia = datos["informe_axiomas"]
    coherente = bool(ia.get("coherente"))
    reg = datos.get("registro_modulos") or {}
    total = reg.get("total", 0)
    vacios = list(reg.get("roles_vacios") or [])
    rechazados = list(reg.get("rechazados") or [])
    ct = datos.get("contratos")
    acciones = construir_acciones(datos)
    bloqueantes = [a for a in acciones if a["tipo"] == "BLOQUEANTE"]
    n_bloqueantes = len(bloqueantes)

    if estado == "OPERATIVO" and coherente and n_bloqueantes == 0:
        salud, icon_salud = "OPERATIVO — listo para avanzar", ICON_OK
    elif estado == "OPERATIVO" and n_bloqueantes == 0:
        salud, icon_salud = "OPERATIVO con huecos no bloqueantes", ICON_WARN
    else:
        salud, icon_salud = "DEGRADADO — hay bloqueos", ICON_FAIL

    # =========================================================================
    # (1) AUDITORÍA DEL VPSI
    # =========================================================================
    av = datos.get("auditoria_vpsi") or {}
    lineas.extend(
        _caja_valuacion(
            "AUDITORÍA DEL VPSI  ·  el repositorio como objeto",
            "Auto-auditoría del sistema (contexto O_VPSI_REPO) · valores LEÍDOS del ciclo",
            av if av else {
                "estado": None,
                "C": None, "L": None, "K": None,
                "tru_ri": None, "tru_total": None,
                "taxonomia": None, "citas": [],
                "razon": "sin ciclo de auto-auditoría depositado",
                "lectura": {"C": False, "L": False, "K": False,
                            "tru_ri": False, "tru_total": False},
            },
        )
    )

    # =========================================================================
    # (2) ÚLTIMO TEST
    # =========================================================================
    ut = datos.get("ultimo_test") or {}
    lineas.extend(
        _caja_valuacion(
            "ÚLTIMO TEST EVALUADO",
            "Último ciclo real depositado (tests / uso) · valores LEÍDOS del ciclo",
            ut if ut else {
                "estado": None,
                "C": None, "L": None, "K": None,
                "tru_ri": None, "tru_total": None,
                "taxonomia": None, "citas": [],
                "razon": "sin evaluaciones.json o lista vacía",
                "lectura": {"C": False, "L": False, "K": False,
                            "tru_ri": False, "tru_total": False},
            },
        )
    )

    # =========================================================================
    # ESTADO GLOBAL
    # =========================================================================
    lineas += [
        "ESTADO GLOBAL",
        "  {0} Engine       : {1}".format(
            ICON_OK if estado == "OPERATIVO" else ICON_FAIL, estado
        ),
        "  {0} Axiomas      : {1}".format(
            ICON_OK if coherente else ICON_FAIL,
            "coherente" if coherente else "INCOHERENTE",
        ),
        "  {0} Contenedores : {1}".format(ICON_MOD, total),
        "  {0} Roles vacíos : {1}".format(
            ICON_OK if not vacios else ICON_WARN, len(vacios)
        ),
        "  {0} Rechazados   : {1}".format(
            ICON_OK if not rechazados else ICON_FAIL, len(rechazados)
        ),
        "  {0} Salud        : {1}".format(icon_salud, salud),
        "",
    ]

    # =========================================================================
    # MÓDULOS
    # =========================================================================
    roles = reg.get("roles") or {}
    todos = sorted(set(list(roles.keys()) + list(vacios)))
    rows_m = []
    for rol in todos:
        mods = roles.get(rol) or []
        if mods:
            rows_m.append([str(rol), "CARGADO", str(len(mods)), ", ".join(str(m) for m in mods)])
        else:
            rows_m.append([str(rol), "VACÍO", "0", "(sin módulo)"])
    lineas.append("{0}  MÓDULOS Y ROLES".format(ICON_MOD))
    if rows_m:
        lineas.extend(
            "  " + l
            for l in _tabla(["ROL", "ESTADO", "N", "MÓDULOS"], rows_m, [4, 9, 3, 36])
        )
    lineas.append("")

    # =========================================================================
    # INTERVENCIÓN
    # =========================================================================
    lineas.append("=" * 80)
    lineas.append("{0}  MAPA DE INTERVENCIÓN".format(ICON_WARN))
    lineas.append("=" * 80)
    lineas.append("")
    if not acciones:
        lineas.append("  {0} Sin acciones pendientes.".format(ICON_OK))
        lineas.append("")
    else:
        for i, a in enumerate(acciones, 1):
            tipo = a["tipo"]
            ic = (
                ICON_FAIL
                if tipo in ("BLOQUEANTE", "CONTRATO", "RECHAZADO")
                else (ICON_PEND if tipo == "DATOS" else ICON_WARN)
            )
            lineas.append("  {0} {1}. [{2}] {3}".format(ic, i, tipo, a["item"]))
            lineas.append("     Detalle   : {0}".format(a["detalle"]))
            lineas.append("     Impacto   : {0}".format(a["impacto"]))
            lineas.append("     Acción    : {0}".format(a["accion"]))
            lineas.append("")

    # =========================================================================
    # SALUD POR CAPA
    # =========================================================================
    lineas.append("=" * 80)
    lineas.append("{0}  SALUD POR CAPA".format(ICON_INFO))
    lineas.append("=" * 80)
    lineas.append("")

    const = datos.get("constantes") or {}
    lineas.append("  {0} Constantes (CT)".format(ICON_OK if const else ICON_PEND))
    lineas.append(
        "      ALPHA = {0}   BETA = {1}".format(const.get("ALPHA"), const.get("BETA"))
    )
    lineas.append("")

    lineas.append("  {0} Axiomas (AX)".format(ICON_OK if coherente else ICON_FAIL))
    lineas.append("      declaraciones = {0}".format(ia.get("declaraciones", "?")))
    lineas.append("      choques       = {0}".format(len(ia.get("choques") or [])))
    lineas.append("      errores       = {0}".format(len(ia.get("errores") or [])))
    if ia.get("por_tipo"):
        lineas.append("      por_tipo      = {0}".format(ia.get("por_tipo")))
    lineas.append("")

    fo = datos.get("informe_formulas")
    if fo:
        lineas.append(
            "  {0} Fórmulas (FO)".format(
                ICON_OK if fo.get("coherente", True) else ICON_FAIL
            )
        )
        lineas.append("      coherente = {0}".format(fo.get("coherente")))
    else:
        lineas.append("  {0} Fórmulas (FO) — no entregado".format(ICON_PEND))
    lineas.append("")

    mc = datos.get("informe_mecanica")
    if mc:
        lineas.append(
            "  {0} Mecánica (MC)".format(
                ICON_OK if mc.get("coherente") else ICON_FAIL
            )
        )
        lineas.append("      coherente = {0}".format(mc.get("coherente")))
    else:
        lineas.append("  {0} Mecánica (MC) — no entregado".format(ICON_PEND))
    lineas.append("")

    ca = datos.get("informe_calculator")
    if ca:
        lineas.append(
            "  {0} Calculator (CA)".format(
                ICON_OK if ca.get("coherente", True) else ICON_FAIL
            )
        )
        lineas.append("      coherente = {0}".format(ca.get("coherente")))
    else:
        lineas.append("  {0} Calculator (CA) — no entregado".format(ICON_PEND))
    lineas.append("")

    if isinstance(ct, dict) and "coherente" in ct:
        res = ct.get("resumen") or {}
        lineas.append(
            "  {0} Contratos (CI)".format(
                ICON_OK if ct.get("coherente") else ICON_FAIL
            )
        )
        lineas.append(
            "      coherente={0}  validos={1}  caps_ok={2}  caps_fallo={3}".format(
                ct.get("coherente"),
                res.get("contratos_validos", "?"),
                res.get("capacidades_verificadas", "?"),
                res.get("capacidades_fallidas", "?"),
            )
        )
    else:
        lineas.append("  {0} Contratos (CI) — sin report".format(ICON_PEND))
    lineas.append("")

    tests = datos.get("tests")
    if tests:
        ok_t = tests.get("fallidos", 1) == 0
        lineas.append(
            "  {0} Tests (pytest — forma)".format(ICON_OK if ok_t else ICON_FAIL)
        )
        lineas.append(
            "      total={0}  pasados={1}  fallidos={2}  tasa={3}%".format(
                tests.get("total"),
                tests.get("pasados"),
                tests.get("fallidos"),
                tests.get("tasa"),
            )
        )
    else:
        lineas.append("  {0} Tests — no entregados".format(ICON_PEND))
    lineas.append("")

    lineas.extend(_lineas_generatividad(datos.get("generatividad")))

    # inventario
    lineas.append("=" * 80)
    lineas.append("{0}  INVENTARIO RÁPIDO".format(ICON_MOD))
    lineas.append("=" * 80)
    lineas.append("Presente:")
    hay = False
    for rol, mods in sorted(roles.items()):
        if mods:
            hay = True
            lineas.append(
                "  {0} {1}: {2}".format(ICON_OK, rol, ", ".join(str(m) for m in mods))
            )
    if not hay:
        lineas.append("  {0} (ninguno)".format(ICON_PEND))
    lineas.append("Ausente:")
    if vacios:
        for rol in vacios:
            lineas.append("  {0} {1}".format(ICON_PEND, rol))
    else:
        lineas.append("  {0} (ninguno)".format(ICON_OK))
    lineas.append("Rechazado:")
    if rechazados:
        for r in rechazados:
            if isinstance(r, dict):
                lineas.append(
                    "  {0} {1} → {2}".format(
                        ICON_REJ,
                        Path(str(r.get("ruta", "?"))).parent.name,
                        r.get("razon", "?"),
                    )
                )
    else:
        lineas.append("  {0} (ninguno)".format(ICON_OK))
    lineas.append("")

    lineas += [
        "=" * 80,
        "{0}  CIERRE".format(icon_salud),
        "=" * 80,
        "  Versión Omega      : {0}".format(VERSION),
        "  Salud              : {0} {1}".format(icon_salud, salud),
        "  Acciones abiertas  : {0}".format(len(acciones)),
        "  Bloqueantes        : {0}".format(n_bloqueantes),
        "  Caja 1             : Auditoría del VPSI (sistema) — LECTURA",
        "  Caja 2             : Último test evaluado — LECTURA",
        "  Omega no inventa C/L/K/Tru; lee lo que el ciclo depositó.",
        "  0 = cero real · UNDEFINED = base nula · no depositado = no vino",
        "=" * 80,
    ]
    return "\n".join(lineas)


# =============================================================================
# CARGA — orquesta lectura + un ciclo real de auto-auditoría del repo
# =============================================================================
def _leer_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _enriquecer_citas_desde_ax(
    valuacion: Dict[str, Any],
    ia: Dict[str, Any],
) -> Dict[str, Any]:
    if valuacion.get("citas"):
        return valuacion
    for key in ("muestra_ids", "ids", "ids_relevantes", "normas"):
        raw = ia.get(key)
        if isinstance(raw, list) and raw:
            valuacion["citas"] = [str(x) for x in raw[:24]]
            break
    return valuacion


def cargar_datos_desde_engine() -> Dict[str, Any]:
    datos: Dict[str, Any] = {
        "estado_engine": "NO_INICIADO",
        "constantes": {},
        "informe_axiomas": {},
        "errores_arranque": [],
        "resultados_evaluacion": [],
        "fallos_engine": [],
        "inventario_engine": {},
        "contratos": None,
        "evidencia_evaluacion": {},
        "auditoria_vpsi": {},
        "ultimo_test": {},
    }

    contratos = _leer_json(DIAGNOSTICS_DIR / "contratos_report.json")
    if isinstance(contratos, dict):
        datos["contratos"] = contratos

    eng = None
    try:
        from core.engine import Engine, ArranqueError

        try:
            eng = Engine(
                raiz_modulos=str(REPO_ROOT / "modules"),
                invocador_id="omega_report",
                strict=False,
            )
        except TypeError:
            try:
                eng = Engine(
                    str(REPO_ROOT / "modules"),
                    invocador_id="omega_report",
                    verificar_axiomas=False,
                    strict=False,
                )
            except Exception as e:  # noqa: BLE001
                datos["estado_engine"] = "RECHAZADO"
                datos["errores_arranque"] = [str(e)]
                return datos
        except ArranqueError as e:
            datos["estado_engine"] = "RECHAZADO"
            datos["errores_arranque"] = [str(e)]
            return datos

        datos["estado_engine"] = getattr(eng, "estado", "OPERATIVO")
        datos["errores_arranque"] = list(getattr(eng, "errores_arranque", None) or [])
        datos["informe_axiomas"] = getattr(eng, "informe_axiomas", None) or {}
        datos["informe_mecanica"] = getattr(eng, "informe_mecanica", None) or {}
        datos["fallos_engine"] = list(getattr(eng, "fallos", None) or [])

        if hasattr(eng, "registro") and hasattr(eng.registro, "resumen"):
            datos["registro_modulos"] = eng.registro.resumen()
        elif hasattr(eng, "censar"):
            datos["registro_modulos"] = eng.censar()

        try:
            if hasattr(eng, "get_constantes"):
                datos["constantes"] = {
                    k: str(v) for k, v in eng.get_constantes().items()
                }
        except Exception:  # noqa: BLE001
            pass

        # ----- (1) Auto-auditoría del VPSI: un ciclo REAL del Engine -----
        if getattr(eng, "estado", None) == "OPERATIVO" and hasattr(eng, "evaluar"):
            try:
                r_sys = eng.evaluar(dict(PETICION_AUDITORIA_VPSI))
                pack = {
                    "secuencia": None,
                    "invocador_id": "omega_report_auditoria_vpsi",
                    "resultado": r_sys if isinstance(r_sys, dict) else {},
                }
                if hasattr(eng, "get_resultados_evaluacion"):
                    evs = list(eng.get_resultados_evaluacion() or [])
                    if evs:
                        pack = evs[-1] if isinstance(evs[-1], dict) else pack
                elif hasattr(eng, "resultados_evaluacion"):
                    evs = list(eng.resultados_evaluacion or [])
                    if evs:
                        pack = evs[-1] if isinstance(evs[-1], dict) else pack

                av = _extraer_valuacion(pack)
                av = _enriquecer_citas_desde_ax(av, datos.get("informe_axiomas") or {})
                av["origen"] = "omega_report:PETICION_AUDITORIA_VPSI"
                datos["auditoria_vpsi"] = av
                datos["ciclo_auditoria_vpsi_raw"] = pack
            except Exception as e:  # noqa: BLE001
                datos["auditoria_vpsi"] = {
                    "estado": "ERROR",
                    "razon": "auto-auditoría: {0}: {1}".format(type(e).__name__, e),
                    "C": None, "L": None, "K": None,
                    "tru_ri": None, "tru_total": None,
                    "taxonomia": None, "citas": [],
                    "lectura": {
                        "C": False, "L": False, "K": False,
                        "tru_ri": False, "tru_total": False,
                    },
                }

        # ----- (2) Último test: evaluations.json (pytest / CI) -----
        eval_path = DIAGNOSTICS_DIR / "evaluaciones.json"
        datos["resultados_evaluacion"] = []
        if eval_path.exists():
            try:
                doc = json.loads(eval_path.read_text(encoding="utf-8"))
                if isinstance(doc, dict):
                    resultados = doc.get("resultados")
                    if isinstance(resultados, list):
                        datos["resultados_evaluacion"] = resultados
                        datos["evidencia_evaluacion"] = {
                            "origen": doc.get("origen"),
                            "n": doc.get("n", len(resultados)),
                            "path": str(eval_path.name),
                            "invocador_id": doc.get("invocador_id"),
                        }
                        if resultados:
                            datos["ultimo_test"] = _extraer_valuacion(resultados[-1])
                            datos["ultimo_test"]["origen"] = doc.get(
                                "origen", "evaluaciones.json"
                            )
            except Exception:  # noqa: BLE001
                datos["evidencia_evaluacion"] = {
                    "path": str(eval_path.name),
                    "error": "json ilegible",
                }

        try:
            if hasattr(eng, "inventario"):
                inv = eng.inventario()
                if isinstance(inv, dict):
                    datos["inventario_engine"] = inv
        except Exception:  # noqa: BLE001
            pass

        try:
            cont_fo = eng.registro.primero("FO") if hasattr(eng, "registro") else None
            if cont_fo is not None:
                for cap in ("verificar", "barrer", "inventario"):
                    fn = cont_fo.fn(cap)
                    if callable(fn):
                        out = fn()
                        if isinstance(out, dict):
                            datos["informe_formulas"] = out
                            break
        except Exception:  # noqa: BLE001
            pass

        try:
            if hasattr(eng, "censar_generatividad"):
                datos["generatividad"] = eng.censar_generatividad()
            else:
                cont_ax = (
                    eng.registro.primero("AX") if hasattr(eng, "registro") else None
                )
                if cont_ax is not None:
                    fn = cont_ax.fn("generatividad")
                    if callable(fn):
                        g = fn()
                        if isinstance(g, dict):
                            datos["generatividad"] = g
        except Exception as e:  # noqa: BLE001
            datos["generatividad"] = {
                "estado": "UNDEFINED",
                "razon": "{0}: {1}".format(type(e).__name__, e),
            }

        try:
            cont_ca = eng.registro.primero("CA") if hasattr(eng, "registro") else None
            if cont_ca is not None:
                for cap in ("verificar", "barrer", "inventario"):
                    fn = cont_ca.fn(cap)
                    if callable(fn):
                        out = fn()
                        if isinstance(out, dict):
                            datos["informe_calculator"] = out
                            break
        except Exception:  # noqa: BLE001
            pass

    except Exception as e:  # noqa: BLE001
        datos["estado_engine"] = "RECHAZADO"
        datos["errores_arranque"] = ["{0}: {1}".format(type(e).__name__, e)]

    xml_path = DIAGNOSTICS_DIR / "test_results.xml"
    if xml_path.exists():
        try:
            import xml.etree.ElementTree as ET

            raiz = ET.parse(xml_path).getroot()
            suites = (
                [raiz]
                if raiz.tag == "testsuite"
                else list(raiz.iter("testsuite"))
            )
            total = fallos = errores = omitidos = 0
            for s in suites:
                total += int(s.get("tests", 0))
                fallos += int(s.get("failures", 0))
                errores += int(s.get("errors", 0))
                omitidos += int(s.get("skipped", 0))
            fallidos = fallos + errores
            pasados = total - fallidos - omitidos
            tasa = (pasados / total * 100) if total else 0.0
            datos["tests"] = {
                "total": total,
                "pasados": pasados,
                "fallidos": fallidos,
                "omitidos": omitidos,
                "tasa": round(tasa, 2),
            }
        except Exception:  # noqa: BLE001
            pass

    return datos


def main() -> None:
    datos = cargar_datos_desde_engine()
    texto = presentar(datos)
    print(texto)

    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = DIAGNOSTICS_DIR / "omega_report_data.json"
    dump = {
        k: v
        for k, v in datos.items()
        if k != "ciclo_auditoria_vpsi_raw"
    }
    out_json.write_text(
        json.dumps(dump, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print("\nJSON: {0}".format(out_json))

    faltas = validar_entrada(datos)
    if STRICT and (datos.get("estado_engine") != "OPERATIVO" or faltas):
        sys.exit(1)


if __name__ == "__main__":
    main()
