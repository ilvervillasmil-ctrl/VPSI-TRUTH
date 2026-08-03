#!/usr/bin/env python3
"""
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.7.1)
==============================

Presentador objetivo + mapa de intervención + valuación detallada.

Contrato:
  - Solo reporta.
  - No recalcula Tru_Ri / Tru_total / C / L / K.
  - No inventa evaluaciones (sin humo).
  - No llama evaluar().
  - Lee únicamente Engine (lectura) + artefactos CI ya producidos.
  - C, L, K, Tru, citación: solo si están en evaluations / resultado del ciclo.
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

OK = "OK"
FALLO = "FALLO"
PENDIENTE = "PENDIENTE"
STRICT = os.getenv("OMEGA_STRICT", "0") == "1"
VERSION = "9.7.1"

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
# HELPERS
# =============================================================================
def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    s = str(v).strip()
    return s if s else "—"


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
    """
    Engine._emit guarda { secuencia, entrada, resultado: {...} }.
    Acepta también dict plano de resultado.
    """
    if not isinstance(r, dict):
        return {}
    inner = r.get("resultado")
    if isinstance(inner, dict) and (
        "estado" in inner
        or "tru_total" in inner
        or "factores" in inner
        or "Tru_total" in inner
        or "citacion" in inner
    ):
        return inner
    return r


def _factores_de(r: Dict[str, Any]) -> Dict[str, Any]:
    body = _cuerpo_resultado(r)
    fac = body.get("factores") if isinstance(body.get("factores"), dict) else {}
    return {
        "C": fac.get("C", _pick(body, "C", "c")),
        "L": fac.get("L", _pick(body, "L", "l")),
        "K": fac.get("K", _pick(body, "K", "k")),
    }


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


def _marca_estado(est_s: str) -> str:
    if est_s in ("OK", "OPERATIVO", "COMPLETO"):
        return ICON_OK
    if est_s in ("FALLO", "ERROR", "RECHAZADO"):
        return ICON_FAIL
    if est_s in ("UNDEFINED", "PARCIAL", "SIN_OFICIO", "FALLO_OFICIO"):
        return ICON_WARN
    if est_s == "—":
        return ICON_PEND
    return ICON_DOT


# =============================================================================
# VALUACIÓN DETALLADA (solo lectura de evidencia)
# =============================================================================
def _lineas_valuacion_ciclo(
    seq: int,
    total: int,
    r: Any,
    *,
    destacar: bool = False,
) -> List[str]:
    """Detalle de un ciclo: estado, C/L/K, Tru, citación — sin recalcular."""
    out: List[str] = []
    if not isinstance(r, dict):
        out.append(
            "    {0} seq {1}/{2}  (entrada no es dict)".format(ICON_WARN, seq, total)
        )
        return out

    body = _cuerpo_resultado(r)
    fac = _factores_de(r)
    estado = _pick(body, "estado", "status", "state") or _pick(
        r, "estado", "status", "state"
    )
    tru_ri = _pick(body, "tru_ri", "Tru_Ri", "Tru_ri")
    tru_total = _pick(body, "tru_total", "Tru_total", "Tru_Total")
    seq_id = _pick(r, "secuencia", "seq", "n", "id")
    razon = body.get("razon")
    cx = body.get("contexto_cx") if isinstance(body.get("contexto_cx"), dict) else {}
    cit = body.get("citacion") if isinstance(body.get("citacion"), dict) else None
    val = body.get("valuacion") if isinstance(body.get("valuacion"), dict) else {}
    entrada = r.get("entrada") if isinstance(r.get("entrada"), dict) else {}

    est_s = _fmt(estado)
    m = _marca_estado(est_s)
    cab = "    {0} seq {1}/{2}".format(m, seq, total)
    if destacar:
        cab = "    {0} seq {1}/{2}  «último ciclo con evidencia»".format(
            m, seq, total
        )
    out.append(cab)
    if seq_id is not None and str(seq_id) != str(seq):
        out.append("      id_interno     : {0}".format(seq_id))

    out.append("      estado         : {0}".format(est_s))
    if razon:
        out.append("      razon          : {0}".format(_fmt(razon)[:160]))

    out.append(
        "      {0} C={1}  L={2}  K={3}".format(
            ICON_CLK, _fmt(fac["C"]), _fmt(fac["L"]), _fmt(fac["K"])
        )
    )
    out.append("      Tru_Ri        : {0}".format(_fmt(tru_ri)))
    out.append("      Tru_total     : {0}".format(_fmt(tru_total)))

    if body.get("alpha") is not None or body.get("beta") is not None:
        out.append(
            "      ancla         : α={0}  β={1}".format(
                _fmt(body.get("alpha")), _fmt(body.get("beta"))
            )
        )

    if cx:
        out.append(
            "      CX            : permite_k={0}  pedir_anuncio={1}  modo={2}".format(
                _fmt(cx.get("permite_k")),
                _fmt(cx.get("pedir_anuncio")),
                _fmt(cx.get("modo_entrada")),
            )
        )

    if entrada:
        out.append(
            "      entrada       : contexto={0}  C?={1} L?={2} K?={3}  anuncio?={4}".format(
                _fmt(entrada.get("contexto"))[:40],
                entrada.get("tiene_C"),
                entrada.get("tiene_L"),
                entrada.get("tiene_K"),
                entrada.get("pedir_anuncio"),
            )
        )

    if val:
        out.append(
            "      valuacion     : capa_objeto={0}  capa_meta={1}  error_sistema={2}".format(
                _fmt(val.get("capa_objeto")),
                _fmt(val.get("capa_meta")),
                _fmt(val.get("es_error_sistema")),
            )
        )
        ids = val.get("ids")
        if isinstance(ids, list) and ids:
            out.append(
                "      ids           : {0}".format(
                    ", ".join(str(i) for i in ids[:12])
                    + ("…" if len(ids) > 12 else "")
                )
            )

    if cit:
        out.append(
            "      {0} citacion   : estado={1}  n_citas={2}  n_anuncios={3}".format(
                ICON_CIT,
                _fmt(cit.get("estado") if cit.get("estado") is not None else cit.get("ok")),
                _fmt(cit.get("n_citas")),
                _fmt(cit.get("n_anuncios")),
            )
        )
        anuncios = cit.get("anuncios") or []
        if isinstance(anuncios, list):
            for a in anuncios[:5]:
                if not isinstance(a, dict):
                    continue
                out.append(
                    "        · [{0}] {1}".format(
                        _fmt(a.get("tipo")),
                        _fmt(a.get("titulo") or a.get("enunciado"))[:72],
                    )
                )
            if len(anuncios) > 5:
                out.append(
                    "        · … y {0} anuncios más".format(len(anuncios) - 5)
                )
    return out


def _resumen_citaciones(evals: List[Any]) -> List[str]:
    """Agrega citación presente en los ciclos (solo lectura)."""
    out: List[str] = []
    total_citas = 0
    total_anuncios = 0
    ciclos_con_cit = 0
    for r in evals:
        if not isinstance(r, dict):
            continue
        body = _cuerpo_resultado(r)
        cit = body.get("citacion") if isinstance(body.get("citacion"), dict) else None
        if not cit:
            continue
        ciclos_con_cit += 1
        try:
            total_citas += int(cit.get("n_citas") or 0)
        except (TypeError, ValueError):
            pass
        try:
            total_anuncios += int(cit.get("n_anuncios") or 0)
        except (TypeError, ValueError):
            pass
    if ciclos_con_cit == 0:
        out.append(
            "  {0} Citación: ningún ciclo trajo bloque citacion".format(ICON_PEND)
        )
    else:
        out.append(
            "  {0} Citación: ciclos_con_cit={1}  n_citas≈{2}  n_anuncios≈{3}".format(
                ICON_CIT, ciclos_con_cit, total_citas, total_anuncios
            )
        )
    return out


def _lineas_generatividad(g: Dict[str, Any] | None) -> List[str]:
    out: List[str] = [
        "=" * 80,
        "{0}  GENERATIVIDAD (TR1 / U1)".format(ICON_INFO),
        "=" * 80,
    ]
    if not g or g.get("estado") == "UNDEFINED":
        out.append(
            "  {0} sin datos — AX.generatividad no disponible en el paquete".format(
                ICON_PEND
            )
        )
        if g:
            out.append("  U1 (proxy roles): {0}".format(g.get("u1_estado", "REVISAR")))
            out.append("  roles vacíos    : {0}".format(g.get("roles_vacios", [])))
            if g.get("razon"):
                out.append("  razon           : {0}".format(g.get("razon")))
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


# =============================================================================
# MAPA DE INTERVENCIÓN
# =============================================================================
def construir_acciones(datos: Dict[str, Any]) -> List[Dict[str, Any]]:
    acciones: List[Dict[str, Any]] = []
    reg = datos.get("registro_modulos") or {}
    vacios = list(reg.get("roles_vacios") or [])
    rechazados = list(reg.get("rechazados") or [])
    roles = reg.get("roles") or {}
    ct = datos.get("contratos")

    if datos.get("estado_engine") != "OPERATIVO":
        acciones.append({
            "prioridad": 1,
            "tipo": "BLOQUEANTE",
            "item": "Engine",
            "detalle": "estado = {0}".format(datos.get("estado_engine")),
            "impacto": "Nada confiable si el Engine no está OPERATIVO",
            "accion": "Revisar errores_arranque y compuertas de arranque",
            "errores": list(datos.get("errores_arranque") or []),
        })

    ia = datos.get("informe_axiomas") or {}
    if not ia.get("coherente", False):
        acciones.append({
            "prioridad": 1,
            "tipo": "BLOQUEANTE",
            "item": "Axiomas",
            "detalle": "choques={0} errores={1}".format(
                len(ia.get("choques") or []),
                len(ia.get("errores") or []),
            ),
            "impacto": "Sin axiomatización coherente el sistema no debe avanzar",
            "accion": "Resolver choques en modules/axiomas",
            "errores": list(ia.get("choques") or [])[:5],
        })

    if isinstance(ct, dict) and ct.get("coherente") is False:
        acciones.append({
            "prioridad": 2,
            "tipo": "CONTRATO",
            "item": "auditoria_contratos",
            "detalle": "contratos_report coherente=False errores_n={0}".format(
                len(ct.get("errores") or [])
            ),
            "impacto": "El juez CI reportó fallos de contrato",
            "accion": "Leer diagnostics/contratos_report.json",
            "errores": [
                (e.get("mensaje") if isinstance(e, dict) else str(e))
                for e in (ct.get("errores") or [])[:5]
            ],
        })

    for r in rechazados:
        if not isinstance(r, dict):
            continue
        ruta = r.get("ruta", "?")
        razon = r.get("razon", "?")
        acciones.append({
            "prioridad": 2,
            "tipo": "RECHAZADO",
            "item": Path(str(ruta)).parent.name if ruta != "?" else "?",
            "detalle": str(razon),
            "impacto": "Módulo en disco ignorado por Engine",
            "accion": "Registrar rol en ROLES o corregir CONTENEDOR['rol']",
            "errores": ["{0} → {1}".format(ruta, razon)],
        })

    for rol in vacios:
        acciones.append({
            "prioridad": 3,
            "tipo": "VACÍO",
            "item": str(rol),
            "detalle": "rol admitido sin módulo montado",
            "impacto": "Capacidad del rol {0} no disponible".format(rol),
            "accion": "Crear o activar módulo con CONTENEDOR['rol']='{0}'".format(rol),
            "errores": [],
        })

    # CIT: si el rol no está cargado
    if "CIT" in vacios or not (roles.get("CIT") or []):
        # evitar duplicar si ya está en vacios como acción VACÍO
        if "CIT" not in vacios:
            acciones.append({
                "prioridad": 3,
                "tipo": "VACÍO",
                "item": "CIT",
                "detalle": "rol CIT sin módulo montado",
                "impacto": "No habrá cadena de anuncio aunque pedir_anuncio=True",
                "accion": "Montar modules/citacion con CONTENEDOR rol=CIT",
                "errores": [],
            })

    evidencia = datos.get("evidencia_evaluacion") or {}
    n_ev = int(evidencia.get("n") or 0)
    if not (datos.get("resultados_evaluacion") or []) and n_ev == 0:
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "resultados_evaluacion",
            "detalle": (
                "Sin ciclos en evaluaciones.json (normal si CI va sin humo "
                "y los tests no depositaron en ese artefacto)"
            ),
            "impacto": "Omega no puede mostrar C/L/K/Tru de ciclos",
            "accion": (
                "Que los tests reales escriban evidencia o que un proceso "
                "legítimo deposite evaluaciones.json tras evaluar()"
            ),
            "errores": [],
        })

    if not datos.get("tests"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "tests",
            "detalle": "pytest no entregó test_results.xml",
            "impacto": "No se ve tasa de tests en el mapa",
            "accion": "Generar diagnostics/test_results.xml antes de Omega",
            "errores": [],
        })

    if not isinstance(ct, dict):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "contratos_report",
            "detalle": "diagnostics/contratos_report.json ausente",
            "impacto": "Sin mapa del juez CI de contratos",
            "accion": "Ejecutar auditoría estructural antes de Omega",
            "errores": [],
        })

    if not datos.get("informe_formulas"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "informe_formulas",
            "detalle": "FO no entregó verificar/barrer/inventario",
            "impacto": "No se confirma estado FO desde el reporte",
            "accion": "Exponer verificar/barrer en FO",
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
            "accion": "Capacidad generatividad en AX + censar_generatividad",
            "errores": [g.get("razon")] if g and g.get("razon") else [],
        })
    elif g.get("im_vs_theta") == "ESTANCADO":
        acciones.append({
            "prioridad": 5,
            "tipo": "TR1",
            "item": "generatividad",
            "detalle": "|Θ|={0} novedosos={1} → ESTANCADO".format(
                g.get("theta_n"), g.get("pares_novedosos")
            ),
            "impacto": "Cuerpo axiomático no expande por recombinación",
            "accion": "Revisar gobierna / dominios cruzados",
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
        "Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · C/L/K solo si el ciclo los trajo",
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
    vacios = list(reg.get("roles_vacios") or [])
    rechazados = list(reg.get("rechazados") or [])
    ct = datos.get("contratos")  # obligatorio: usado abajo y en mapa
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

    # ----- VALUACIÓN (CLK + Tru) desde evidencia -----
    evals = list(datos.get("resultados_evaluacion") or [])
    ev = datos.get("evidencia_evaluacion") or {}
    n_ev = len(evals)

    lineas.append("=" * 80)
    lineas.append(
        "{0}  VALUACIÓN (C · L · K → Tru) — solo evidencia depositada".format(ICON_CLK)
    )
    lineas.append("=" * 80)
    lineas.append(
        "  origen evidencia : {0}   n_ciclos={1}".format(
            _fmt(ev.get("origen") or ev.get("path")), n_ev
        )
    )
    lineas.append(
        "  Omega no calcula. Si C/L/K/Tru aparecen, salieron del ciclo (CA/FO)."
    )
    lineas.extend(_resumen_citaciones(evals))
    lineas.append("")

    if not evals:
        lineas.append(
            "  {0} Sin ciclos en evaluaciones.json — nada que cuantificar aquí.".format(
                ICON_PEND
            )
        )
        lineas.append(
            "  pytest mide forma; la valuación de contenido aparece cuando "
            "un ciclo real deposita resultado."
        )
        lineas.append("")
    else:
        rows = []
        for j, r in enumerate(evals, 1):
            body = _cuerpo_resultado(r) if isinstance(r, dict) else {}
            fac = _factores_de(r) if isinstance(r, dict) else {}
            rows.append([
                str(j),
                _fmt(_pick(body, "estado") or _pick(r if isinstance(r, dict) else {}, "estado")),
                _fmt(fac.get("C")),
                _fmt(fac.get("L")),
                _fmt(fac.get("K")),
                _fmt(_pick(body, "tru_ri", "Tru_Ri")),
                _fmt(_pick(body, "tru_total", "Tru_total")),
            ])
        lineas.append("  Resumen de ciclos:")
        lineas.extend(
            "  " + l
            for l in _tabla(
                ["#", "estado", "C", "L", "K", "Tru_Ri", "Tru_total"],
                rows,
                [3, 10, 12, 12, 12, 12, 12],
            )
        )
        lineas.append("")

        lineas.append("  Detalle por ciclo:")
        limite = 8
        for j, r in enumerate(evals[:limite], 1):
            is_last = j == n_ev
            lineas.extend(
                _lineas_valuacion_ciclo(j, n_ev, r, destacar=is_last)
            )
            lineas.append("")
        if n_ev > limite:
            lineas.append(
                "  {0} … y {1} ciclos más (ver evaluaciones.json)".format(
                    ICON_DOT, n_ev - limite
                )
            )
            lineas.append("  Último ciclo (completo):")
            lineas.extend(
                _lineas_valuacion_ciclo(n_ev, n_ev, evals[-1], destacar=True)
            )
            lineas.append("")

    # ----- Módulos -----
    roles = reg.get("roles") or {}
    todos_roles = sorted(set(list(roles.keys()) + list(vacios)))
    rows_m = []
    for rol in todos_roles:
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
    else:
        lineas.append("  {0} (sin registro de módulos)".format(ICON_PEND))
    lineas.append("")

    # ----- Intervención -----
    lineas.append("=" * 80)
    lineas.append("{0}  MAPA DE INTERVENCIÓN (por prioridad)".format(ICON_WARN))
    lineas.append("=" * 80)
    lineas.append("")
    if not acciones:
        lineas.append("  {0} No hay acciones pendientes.".format(ICON_OK))
        lineas.append("")
    else:
        for i, a in enumerate(acciones, 1):
            tipo = a["tipo"]
            if tipo in ("BLOQUEANTE", "CONTRATO", "RECHAZADO"):
                ic = ICON_FAIL
            elif tipo == "DATOS":
                ic = ICON_PEND
            else:
                ic = ICON_WARN
            lineas.append("  {0} {1}. [{2}] {3}".format(ic, i, tipo, a["item"]))
            lineas.append("     Detalle   : {0}".format(a["detalle"]))
            lineas.append("     Impacto   : {0}".format(a["impacto"]))
            lineas.append("     Acción    : {0}".format(a["accion"]))
            if a.get("errores"):
                lineas.append("     Evidencia :")
                for e in a["errores"][:3]:
                    lineas.append("       {0} {1}".format(ICON_DOT, e))
            lineas.append("")

    # ----- Salud por capa -----
    lineas.append("=" * 80)
    lineas.append("{0}  SALUD POR CAPA".format(ICON_INFO))
    lineas.append("=" * 80)
    lineas.append("")

    const = datos.get("constantes") or {}
    lineas.append("  {0} Constantes (CT)".format(ICON_OK if const else ICON_PEND))
    lineas.append(
        "      ALPHA = {0}   BETA = {1}".format(
            const.get("ALPHA"), const.get("BETA")
        )
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
        ok_fo = bool(fo.get("coherente", True))
        lineas.append("  {0} Fórmulas (FO)".format(ICON_OK if ok_fo else ICON_FAIL))
        lineas.append(
            "      coherente = {0}   faltas = {1}".format(
                fo.get("coherente"), fo.get("faltas", [])
            )
        )
    else:
        lineas.append("  {0} Fórmulas (FO) — informe no entregado".format(ICON_PEND))
    lineas.append("")

    mc = datos.get("informe_mecanica")
    if mc:
        ok_mc = bool(mc.get("coherente"))
        lineas.append("  {0} Mecánica (MC)".format(ICON_OK if ok_mc else ICON_FAIL))
        lineas.append("      coherente = {0}".format(mc.get("coherente")))
    else:
        lineas.append("  {0} Mecánica (MC) — informe no entregado".format(ICON_PEND))
    lineas.append("")

    ca = datos.get("informe_calculator")
    if ca:
        ok_ca = bool(ca.get("coherente", True))
        lineas.append("  {0} Calculator (CA)".format(ICON_OK if ok_ca else ICON_FAIL))
        lineas.append(
            "      coherente = {0}  detalle = {1}".format(
                ca.get("coherente"),
                ca.get("factores_api") or ca.get("archivos") or ca.get("errores") or "—",
            )
        )
    else:
        lineas.append(
            "  {0} Calculator (CA) — informe no entregado".format(ICON_PEND)
        )
    lineas.append("")

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
        lineas.append(
            "      nota: pytest no es Tru; cuantificación de contenido = tabla de ciclos"
        )
    else:
        lineas.append("  {0} Tests — resultados no entregados".format(ICON_PEND))
    lineas.append("")

    lineas.extend(_lineas_generatividad(datos.get("generatividad")))

    lineas.append("=" * 80)
    lineas.append("{0}  INVENTARIO RÁPIDO".format(ICON_MOD))
    lineas.append("=" * 80)
    lineas.append("Presente:")
    hay_presente = False
    for rol, mods in sorted(roles.items()):
        if mods:
            hay_presente = True
            lineas.append(
                "  {0} {1}: {2}".format(ICON_OK, rol, ", ".join(str(m) for m in mods))
            )
    if not hay_presente:
        lineas.append("  {0} (ninguno cargado en registro)".format(ICON_PEND))
    lineas.append("Ausente:")
    if vacios:
        for rol in vacios:
            lineas.append("  {0} {1}".format(ICON_PEND, rol))
    else:
        lineas.append("  {0} (ninguno)".format(ICON_OK))
    lineas.append("Rechazado:")
    if rechazados:
        for r in rechazados:
            if not isinstance(r, dict):
                continue
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

    inv = datos.get("inventario_engine") or {}
    if inv:
        lineas.append("=" * 80)
        lineas.append("{0}  INVENTARIO ENGINE (solo lectura)".format(ICON_INFO))
        lineas.append("=" * 80)
        lineas.append(
            "  estado={0}  n_eval_proceso_omega={1}  "
            "(valuación mostrada = artefacto CI/tests, no este proceso)".format(
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
        "  Ciclos valuados    : {0}".format(n_ev),
        "  Este reporte no recalculó C, L, K ni Tru.",
        "  Este reporte no ejecutó humo ni evaluar().",
        "  Los números salen del sistema (CA/FO) vía evidencia depositada.",
        "=" * 80,
    ]
    return "\n".join(lineas)


# =============================================================================
# CARGA (solo lectura)
# =============================================================================
def _leer_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def cargar_datos_desde_engine() -> Dict[str, Any]:
    """No llama evaluar(). No inventa resultados_evaluacion."""
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

        # Valuación: SOLO evaluaciones.json
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
                            "nota": doc.get("nota"),
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

        try:
            cont_cit = eng.registro.primero("CIT") if hasattr(eng, "registro") else None
            if cont_cit is not None:
                for cap in ("verificar", "barrer", "inventario"):
                    fn = cont_cit.fn(cap)
                    if callable(fn):
                        out = fn()
                        if isinstance(out, dict):
                            datos["informe_citacion"] = out
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
