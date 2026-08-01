#!/usr/bin/env python3
"""
OMEGA REPORT — MAPA DE TRABAJO
VPSI-TRUTH (Versión 9.4)
==============================

Presentador objetivo + mapa de intervención.

No recalcula.
Lee solo lo que el Engine y los módulos ya produjeron.
Ordena lo que falta por prioridad de trabajo.
Cada hueco indica: qué es · dónde · por qué importa · qué hacer.

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
            faltas.append(f"falta campo obligatorio: {campo}")
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
            faltas.append(f"estado_engine inválido: {datos['estado_engine']}")
    return faltas


# =============================================================================
# HELPERS DE PRESENTACIÓN
# =============================================================================
def _tabla(headers: List[str], rows: List[List[str]], anchos: List[int] | None = None) -> List[str]:
    if anchos is None:
        anchos = [
            max(len(h), max((len(str(r[i])) for r in rows), default=0))
            for i, h in enumerate(headers)
        ]
    sep = "+" + "+".join("-" * (w + 2) for w in anchos) + "+"

    def fila(vals: List[str]) -> str:
        return "| " + " | ".join(str(v).ljust(anchos[i]) for i, v in enumerate(vals)) + " |"

    out = [sep, fila(headers), sep]
    for r in rows:
        out.append(fila(r))
    out.append(sep)
    return out


def _bloque(titulo: str, lineas_bloq: List[str]) -> List[str]:
    return [titulo, *lineas_bloq, ""]


def _lineas_generatividad(g: Dict[str, Any] | None) -> List[str]:
    """Presenta TR1/U1. Solo lectura del paquete; no calcula."""
    out: List[str] = [
        "=" * 80,
        "GENERATIVIDAD (TR1 / U1)",
        "=" * 80,
    ]
    if not g or g.get("estado") == "UNDEFINED":
        out.append("  (sin datos — AX.generatividad no disponible)")
        if g:
            out.append(f"  U1 (proxy roles): {g.get('u1_estado', 'REVISAR')}")
            out.append(f"  roles vacíos    : {g.get('roles_vacios', [])}")
            if g.get("razon"):
                out.append(f"  razon           : {g.get('razon')}")
        out.append("")
        return out

    out.append(f"  |Θ| (AX)           : {g.get('theta_n', '—')}")
    out.append(f"  pares totales      : {g.get('pares_totales', '—')}")
    out.append(f"  pares compatibles  : {g.get('pares_compatibles', '—')}")
    out.append(f"  pares novedosos    : {g.get('pares_novedosos', '—')}")
    out.append(f"  |Im(⊕)| ? |Θ|      : {g.get('im_vs_theta', '—')}")
    out.append(f"  dominios           : {g.get('dominios', [])}")
    out.append(f"  roles vacíos       : {g.get('roles_vacios', [])}")
    out.append(f"  U1                 : {g.get('u1_estado', '—')}")
    if g.get("por_tipo_theta"):
        out.append(f"  por_tipo_theta     : {g.get('por_tipo_theta')}")
    if g.get("nota"):
        out.append(f"  nota               : {g['nota']}")
    out.append("")
    return out

    can = (g or {}).get("canonica") or {}
    if can:
        out.append("  --- capa canónica (paper TR1) ---")
        out.append(f"  |Θ|_can           : {can.get('theta_n', '—')} / 24")
        out.append(f"  novedosos_can     : {can.get('pares_novedosos', '—')}  (paper: 153)")
        out.append(f"  |Im| ? |Θ| can    : {can.get('im_vs_theta', '—')}")
        out.append(f"  ids_faltantes     : {can.get('ids_faltantes', [])}")
        out.append(f"  ids_sin_dominio   : {can.get('ids_sin_dominio', [])}")
        out.append(f"  dominios_can      : {can.get('dominios', [])}")
        
# =============================================================================
# CONSTRUCCIÓN DEL MAPA DE TRABAJO
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
            "detalle": f"estado = {datos.get('estado_engine')}",
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
                f"choques={len(ia.get('choques', []))} "
                f"errores={len(ia.get('errores', []))}"
            ),
            "impacto": "Sin axiomatización coherente el sistema no debe avanzar",
            "accion": "Resolver choques en modules/axiomas y VPSI.py",
            "errores": ia.get("choques", [])[:5],
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
            "errores": [f"{ruta} → {razon}"],
        })

    for rol in vacios:
        acciones.append({
            "prioridad": 3,
            "tipo": "VACÍO",
            "item": rol,
            "detalle": "rol admitido sin módulo montado",
            "impacto": f"Capacidad del rol {rol} no disponible",
            "accion": f"Crear o activar módulo con CONTENEDOR['rol'] = '{rol}'",
            "errores": [],
        })

    if not datos.get("resultados_evaluacion"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "resultados_evaluacion",
            "detalle": "Engine no pasó resultados de evaluar() al reporte",
            "impacto": "No se puede auditar el camino de evaluación desde Omega Report",
            "accion": "Hacer que el Engine entregue la lista de evaluaciones al paquete de datos",
            "errores": [],
        })

    if not datos.get("tests"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "tests",
            "detalle": "resultados de pytest no entregados al reporte",
            "impacto": "No se ve cobertura ni regresiones desde el mapa",
            "accion": "Parsear diagnostics/test_results.xml y pasarlo en el paquete de datos",
            "errores": [],
        })

    if not datos.get("informe_formulas"):
        acciones.append({
            "prioridad": 4,
            "tipo": "DATOS",
            "item": "informe_formulas",
            "detalle": "no entregado",
            "impacto": "No se confirma el estado del módulo FO desde el reporte",
            "accion": "Engine debe invocar formulas.barrer() y adjuntar el resultado",
            "errores": [],
        })

    # Generatividad ausente o estancada (no bloquea arranque; informa mapa)
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
                f"|Θ|={g.get('theta_n')} novedosos={g.get('pares_novedosos')} "
                f"→ ESTANCADO"
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
        "VPSI-TRUTH (Versión 9.4)",
        f"Generado: {ahora}    Commit: {sha}",
        "Modo: SOLO PRESENTACIÓN · prioriza intervención · no recalcula",
        "=" * 80,
        "",
    ]

    if faltas:
        lineas.append(f"[{FALLO}] Entrada incompleta — no se puede construir el mapa")
        for f in faltas:
            lineas.append(f"    - {f}")
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
        f"  Engine          : {estado}",
        f"  Axiomas         : {'coherente' if coherente else 'INCOHERENTE'}",
        f"  Contenedores    : {total}",
        f"  Roles vacíos    : {len(vacios)}",
        f"  Rechazados      : {len(rechazados)}",
        f"  Acciones abiertas: {len(acciones)}",
        f"  Salud           : {salud}",
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
    lineas.extend("  " + l for l in _tabla(
        ["ROL", "ESTADO", "N", "MÓDULOS"],
        rows,
        [4, 9, 3, 36],
    ))
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
            lineas.append(f"  {i}. [{a['tipo']}] {a['item']}")
            lineas.append(f"     Detalle   : {a['detalle']}")
            lineas.append(f"     Impacto   : {a['impacto']}")
            lineas.append(f"     Acción    : {a['accion']}")
            if a["errores"]:
                lineas.append("     Evidencia :")
                for e in a["errores"][:3]:
                    lineas.append(f"       · {e}")
            lineas.append("")

    lineas.append("=" * 80)
    lineas.append("SALUD POR CAPA")
    lineas.append("=" * 80)
    lineas.append("")

    const = datos.get("constantes") or {}
    lineas.append(f"  [{OK}] Constantes (CT)")
    lineas.append(f"      ALPHA = {const.get('ALPHA')}   BETA = {const.get('BETA')}")
    lineas.append("")

    marca_ax = OK if coherente else FALLO
    lineas.append(f"  [{marca_ax}] Axiomas (AX)")
    lineas.append(f"      declaraciones = {ia.get('declaraciones', '?')}")
    lineas.append(f"      choques       = {len(ia.get('choques', []))}")
    lineas.append(f"      errores       = {len(ia.get('errores', []))}")
    if ia.get("por_tipo"):
        lineas.append(f"      por_tipo      = {ia.get('por_tipo')}")
    lineas.append("")

    fo = datos.get("informe_formulas")
    if fo:
        marca_fo = OK if fo.get("coherente") else FALLO
        lineas.append(f"  [{marca_fo}] Fórmulas (FO)")
        lineas.append(
            f"      coherente = {fo.get('coherente')}   faltas = {fo.get('faltas', [])}"
        )
    else:
        lineas.append(f"  [{PENDIENTE}] Fórmulas (FO) — informe no entregado")
    lineas.append("")

    mc = datos.get("informe_mecanica")
    if mc:
        marca_mc = OK if mc.get("coherente") else FALLO
        lineas.append(f"  [{marca_mc}] Mecánica (MC)")
        lineas.append(f"      coherente = {mc.get('coherente')}")
    else:
        lineas.append(f"  [{PENDIENTE}] Mecánica (MC) — informe no entregado")
    lineas.append("")

    evals = datos.get("resultados_evaluacion") or []
    if evals:
        lineas.append(f"  [{OK}] Camino de evaluación")
        lineas.append(f"      evaluaciones = {len(evals)}")
        for j, r in enumerate(evals[:4], 1):
            lineas.append(
                f"      [{j}] estado={r.get('estado')}  "
                f"Tru_Ri={r.get('tru_ri')}  Tru_total={r.get('tru_total')}"
            )
    else:
        lineas.append(f"  [{PENDIENTE}] Camino de evaluación — sin resultados entregados")
    lineas.append("")

    tests = datos.get("tests")
    if tests:
        marca_t = OK if tests.get("fallidos", 1) == 0 else FALLO
        lineas.append(f"  [{marca_t}] Tests")
        lineas.append(
            f"      total={tests.get('total')}  pasados={tests.get('pasados')}  "
            f"fallidos={tests.get('fallidos')}  tasa={tests.get('tasa')}%"
        )
    else:
        lineas.append(f"  [{PENDIENTE}] Tests — resultados no entregados")
    lineas.append("")

    # TR1 / U1 (presentación pura)
    lineas.extend(_lineas_generatividad(datos.get("generatividad")))

    lineas.append("=" * 80)
    lineas.append("INVENTARIO RÁPIDO")
    lineas.append("=" * 80)
    lineas.append("Presente:")
    for rol, mods in sorted(roles.items()):
        if mods:
            lineas.append(f"  ✓ {rol}: {', '.join(mods)}")
    lineas.append("Ausente:")
    for rol in vacios:
        lineas.append(f"  · {rol}")
    lineas.append("Rechazado:")
    if rechazados:
        for r in rechazados:
            lineas.append(
                f"  ✗ {Path(r.get('ruta', '?')).parent.name} → {r.get('razon', '?')}"
            )
    else:
        lineas.append("  (ninguno)")
    lineas.append("")

    lineas += [
        "=" * 80,
        "CIERRE",
        "=" * 80,
        f"  Salud              : {salud}",
        f"  Acciones abiertas  : {len(acciones)}",
        f"  Bloqueantes        : {n_bloqueantes}",
        "  Este reporte no recalculó nada.",
        "  El orden de la lista = orden recomendado de trabajo.",
        "=" * 80,
    ]

    return "\n".join(lineas)


# =============================================================================
# CARGA DESDE ENGINE
# =============================================================================
def cargar_datos_desde_engine() -> Dict[str, Any]:
    datos: Dict[str, Any] = {
        "estado_engine": "NO_INICIADO",
        "constantes": {},
        "informe_axiomas": {},
        "errores_arranque": [],
    }

    try:
        from core.engine import Engine, ArranqueError

        try:
            eng = Engine(
                raiz_modulos=str(REPO_ROOT / "modules"),
                invocador_id="core",
                strict=False,
            )
        except TypeError:
            # firmas antiguas
            try:
                eng = Engine(
                    str(REPO_ROOT / "modules"),
                    invocador_id="core",
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

        # FO
        try:
            reg = datos.get("registro_modulos") or {}
            roles = reg.get("roles") or {}
            # fallback: intentar capacidad FO vía Engine
            if hasattr(eng, "ejecutar_capacidad"):
                fo_out = eng.ejecutar_capacidad("FO", "verificar")
                if isinstance(fo_out, dict):
                    datos["informe_formulas"] = fo_out
                else:
                    fo_out = eng.ejecutar_capacidad("FO", "barrer")
                    if isinstance(fo_out, dict):
                        datos["informe_formulas"] = fo_out
        except Exception:  # noqa: BLE001
            pass

        # TR1 / U1
        try:
            if hasattr(eng, "censar_generatividad"):
                datos["generatividad"] = eng.censar_generatividad()
            elif hasattr(eng, "ejecutar_capacidad"):
                g = eng.ejecutar_capacidad("AX", "generatividad")
                if isinstance(g, dict):
                    datos["generatividad"] = g
        except Exception as e:  # noqa: BLE001
            datos["generatividad"] = {
                "estado": "UNDEFINED",
                "razon": f"{type(e).__name__}: {e}",
            }

        # tests xml
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

    except Exception as e:  # noqa: BLE001
        datos["estado_engine"] = "RECHAZADO"
        datos["errores_arranque"] = [f"{type(e).__name__}: {e}"]

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
    print(f"\nJSON: {out_json}")

    faltas = validar_entrada(datos)
    if STRICT and (datos.get("estado_engine") != "OPERATIVO" or faltas):
        sys.exit(1)


if __name__ == "__main__":
    main()
