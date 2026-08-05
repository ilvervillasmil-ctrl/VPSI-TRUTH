#!/usr/bin/env python3
"""
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 10.1)
==============================

Orden de presentación (contrato de salida):
  1) AUDITORÍA DEL VPSI  — valuación del repositorio (Tru_Ri / Tru_total del repo)
  2) SUJETOS 1…N         — Tru total por sujeto si el ciclo los depositó
  3) ÚLTIMO TEST         — valuación del último ciclo de prueba
  4) Resto del mapa      — salud, intervención, capas, generatividad

Contrato de cálculo (inviolable):
  - C, L, K, Tru_Ri, Tru_total los produce el sistema (CA / FO / Engine).
  - Omega NO inventa Fraction, NO aplica la fórmula, NO rellena huecos.
  - Omega SOLO LEE lo que el ciclo depositó y lo presenta tal cual.
  - 0 es 0. UNDEFINED es UNDEFINED. None es "no depositado".
  - Si hay N sujetos en el material y el ciclo depositó totales por sujeto,
    Omega lista S_1…S_N automáticamente. Si no depositó, marca no depositado.
  - Catálogos TT / CC: solo referencia de ids si vienen en el ciclo.

Autor: Ilver Villasmil
ORCID: 0009-0009-3413-4270
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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
ICON_READ = "📖"
ICON_SUB = "👤"
ICON_REPO = "🗂"

STRICT = os.getenv("OMEGA_STRICT", "0") == "1"
VERSION = "10.1"

CAMPOS_OBLIGATORIOS = (
    "estado_engine",
    "constantes",
    "informe_axiomas",
)

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
    "texto": (
        "Estado observable del repositorio VPSI-TRUTH "
        "(axiomas, contratos, módulos, generatividad) en el run actual."
    ),
    "pedir_anuncio": True,
    "tipos_peticion": [
        "dame_cadena_completa",
        "dame_normas",
        "auto_auditoria",
    ],
    # señal de catálogo TT (Engine puede usarla; Omega solo reporta si calculó)
    "categoria_tru": "tru_repositorio",
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
    if v is None:
        return False
    if type(v).__name__ in ("_Undefined", "Undefined"):
        return True
    s = str(v).strip().upper()
    return s in ("UNDEFINED", "INDEFINIDO", "<UNDEFINED>")


def _depositado(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str) and not v.strip():
        return False
    return True


def _fmt(v: Any) -> str:
    if v is None:
        return "no depositado"
    if _es_undefined(v):
        return "UNDEFINED"
    s = str(v).strip()
    if not s:
        return "no depositado"
    if s in ("0", "0/1", "0.0"):
        return "0"
    return s


def _marca_lectura(v: Any) -> str:
    if not _depositado(v):
        return ICON_PEND
    if _es_undefined(v):
        return ICON_WARN
    return ICON_OK


def _pick(d: Dict[str, Any], *keys: str) -> Any:
    if not isinstance(d, dict):
        return None
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    for nest in ("resultado", "truth", "valores", "salida", "factores", "valuacion"):
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
        or "sujetos" in inner
        or "por_sujeto" in inner
    ):
        return inner
    return r


def _factores_de(r: Dict[str, Any]) -> Dict[str, Any]:
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


def _extraer_sujetos(r: Any) -> List[Dict[str, Any]]:
    """
    Lee sujetos depositados por el ciclo (S_1…S_N).
    Formas admitidas (solo lectura; no inventa N):
      resultado.sujetos = [ {indice|id|nombre, Tru_total, Tru_Ri, C, L, K, ...}, ... ]
      resultado.por_sujeto = { "1": {...}, "Maria": {...}, ... }
      resultado.valuacion.sujetos = ...
    Si no hay nada → lista vacía (Omega no inventa sujetos).
    """
    if not isinstance(r, dict):
        return []
    body = _cuerpo_resultado(r)
    candidatos: List[Any] = []

    for src in (
        body.get("sujetos"),
        body.get("por_sujeto"),
        (body.get("valuacion") or {}).get("sujetos") if isinstance(body.get("valuacion"), dict) else None,
        r.get("sujetos"),
        r.get("por_sujeto"),
    ):
        if src is None:
            continue
        if isinstance(src, list) and src:
            candidatos = src
            break
        if isinstance(src, dict) and src:
            # dict → lista ordenada
            items = []
            for k, v in src.items():
                if isinstance(v, dict):
                    item = dict(v)
                    item.setdefault("id", k)
                    item.setdefault("indice", k)
                    items.append(item)
                else:
                    items.append({"id": k, "Tru_total": v})
            candidatos = items
            break

    out: List[Dict[str, Any]] = []
    for i, raw in enumerate(candidatos, 1):
        if not isinstance(raw, dict):
            out.append({
                "indice": i,
                "etiqueta": "S_{0}".format(i),
                "C": None, "L": None, "K": None,
                "tru_ri": None, "tru_total": raw if raw is not None else None,
                "lectura": {
                    "C": False, "L": False, "K": False,
                    "tru_ri": False,
                    "tru_total": _depositado(raw),
                },
            })
            continue
        fac = raw.get("factores") if isinstance(raw.get("factores"), dict) else {}
        C = fac.get("C", raw.get("C", raw.get("c")))
        L = fac.get("L", raw.get("L", raw.get("l")))
        K = fac.get("K", raw.get("K", raw.get("k")))
        tru_ri = raw.get("Tru_Ri", raw.get("tru_ri"))
        tru_total = raw.get("Tru_total", raw.get("tru_total"))
        indice = raw.get("indice", raw.get("i", i))
        etiqueta = (
            raw.get("nombre")
            or raw.get("etiqueta")
            or raw.get("id")
            or raw.get("sujeto")
            or "S_{0}".format(indice)
        )
        out.append({
            "indice": indice,
            "etiqueta": str(etiqueta),
            "C": C, "L": L, "K": K,
            "tru_ri": tru_ri,
            "tru_total": tru_total,
            "estado": raw.get("estado"),
            "lectura": {
                "C": _depositado(C),
                "L": _depositado(L),
                "K": _depositado(K),
                "tru_ri": _depositado(tru_ri),
                "tru_total": _depositado(tru_total),
            },
        })
    return out


def _extraer_valuacion(r: Any) -> Dict[str, Any]:
    vacio = {
        "estado": None,
        "C": None, "L": None, "K": None,
        "tru_ri": None, "tru_total": None,
        "alpha": None, "beta": None,
        "taxonomia": None, "citas": [],
        "razon": None, "permite_k": None, "origen": None,
        "sujetos": [],
        "lectura": {
            "C": False, "L": False, "K": False,
            "tru_ri": False, "tru_total": False,
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
    )

    C = fac.get("C")
    L = fac.get("L")
    K = fac.get("K")
    tru_ri = _pick(body, "tru_ri", "Tru_Ri")
    if tru_ri is None:
        tru_ri = r.get("tru_ri") or r.get("Tru_Ri")
    tru_total = _pick(body, "tru_total", "Tru_total")
    if tru_total is None:
        tru_total = r.get("tru_total") or r.get("Tru_total")

    # Tru de repositorio si el ciclo lo etiquetó aparte
    tru_repo_ri = _pick(body, "tru_ri_repositorio", "Tru_Ri_repositorio", "tru_repo_ri")
    tru_repo_total = _pick(
        body, "tru_total_repositorio", "Tru_total_repositorio", "tru_repo_total"
    )
    if tru_repo_ri is None and body.get("categoria_tru") in ("tru_repositorio", "repo"):
        tru_repo_ri = tru_ri
        tru_repo_total = tru_total

    fuentes = body.get("fuentes_usadas") or r.get("fuentes_usadas") or []
    if not isinstance(fuentes, list):
        fuentes = [fuentes] if fuentes else []
    fallos = body.get("fallos") or r.get("fallos") or []
    if not isinstance(fallos, list):
        fallos = [fallos] if fallos else []

    sujetos = _extraer_sujetos(r)

    return {
        "estado": _pick(body, "estado") or _pick(r, "estado"),
        "C": C, "L": L, "K": K,
        "tru_ri": tru_ri,
        "tru_total": tru_total,
        "tru_ri_repositorio": tru_repo_ri,
        "tru_total_repositorio": tru_repo_total,
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
        "fuentes_usadas": [str(x) for x in fuentes],
        "fallos": [str(x) for x in fallos],
        "engine_version": body.get("engine_version") or r.get("engine_version"),
        "modo_entrada": cx.get("modo_entrada") or body.get("modo_entrada"),
        "ids_cx": list(cx.get("ids_cx_relevantes") or []),
        "coherente_cx": cx.get("coherente"),
        "contexto_texto": body.get("contexto") or r.get("contexto"),
        "categoria_tru": body.get("categoria_tru") or r.get("categoria_tru"),
        "sujetos": sujetos,
        "n_sujetos": len(sujetos),
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
    if v.get("categoria_tru"):
        lineas.append("  categoría TT: {0}".format(_fmt(v.get("categoria_tru"))))
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
        ) + "│"
    )
    lineas.append(
        "  │  {0} Tru_total  =  {1}".format(
            m_tt, _fmt(v.get("tru_total")).ljust(40)
        ) + "│"
    )

    # Repo explícito si vino etiquetado
    if v.get("tru_ri_repositorio") is not None or v.get("tru_total_repositorio") is not None:
        lineas.append("  │─────────────────────────────────────────────────────────│")
        lineas.append(
            "  │  {0} Tru_Ri  repo =  {1}".format(
                _marca_lectura(v.get("tru_ri_repositorio")),
                _fmt(v.get("tru_ri_repositorio")).ljust(36),
            ) + "│"
        )
        lineas.append(
            "  │  {0} Tru_total repo = {1}".format(
                _marca_lectura(v.get("tru_total_repositorio")),
                _fmt(v.get("tru_total_repositorio")).ljust(35),
            ) + "│"
        )

    if v.get("alpha") is not None or v.get("beta") is not None:
        lineas.append(
            "  │  ancla      α={0}  β={1}".format(
                _fmt(v.get("alpha")), _fmt(v.get("beta"))
            ).ljust(58) + "│"
        )
    lineas.append("  └─────────────────────────────────────────────────────────┘")
    lineas.append(
        "  Nota: ✅ leído del ciclo · ⚠️ UNDEFINED · ⚪ no depositado"
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
    if v.get("engine_version"):
        lineas.append("  Engine     : {0}".format(_fmt(v.get("engine_version"))))
    if v.get("modo_entrada"):
        lineas.append("  modo_entrada: {0}".format(_fmt(v.get("modo_entrada"))))
    if v.get("coherente_cx") is not None:
        lineas.append("  coherente_cx: {0}".format(_fmt(v.get("coherente_cx"))))
    fuentes = list(v.get("fuentes_usadas") or [])
    if fuentes:
        lineas.append("  Fuentes    : {0}".format(", ".join(fuentes)))
    ids_cx = list(v.get("ids_cx") or [])
    if ids_cx:
        lineas.append("  ids_cx     : {0}".format(", ".join(str(x) for x in ids_cx[:16])))
    fallos = list(v.get("fallos") or [])
    if fallos:
        lineas.append("  Fallos     : {0}".format(len(fallos)))
        for f in fallos[:6]:
            lineas.append("      - {0}".format(str(f)[:80]))
    ctx = v.get("contexto_texto")
    if ctx:
        s = str(ctx).strip()
        if len(s) > 110:
            s = s[:107] + "..."
        lineas.append("  Contexto   : {0}".format(s))
    lineas.append(borde)
    lineas.append("")
    return lineas


def _caja_sujetos(sujetos: List[Dict[str, Any]], *, ancho: int = 78) -> List[str]:
    """
    Lista automática S_1…S_N según lo depositado.
    Omega no descubre hablantes: solo reporta la lista que trajo el ciclo.
    """
    lineas: List[str] = []
    borde = "═" * ancho
    lineas.append(borde)
    lineas.append(
        "  {0}  SUJETOS (S_1…S_N)  ·  Tru total por sujeto".format(ICON_SUB)
    )
    lineas.append(
        "  Solo lectura · N = {0} depositado(s) por el ciclo · Omega no calcula".format(
            len(sujetos)
        )
    )
    lineas.append(borde)

    if not sujetos:
        lineas.append(
            "  {0} Ningún sujeto depositado en el ciclo.".format(ICON_PEND)
        )
        lineas.append(
            "  Cuando Engine deposite resultado.sujetos / por_sujeto,"
        )
        lineas.append(
            "  aquí aparecerán automáticamente Tru_total de S_1…S_N."
        )
        lineas.append(borde)
        lineas.append("")
        return lineas

    for s in sujetos:
        idx = s.get("indice", "?")
        etiq = s.get("etiqueta", "S_{0}".format(idx))
        lineas.append(
            "  ── Sujeto {0} · {1} ──────────────────────────────".format(idx, etiq)
        )
        lineas.append(
            "     {0} C={1}  {2} L={3}  {4} K={5}".format(
                _marca_lectura(s.get("C")), _fmt(s.get("C")),
                _marca_lectura(s.get("L")), _fmt(s.get("L")),
                _marca_lectura(s.get("K")), _fmt(s.get("K")),
            )
        )
        lineas.append(
            "     {0} Tru_Ri    = {1}".format(
                _marca_lectura(s.get("tru_ri")), _fmt(s.get("tru_ri"))
            )
        )
        lineas.append(
            "     {0} Tru_total = {1}".format(
                _marca_lectura(s.get("tru_total")), _fmt(s.get("tru_total"))
            )
        )
        if s.get("estado") is not None:
            lineas.append("     estado    = {0}".format(_fmt(s.get("estado"))))
        lineas.append("")

    lineas.append(
        "  Total sujetos reportados: {0}".format(len(sujetos))
    )
    lineas.append(borde)
    lineas.append("")
    return lineas


def _tabla(
    headers: List[str],
    rows: List[List[str]],
    anchos: Optional[List[int]] = None,
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


def _lineas_generatividad(g: Optional[Dict[str, Any]]) -> List[str]:
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
    out.append("  U1                 : {0}".format(g.get("u1_estado", g.get("u1_proxy", "—"))))
    can = g.get("canonica") or {}
    if can:
        out.append("  --- capa canónica ---")
        out.append("  |Θ|_can            : {0} / 24".format(can.get("theta_n", "—")))
        out.append("  novedosos_can      : {0}".format(can.get("pares_novedosos", "—")))
        out.append("  |Im| ? |Θ| can     : {0}".format(can.get("im_vs_theta", "—")))
    out.append("")
    return out


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
    if not av or not (
        lec.get("C") or lec.get("L") or lec.get("K") or av.get("tru_total") is not None
    ):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "auditoria_vpsi",
            "detalle": "Ciclo de auto-auditoría sin factores depositados legibles",
            "impacto": "La caja repo no muestra C/L/K / Tru leídos",
            "accion": "Engine.evaluar(PETICION_AUDITORIA_VPSI) debe depositar resultado",
            "errores": [],
        })

    # Sujetos: informativo si el último test no trajo lista
    ut = datos.get("ultimo_test") or {}
    if ut and not (ut.get("sujetos") or []):
        acciones.append({
            "prioridad": 5,
            "tipo": "DATOS",
            "item": "sujetos",
            "detalle": "ciclo sin resultado.sujetos / por_sujeto",
            "impacto": "No se listan Tru_total de S_1…S_N",
            "accion": (
                "Engine debe depositar totales por sujeto cuando el material "
                "tenga varios hablantes (catálogo TT tru_sujeto)"
            ),
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
        "Orden: (1) Repo Tru  (2) Sujetos 1…N  (3) Último test  (4) Mapa",
        "Contrato: Omega SOLO LEE · no calcula · no rellena · reporta todo",
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

    # (1) REPOSITORIO — Tru_Ri / Tru_total del repo
    av = datos.get("auditoria_vpsi") or {}
    lineas.extend(
        _caja_valuacion(
            "{0}  AUDITORÍA DEL VPSI  ·  Tru del repositorio".format(ICON_REPO),
            "Tru_Ri y Tru_total del sistema (O_VPSI_REPO) · valores LEÍDOS del ciclo",
            av if av else {
                "estado": None,
                "C": None, "L": None, "K": None,
                "tru_ri": None, "tru_total": None,
                "taxonomia": None, "citas": [],
                "razon": "sin ciclo de auto-auditoría depositado",
                "lectura": {
                    "C": False, "L": False, "K": False,
                    "tru_ri": False, "tru_total": False,
                },
            },
        )
    )

    # (2) SUJETOS — del último test o de auditoría si trae sujetos
    sujetos = list((datos.get("ultimo_test") or {}).get("sujetos") or [])
    if not sujetos:
        sujetos = list((datos.get("auditoria_vpsi") or {}).get("sujetos") or [])
    lineas.extend(_caja_sujetos(sujetos))

    # (3) ÚLTIMO TEST
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
                "lectura": {
                    "C": False, "L": False, "K": False,
                    "tru_ri": False, "tru_total": False,
                },
            },
        )
    )

    # ESTADO GLOBAL
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
        "  {0} Sujetos (N)  : {1}".format(
            ICON_SUB if sujetos else ICON_PEND, len(sujetos)
        ),
        "  {0} Salud        : {1}".format(icon_salud, salud),
        "",
    ]

    # MÓDULOS
    roles = reg.get("roles") or {}
    todos = sorted(set(list(roles.keys()) + list(vacios)))
    rows_m = []
    for rol in todos:
        mods = roles.get(rol) or []
        if mods:
            rows_m.append(
                [str(rol), "CARGADO", str(len(mods)), ", ".join(str(m) for m in mods)]
            )
        else:
            rows_m.append([str(rol), "VACÍO", "0", "(sin módulo)"])
    lineas.append("{0}  MÓDULOS Y ROLES".format(ICON_MOD))
    if rows_m:
        lineas.extend(
            "  " + l
            for l in _tabla(["ROL", "ESTADO", "N", "MÓDULOS"], rows_m, [4, 9, 3, 36])
        )
    lineas.append("")

    # INTERVENCIÓN
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

    # SALUD POR CAPA
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
        "  Sección 1          : Tru_Ri / Tru_total del repositorio — LECTURA",
        "  Sección 2          : Sujetos S_1…S_N (N={0}) — LECTURA".format(len(sujetos)),
        "  Sección 3          : Último test — LECTURA",
        "  Omega no inventa C/L/K/Tru; lee lo que el ciclo depositó.",
        "  0 = cero real · UNDEFINED = base nula · no depositado = no vino",
        "=" * 80,
    ]
    return "\n".join(lineas)


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
    for key in ("muestra_ids", "ids", "ids_relevantes", "normas", "ids_dominio_k_o"):
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
                    "taxonomia": None, "citas": [], "sujetos": [],
                    "lectura": {
                        "C": False, "L": False, "K": False,
                        "tru_ri": False, "tru_total": False,
                    },
                }

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
