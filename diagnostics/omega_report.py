#!/usr/bin/env python3
"""
OMEGA REPORT - VPSI-TRUTH (Versión 9.4)
======================================

Rol: presentador objetivo.

Este script NO calcula.
NO vuelve a barrer axiomas.
NO vuelve a ejecutar tru_ri / tru_total.
NO inventa sondas ni puntos de prueba.

Solo recibe los informes reales que el Engine ya obtuvo de los módulos
y los presenta de forma estructurada.

Flujo correcto:
    Módulos → Engine (recolecta) → Omega Report (presenta)

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

# =============================================================================
# RUTAS
# =============================================================================
CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# =============================================================================
# ESTADOS
# =============================================================================
OK = "OK"
FALLO = "FALLO"
PENDIENTE = "PENDIENTE"
STRICT = os.getenv("OMEGA_STRICT", "0") == "1"


# =============================================================================
# LO QUE EL REPORTE EXIGE RECIBIR (datos reales del sistema)
# =============================================================================
CAMPOS_OBLIGATORIOS = (
    "estado_engine",
    "constantes",
    "informe_axiomas",
)

CAMPOS_RECOMENDADOS = (
    "informe_formulas",
    "informe_mecanica",
    "resultados_evaluacion",
    "errores_arranque",
    "registro_modulos",
    "tests",
)


def validar_entrada(datos: Dict[str, Any]) -> List[str]:
    """Solo comprueba presencia y forma. No recalcula."""
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
        if not isinstance(ia, dict):
            faltas.append("informe_axiomas debe ser dict")
        elif "coherente" not in ia:
            faltas.append("informe_axiomas sin clave 'coherente'")

    if "estado_engine" in datos:
        if datos["estado_engine"] not in ("OPERATIVO", "RECHAZADO", "NO_INICIADO"):
            faltas.append(f"estado_engine inválido: {datos['estado_engine']}")

    return faltas


# =============================================================================
# PRESENTACIÓN
# =============================================================================
def _linea(marca: str, titulo: str, detalle: List[str] | None = None) -> str:
    out = [f"[{marca}] {titulo}"]
    if detalle:
        for d in detalle:
            if d:
                out.append(f"    {d}")
    return "\n".join(out)


def presentar(datos: Dict[str, Any]) -> str:
    """
    Genera el texto del Omega Report a partir de datos reales.
    No ejecuta lógica de negocio.
    """
    faltas = validar_entrada(datos)
    lineas: List[str] = []

    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sha = os.getenv("GITHUB_SHA", "local")[:12]

    lineas.append("=" * 80)
    lineas.append("OMEGA REPORT - VPSI-TRUTH (Versión 9.4)")
    lineas.append(f"Generado: {ahora}    Commit: {sha}")
    lineas.append("Modo: SOLO PRESENTACIÓN (no recalcula)")
    lineas.append("=" * 80)
    lineas.append("")

    if faltas:
        lineas.append(_linea(FALLO, "Entrada incompleta", faltas))
        lineas.append("")
        lineas.append("El reporte no puede afirmar coherencia del sistema.")
        lineas.append("Faltan datos reales producidos por el Engine / módulos.")
        return "\n".join(lineas)

    # --- Estado del Engine ---
    estado = datos["estado_engine"]
    marca_eng = OK if estado == "OPERATIVO" else FALLO
    lineas.append(_linea(marca_eng, "Estado del Engine", [f"estado = {estado}"]))
    if datos.get("errores_arranque"):
        for e in datos["errores_arranque"]:
            lineas.append(f"    - {e}")
    lineas.append("")

    # --- Constantes (solo lectura) ---
    const = datos["constantes"]
    lineas.append(_linea(OK, "Constantes ALPHA / BETA", [
        f"ALPHA = {const.get('ALPHA')}",
        f"BETA  = {const.get('BETA')}",
        "Fuente: módulo CT (no recalculado aquí)",
    ]))
    lineas.append("")

    # --- Axiomas (solo lectura del informe real) ---
    ia = datos["informe_axiomas"]
    coherente = ia.get("coherente", False)
    marca_ax = OK if coherente else FALLO
    detalle_ax = [
        f"coherente     = {coherente}",
        f"declaraciones = {ia.get('declaraciones', '?')}",
        f"choques       = {len(ia.get('choques', []))}",
        f"errores       = {len(ia.get('errores', []))}",
        "Fuente: modules.axiomas.barrer() vía Engine",
    ]
    lineas.append(_linea(marca_ax, "Barrido axiomático", detalle_ax))
    lineas.append("")

    # --- Fórmulas (si el Engine las entregó) ---
    if "informe_formulas" in datos and datos["informe_formulas"]:
        fo = datos["informe_formulas"]
        marca_fo = OK if fo.get("coherente", False) else FALLO
        lineas.append(_linea(marca_fo, "Fórmulas", [
            f"coherente = {fo.get('coherente')}",
            f"faltas    = {fo.get('faltas', [])}",
            "Fuente: modules.formulas.barrer() vía Engine",
        ]))
    else:
        lineas.append(_linea(PENDIENTE, "Fórmulas", [
            "informe_formulas no entregado por el Engine"
        ]))
    lineas.append("")

    # --- Mecánica (si existe) ---
    if "informe_mecanica" in datos and datos["informe_mecanica"]:
        mc = datos["informe_mecanica"]
        marca_mc = OK if mc.get("coherente", False) else FALLO
        lineas.append(_linea(marca_mc, "Mecánica", [
            f"coherente = {mc.get('coherente')}",
            f"choques   = {mc.get('choques', [])}",
            "Fuente: modules.correlacion_mecanica.barrer() vía Engine",
        ]))
    else:
        lineas.append(_linea(PENDIENTE, "Mecánica", [
            "informe_mecanica no entregado por el Engine"
        ]))
    lineas.append("")

    # --- Evaluaciones (si el Engine las corrió) ---
    evals = datos.get("resultados_evaluacion") or []
    if evals:
        lineas.append(_linea(OK, "Camino de evaluación", [
            f"evaluaciones recibidas: {len(evals)}",
            "Fuente: engine.evaluar() (resultados ya calculados)",
        ]))
        for i, r in enumerate(evals[:5], 1):
            lineas.append(
                f"    [{i}] estado={r.get('estado')}  "
                f"Tru_Ri={r.get('tru_ri')}  Tru_total={r.get('tru_total')}"
            )
    else:
        lineas.append(_linea(PENDIENTE, "Camino de evaluación", [
            "Ningún resultado de evaluar() fue entregado"
        ]))
    lineas.append("")

    # --- Módulos registrados ---
    if "registro_modulos" in datos and datos["registro_modulos"]:
        reg = datos["registro_modulos"]
        lineas.append(_linea(OK, "Módulos y roles", [
            f"total contenedores = {reg.get('total', '?')}",
            f"roles              = {reg.get('roles', {})}",
            f"roles vacíos       = {reg.get('roles_vacios', [])}",
            f"rechazados         = {len(reg.get('rechazados', []))}",
            "Fuente: Engine.registro",
        ]))
    else:
        lineas.append(_linea(PENDIENTE, "Módulos y roles", [
            "registro_modulos no entregado"
        ]))
    lineas.append("")

    # --- Tests (si se entregaron) ---
    if "tests" in datos and datos["tests"]:
        t = datos["tests"]
        marca_t = OK if t.get("fallidos", 1) == 0 else FALLO
        lineas.append(_linea(marca_t, "Tests", [
            f"total={t.get('total')}  pasados={t.get('pasados')}  "
            f"fallidos={t.get('fallidos')}  tasa={t.get('tasa')}%",
            "Fuente: junit xml / pytest (ya ejecutado)",
        ]))
    else:
        lineas.append(_linea(PENDIENTE, "Tests", [
            "resultados de tests no entregados"
        ]))
    lineas.append("")

    # --- Resumen ---
    lineas.append("=" * 80)
    lineas.append("RESUMEN")
    lineas.append("=" * 80)
    lineas.append(f"  Engine        : {estado}")
    lineas.append(f"  Axiomas       : {'coherente' if coherente else 'incoherente'}")
    lineas.append(f"  Datos faltantes: {len(faltas)}")
    lineas.append("  Este reporte no recalculó ninguna fórmula ni barrido.")
    lineas.append("=" * 80)

    return "\n".join(lineas)


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
def cargar_datos_desde_engine() -> Dict[str, Any]:
    """
    Pide al Engine los informes reales y arma el paquete de datos.
    Si el Engine no arranca, devuelve lo mínimo para que el reporte lo diga.
    """
    datos: Dict[str, Any] = {
        "estado_engine": "NO_INICIADO",
        "constantes": {},
        "informe_axiomas": {},
        "errores_arranque": [],
    }

    try:
        from core.engine import Engine, ArranqueError
        from pathlib import Path as P

        try:
            eng = Engine(
                raiz_modulos=str(REPO_ROOT / "modules"),
                invocador_id="omega_report",
                strict=False,  # no lanzar; solo reportar
            )
        except ArranqueError as e:
            datos["estado_engine"] = "RECHAZADO"
            datos["errores_arranque"] = [str(e)]
            return datos

        datos["estado_engine"] = eng.estado
        datos["errores_arranque"] = eng.errores_arranque
        datos["informe_axiomas"] = eng.informe_axiomas or {}
        datos["informe_mecanica"] = eng.informe_mecanica or {}
        datos["registro_modulos"] = eng.registro.resumen()

        try:
            datos["constantes"] = {
                k: str(v) for k, v in eng.get_constantes().items()
            }
        except Exception:
            datos["constantes"] = {}

        # Intentar informe de fórmulas si el módulo lo expone
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

    # Guardar JSON objetivo (solo lo recibido)
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    out = DIAGNOSTICS_DIR / "omega_report_data.json"
    out.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nJSON: {out}")

    # En modo STRICT solo falla si el Engine no está operativo
    # o si faltan datos obligatorios.
    faltas = validar_entrada(datos)
    if STRICT and (datos.get("estado_engine") != "OPERATIVO" or faltas):
        sys.exit(1)


if __name__ == "__main__":
    main()
