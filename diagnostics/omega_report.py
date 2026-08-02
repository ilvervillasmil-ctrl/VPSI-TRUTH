#!/usr/bin/env python3
"""
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.5)
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
from typing import Any, Dict, List

CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OK = "OK"
FALLO = "FALLO"
PENDIENTE = "PENDIENTE"
STRICT = os.getenv("OMEGA_STRICT", "0") == "1"
VERSION = "9.5"

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
        "GENERATIVIDAD (TR1 / U1)",
        "=" * 80,
    ]
    if not g or g.get("estado") == "UNDEFINED":
        out.append("  (sin datos — AX.generatividad no disponible en el paquete)")
        if g:
            out.append("  U1 (proxy roles): {0}".format(g.get("u1_estado", "REVISAR")))
            out.append("  roles vacíos    : {0}".format(g.get("roles_vacios", [])))
            if g.get("razon"):
                out.append("  razon           : {0}".format(g.get("razon")))
        out.append("")
        return out

    out.append("  |Θ| (AX)           : {0}".format(g.get("theta_n", "—")))
    out.append("  pares totales      : {0}".format(g.get("pares_totales", "—")))
    out.append("  pares compatibles  : {0}".format(g.get("pares_compatibles", "—")))
    out.append("  pares novedosos    : {0}".format(g.get("pares_novedosos", "—")))
    out.append("  |Im(⊕)| ? |Θ|      : {0}".format(g.get("im_vs_theta", "—")))
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
        out.append("  (sin datos canónicos en el paquete)")

    if g.get("nota"):
        out.append("  nota               : {0}".format(g["nota"]))
    out.append("")
    return out


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

    # Solo reporta ausencia: no inventa evaluaciones
    if not datos.get("resultados_evaluacion"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "resultados_evaluacion",
            "detalle": (
                "Lista vacía en el paquete (Engine no entregó evaluaciones "
                "acumuladas en esta sesión de carga)"
            ),
            "impacto": "No se puede auditar el camino de evaluación desde Omega",
            "accion": (
                "Quien invoque evaluar() debe dejar la lista en Engine; "
                "Omega solo la lee (get_resultados_evaluacion / inventario)"
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
        "OMEGA REPORT — MAPA DE TRABAJO",
        "VPSI-TRUTH (Versión {0})".format(VERSION),
        "Generado: {0}    Commit: {1}".format(ahora, sha),
        "Modo: SOLO PRESENTACIÓN · sin humo · sin recálculo · prioriza intervención",
        "=" * 80,
        "",
    ]

    if faltas:
        lineas.append("[{0}] Entrada incompleta — no se puede construir el mapa".format(FALLO))
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
    elif estado == "OPERATIVO" and n_bloqueantes == 0:
        salud = "OPERATIVO con huecos no bloqueantes"
    else:
        salud = "DEGRADADO — hay bloqueos"

    lineas += _bloque("ESTADO GLOBAL", [
        "  Engine          : {0}".format(estado),
        "  Axiomas         : {0}".format(
            "coherente" if coherente else "INCOHERENTE"
        ),
        "  Contenedores    : {0}".format(total),
        "  Roles vacíos    : {0}".format(len(vacios)),
        "  Rechazados      : {0}".format(len(rechazados)),
        "  Acciones abiertas: {0}".format(len(acciones)),
        "  Salud           : {0}".format(salud),
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

    lineas.append("MÓDULOS Y ROLES")
    lineas.extend(
        "  " + l
        for l in _tabla(["ROL", "ESTADO", "N", "MÓDULOS"], rows, [4, 9, 3, 36])
    )
    lineas.append("")

    lineas.append("=" * 80)
    lineas.append("MAPA DE INTERVENCIÓN (ordenado por prioridad)")
    lineas.append("=" * 80)
    lineas.append("")

    if not acciones:
        lineas.append("  No hay acciones pendientes. Sistema limpio.")
        lineas.append("")
    else:
        for i, a in enumerate(acciones, 1):
            lineas.append("  {0}. [{1}] {2}".format(i, a["tipo"], a["item"]))
            lineas.append("     Detalle   : {0}".format(a["detalle"]))
            lineas.append("     Impacto   : {0}".format(a["impacto"]))
            lineas.append("     Acción    : {0}".format(a["accion"]))
            if a["errores"]:
                lineas.append("     Evidencia :")
                for e in a["errores"][:3]:
                    lineas.append("       · {0}".format(e))
            lineas.append("")

    lineas.append("=" * 80)
    lineas.append("SALUD POR CAPA")
    lineas.append("=" * 80)
    lineas.append("")

    const = datos.get("constantes") or {}
    lineas.append("  [{0}] Constantes (CT)".format(OK))
    lineas.append(
        "      ALPHA = {0}   BETA = {1}".format(
            const.get("ALPHA"), const.get("BETA")
        )
    )
    lineas.append("")

    marca_ax = OK if coherente else FALLO
    lineas.append("  [{0}] Axiomas (AX)".format(marca_ax))
    lineas.append("      declaraciones = {0}".format(ia.get("declaraciones", "?")))
    lineas.append("      choques       = {0}".format(len(ia.get("choques", []))))
    lineas.append("      errores       = {0}".format(len(ia.get("errores", []))))
    if ia.get("por_tipo"):
        lineas.append("      por_tipo      = {0}".format(ia.get("por_tipo")))
    lineas.append("")

    fo = datos.get("informe_formulas")
    if fo:
        marca_fo = OK if fo.get("coherente", True) else FALLO
        lineas.append("  [{0}] Fórmulas (FO)".format(marca_fo))
        lineas.append(
            "      coherente = {0}   faltas = {1}".format(
                fo.get("coherente"), fo.get("faltas", [])
            )
        )
    else:
        lineas.append("  [{0}] Fórmulas (FO) — informe no entregado".format(PENDIENTE))
    lineas.append("")

    mc = datos.get("informe_mecanica")
    if mc:
        marca_mc = OK if mc.get("coherente") else FALLO
        lineas.append("  [{0}] Mecánica (MC)".format(marca_mc))
        lineas.append("      coherente = {0}".format(mc.get("coherente")))
    else:
        lineas.append(
            "  [{0}] Mecánica (MC) — informe no entregado".format(PENDIENTE)
        )
    lineas.append("")

    ct = datos.get("contratos")
    if isinstance(ct, dict) and "coherente" in ct:
        marca_ct = OK if ct.get("coherente") else FALLO
        res = ct.get("resumen") or {}
        lineas.append("  [{0}] Contratos (CI)".format(marca_ct))
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
            "  [{0}] Contratos (CI) — sin contratos_report.json".format(PENDIENTE)
        )
    lineas.append("")

    evals = datos.get("resultados_evaluacion") or []
    if evals:
        lineas.append("  [{0}] Camino de evaluación".format(OK))
        lineas.append("      evaluaciones = {0}".format(len(evals)))
        for j, r in enumerate(evals[:4], 1):
            lineas.append(
                "      [{0}] estado={1}  Tru_Ri={2}  Tru_total={3}".format(
                    j,
                    r.get("estado"),
                    r.get("tru_ri"),
                    r.get("tru_total"),
                )
            )
    else:
        lineas.append(
            "  [{0}] Camino de evaluación — sin resultados en el paquete".format(
                PENDIENTE
            )
        )
    lineas.append("")

    tests = datos.get("tests")
    if tests:
        marca_t = OK if tests.get("fallidos", 1) == 0 else FALLO
        lineas.append("  [{0}] Tests".format(marca_t))
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
            "  [{0}] Tests — resultados no entregados".format(PENDIENTE)
        )
    lineas.append("")

    lineas.extend(_lineas_generatividad(datos.get("generatividad")))

    lineas.append("=" * 80)
    lineas.append("INVENTARIO RÁPIDO")
    lineas.append("=" * 80)
    lineas.append("Presente:")
    for rol, mods in sorted(roles.items()):
        if mods:
            lineas.append("  ✓ {0}: {1}".format(rol, ", ".join(mods)))
    lineas.append("Ausente:")
    for rol in vacios:
        lineas.append("  · {0}".format(rol))
    lineas.append("Rechazado:")
    if rechazados:
        for r in rechazados:
            lineas.append(
                "  ✗ {0} → {1}".format(
                    Path(r.get("ruta", "?")).parent.name,
                    r.get("razon", "?"),
                )
            )
    else:
        lineas.append("  (ninguno)")
    lineas.append("")

    inv = datos.get("inventario_engine") or {}
    if inv:
        lineas.append("=" * 80)
        lineas.append("INVENTARIO ENGINE (solo lectura)")
        lineas.append("=" * 80)
        lineas.append("  estado={0}  n_eval={1}".format(
            inv.get("estado"),
            inv.get("resultados_evaluacion_n", len(evals)),
        ))
        lineas.append("")

    lineas += [
        "=" * 80,
        "CIERRE",
        "=" * 80,
        "  Versión Omega      : {0}".format(VERSION),
        "  Salud              : {0}".format(salud),
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
    Solo agrega lo que ya existe:
      - estado e informes del Engine al arrancar
      - capacidades de módulos vía contrato (fn exacta)
      - diagnostics/*.json y test_results.xml si el CI los dejó
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
    }

    # Artefactos CI (pueden existir antes que el Engine)
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

        # Camino de evaluación: SOLO evidencia de auditoría (sin humo, sin evaluar)
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
        # No llamar eng.evaluar(). No inventar entradas.

        # Inventario (solo lectura de contratos montados)
        try:
            if hasattr(eng, "inventario"):
                inv = eng.inventario()
                if isinstance(inv, dict):
                    datos["inventario_engine"] = inv
                    # si inventario expone la lista, usarla solo si aún está vacía
                    if not datos["resultados_evaluacion"]:
                        re = inv.get("resultados_evaluacion")
                        if isinstance(re, list):
                            datos["resultados_evaluacion"] = re
        except Exception:  # noqa: BLE001
            pass

        # FO vía contrato (clave exacta del CONTENEDOR)
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

        # AX generatividad vía contrato
        try:
            if hasattr(eng, "censar_generatividad"):
                datos["generatividad"] = eng.censar_generatividad()
            else:
                cont_ax = eng.registro.primero("AX") if hasattr(eng, "registro") else None
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

        # CA centinela (barrer/verificar) — informe opcional
        try:
            cont_ca = eng.registro.primero("CA") if hasattr(eng, "registro") else None
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

    # tests xml (artefacto CI)
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
