# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- tests/test_diagnostico_conexiones_escala.py

Test de diagnóstico (no de valuación).

Pregunta al repositorio:
  ¿Por qué no aparece Tru por sujeto / átomo / frase / conversación / repo?

Recorre la cadena de conexiones y REPORTA fallas de enlace.
No inventa C/L/K/Tru. No deposita. Solo inspecciona.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest


IDS_ESPERADOS = (
    "tru_atomo",
    "tru_frase",
    "tru_sujeto",
    "tru_conversacion",
    "tru_repositorio",
)

SKILLS_CE_ESPERADOS = (
    "ce_mandato_catalogo",
    "ce_mandato_escala_tt",
    "ce_mandato_sujetos",
    "ce_mandato_aplicar_escala",
)


def _falla(informe: List[str], msg: str) -> None:
    informe.append("FALLO: " + msg)


def _ok(informe: List[str], msg: str) -> None:
    informe.append("OK:    " + msg)


def _aviso(informe: List[str], msg: str) -> None:
    informe.append("AVISO: " + msg)


def test_diagnostico_conexiones_escala_sujeto_frase_conversacion():
    """
    Identifica dónde no hay conexión para calcular
    sujeto / átomo / frase / conversación / repositorio.
    """
    informe: List[str] = []
    fallos: List[str] = []

    root = Path(__file__).resolve().parents[1]
    modules = root / "modules"

    # ------------------------------------------------------------------
    # 1) Archivo mapa de ids bajo calculator
    # ------------------------------------------------------------------
    escalas_path = modules / "calculator" / "escalas_ids.py"
    if not escalas_path.is_file():
        _falla(informe, "no existe modules/calculator/escalas_ids.py")
        fallos.append("escalas_ids_ausente")
    else:
        _ok(informe, "existe escalas_ids.py")

    # ------------------------------------------------------------------
    # 2) CA puede importar calcular y leer ids
    # ------------------------------------------------------------------
    try:
        from modules.calculator import calcular, barrer  # noqa: F401
        _ok(informe, "modules.calculator exporta calcular")
    except Exception as e:
        _falla(
            informe,
            "no se puede importar calcular desde modules.calculator: {0}".format(e),
        )
        fallos.append("ca_import_calcular")
        # sin CA el resto del diagnóstico de cálculo no aplica
        _emitir(informe, fallos)
        pytest.fail("\n".join(informe))

    leer_ids = None
    try:
        from modules.calculator import leer_ids_escala
        leer_ids = leer_ids_escala
        _ok(informe, "CA exporta leer_ids_escala")
    except Exception:
        _falla(informe, "CA no exporta leer_ids_escala (sin capacidad de leer ids)")
        fallos.append("ca_sin_leer_ids")

    ids_ca: List[str] = []
    if callable(leer_ids):
        try:
            inv = leer_ids()
            ids_ca = list(inv.get("ids") or [])
            _ok(
                informe,
                "CA leer_ids_escala → n={0} origenes={1}".format(
                    inv.get("n"), inv.get("origenes")
                ),
            )
        except Exception as e:
            _falla(informe, "leer_ids_escala() lanzó: {0}".format(e))
            fallos.append("ca_leer_ids_error")

    for eid in IDS_ESPERADOS:
        if eid in ids_ca:
            _ok(informe, "id visible en CA: {0}".format(eid))
        else:
            _falla(informe, "id NO visible en CA: {0}".format(eid))
            fallos.append("ca_falta_id_{0}".format(eid))

    # ------------------------------------------------------------------
    # 3) Catálogo TT
    # ------------------------------------------------------------------
    try:
        import modules.tru_totales as TT
        _ok(informe, "modules.tru_totales importable")
        ids_tt: List[str] = []
        for nombre in ("ids", "categorias"):
            fn = getattr(TT, nombre, None)
            if not callable(fn):
                continue
            out = fn()
            if isinstance(out, list):
                for item in out:
                    if isinstance(item, str):
                        ids_tt.append(item.strip().lower())
                    elif isinstance(item, dict) and item.get("id"):
                        ids_tt.append(str(item["id"]).strip().lower())
        if ids_tt:
            _ok(informe, "TT expone ids: {0}".format(sorted(set(ids_tt))))
        else:
            _aviso(informe, "TT cargó pero no expuso lista de ids")
            fallos.append("tt_sin_ids")
        for eid in IDS_ESPERADOS:
            if eid not in [x.lower() for x in ids_tt] and eid not in ids_ca:
                _aviso(
                    informe,
                    "id {0} no visto en TT (puede vivir solo en escalas_ids)".format(
                        eid
                    ),
                )
    except Exception as e:
        _falla(informe, "tru_totales no importable: {0}".format(e))
        fallos.append("tt_import")

    # ------------------------------------------------------------------
    # 4) Skills CE (mandatos Engine)
    # ------------------------------------------------------------------
    try:
        import modules.capacidades_engine as CE
        _ok(informe, "modules.capacidades_engine importable")
        ids_ce: List[str] = []
        for nombre in ("ids", "skills", "capacidades"):
            fn = getattr(CE, nombre, None)
            if not callable(fn):
                continue
            out = fn()
            if isinstance(out, list):
                for item in out:
                    if isinstance(item, str):
                        ids_ce.append(item.strip().lower())
                    elif isinstance(item, dict) and item.get("id"):
                        ids_ce.append(str(item["id"]).strip().lower())
        if not ids_ce and hasattr(CE, "barrer"):
            b = CE.barrer()
            ids_ce = [str(x).lower() for x in (b.get("ids") or [])]
        _ok(informe, "CE skills/ids: {0}".format(ids_ce or "(ninguno)"))
        for sid in SKILLS_CE_ESPERADOS:
            if sid in ids_ce:
                _ok(informe, "skill CE presente: {0}".format(sid))
            else:
                _falla(informe, "skill CE AUSENTE: {0}".format(sid))
                fallos.append("ce_falta_{0}".format(sid))
    except Exception as e:
        _falla(informe, "capacidades_engine no importable: {0}".format(e))
        fallos.append("ce_import")

    # ------------------------------------------------------------------
    # 5) Engine arranca y ve roles CE / CA / TT
    # ------------------------------------------------------------------
    eng = None
    try:
        from core.engine import Engine

        eng = Engine(Path("modules"), invocador_id="diag_conexiones", strict=True)
        _ok(informe, "Engine arrancó estado={0}".format(getattr(eng, "estado", "?")))
        censar = eng.censar() if hasattr(eng, "censar") else {}
        roles = censar.get("roles") or {}
        for rol, nombre in (("CA", "calculator"), ("TT", "tru_totales"), ("CE", "capacidades_engine")):
            mods = list(roles.get(rol) or [])
            if mods:
                _ok(informe, "rol {0} cargado: {1}".format(rol, mods))
            else:
                _falla(informe, "rol {0} NO cargado (falta {1})".format(rol, nombre))
                fallos.append("rol_ausente_{0}".format(rol))
    except Exception as e:
        _falla(informe, "Engine no arrancó: {0}".format(e))
        fallos.append("engine_arranque")

    # ------------------------------------------------------------------
    # 6) CA calcular reconoce id (no exige Tru; solo conexión de id)
    # ------------------------------------------------------------------
    try:
        from modules.calculator import calcular

        for eid in ("tru_sujeto", "tru_frase", "tru_conversacion"):
            out = calcular({
                "mensaje": "Carlos dice una cosa. Luis dice otra.",
                "contexto": "conversacion de prueba diagnostico",
                "metodo": "operacional",
                "escala_id": eid,
            })
            esc = out.get("escala") if isinstance(out, dict) else None
            if isinstance(esc, dict) and esc.get("escala_id") == eid:
                _ok(
                    informe,
                    "calcular(escala_id={0}) anota escala conocido={1}".format(
                        eid, esc.get("conocido")
                    ),
                )
                if not esc.get("conocido"):
                    fallos.append("calcular_id_desconocido_{0}".format(eid))
            else:
                _falla(
                    informe,
                    "calcular(escala_id={0}) NO anotó escala en salida".format(eid),
                )
                fallos.append("calcular_sin_escala_{0}".format(eid))
            # factores presentes (conexión de oficio CA)
            if not isinstance(out, dict) or not all(k in out for k in ("C", "L", "K")):
                _falla(informe, "calcular({0}) no devolvió C/L/K".format(eid))
                fallos.append("calcular_sin_clk_{0}".format(eid))
            else:
                _ok(informe, "calcular({0}) devolvió C/L/K (oficio CA intacto)".format(eid))
    except Exception as e:
        _falla(informe, "calcular con escala_id falló: {0}".format(e))
        fallos.append("calcular_escala_error")

    # ------------------------------------------------------------------
    # 7) Evidencia / depósito de sujetos (por qué Omega N=0)
    # ------------------------------------------------------------------
    eval_path = root / "diagnostics" / "evaluaciones.json"
    if not eval_path.is_file():
        _aviso(informe, "no hay diagnostics/evaluaciones.json aún")
        fallos.append("sin_evaluaciones_json")
    else:
        import json

        try:
            doc = json.loads(eval_path.read_text(encoding="utf-8"))
            resultados = doc.get("resultados") or doc.get("resultados_evaluacion") or []
            if not isinstance(resultados, list):
                resultados = []
            n_suj = 0
            for r in resultados:
                if not isinstance(r, dict):
                    continue
                body = r.get("resultado") or r
                if isinstance(body, dict):
                    suj = body.get("sujetos") or body.get("por_sujeto")
                    if suj:
                        n_suj += 1
            if n_suj:
                _ok(informe, "evaluaciones.json tiene {0} ciclo(s) con sujetos".format(n_suj))
            else:
                _falla(
                    informe,
                    "evaluaciones.json sin resultado.sujetos / por_sujeto "
                    "(por eso Omega N=0)",
                )
                fallos.append("deposito_sujetos_ausente")
        except Exception as e:
            _falla(informe, "no se pudo leer evaluaciones.json: {0}".format(e))
            fallos.append("evaluaciones_json_error")

    # ------------------------------------------------------------------
    # 8) Resumen de cadena
    # ------------------------------------------------------------------
    informe.append("")
    informe.append("===== CADENA ESPERADA =====")
    informe.append("ids (escalas_ids/TT) → CA lee ids → calcular C/L/K")
    informe.append("→ CE mandato → Engine deposita sujetos/Tru → Omega lee")
    informe.append("===== FIN DIAGNÓSTICO =====")

    _emitir(informe, fallos)

    # El test FALLA si hay fallos de conexión (para que el CI los muestre)
    if fallos:
        pytest.fail(
            "Conexiones rotas ({0}):\n".format(len(fallos))
            + "\n".join(informe)
        )


def _emitir(informe: List[str], fallos: List[str]) -> None:
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO CONEXIONES ESCALA / SUJETO / FRASE / CONVERSACIÓN")
    print("=" * 60)
    for line in informe:
        print(line)
    print("-" * 60)
    print("total_fallos_conexion:", len(fallos))
    if fallos:
        print("ids_fallo:", ", ".join(fallos))
    print("=" * 60 + "\n")
