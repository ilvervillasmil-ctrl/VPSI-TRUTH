# -*- coding: utf-8 -*-
"""
tests/test_trazabilidad_pipeline_completo.py

Un solo Test forense.
No celebra lo que existe: busca dónde se rompe el contrato
y nombra el primer corte + la propagación.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


def _mods_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "modules"


def test_trazabilidad_pipeline_completo() -> None:
    from core.engine import Engine, ROLES, OBLIGATORIOS

    cortes: List[str] = []          # fallas reales
    evidencias: List[str] = []      # detalle del corte
    cadena: List[str] = []          # log ordenado del recorrido

    def corte(lugar: str, detalle: str) -> None:
        msg = "[{0}] {1}".format(lugar, detalle)
        cortes.append(msg)
        evidencias.append(msg)
        cadena.append("CORTE  " + msg)

    def paso(msg: str) -> None:
        cadena.append("paso   " + msg)

    def esperado_vs_real(
        lugar: str,
        campo: str,
        esperado: str,
        real: Any,
    ) -> None:
        if real is None or real == "" or real == "UNDEFINED":
            corte(
                lugar,
                "campo '{0}' esperado ({1}) ausente; real={2!r}".format(
                    campo, esperado, real
                ),
            )
        else:
            paso("{0}: {1}={2!r}".format(lugar, campo, real))

    # ------------------------------------------------------------------
    # 0) Engine
    # ------------------------------------------------------------------
    raiz = _mods_dir()
    try:
        eng = Engine(
            raiz_modulos=str(raiz),
            invocador_id="test_trazabilidad",
        )
    except Exception as e:
        pytest.fail(
            "Engine no arranco: {0}: {1}".format(type(e).__name__, e)
        )
        return

    if eng.estado != "OPERATIVO":
        corte(
            "ARRANQUE",
            "estado={0} errores={1}".format(
                eng.estado, eng.errores_arranque
            ),
        )

    # ------------------------------------------------------------------
    # 1) Cobertura: todo ROL debe existir; obligatorio no vacio
    # ------------------------------------------------------------------
    por_rol = eng.registro.por_rol
    for rol in ROLES:
        lista = por_rol.get(rol) or []
        if not lista and rol in OBLIGATORIOS:
            corte("COBERTURA", "rol obligatorio vacio: {0}".format(rol))
        elif not lista:
            corte(
                "COBERTURA",
                "rol declarado en ROLES sin contenedor: {0}".format(rol),
            )

    for cont in eng.registro.contenedores.values():
        for cap in (cont.capacidades or {}).keys():
            if not callable(cont.fn(str(cap))) and not callable(
                cont.fn_oficio(str(cap))
            ):
                corte(
                    "CONTRATO/{0}".format(cont.nombre),
                    "capacidad '{0}' no resoluble".format(cap),
                )

    # ------------------------------------------------------------------
    # 2) Ciclo forense A — auditoria (donde Omega ve PARCIAL sin C/L/K)
    # ------------------------------------------------------------------
    pet_a: Dict[str, Any] = {
        "contexto": (
            "Auditoría estructural del repositorio VPSI-TRUTH: "
            "coherencia axiomática, contratos, mecánica y correlación."
        ),
        "O_context": (
            "Auditoría estructural del repositorio VPSI-TRUTH: "
            "coherencia axiomática, contratos, mecánica y correlación."
        ),
        "mensaje": "Auditar el repositorio VPSI-TRUTH y sus contratos.",
        "pedir_anuncio": True,
    }

    # 2a) CE
    ce = eng._ce_ids_skills() if hasattr(eng, "_ce_ids_skills") else {}
    if not ce.get("ids"):
        corte("CE", "sin ids/skills; mandatos no aplicables")
    else:
        paso("CE ids={0}".format(ce.get("ids")))

    mand_a = (
        eng._mandatos_aplicables(pet_a, ce)
        if hasattr(eng, "_mandatos_aplicables")
        else []
    )
    paso("CE mandatos A={0}".format(mand_a))

    # 2b) CX directo (oficio)
    cx_cont = eng.registro.primero("CX")
    if cx_cont is None:
        corte("CX", "rol CX no cargado")
        cx_out: Dict[str, Any] = {}
    else:
        cx_out = eng._marco_cx(pet_a) if hasattr(eng, "_marco_cx") else None
        if not isinstance(cx_out, dict):
            corte("CX", "evaluar/resolver no devolvio dict; real={0!r}".format(cx_out))
            cx_out = {}
        else:
            paso(
                "CX permite_k={0} coherente={1}".format(
                    cx_out.get("permite_k"), cx_out.get("coherente")
                )
            )
            if cx_out.get("permite_k") is not True:
                corte(
                    "CX",
                    "permite_k={0}; O no reclamable → CA/FO no deben inventar K".format(
                        cx_out.get("permite_k")
                    ),
                )

    # 2c) CA directo (oficio calcular) — aqui suele estar el agujero
    ca_cont = eng.registro.primero("CA")
    calc_a: Any = None
    if ca_cont is None:
        corte("CA", "rol CA no cargado")
    elif not ca_cont.tiene("calcular"):
        corte("CA", "contrato sin capacidad 'calcular'")
    else:
        calc_a = eng._ejecutar_capacidad(ca_cont, "calcular", pet_a)
        if calc_a is None or (
            hasattr(eng, "fallos") and False
        ):
            pass
        from core.engine import es_undefined

        if es_undefined(calc_a):
            corte(
                "CA",
                "calcular() devolvio UNDEFINED (oficio fallo o no resolvio)",
            )
        elif not isinstance(calc_a, dict):
            corte(
                "CA",
                "calcular() tipo={0} valor={1!r}".format(
                    type(calc_a).__name__, calc_a
                ),
            )
        else:
            paso("CA calcular keys={0}".format(sorted(calc_a.keys())))
            for f in ("C", "L", "K"):
                if f not in calc_a or calc_a.get(f) is None:
                    corte(
                        "CA",
                        "calcular() no entrego '{0}'; keys={1}".format(
                            f, sorted(calc_a.keys())
                        ),
                    )
                else:
                    paso("CA {0}={1!r}".format(f, calc_a.get(f)))

    # 2d) FO solo si hay C/L/K
    fo_cont = eng.registro.primero("FO")
    if fo_cont is None:
        corte("FO", "rol FO no cargado")
    else:
        if (
            isinstance(calc_a, dict)
            and all(calc_a.get(x) is not None for x in ("C", "L", "K"))
        ):
            try:
                tru_ri_fn, tru_total_fn = eng.get_formulas()
                ri = tru_ri_fn(calc_a["C"], calc_a["L"], calc_a["K"])
                tt = tru_total_fn(calc_a["C"], calc_a["L"], calc_a["K"])
                paso("FO tru_ri={0} tru_total={1}".format(ri, tt))
            except Exception as e:
                corte(
                    "FO",
                    "tru_* lanzo {0}: {1}".format(type(e).__name__, e),
                )
        else:
            corte(
                "FO",
                "no invocable: CA no entrego C/L/K completos "
                "(propagacion desde CA)",
            )

    # 2e) Engine.evaluar A (orquestacion)
    out_a = eng.evaluar(pet_a)
    if not isinstance(out_a, dict):
        corte("EVALUAR_A", "no dict: {0!r}".format(out_a))
        out_a = {}
    else:
        paso("EVALUAR_A estado={0}".format(out_a.get("estado")))
        fac = out_a.get("factores") or {}
        for f in ("C", "L", "K"):
            val = fac.get(f) if isinstance(fac, dict) else None
            if val is None:
                corte(
                    "EVALUAR_A",
                    "body.factores.{0} ausente (estado={1}, razon={2!r})".format(
                        f, out_a.get("estado"), out_a.get("razon")
                    ),
                )
            else:
                paso("EVALUAR_A factores.{0}={1}".format(f, val))
        for t in ("tru_ri", "tru_total"):
            if out_a.get(t) in (None, "UNDEFINED"):
                corte(
                    "EVALUAR_A",
                    "body.{0}={1!r} (no depositado para Omega)".format(
                        t, out_a.get(t)
                    ),
                )

    # ------------------------------------------------------------------
    # 3) Ciclo forense B — sujetos
    # ------------------------------------------------------------------
    pet_b: Dict[str, Any] = {
        "contexto": "Conversacion de evaluacion de veracidad entre hablantes.",
        "O_context": "Conversacion de evaluacion de veracidad entre hablantes.",
        "mensaje": (
            "Carlos: Yo no tome el dinero.\n"
            "Maria: Vi a Carlos junto a la caja."
        ),
        "escala_id": "tru_sujeto",
        "categoria_tru": "tru_sujeto",
    }

    mand_b = (
        eng._mandatos_aplicables(pet_b, ce)
        if hasattr(eng, "_mandatos_aplicables")
        else []
    )
    if "ce_mandato_sujetos" not in mand_b:
        corte(
            "CE/SUJETOS",
            "mandato ce_mandato_sujetos NO aplicable; "
            "mandatos={0}".format(mand_b),
        )
    else:
        paso("CE mandato sujetos aplicable")

    # segmentacion cruda
    from core.engine import _segmentar_sujetos, _texto_peticion

    segs = _segmentar_sujetos(_texto_peticion(pet_b))
    if len(segs) < 2:
        corte(
            "SEGMENTACION",
            "se esperaban >=2 hablantes Nombre:; real={0}".format(segs),
        )
    else:
        paso("SEGMENTACION n={0} nombres={1}".format(
            len(segs), [s.get("nombre") for s in segs]
        ))

    out_b = eng.evaluar(pet_b)
    if not isinstance(out_b, dict):
        corte("EVALUAR_B", "no dict")
        out_b = {}
    else:
        paso("EVALUAR_B estado={0}".format(out_b.get("estado")))

    sujetos = out_b.get("sujetos")
    if not isinstance(sujetos, list) or len(sujetos) < 2:
        corte(
            "EVALUAR_B/SUJETOS",
            "body.sujetos ausente o incompleto; real={0!r} n_sujetos={1!r}".format(
                sujetos, out_b.get("n_sujetos")
            ),
        )
    else:
        paso("EVALUAR_B sujetos n={0}".format(len(sujetos)))
        for s in sujetos:
            if not isinstance(s, dict):
                corte("SUJETO", "entrada no dict: {0!r}".format(s))
                continue
            nombre = s.get("nombre")
            if s.get("estado") != "OK":
                corte(
                    "SUJETO/{0}".format(nombre),
                    "estado={0} razon={1!r} factores={2!r}".format(
                        s.get("estado"), s.get("razon"), s.get("factores")
                    ),
                )
            for t in ("tru_ri", "tru_total"):
                if s.get(t) in (None, "UNDEFINED"):
                    corte(
                        "SUJETO/{0}".format(nombre),
                        "{0} ausente (CA/FO no calculo por sujeto)".format(t),
                    )

    # ------------------------------------------------------------------
    # 4) Persistencia: memoria vs disco (solo si hubo sujetos en memoria)
    # ------------------------------------------------------------------
    mem = list(eng.resultados_evaluacion or [])
    body_mem = None
    for reg in reversed(mem):
        if isinstance(reg, dict):
            b = reg.get("resultado") or {}
            if isinstance(b, dict) and b.get("sujetos"):
                body_mem = b
                break

    if body_mem is None and isinstance(sujetos, list) and sujetos:
        corte(
            "MEMORIA",
            "evaluar devolvio sujetos pero resultados_evaluacion no los tiene",
        )

    try:
        from diagnostics.evidencia import leer
        doc = leer() or {}
    except Exception as e:
        corte("DEPOSITARIO", "leer() fallo: {0}: {1}".format(type(e).__name__, e))
        doc = {}

    origen = (
        eng._origen_evidencia()
        if hasattr(eng, "_origen_evidencia")
        else "test_trazabilidad"
    )
    del_origen = [
        r for r in (doc.get("resultados") or [])
        if isinstance(r, dict) and r.get("origen") == origen
    ]

    body_disco = None
    for reg in reversed(del_origen):
        b = reg.get("resultado") or {}
        if isinstance(b, dict) and b.get("sujetos"):
            body_disco = b
            break

    if body_mem is not None and body_disco is None:
        corte(
            "PERSISTENCIA",
            "memoria tiene sujetos; disco origen={0} no".format(origen),
        )
    elif body_mem is not None and body_disco is not None:
        perdidas = set(body_mem.keys()) - set(body_disco.keys())
        if perdidas:
            corte(
                "PERSISTENCIA",
                "claves perdidas en disco: {0}".format(sorted(perdidas)),
            )
        else:
            paso("PERSISTENCIA sujetos conservados origen={0}".format(origen))

    # ------------------------------------------------------------------
    # 5) Propagacion (solo con cortes reales)
    # ------------------------------------------------------------------
    prop: List[str] = []
    lugares = [c.split("]")[0].strip("[") for c in cortes]
    if any(l.startswith("CA") for l in lugares):
        prop.append("CA → FO sin Tru → EVALUAR body PARCIAL/sin factores → Omega ⚪")
    if any("SUJETO" in l or l.endswith("SUJETOS") for l in lugares):
        prop.append("SUJETOS → body incompleto → Omega N=0")
    if any(l.startswith("PERSISTENCIA") for l in lugares):
        prop.append("EMIT/DEPOSITARIO → Omega no ve lo que memoria tiene")
    if any(l.startswith("CX") for l in lugares):
        prop.append("CX permite_k=False → CA no debe fabricar K (fail-closed)")

    # ------------------------------------------------------------------
    # Informe final (solo cortes + cadena)
    # ------------------------------------------------------------------
    lineas = []
    lineas.append("=" * 64)
    lineas.append("TRAZABILIDAD FORENSE — VPSI PIPELINE")
    lineas.append("=" * 64)
    lineas.append("--- CADENA ---")
    lineas.extend(cadena)
    lineas.append("")
    lineas.append("--- CORTES ({0}) ---".format(len(cortes)))
    if cortes:
        for c in cortes:
            lineas.append("FALLO  " + c)
    else:
        lineas.append("ningun corte")
    lineas.append("")
    lineas.append("--- PROPAGACION ---")
    if prop:
        for p in prop:
            lineas.append("  " + p)
    else:
        lineas.append("  (sin propagacion)")
    lineas.append("=" * 64)

    informe = "\n".join(lineas)
    print(informe)

    if cortes:
        pytest.fail(
            "Cortes detectados ({0}):\n{1}".format(len(cortes), informe)
        )
