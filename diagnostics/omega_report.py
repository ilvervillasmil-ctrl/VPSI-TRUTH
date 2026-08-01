#!/usr/bin/env python3
"""
OMEGA REPORT - VPSI-TRUTH (Versión 9.4)
======================================

Presentador objetivo y auto-actualizable.

- No recalcula.
- Lee solo lo que el Engine y los módulos ya produjeron.
- Muestra en tablas qué está presente, qué falta y qué fue rechazado.
- Se adapta automáticamente a nuevos módulos/roles.

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


def _tabla(headers: List[str], rows: List[List[str]], anchos: List[int] | None = None) -> List[str]:
    if anchos is None:
        anchos = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
    sep = "+" + "+".join("-" * (w + 2) for w in anchos) + "+"
    def fila(vals: List[str]) -> str:
        return "| " + " | ".join(v.ljust(anchos[i]) for i, v in enumerate(vals)) + " |"
    out = [sep, fila(headers), sep]
    for r in rows:
        out.append(fila(r))
    out.append(sep)
    return out


def presentar(datos: Dict[str, Any]) -> str:
    faltas = validar_entrada(datos)
    lineas: List[str] = []

    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = os.getenv("GITHUB_SHA", "local")[:12]

    lineas += [
        "=" * 80,
        "OMEGA REPORT - VPSI-TRUTH (Versión 9.4)",
        f"Generado: {ahora}    Commit: {sha}",
        "Modo: SOLO PRESENTACIÓN (no recalcula · se actualiza con cada módulo)",
        "=" * 80,
        "",
    ]

    if faltas:
        lineas.append(f"[{FALLO}] Entrada incompleta")
        for f in faltas:
            lineas.append(f"    - {f}")
        lineas.append("")
        lineas.append("Sin datos reales del Engine el reporte no puede afirmar coherencia.")
        return "\n".join(lineas)

    # ------------------------------------------------------------------
    # 1. Estado del Engine
    # ------------------------------------------------------------------
    estado = datos["estado_engine"]
    marca = OK if estado == "OPERATIVO" else FALLO
    lineas.append(f"[{marca}] Estado del Engine")
    lineas.append(f"    estado = {estado}")
    for e in datos.get("errores_arranque") or []:
        lineas.append(f"    - {e}")
    lineas.append("")

    # ------------------------------------------------------------------
    # 2. Constantes
    # ------------------------------------------------------------------
    const = datos["constantes"]
    lineas.append(f"[{OK}] Constantes (módulo CT)")
    lineas.append(f"    ALPHA = {const.get('ALPHA')}")
    lineas.append(f"    BETA  = {const.get('BETA')}")
    lineas.append("    Fuente: modules.constante (no recalculado)")
    lineas.append("")

    # ------------------------------------------------------------------
    # 3. Tabla de módulos / roles (auto-actualizable)
    # ------------------------------------------------------------------
    reg = datos.get("registro_modulos") or {}
    roles = reg.get("roles") or {}
    vacios = reg.get("roles_vacios") or []
    rechazados = reg.get("rechazados") or []
    total = reg.get("total", 0)

    lineas.append(f"[{OK if total else PENDIENTE}] Módulos y roles")
    lineas.append(f"    total contenedores registrados = {total}")
    lineas.append("")

    # Tabla principal de roles
    headers = ["ROL", "ESTADO", "MÓDULOS", "NOTA"]
    rows = []
    todos_roles = sorted(set(list(roles.keys()) + vacios))
    for rol in todos_roles:
        mods = roles.get(rol) or []
        if mods:
            estado_r = "CARGADO"
            nota = ", ".join(mods)
        else:
            estado_r = "VACÍO"
            nota = "(sin módulo montado)"
        rows.append([rol, estado_r, str(len(mods)), nota])

    lineas.extend("    " + l for l in _tabla(headers, rows, [4, 9, 8, 40]))
    lineas.append("")

    # Rechazados
    if rechazados:
        lineas.append(f"[{FALLO}] Módulos rechazados ({len(rechazados)})")
        for r in rechazados:
            lineas.append(f"    - {r.get('ruta', '?')}: {r.get('razon', '?')}")
        lineas.append("    (roles no admitidos o contrato inválido)")
    else:
        lineas.append(f"[{OK}] Módulos rechazados: 0")
    lineas.append("")

    # ------------------------------------------------------------------
    # 4. Axiomas
    # ------------------------------------------------------------------
    ia = datos["informe_axiomas"]
    coherente = bool(ia.get("coherente"))
    marca_ax = OK if coherente else FALLO
    lineas.append(f"[{marca_ax}] Barrido axiomático")
    lineas.append(f"    coherente     = {coherente}")
    lineas.append(f"    declaraciones = {ia.get('declaraciones', '?')}")
    lineas.append(f"    choques       = {len(ia.get('choques', []))}")
    lineas.append(f"    errores       = {len(ia.get('errores', []))}")
    lineas.append("    Fuente: modules.axiomas.barrer() vía Engine")
    lineas.append("")

    # ------------------------------------------------------------------
    # 5. Fórmulas
    # ------------------------------------------------------------------
    fo = datos.get("informe_formulas")
    if fo:
        marca_fo = OK if fo.get("coherente") else FALLO
        lineas.append(f"[{marca_fo}] Fórmulas")
        lineas.append(f"    coherente = {fo.get('coherente')}")
        lineas.append(f"    faltas    = {fo.get('faltas', [])}")
        lineas.append("    Fuente: modules.formulas.barrer() vía Engine")
    else:
        lineas.append(f"[{PENDIENTE}] Fórmulas")
        lineas.append("    informe_formulas no entregado por el Engine")
    lineas.append("")

    # ------------------------------------------------------------------
    # 6. Mecánica
    # ------------------------------------------------------------------
    mc = datos.get("informe_mecanica")
    if mc:
        marca_mc = OK if mc.get("coherente") else FALLO
        lineas.append(f"[{marca_mc}] Mecánica")
        lineas.append(f"    coherente = {mc.get('coherente')}")
        lineas.append(f"    choques   = {mc.get('choques', [])}")
        lineas.append("    Fuente: modules.correlacion_mecanica.barrer() vía Engine")
    else:
        lineas.append(f"[{PENDIENTE}] Mecánica")
        lineas.append("    informe_mecanica no entregado por el Engine")
    lineas.append("")

    # ------------------------------------------------------------------
    # 7. Evaluaciones
    # ------------------------------------------------------------------
    evals = datos.get("resultados_evaluacion") or []
    if evals:
        lineas.append(f"[{OK}] Camino de evaluación")
        lineas.append(f"    evaluaciones recibidas = {len(evals)}")
        for i, r in enumerate(evals[:6], 1):
            lineas.append(
                f"    [{i}] estado={r.get('estado')}  "
                f"Tru_Ri={r.get('tru_ri')}  Tru_total={r.get('tru_total')}"
            )
        lineas.append("    Fuente: engine.evaluar() (ya calculado)")
    else:
        lineas.append(f"[{PENDIENTE}] Camino de evaluación")
        lineas.append("    Ningún resultado de evaluar() fue entregado al reporte")
    lineas.append("")

    # ------------------------------------------------------------------
    # 8. Tests
    # ------------------------------------------------------------------
    tests = datos.get("tests")
    if tests:
        marca_t = OK if tests.get("fallidos", 1) == 0 else FALLO
        lineas.append(f"[{marca_t}] Tests")
        lineas.append(
            f"    total={tests.get('total')}  pasados={tests.get('pasados')}  "
            f"fallidos={tests.get('fallidos')}  tasa={tests.get('tasa')}%"
        )
    else:
        lineas.append(f"[{PENDIENTE}] Tests")
        lineas.append("    resultados de tests no entregados al reporte")
    lineas.append("")

    # ------------------------------------------------------------------
    # 9. Inventario de presencia / ausencia (detalle)
    # ------------------------------------------------------------------
    lineas.append("=" * 80)
    lineas.append("INVENTARIO DE PRESENCIA")
    lineas.append("=" * 80)

    presentes = []
    ausentes = []
    for rol in todos_roles:
        mods = roles.get(rol) or []
        if mods:
            presentes.append(f"{rol}: {', '.join(mods)}")
        else:
            ausentes.append(rol)

    lineas.append("Presente:")
    if presentes:
        for p in presentes:
            lineas.append(f"  ✓ {p}")
    else:
        lineas.append("  (ninguno)")

    lineas.append("Ausente / vacío:")
    if ausentes:
        for a in ausentes:
            lineas.append(f"  · {a}")
    else:
        lineas.append("  (ninguno)")

    lineas.append("Rechazado:")
    if rechazados:
        for r in rechazados:
            lineas.append(f"  ✗ {r.get('ruta', '?')} → {r.get('razon', '?')}")
    else:
        lineas.append("  (ninguno)")
    lineas.append("")

    # ------------------------------------------------------------------
    # Resumen final
    # ------------------------------------------------------------------
    lineas += [
        "=" * 80,
        "RESUMEN",
        "=" * 80,
        f"  Engine              : {estado}",
        f"  Axiomas             : {'coherente' if coherente else 'incoherente'}",
        f"  Contenedores        : {total}",
        f"  Roles vacíos        : {len(vacios)}",
        f"  Módulos rechazados  : {len(rechazados)}",
        f"  Datos faltantes     : {len(faltas)}",
        "  Este reporte no recalculó ninguna fórmula ni barrido.",
        "  Se actualiza solo con lo que el Engine entregue en cada corrida.",
        "=" * 80,
    ]

    return "\n".join(lineas)


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
                invocador_id="omega_report",
                strict=False,
            )
        except ArranqueError as e:
            datos["estado_engine"] = "RECHAZADO"
            datos["errores_arranque"] = [str(e)]
            return datos

        datos["estado_engine"] = eng.estado
        datos["errores_arranque"] = list(eng.errores_arranque or [])
        datos["informe_axiomas"] = eng.informe_axiomas or {}
        datos["informe_mecanica"] = eng.informe_mecanica or {}
        datos["registro_modulos"] = eng.registro.resumen()

        try:
            datos["constantes"] = {k: str(v) for k, v in eng.get_constantes().items()}
        except Exception:
            pass

        for cont in eng.registro.por_rol.get("FO", []):
            fn = cont.fn("verificar") or cont.fn("barrer")
            if callable(fn):
                try:
                    datos["informe_formulas"] = fn()
                except Exception:
                    pass
                break

    except Exception as e:
        datos["estado_engine"] = "RECHAZADO"
        datos["errores_arranque"] = [f"{type(e).__name__}: {e}"]

    return datos


def main() -> None:
    datos = cargar_datos_desde_engine()
    texto = presentar(datos)
    print(texto)

    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out = DIAGNOSTICS_DIR / "omega_report_data.json"
    out.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nJSON: {out}")

    faltas = validar_entrada(datos)
    if STRICT and (datos.get("estado_engine") != "OPERATIVO" or faltas):
        sys.exit(1)


if __name__ == "__main__":
    main()
