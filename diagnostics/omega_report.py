#!/usr/bin/env python3
"""
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.6)
==============================

Presentador objetivo + mapa de intervención.

Contrato de este artefacto:
  - Solo reporta.
  - No recalcula Tru_Ri / Tru_total.
  - No inventa evaluaciones (sin humo).
  - Lee únicamente lo que Engine, módulos y artefactos CI ya produjeron.
  - Cada hueco indica: qué es · dónde · por qué importa · qué hacer.

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

# Marcas de estado (legibles en CI / terminal / GitHub)
ICON_OK = "✅"
ICON_FAIL = "❌"
ICON_PEND = "⚪"
ICON_WARN = "⚠️"
ICON_INFO = "ℹ️"
ICON_DOT = "·"
ICON_MOD = "📦"
ICON_ABS = "·"
ICON_REJ = "🚫"
ICON_SEQ = "🔹"

OK = "OK"
FALLO = "FALLO"
PENDIENTE = "PENDIENTE"
STRICT = os.getenv("OMEGA_STRICT", "0") == "1"
VERSION = "9.6"

CAMPOS_OBLIGATORIOS = (
    "estado_engine",
    "constantes",
    "informe_axiomas",
)


# =============================================================================
# VALIDACIÓN DE ENTRADA (solo forma)
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
# HELPERS DE PRESENTACIÓN
# =============================================================================
def _marca(ok: bool) -> str:
    return ICON_OK if ok else ICON_FAIL


def _marca_tri(estado: str) -> str:
    """ok | fail | pend."""
    if estado == OK:
        return ICON_OK
    if estado == FALLO:
        return ICON_FAIL
    return ICON_PEND


def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    s = str(v).strip()
    return s if s else "—"


def _pick(d: Dict[str, Any], *keys: str) -> Any:
    """Primera clave presente (soporta mayúsculas / anidados simples)."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    # nested frecuente
    for nest in ("resultado", "truth", "valores", "salida"):
        sub = d.get(nest)
        if isinstance(sub, dict):
            for k in keys:
                if k in sub and sub[k] is not None:
                    return sub[k]
    return None


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


def _bloque(titulo: str, lineas_bloq: List[str]) -> List[str]:
    return [titulo, *lineas_bloq, ""]


def _lineas_generatividad(g: Dict[str, Any] | None) -> List[str]:
    out: List[str] = [
        "=" * 80,
        "{0}  GENERATIVIDAD (TR1 / U1)".format(ICON_INFO),
        "=" * 80,
    ]
    if not g or g.get("estado") == "UNDEFINED":
        out.append("  {0} sin datos — AX.generatividad no disponible en el paquete".format(ICON_PEND))
        if g:
            out.append("  U1 (proxy roles): {0}".format(g.get("u1_estado", "REVISAR")))
            out.append("  roles vacíos    : {0}".format(g.get("roles_vacios", [])))
            if g.get("razon"):
                out.append("  razon           : {0}".format(g.get("razon")))
        out.append("")
        return out

    im = g.get("im_vs_theta", "—")
    marca_im = ICON_OK if im == "GENERATIVO" else (ICON_WARN if im == "ESTANCADO" else ICON_PEND)
    out.append("  |Θ| (AX)           : {0}".format(g.get("theta_n", "—")))
    out.append("  pares totales      : {0}".format(g.get("pares_totales", "—")))
    out.append("  pares compatibles  : {0}".format(g.get("pares_compatibles", "—")))
    out.append("  pares novedosos    : {0}".format(g.get("pares_novedosos", "—")))
    out.append("  |Im(⊕)| ? |Θ|      : {0} {1}".format(marca_im, im))
    out.append("  dominios           : {0}".format(g.get("dominios", [])))
    out.append("  roles vacíos       : {0}".format(g.get("roles_vacios", [])))
    out.append("  U1                 : {0}".format(g.get("u1_estado", "—")))
    if g.get("por_tipo_theta"):
        out.append("  por_tipo_theta     : {0}".format(g.get("por_tipo_theta")))

    can = g.get("canonica") or {}
    out.append("  --- capa canónica (paper TR1) ---")
    if can:
        out.append("  |Θ|_can           : {0} / 24".format(can.get("theta_n", "—")))
        out.append(
            "  novedosos_can     : {0}  (paper: 153)".format(
                can.get("pares_novedosos", "—")
            )
        )
        out.append("  |Im| ? |Θ| can    : {0}".format(can.get("im_vs_theta", "—")))
        out.append("  ids_faltantes     : {0}".format(can.get("ids_faltantes", [])))
        out.append("  ids_sin_dominio   : {0}".format(can.get("ids_sin_dominio", [])))
        out.append("  dominios_can      : {0}".format(can.get("dominios", [])))
    else:
        out.append("  {0} sin datos canónicos en el paquete".format(ICON_PEND))

    if g.get("nota"):
        out.append("  nota               : {0}".format(g["nota"]))
    out.append("")
    return out


