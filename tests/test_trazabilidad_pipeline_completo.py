# -*- coding: utf-8 -*-
"""
tests/test_trazabilidad_pipeline_completo.py

Un solo Test forense del repositorio VPSI-TRUTH.

Principio:
  El sistema decide qué módulos usa.
  Este test no impone secuencia.
  Observa, contrasta contratos, nombra el primer corte y la propagación.

API preferida: pública (Engine, registro, ejecutar_*, evaluar, evidencia.leer).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pytest


def _mods_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "modules"


def test_trazabilidad_pipeline_completo() -> None:
    from core.engine import Engine, ROLES, OBLIGATORIOS, es_undefined

    # ------------------------------------------------------------------
    # acumuladores
    # ------------------------------------------------------------------
    cortes: List[Dict[str, Any]] = []
    cadena: List[str] = []
    participaron: Set[str] = set()
    sin_produccion: Set[str] = set()
    no_invocados: Set[str] = set()

    def log(msg: str) -> None:
        cadena.append(msg)

    def corte(
        modulo: str,
        oficio: str,
        detalle: str,
        campos_perdidos: Optional[List[str]] = None,
    ) -> None:
        cortes.append({
            "modulo": modulo,
            "oficio": oficio,
            "detalle": detalle,
            "campos_perdidos": list(campos_perdidos or []),
        })
        log("CORTE  [{0}.{1}] {2}".format(modulo, oficio, detalle))

    # ------------------------------------------------------------------
    # 0) Arranque (publico)
    # ------------------------------------------------------------------
    try:
        eng = Engine(
            raiz_modulos=str(_mods_dir()),
            invocador_id="test_trazabilidad",
        )
    except Exception as e:
        pytest.fail("Engine no arranco: {0}: {1}".format(type(e).__name__, e))
        return

    if eng.estado != "OPERATIVO":
        corte(
            "Engine",
            "arranque",
            "estado={0} errores={1}".format(eng.estado, eng.errores_arranque),
        )
    else:
        log("Engine OPERATIVO v{0} contenedores={1}".format(
            eng.VERSION, eng.registro.total()
        ))

    # ------------------------------------------------------------------
    # 1) Cobertura total de ROLES + contratos (todos, sin excepcion)
    # ------------------------------------------------------------------
    log("--- COBERTURA ---")
    por_rol = eng.registro.por_rol
    por_nombre = eng.registro.contenedores

    for rol in ROLES:
        lista = por_rol.get(rol) or []
        if not lista:
            if rol in OBLIGATORIOS:
                corte("COBERTURA", rol, "rol obligatorio sin contenedor")
            else:
                log("ROL {0}: sin contenedor (no obligatorio)".format(rol))
            no_invocados.add(rol)
            continue
        cont = lista[0]
        log("ROL {0}: modulo={1} version={2}".format(
            rol, cont.nombre, cont.version
        ))
        # capacidades declaradas deben resolver
        caps = cont.capacidades or {}
        if not isinstance(caps, dict) or not caps:
            corte(cont.nombre, "CONTENEDOR", "sin capacidades declaradas")
            continue
        for cap in caps.keys():
            fn = cont.fn(str(cap))
            if not callable(fn):
                fn = cont.fn_oficio(str(cap)) if hasattr(cont, "fn_oficio") else None
            if not callable(fn):
                corte(
                    cont.nombre,
                    str(cap),
                    "capacidad declarada no resoluble a callable",
                )

        for req in cont.requiere or []:
            if req in ROLES and not (por_rol.get(req) or []):
                corte(cont.nombre, "requiere", "rol {0} vacio".format(req))
            elif req not in ROLES and req not in por_nombre:
                corte(
                    cont.nombre,
                    "requiere",
                    "modulo '{0}' ausente".format(req),
                )

    # ------------------------------------------------------------------
    # 2) Peticiones (el sistema decide el grafo interno)
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
        "mensaje": "Auditar el repositorio VPSI-TRUTH y sus contratos CONTENEDOR.",
        "pedir_anuncio": True,
    }
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

    # ------------------------------------------------------------------
    # 3) Sonda publica CA.calcular (contrato de salida C/L/K)
    #    No impone que deba usarse; si se invoca y no cumple, es corte.
    # ------------------------------------------------------------------
    log("--- SONDA CA.calcular (contrato publico) ---")
    calc_a: Any = eng.ejecutar_capacidad("CA", "calcular", pet_a)
    if es_undefined(calc_a):
        corte(
            "CA",
            "calcular",
            "oficio devolvio UNDEFINED (no resolvio o lanzo)",
        )
        calc_a = None
    elif not isinstance(calc_a, dict):
        corte(
            "CA",
            "calcular",
            "tipo inesperado {0}: {1!r}".format(type(calc_a).__name__, calc_a),
        )
        calc_a = None
    else:
        participaron.add("CA")
        log("CA.calcular keys={0}".format(sorted(calc_a.keys())))
        perdidos_ca = [f for f in ("C", "L", "K") if calc_a.get(f) is None]
        if perdidos_ca:
            corte(
                "CA",
                "calcular",
                "no entrego campos de contrato: {0}".format(perdidos_ca),
                campos_perdidos=perdidos_ca,
            )
            sin_produccion.add("CA")
        else:
            log("CA.calcular C={0!r} L={1!r} K={2!r}".format(
                calc_a.get("C"), calc_a.get("L"), calc_a.get("K")
            ))

    # ------------------------------------------------------------------
    # 4) Sonda publica FO (solo si CA entrego C/L/K — handoff real)
    # ------------------------------------------------------------------
    log("--- HANDOFF CA → FO ---")
    if (
        isinstance(calc_a, dict)
        and all(calc_a.get(x) is not None for x in ("C", "L", "K"))
    ):
        try:
            tru_ri_fn, tru_total_fn = eng.get_formulas()
            ri = tru_ri_fn(calc_a["C"], calc_a["L"], calc_a["K"])
            tt = tru_total_fn(calc_a["C"], calc_a["L"], calc_a["K"])
            participaron.add("FO")
            log("FO handoff OK tru_ri={0} tru_total={1}".format(ri, tt))
        except Exception as e:
            corte(
                "FO",
                "tru_*",
                "CA entrego C/L/K pero FO fallo: {0}: {1}".format(
                    type(e).__name__, e
                ),
            )
    else:
        log(
            "FO no sondado: CA no entrego C/L/K completos "
            "(no se inventa entrada a FO)"
        )
        if "CA" in {c["modulo"] for c in cortes}:
            log("propagacion: corte CA bloquea FO")

    # ------------------------------------------------------------------
    # 5) Ciclo A — evaluar (caja negra; el sistema arma el grafo)
    # ------------------------------------------------------------------
    log("--- EVALUAR A (auditoria) ---")
    out_a = eng.evaluar(pet_a)
    if not isinstance(out_a, dict):
        corte("Engine", "evaluar_A", "no devolvio dict: {0!r}".format(out_a))
        out_a = {}
    else:
        log("evaluar_A estado={0} razon={1!r}".format(
            out_a.get("estado"), out_a.get("razon")
        ))
        # señales de participacion por huella en el body
        if out_a.get("contexto_cx") is not None:
            participaron.add("CX")
        if out_a.get("ce_ids") or out_a.get("mandatos_aplicados"):
            participaron.add("CE")
        if out_a.get("citacion") is not None:
            participaron.add("CIT")
        if out_a.get("factores") is not None or out_a.get("estado") in (
            "OK", "PARCIAL", "ERROR"
        ):
            participaron.add("CA")
        if out_a.get("tru_ri") not in (None,) or out_a.get("tru_total") not in (None,):
            participaron.add("FO")

        fac = out_a.get("factores") if isinstance(out_a.get("factores"), dict) else {}
        perdidos_body = []
        for f in ("C", "L", "K"):
            if fac.get(f) is None:
                perdidos_body.append("factores.{0}".format(f))
        for t in ("tru_ri", "tru_total"):
            if out_a.get(t) in (None, "UNDEFINED"):
                perdidos_body.append(t)
        if perdidos_body and out_a.get("estado") != "UNDEFINED":
            # UNDEFINED sin O es fail-closed legitimo; PARCIAL/OK sin factores es corte
            corte(
                "Engine",
                "evaluar_A",
                "body incompleto estado={0}: faltan {1}".format(
                    out_a.get("estado"), perdidos_body
                ),
                campos_perdidos=perdidos_body,
            )

    # ------------------------------------------------------------------
    # 6) Ciclo B — sujetos
    # ------------------------------------------------------------------
    log("--- EVALUAR B (sujetos) ---")
    out_b = eng.evaluar(pet_b)
    if not isinstance(out_b, dict):
        corte("Engine", "evaluar_B", "no devolvio dict")
        out_b = {}
    else:
        log("evaluar_B estado={0}".format(out_b.get("estado")))
        if out_b.get("contexto_cx") is not None:
            participaron.add("CX")
        if out_b.get("ce_ids") or out_b.get("mandatos_aplicados"):
            participaron.add("CE")

        sujetos = out_b.get("sujetos")
        if not isinstance(sujetos, list) or len(sujetos) < 2:
            corte(
                "Engine",
                "evaluar_B",
                "sujetos ausentes o <2; real={0!r} n={1!r}".format(
                    sujetos, out_b.get("n_sujetos")
                ),
                campos_perdidos=["sujetos", "n_sujetos"],
            )
        else:
            participaron.add("CE")  # mandato sujetos / segmentacion via engine
            log("sujetos n={0}".format(len(sujetos)))
            for s in sujetos:
                if not isinstance(s, dict):
                    corte("SUJETO", "item", "no dict: {0!r}".format(s))
                    continue
                nom = s.get("nombre")
                if s.get("estado") != "OK":
                    corte(
                        "SUJETO/{0}".format(nom),
                        "ciclo",
                        "estado={0} razon={1!r}".format(
                            s.get("estado"), s.get("razon")
                        ),
                    )
                perd_s = [
                    t for t in ("tru_ri", "tru_total")
                    if s.get(t) in (None, "UNDEFINED")
                ]
                if perd_s:
                    corte(
                        "SUJETO/{0}".format(nom),
                        "tru",
                        "sin {0}".format(perd_s),
                        campos_perdidos=perd_s,
                    )

    # ------------------------------------------------------------------
    # 7) Conservacion memoria → depositario (todas las claves criticas)
    # ------------------------------------------------------------------
    log("--- PERSISTENCIA ---")
    mem = list(eng.get_resultados_evaluacion() or [])
    claves_criticas = (
        "estado", "factores", "tru_ri", "tru_total",
        "sujetos", "n_sujetos", "por_sujeto",
        "citacion", "contexto_cx", "ce_ids", "mandatos_aplicados",
        "razon", "fallos",
    )

    try:
        from diagnostics.evidencia import leer
        doc = leer() or {}
    except Exception as e:
        corte(
            "evidencia",
            "leer",
            "{0}: {1}".format(type(e).__name__, e),
        )
        doc = {}

    origen = str(getattr(eng, "invocador_id", None) or "test_trazabilidad")
    # si existe helper publico de origen, usarlo; si no, invocador_id
    if hasattr(eng, "_origen_evidencia") and callable(eng._origen_evidencia):
        try:
            origen = eng._origen_evidencia()
        except Exception:
            pass

    del_origen = [
        r for r in (doc.get("resultados") or [])
        if isinstance(r, dict) and r.get("origen") == origen
    ]
    log("memoria n={0} | disco origen={1} n={2}".format(
        len(mem), origen, len(del_origen)
    ))

    if len(mem) == 0:
        corte("Engine", "memoria", "resultados_evaluacion vacio tras evaluar")
    elif len(del_origen) == 0:
        corte(
            "evidencia",
            "depositar",
            "disco sin entradas para origen={0}".format(origen),
        )
    else:
        # comparar ultimo ciclo de memoria con ultimo del origen
        reg_m = mem[-1] if mem else {}
        reg_d = del_origen[-1] if del_origen else {}
        body_m = reg_m.get("resultado") if isinstance(reg_m, dict) else {}
        body_d = reg_d.get("resultado") if isinstance(reg_d, dict) else {}
        if not isinstance(body_m, dict):
            body_m = {}
        if not isinstance(body_d, dict):
            body_d = {}

        perdidas = []
        for k in claves_criticas:
            if k in body_m and k not in body_d:
                perdidas.append(k)
        if perdidas:
            corte(
                "evidencia",
                "conservacion",
                "claves en memoria ausentes en disco: {0}".format(perdidas),
                campos_perdidos=perdidas,
            )
        else:
            log("conservacion OK (claves criticas presentes en disco)")

        # factores internos
        fac_m = body_m.get("factores") if isinstance(body_m.get("factores"), dict) else {}
        fac_d = body_d.get("factores") if isinstance(body_d.get("factores"), dict) else {}
        for f in ("C", "L", "K"):
            if f in fac_m and f not in fac_d:
                corte(
                    "evidencia",
                    "conservacion",
                    "factores.{0} perdido en disco".format(f),
                    campos_perdidos=["factores.{0}".format(f)],
                )

    # ------------------------------------------------------------------
    # 8) Clasificacion de modulos (observado, no impuesto)
    # ------------------------------------------------------------------
    for rol in ROLES:
        if rol in participaron:
            continue
        lista = por_rol.get(rol) or []
        if lista:
            no_invocados.add(rol)

    # ------------------------------------------------------------------
    # 9) Primer corte + propagacion
    # ------------------------------------------------------------------
    lineas: List[str] = []
    lineas.append("=" * 64)
    lineas.append("TRAZABILIDAD FORENSE — UN SOLO TEST")
    lineas.append("=" * 64)
    lineas.append("CADENA OBSERVADA")
    for c in cadena:
        lineas.append("  " + c)

    lineas.append("")
    if cortes:
        prim = cortes[0]
        lineas.append("PRIMER CORTE")
        lineas.append("  modulo   : {0}".format(prim["modulo"]))
        lineas.append("  oficio   : {0}".format(prim["oficio"]))
        lineas.append("  detalle  : {0}".format(prim["detalle"]))
        if prim["campos_perdidos"]:
            lineas.append(
                "  perdidos : {0}".format(prim["campos_perdidos"])
            )
        lineas.append("")
        lineas.append("TODOS LOS CORTES ({0})".format(len(cortes)))
        for i, c in enumerate(cortes, 1):
            lineas.append(
                "  {0}. {1}.{2}: {3}".format(
                    i, c["modulo"], c["oficio"], c["detalle"]
                )
            )
        lineas.append("")
        lineas.append("PROPAGACION (desde primer corte)")
        m0 = prim["modulo"]
        lineas.append("  {0}".format(m0))
        if m0 in ("CA", "Engine") or m0.startswith("SUJETO"):
            lineas.append("    ↓ FO / Tru")
            lineas.append("    ↓ body evaluar")
            lineas.append("    ↓ evidencia.depositar")
            lineas.append("    ↓ evaluaciones.json")
            lineas.append("    ↓ Omega (lee vacio/parcial)")
        elif m0 == "evidencia":
            lineas.append("    ↓ evaluaciones.json")
            lineas.append("    ↓ Omega")
        elif m0 == "FO":
            lineas.append("    ↓ body sin Tru")
            lineas.append("    ↓ Omega")
    else:
        lineas.append("PRIMER CORTE: (ninguno)")

    lineas.append("")
    lineas.append("PARTICIPARON   : {0}".format(sorted(participaron) or ["—"]))
    lineas.append("NO INVOCADOS   : {0}".format(sorted(no_invocados) or ["—"]))
    lineas.append(
        "SIN PRODUCCION : {0}".format(sorted(sin_produccion) or ["—"])
    )
    lineas.append("=" * 64)

    informe = "\n".join(lineas)
    print(informe)

    if cortes:
        pytest.fail(
            "Cortes ({0}). Primer responsable: {1}.{2}\n{3}".format(
                len(cortes),
                cortes[0]["modulo"],
                cortes[0]["oficio"],
                informe,
            )
        )
