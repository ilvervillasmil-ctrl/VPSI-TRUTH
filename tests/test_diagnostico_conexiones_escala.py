# -*- coding: utf-8 -*-
"""
VPSI-TRUTH --- tests/test_diagnostico_conexiones_escala.py

Test de diagnostico (no de valuacion).
Recorre la cadena de conexiones y REPORTA fallas de enlace.
Seccion 7 EJECUTA un ciclo real para verificar deposito de sujetos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

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
    informe: List[str] = []
    fallos: List[str] = []

    root = Path(__file__).resolve().parents[1]
    modules = root / "modules"

    # 1) escalas_ids
    escalas_path = modules / "calculator" / "escalas_ids.py"
    if not escalas_path.is_file():
        _falla(informe, "no existe modules/calculator/escalas_ids.py")
        fallos.append("escalas_ids_ausente")
    else:
        _ok(informe, "existe escalas_ids.py")

    # 2) CA
    try:
        from modules.calculator import calcular  # noqa: F401
        _ok(informe, "modules.calculator exporta calcular")
    except Exception as e:
        _falla(informe, "no se puede importar calcular: {0}".format(e))
        fallos.append("ca_import_calcular")
        _emitir(informe, fallos)
        pytest.fail("\n".join(informe))

    leer_ids = None
    try:
        from modules.calculator import leer_ids_escala
        leer_ids = leer_ids_escala
        _ok(informe, "CA exporta leer_ids_escala")
    except Exception:
        try:
            import modules.calculator as CA
            leer_ids = getattr(CA, "leer_ids_escala", None)
            if callable(leer_ids):
                _ok(informe, "CA exporta leer_ids_escala")
            else:
                _falla(informe, "CA no exporta leer_ids_escala")
                fallos.append("ca_sin_leer_ids")
        except Exception as e:
            _falla(informe, "CA leer_ids_escala: {0}".format(e))
            fallos.append("ca_sin_leer_ids")

    if callable(leer_ids):
        try:
            out = leer_ids()
            if isinstance(out, dict):
                ids = list(out.get("ids") or out.keys())
                origenes = out.get("origenes") or []
            elif isinstance(out, (list, tuple, set)):
                ids = list(out)
                origenes = []
            else:
                ids = []
                origenes = []
            _ok(
                informe,
                "CA leer_ids_escala â n={0} origenes={1}".format(
                    len(ids), origenes
                ),
            )
            for eid in IDS_ESPERADOS:
                if eid in ids or eid in [str(x) for x in ids]:
                    _ok(informe, "id visible en CA: {0}".format(eid))
                else:
                    _falla(informe, "id no visible en CA: {0}".format(eid))
                    fallos.append("id_ca_{0}".format(eid))
        except Exception as e:
            _falla(informe, "leer_ids_escala fallo: {0}".format(e))
            fallos.append("leer_ids_error")

    # 3) TT
    try:
        import modules.tru_totales as TT
        _ok(informe, "modules.tru_totales importable")
        ids_tt = []
        if hasattr(TT, "ids") and callable(TT.ids):
            ids_tt = list(TT.ids())
        elif hasattr(TT, "IDS"):
            ids_tt = list(TT.IDS)
        _ok(informe, "TT expone ids: {0}".format(sorted(ids_tt)))
    except Exception as e:
        _falla(informe, "TT no importable: {0}".format(e))
        fallos.append("tt_import")

    # 4) CE
    try:
        import modules.capacidades_engine as CE
        _ok(informe, "modules.capacidades_engine importable")
        ids_ce = []
        if hasattr(CE, "ids") and callable(CE.ids):
            ids_ce = list(CE.ids())
        if hasattr(CE, "skills") and callable(CE.skills):
            sk = CE.skills()
            for s in sk or []:
                if isinstance(s, dict) and s.get("id"):
                    ids_ce.append(str(s["id"]))
        _ok(informe, "CE skills/ids: {0}".format(ids_ce))
        for sid in SKILLS_CE_ESPERADOS:
            if sid in [str(x).lower() for x in ids_ce]:
                _ok(informe, "skill CE presente: {0}".format(sid))
            else:
                _falla(informe, "skill CE ausente: {0}".format(sid))
                fallos.append("ce_skill_{0}".format(sid))
    except Exception as e:
        _falla(informe, "capacidades_engine no importable: {0}".format(e))
        fallos.append("ce_import")

    # 5) Engine arranque
    eng = None
    try:
        from core.engine import Engine
        eng = Engine(Path("modules"), invocador_id="diag_conexiones", strict=True)
        _ok(informe, "Engine arranco estado={0}".format(getattr(eng, "estado", "?")))
        for rol, nombre in (
            ("CA", "calculator"),
            ("TT", "tru_totales"),
            ("CE", "capacidades_engine"),
        ):
            lista = (eng.registro.por_rol.get(rol) or [])
            nombres = [c.nombre for c in lista]
            if nombre in nombres or lista:
                _ok(informe, "rol {0} cargado: {1}".format(rol, nombres or [nombre]))
            else:
                _falla(informe, "rol {0} no cargado".format(rol))
                fallos.append("rol_{0}".format(rol))
    except Exception as e:
        _falla(informe, "Engine no arranco: {0}".format(e))
        fallos.append("engine_arranque")

    # 6) CA calcular por escala
    try:
        from modules.calculator import calcular as _calc
        for eid in ("tru_sujeto", "tru_frase", "tru_conversacion"):
            r = _calc({"escala_id": eid, "mensaje": "probe", "contexto": "probe O"})
            conocido = False
            if isinstance(r, dict):
                conocido = bool(
                    r.get("escala_conocido")
                    or r.get("escala_id") == eid
                    or r.get("categoria_tru") == eid
                    or (r.get("C") is not None)
                )
            if conocido:
                _ok(informe, "calcular(escala_id={0}) anota escala conocido=True".format(eid))
            else:
                _aviso(informe, "calcular({0}) sin marca de escala".format(eid))
            if isinstance(r, dict) and r.get("C") is not None:
                _ok(informe, "calcular({0}) devolvio C/L/K (oficio CA intacto)".format(eid))
            else:
                _aviso(informe, "calcular({0}) sin C/L/K en probe".format(eid))
    except Exception as e:
        _falla(informe, "calcular por escala fallo: {0}".format(e))
        fallos.append("ca_calcular_escala")

    # 7) CICLO REAL: Engine.evaluar con hablantes â deposito sujetos
    try:
        from core.engine import Engine as _Eng
        eng2 = _Eng(Path("modules"), invocador_id="diag_deposito", strict=True)
        pet = {
            "mensaje": (
                "Carlos: Yo no tome el dinero.\n"
                "Maria: Yo vi a Carlos cerca de la caja."
            ),
            "contexto": (
                "Evaluar coherencia de cada hablante bajo el mismo O "
                "de conversacion sobre el dinero."
            ),
            "O_context": (
                "Evaluar coherencia de cada hablante bajo el mismo O "
                "de conversacion sobre el dinero."
            ),
            "escala_id": "tru_sujeto",
            "categoria_tru": "tru_sujeto",
        }
        res = eng2.evaluar(pet)
        body = res if isinstance(res, dict) else {}

        sujetos = body.get("sujetos")
        n_suj = body.get("n_sujetos")
        tiene_clave = "sujetos" in body
        tiene_lista = isinstance(sujetos, list)
        tiene_n = n_suj is not None

        if tiene_clave and tiene_lista:
            _ok(
                informe,
                "Engine deposita sujetos (n={0}, n_sujetos={1})".format(
                    len(sujetos), n_suj
                ),
            )
            if len(sujetos) < 1:
                _falla(informe, "sujetos depositado pero vacio con material de 2 hablantes")
                fallos.append("deposito_sujetos_vacio")
        else:
            _falla(
                informe,
                "Engine.evaluar sin clave sujetos "
                "(tiene_clave={0}, tipo={1})".format(
                    tiene_clave, type(sujetos).__name__
                ),
            )
            fallos.append("deposito_sujetos_ausente")

        # disco
        eval_path = root / "diagnostics" / "evaluaciones.json"
        if not eval_path.is_file():
            _falla(informe, "no se escribio diagnostics/evaluaciones.json")
            fallos.append("sin_evaluaciones_json")
        else:
            import json
            doc = json.loads(eval_path.read_text(encoding="utf-8"))
            resultados = doc.get("resultados") or doc.get("resultados_evaluacion") or []
            if not isinstance(resultados, list):
                resultados = []
            n_dep = 0
            for r in resultados:
                if not isinstance(r, dict):
                    continue
                b = r.get("resultado") or r
                if not isinstance(b, dict):
                    continue
                # presencia de clave (lista puede ir llena)
                if "sujetos" in b and isinstance(b.get("sujetos"), list):
                    if len(b["sujetos"]) > 0 or b.get("n_sujetos"):
                        n_dep += 1
                    elif len(b["sujetos"]) == 0 and b.get("n_sujetos") == 0:
                        # ciclo sin hablantes â no cuenta como deposito util
                        pass
                    else:
                        n_dep += 1
            if n_dep:
                _ok(
                    informe,
                    "evaluaciones.json tiene {0} ciclo(s) con sujetos".format(n_dep),
                )
            else:
                # si el body en memoria si tiene, el fallo es de persistencia
                if tiene_lista and len(sujetos or []) > 0:
                    _falla(
                        informe,
                        "memoria tiene sujetos pero evaluaciones.json no los refleja",
                    )
                    fallos.append("persistencia_sujetos")
                else:
                    _falla(
                        informe,
                        "evaluaciones.json sin resultado.sujetos "
                        "(por eso Omega N=0)",
                    )
                    fallos.append("deposito_sujetos_ausente")
    except Exception as e:
        _falla(informe, "ciclo deposito fallo: {0}".format(e))
        fallos.append("deposito_ciclo_error")

    # 8) cadena
    informe.append("")
    informe.append("===== CADENA ESPERADA =====")
    informe.append("ids (escalas_ids/TT) â CA lee ids â calcular C/L/K")
    informe.append("â CE mandato â Engine deposita sujetos/Tru â Omega lee")
    informe.append("===== FIN DIAGNOSTICO =====")

    _emitir(informe, fallos)
    if fallos:
        pytest.fail(
            "Conexiones rotas ({0}):\n".format(len(fallos))
            + "\n".join(informe)
        )


def _emitir(informe: List[str], fallos: List[str]) -> None:
    print("\n" + "=" * 60)
    print("DIAGNOSTICO CONEXIONES ESCALA / SUJETO / FRASE / CONVERSACION")
    print("=" * 60)
    for line in informe:
        print(line)
    print("-" * 60)
    print("total_fallos_conexion:", len(fallos))
    if fallos:
        print("ids_fallo:", ", ".join(fallos))
    print("=" * 60 + "\n")