def _linea_eval(seq: int, total: int, r: Any) -> str:
    """Una evaluación: seq k/n — nunca [1] solo (evita confusión con techo Tru=1)."""
    if not isinstance(r, dict):
        return "    {0} seq {1}/{2}  (entrada no es dict)".format(ICON_WARN, seq, total)

    estado = _pick(r, "estado", "status", "state", "resultado_estado")
    tru_ri = _pick(r, "tru_ri", "Tru_Ri", "Tru_ri", "ri", "TRU_RI")
    tru_total = _pick(
        r, "tru_total", "Tru_total", "Tru_Total", "total", "TRU_TOTAL"
    )
    seq_id = _pick(r, "secuencia", "seq", "n", "id")

    est_s = _fmt(estado)
    # marca por estado textual si existe
    if est_s in ("OK", "OPERATIVO", "COMPLETO"):
        m = ICON_OK
    elif est_s in ("FALLO", "ERROR", "RECHAZADO"):
        m = ICON_FAIL
    elif est_s == "—":
        m = ICON_PEND
    else:
        m = ICON_DOT

    extra = ""
    if seq_id is not None and str(seq_id) != str(seq):
        extra = "  id_interno={0}".format(seq_id)

    return (
        "    {0} seq {1}/{2}  estado={3}  Tru_Ri={4}  Tru_total={5}{6}".format(
            m, seq, total, est_s, _fmt(tru_ri), _fmt(tru_total), extra
        )
    )


# =============================================================================
# MAPA DE INTERVENCIÓN (solo a partir del paquete)
# =============================================================================
def construir_acciones(datos: Dict[str, Any]) -> List[Dict[str, Any]]:
    acciones: List[Dict[str, Any]] = []
    reg = datos.get("registro_modulos") or {}
    vacios = reg.get("roles_vacios") or []
    rechazados = reg.get("rechazados") or []

    if datos.get("estado_engine") != "OPERATIVO":
        acciones.append({
            "prioridad": 1,
            "tipo": "BLOQUEANTE",
            "item": "Engine",
            "detalle": "estado = {0}".format(datos.get("estado_engine")),
            "impacto": "Nada confiable puede evaluarse si el Engine no está OPERATIVO",
            "accion": "Revisar errores_arranque y compuertas de arranque",
            "errores": datos.get("errores_arranque") or [],
        })

    ia = datos.get("informe_axiomas") or {}
    if not ia.get("coherente", False):
        acciones.append({
            "prioridad": 1,
            "tipo": "BLOQUEANTE",
            "item": "Axiomas",
            "detalle": (
                "choques={0} errores={1}".format(
                    len(ia.get("choques", [])),
                    len(ia.get("errores", [])),
                )
            ),
            "impacto": "Sin axiomatización coherente el sistema no debe avanzar",
            "accion": "Resolver choques en modules/axiomas y VPSI.py",
            "errores": (ia.get("choques") or [])[:5],
        })

    ct = datos.get("contratos")
    if isinstance(ct, dict) and ct.get("coherente") is False:
        acciones.append({
            "prioridad": 2,
            "tipo": "CONTRATO",
            "item": "auditoria_contratos",
            "detalle": (
                "contratos_report coherente=False errores_n={0}".format(
                    len(ct.get("errores") or [])
                )
            ),
            "impacto": "El juez CI reportó fallos de contrato o ejecución",
            "accion": "Leer diagnostics/contratos_report.json y corregir init/Engine",
            "errores": [
                (e.get("mensaje") if isinstance(e, dict) else str(e))
                for e in (ct.get("errores") or [])[:5]
            ],
        })

    for r in rechazados:
        ruta = r.get("ruta", "?")
        razon = r.get("razon", "?")
        acciones.append({
            "prioridad": 2,
            "tipo": "RECHAZADO",
            "item": Path(ruta).parent.name if ruta != "?" else "?",
            "detalle": razon,
            "impacto": "El módulo existe en disco pero el Engine lo ignora",
            "accion": "Registrar el rol en core.engine.ROLES o corregir CONTENEDOR['rol']",
            "errores": ["{0} → {1}".format(ruta, razon)],
        })

    for rol in vacios:
        acciones.append({
            "prioridad": 3,
            "tipo": "VACÍO",
            "item": rol,
            "detalle": "rol admitido sin módulo montado",
            "impacto": "Capacidad del rol {0} no disponible".format(rol),
            "accion": "Crear o activar módulo con CONTENEDOR['rol'] = '{0}'".format(rol),
            "errores": [],
        })

    # Evidencia de evaluación: artefacto CI, no Engine limpio de Omega
    evidencia = datos.get("evidencia_evaluacion") or {}
    n_ev = int(evidencia.get("n") or 0)
    if not datos.get("resultados_evaluacion") and n_ev == 0:
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "resultados_evaluacion",
            "detalle": (
                "Sin diagnostics/evaluaciones.json o lista vacía "
                "(la auditoría aún no depositó evidencia)"
            ),
            "impacto": "No se puede auditar el camino de evaluación desde Omega",
            "accion": (
                "Ejecutar auditoría de contratos antes de Omega; "
                "debe escribir diagnostics/evaluaciones.json"
            ),
            "errores": [],
        })

    if not datos.get("tests"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "tests",
            "detalle": "resultados de pytest no entregados al reporte",
            "impacto": "No se ve cobertura ni regresiones desde el mapa",
            "accion": "Generar diagnostics/test_results.xml antes de Omega",
            "errores": [],
        })

    if not datos.get("informe_formulas"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "informe_formulas",
            "detalle": "no entregado por FO en el paquete",
            "impacto": "No se confirma el estado del módulo FO desde el reporte",
            "accion": "Exponer verificar/barrer en FO y que Engine lo adjunte al cargar",
            "errores": [],
        })

    if not isinstance(ct, dict):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "contratos_report",
            "detalle": "diagnostics/contratos_report.json ausente",
            "impacto": "Sin mapa del juez CI de contratos en este run",
            "accion": "Ejecutar auditoría estructural de contratos antes de Omega",
            "errores": [],
        })

    g = datos.get("generatividad")
    if not g or g.get("estado") == "UNDEFINED":
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "generatividad",
            "detalle": "AX.generatividad no entregada o UNDEFINED",
            "impacto": "No se mide TR1/U1 desde el mapa",
            "accion": "Asegurar capacidad generatividad en AX y censar_generatividad en Engine",
            "errores": [g.get("razon")] if g and g.get("razon") else [],
        })
    elif g.get("im_vs_theta") == "ESTANCADO":
        acciones.append({
            "prioridad": 5,
            "tipo": "TR1",
            "item": "generatividad",
            "detalle": (
                "|Θ|={0} novedosos={1} → ESTANCADO".format(
                    g.get("theta_n"), g.get("pares_novedosos")
                )
            ),
            "impacto": "El cuerpo axiomático no expande dominios por recombinación",
            "accion": "Revisar campo gobierna en declaraciones o ampliar dominios cruzados",
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
        "Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · prioriza intervención",
        "=" * 80,
        "",
    ]

    if faltas:
        lineas.append(
            "{0} Entrada incompleta — no se puede construir el mapa".format(ICON_FAIL)
        )
        for f in faltas:
            lineas.append("    - {0}".format(f))
        return "\n".join(lineas)

    estado = datos["estado_engine"]
    ia = datos["informe_axiomas"]
    coherente = bool(ia.get("coherente"))
    reg = datos.get("registro_modulos") or {}
    total = reg.get("total", 0)
    vacios = reg.get("roles_vacios") or []
    rechazados = reg.get("rechazados") or []
    acciones = construir_acciones(datos)
    bloqueantes = [a for a in acciones if a["tipo"] == "BLOQUEANTE"]
    n_bloqueantes = len(bloqueantes)

    if estado == "OPERATIVO" and coherente and n_bloqueantes == 0:
        salud = "OPERATIVO — listo para avanzar"
        icon_salud = ICON_OK
    elif estado == "OPERATIVO" and n_bloqueantes == 0:
        salud = "OPERATIVO con huecos no bloqueantes"
        icon_salud = ICON_WARN
    else:
        salud = "DEGRADADO — hay bloqueos"
        icon_salud = ICON_FAIL

    lineas += _bloque("ESTADO GLOBAL", [
        "  {0} Engine          : {1}".format(
            ICON_OK if estado == "OPERATIVO" else ICON_FAIL, estado
        ),
        "  {0} Axiomas         : {1}".format(
            ICON_OK if coherente else ICON_FAIL,
            "coherente" if coherente else "INCOHERENTE",
        ),
        "  {0} Contenedores    : {1}".format(ICON_MOD, total),
        "  {0} Roles vacíos    : {1}".format(
            ICON_OK if len(vacios) == 0 else ICON_WARN, len(vacios)
        ),
        "  {0} Rechazados      : {1}".format(
            ICON_OK if len(rechazados) == 0 else ICON_FAIL, len(rechazados)
        ),
        "  {0} Acciones abiertas: {1}".format(
            ICON_OK if len(acciones) == 0 else ICON_WARN, len(acciones)
        ),
        "  {0} Salud           : {1}".format(icon_salud, salud),
    ])

    roles = reg.get("roles") or {}
    todos_roles = sorted(set(list(roles.keys()) + list(vacios)))
    rows = []
    for rol in todos_roles:
        mods = roles.get(rol) or []
        if mods:
            rows.append([rol, "CARGADO", str(len(mods)), ", ".join(mods)])
        else:
            rows.append([rol, "VACÍO", "0", "(sin módulo)"])

    lineas.append("{0}  MÓDULOS Y ROLES".format(ICON_MOD))
    lineas.extend(
        "  " + l
        for l in _tabla(["ROL", "ESTADO", "N", "MÓDULOS"], rows, [4, 9, 3, 36])
    )
    lineas.append("")

    lineas.append("=" * 80)
    lineas.append("{0}  MAPA DE INTERVENCIÓN (ordenado por prioridad)".format(ICON_WARN))
    lineas.append("=" * 80)
    lineas.append("")

    if not acciones:
        lineas.append("  {0} No hay acciones pendientes. Sistema limpio.".format(ICON_OK))
        lineas.append("")
    else:
        for i, a in enumerate(acciones, 1):
            tipo = a["tipo"]
            if tipo == "BLOQUEANTE":
                ic = ICON_FAIL
            elif tipo in ("CONTRATO", "RECHAZADO"):
                ic = ICON_FAIL
            elif tipo == "DATOS":
                ic = ICON_PEND
            else:
                ic = ICON_WARN
            lineas.append("  {0} {1}. [{2}] {3}".format(ic, i, tipo, a["item"]))
            lineas.append("     Detalle   : {0}".format(a["detalle"]))
            lineas.append("     Impacto   : {0}".format(a["impacto"]))
            lineas.append("     Acción    : {0}".format(a["accion"]))
            if a["errores"]:
                lineas.append("     Evidencia :")
                for e in a["errores"][:3]:
                    lineas.append("       {0} {1}".format(ICON_DOT, e))
            lineas.append("")

    lineas.append("=" * 80)
    lineas.append("{0}  SALUD POR CAPA".format(ICON_INFO))
    lineas.append("=" * 80)
    lineas.append("")

    const = datos.get("constantes") or {}
    lineas.append("  {0} Constantes (CT)".format(ICON_OK))
    lineas.append(
        "      ALPHA = {0}   BETA = {1}".format(
            const.get("ALPHA"), const.get("BETA")
        )
    )
    lineas.append("")

    lineas.append("  {0} Axiomas (AX)".format(ICON_OK if coherente else ICON_FAIL))
    lineas.append("      declaraciones = {0}".format(ia.get("declaraciones", "?")))
    lineas.append("      choques       = {0}".format(len(ia.get("choques", []))))
    lineas.append("      errores       = {0}".format(len(ia.get("errores", []))))
    if ia.get("por_tipo"):
        lineas.append("      por_tipo      = {0}".format(ia.get("por_tipo")))
    lineas.append("")

    fo = datos.get("informe_formulas")
    if fo:
        ok_fo = bool(fo.get("coherente", True))
        lineas.append("  {0} Fórmulas (FO)".format(ICON_OK if ok_fo else ICON_FAIL))
        lineas.append(
            "      coherente = {0}   faltas = {1}".format(
                fo.get("coherente"), fo.get("faltas", [])
            )
        )
    else:
        lineas.append(
            "  {0} Fórmulas (FO) — informe no entregado".format(ICON_PEND)
        )
    lineas.append("")

    mc = datos.get("informe_mecanica")
    if mc:
        ok_mc = bool(mc.get("coherente"))
        lineas.append("  {0} Mecánica (MC)".format(ICON_OK if ok_mc else ICON_FAIL))
        lineas.append("      coherente = {0}".format(mc.get("coherente")))
    else:
        lineas.append(
            "  {0} Mecánica (MC) — informe no entregado".format(ICON_PEND)
        )
    lineas.append("")

    ct = datos.get("contratos")
    if isinstance(ct, dict) and "coherente" in ct:
        ok_ct = bool(ct.get("coherente"))
        res = ct.get("resumen") or {}
        lineas.append("  {0} Contratos (CI)".format(ICON_OK if ok_ct else ICON_FAIL))
        lineas.append(
            "      coherente={0}  validos={1}  caps_ok={2}  caps_fallo={3}".format(
                ct.get("coherente"),
                res.get("contratos_validos", "?"),
                res.get("capacidades_verificadas", "?"),
                res.get("capacidades_fallidas", "?"),
            )
        )
    else:
        lineas.append(
            "  {0} Contratos (CI) — sin contratos_report.json".format(ICON_PEND)
        )
    lineas.append("")

    # Camino de evaluación (seq k/n — no [1][2][3] sueltos)
    evals = datos.get("resultados_evaluacion") or []
    ev = datos.get("evidencia_evaluacion") or {}
    n_ev = len(evals)
    if evals:
        lineas.append("  {0} Camino de evaluación".format(ICON_OK))
        lineas.append(
            "      n = {0}   origen = {1}".format(
                n_ev, _fmt(ev.get("origen"))
            )
        )
        for j, r in enumerate(evals[:6], 1):
            lineas.append(_linea_eval(j, n_ev, r))
        if n_ev > 6:
            lineas.append(
                "      {0} … y {1} más (ver evaluaciones.json)".format(
                    ICON_DOT, n_ev - 6
                )
            )
    else:
        lineas.append(
            "  {0} Camino de evaluación — sin evidencia en evaluaciones.json".format(
                ICON_PEND
            )
        )
    lineas.append("")

    tests = datos.get("tests")
    if tests:
        ok_t = tests.get("fallidos", 1) == 0
        lineas.append("  {0} Tests".format(ICON_OK if ok_t else ICON_FAIL))
        lineas.append(
            "      total={0}  pasados={1}  fallidos={2}  tasa={3}%".format(
                tests.get("total"),
                tests.get("pasados"),
                tests.get("fallidos"),
                tests.get("tasa"),
            )
        )
    else:
        lineas.append(
            "  {0} Tests — resultados no entregados".format(ICON_PEND)
        )
    lineas.append("")

    lineas.extend(_lineas_generatividad(datos.get("generatividad")))

    lineas.append("=" * 80)
    lineas.append("{0}  INVENTARIO RÁPIDO".format(ICON_MOD))
    lineas.append("=" * 80)
    lineas.append("Presente:")
    for rol, mods in sorted(roles.items()):
        if mods:
            lineas.append(
                "  {0} {1}: {2}".format(ICON_OK, rol, ", ".join(mods))
            )
    lineas.append("Ausente:")
    if vacios:
        for rol in vacios:
            lineas.append("  {0} {1}".format(ICON_PEND, rol))
    else:
        lineas.append("  {0} (ninguno)".format(ICON_OK))
    lineas.append("Rechazado:")
    if rechazados:
        for r in rechazados:
            lineas.append(
                "  {0} {1} → {2}".format(
                    ICON_REJ,
                    Path(r.get("ruta", "?")).parent.name,
                    r.get("razon", "?"),
                )
            )
    else:
        lineas.append("  {0} (ninguno)".format(ICON_OK))
    lineas.append("")

    inv = datos.get("inventario_engine") or {}
    if inv:
        lineas.append("=" * 80)
        lineas.append("{0}  INVENTARIO ENGINE (solo lectura)".format(ICON_INFO))
        lineas.append("=" * 80)
        lineas.append(
            "  estado={0}  n_eval_en_este_proceso={1}  "
            "(el n del camino viene del artefacto CI)".format(
                inv.get("estado"),
                inv.get("resultados_evaluacion_n", 0),
            )
        )
        lineas.append("")

    lineas += [
        "=" * 80,
        "{0}  CIERRE".format(icon_salud),
        "=" * 80,
        "  Versión Omega      : {0}".format(VERSION),
        "  Salud              : {0} {1}".format(icon_salud, salud),
        "  Acciones abiertas  : {0}".format(len(acciones)),
        "  Bloqueantes        : {0}".format(n_bloqueantes),
        "  Este reporte no recalculó nada.",
        "  Este reporte no ejecutó humo ni evaluar().",
        "  El orden de la lista = orden recomendado de trabajo.",
        "=" * 80,
    ]

    return "\n".join(lineas)


# =============================================================================
# CARGA DESDE ENGINE + ARTEFACTOS (solo lectura)
# =============================================================================
def _leer_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def cargar_datos_desde_engine() -> Dict[str, Any]:
    """
    Solo agrega lo que ya existe.
    No llama evaluar(). No inventa resultados_evaluacion.
    """
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
    }

    contratos = _leer_json(DIAGNOSTICS_DIR / "contratos_report.json")
    if isinstance(contratos, dict):
        datos["contratos"] = contratos

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
        datos["errores_arranque"] = list(
            getattr(eng, "errores_arranque", None) or []
        )
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

        # Camino: SOLO evaluaciones.json
        datos["resultados_evaluacion"] = []
        eval_path = DIAGNOSTICS_DIR / "evaluaciones.json"
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
            cont_fo = None
            if hasattr(eng, "registro"):
                cont_fo = eng.registro.primero("FO")
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
                    eng.registro.primero("AX")
                    if hasattr(eng, "registro")
                    else None
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
            cont_ca = (
                eng.registro.primero("CA")
                if hasattr(eng, "registro")
                else None
            )
            if cont_ca is not None:
                fn = cont_ca.fn("verificar")
                if callable(fn):
                    out = fn()
                    if isinstance(out, dict):
                        datos["informe_calculator"] = out
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
    out_json.write_text(
        json.dumps(datos, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print("\nJSON: {0}".format(out_json))

    faltas = validar_entrada(datos)
    if STRICT and (datos.get("estado_engine") != "OPERATIVO" or faltas):
        sys.exit(1)


if __name__ == "__main__":
    main()
