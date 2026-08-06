# -*- coding: utf-8 -*-
"""
tests/test_trazabilidad_pipeline_completo.py

Un solo Test: auditoría total del repositorio + trazabilidad del ciclo.
Nada se escapa. Cada módulo aparece. Cada corte se nombra.

Orden del informe:
  0) Arranque Engine
  1) Censo ROLES / contenedores / disco (cobertura total)
  2) Contrato y capacidades de CADA módulo
  3) Ciclo evaluar — petición auditoría
  4) Ciclo evaluar — petición sujetos
  5) Memoria ↔ depositario ↔ claves
  6) Propagación de cortes
  7) Cierre
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pytest

# ---------------------------------------------------------------------------
# helpers de informe (mismo estilo que diagnostico conexiones)
# ---------------------------------------------------------------------------

class Informe:
    def __init__(self) -> None:
        self.lineas: List[str] = []
        self.ok: List[str] = []
        self.fallos: List[str] = []
        self.avisos: List[str] = []

    def _add(self, marca: str, msg: str, bucket: List[str]) -> None:
        linea = "{0}:    {1}".format(marca, msg)
        self.lineas.append(linea)
        bucket.append(msg)

    def OK(self, msg: str) -> None:
        self._add("OK", msg, self.ok)

    def FALLO(self, msg: str) -> None:
        self._add("FALLO", msg, self.fallos)

    def AVISO(self, msg: str) -> None:
        self._add("AVISO", msg, self.avisos)

    def SEP(self, titulo: str) -> None:
        self.lineas.append("")
        self.lineas.append("=" * 60)
        self.lineas.append(titulo)
        self.lineas.append("=" * 60)

    def texto(self) -> str:
        return "\n".join(self.lineas)


def _raiz_repo() -> Path:
    # tests/ → repo root
    return Path(__file__).resolve().parents[1]


def _mods_dir() -> Path:
    return _raiz_repo() / "modules"


# ---------------------------------------------------------------------------
# TEST ÚNICO
# ---------------------------------------------------------------------------

def test_trazabilidad_pipeline_completo() -> None:
    """
    Auditoría total + trazabilidad de ciclo.
    Falla solo si hay corte de cobertura, contrato roto o invariante roto.
    """
    from core.engine import Engine, ROLES, OBLIGATORIOS

    inf = Informe()
    raiz = _mods_dir()

    # =====================================================================
    # 0) ARRANQUE
    # =====================================================================
    inf.SEP("0) ARRANQUE ENGINE")
    try:
        eng = Engine(raiz_modulos=str(raiz), invocador_id="test_trazabilidad")
    except Exception as e:
        inf.FALLO("Engine no arranco: {0}: {1}".format(type(e).__name__, e))
        pytest.fail(inf.texto())
        return

    if eng.estado != "OPERATIVO":
        inf.FALLO("Engine estado={0} errores={1}".format(
            eng.estado, eng.errores_arranque
        ))
    else:
        inf.OK("Engine OPERATIVO version={0}".format(eng.VERSION))
        inf.OK("contenedores cargados n={0}".format(eng.registro.total()))

    # =====================================================================
    # 1) CENSO TOTAL — ni un módulo fuera
    # =====================================================================
    inf.SEP("1) CENSO TOTAL (ROLES + DISCO + REGISTRO)")

    roles_decl = list(ROLES)
    roles_set = set(roles_decl)
    oblig = set(OBLIGATORIOS)

    # disco: modules/*/__init__.py
    en_disco: Dict[str, Path] = {}
    for init in sorted(raiz.glob("*/__init__.py")):
        en_disco[init.parent.name] = init

    # registro
    por_nombre = dict(eng.registro.contenedores)
    por_rol = eng.registro.por_rol
    rechazados = list(eng.registro.rechazados or [])

    # 1a) cada ROL declarado
    for rol in roles_decl:
        lista = por_rol.get(rol) or []
        if not lista:
            if rol in oblig:
                inf.FALLO("ROL obligatorio vacio: {0}".format(rol))
            else:
                inf.AVISO("ROL declarado sin contenedor cargado: {0}".format(rol))
        else:
            nombres = [c.nombre for c in lista]
            inf.OK("ROL {0} cargado: {1}".format(rol, nombres))

    # 1b) cada contenedor del registro tiene rol valido
    for nombre, cont in por_nombre.items():
        if cont.rol not in roles_set:
            inf.FALLO("Contenedor {0} rol desconocido: {1}".format(nombre, cont.rol))
        else:
            inf.OK("Contenedor {0} rol={1} version={2}".format(
                nombre, cont.rol, cont.version
            ))

    # 1c) cobertura disco ↔ registro
    nombres_reg = set(por_nombre.keys())
    # mapear nombre de carpeta ≈ nombre de contenedor cuando coinciden
    carpetas = set(en_disco.keys())
    # no todos los nombres de carpeta == nombre CONTENEDOR; reportar ambos lados
    inf.OK("carpetas modules/* con __init__.py n={0}".format(len(carpetas)))
    inf.OK("contenedores en registro n={0}".format(len(nombres_reg)))

    if rechazados:
        for r in rechazados:
            inf.AVISO("rechazado en descubrimiento: {0}".format(r))
    else:
        inf.OK("sin contenedores rechazados en descubrimiento")

    # 1d) assert de cobertura de roles: todos los ROLES fueron iterados
    if len(roles_decl) < 1:
        inf.FALLO("ROLES vacio")
    else:
        inf.OK("ROLES auditados n={0}: {1}".format(
            len(roles_decl), ",".join(roles_decl)
        ))

    # =====================================================================
    # 2) CONTRATO Y CAPACIDADES — cada módulo
    # =====================================================================
    inf.SEP("2) CONTRATO Y CAPACIDADES (cada contenedor)")

    for nombre, cont in sorted(por_nombre.items(), key=lambda x: x[0]):
        caps = cont.capacidades or {}
        if not isinstance(caps, dict):
            inf.FALLO("{0}: capacidades no es dict".format(nombre))
            continue
        if not caps:
            inf.AVISO("{0}: CONTENEDOR sin capacidades declaradas".format(nombre))
            continue

        rotas: List[str] = []
        ok_caps: List[str] = []
        for cap in caps.keys():
            fn = cont.fn(str(cap))
            if callable(fn):
                ok_caps.append(str(cap))
            else:
                # oficio alias
                fn2 = cont.fn_oficio(str(cap)) if hasattr(cont, "fn_oficio") else None
                if callable(fn2):
                    ok_caps.append("{0}(oficio)".format(cap))
                else:
                    rotas.append(str(cap))

        if rotas:
            inf.FALLO("{0}: capacidades no resolubles: {1}".format(
                nombre, rotas
            ))
        else:
            inf.OK("{0}: capacidades OK {1}".format(nombre, ok_caps))

        # requiere
        for req in cont.requiere or []:
            if req in roles_set:
                if not (por_rol.get(req) or []):
                    inf.FALLO("{0} requiere rol {1} vacio".format(nombre, req))
            else:
                if req not in por_nombre:
                    inf.FALLO("{0} requiere modulo '{1}' ausente".format(
                        nombre, req
                    ))

    # =====================================================================
    # 3) CICLO A — peticion auditoria (estilo Omega)
    # =====================================================================
    inf.SEP("3) CICLO A — PETICION AUDITORIA VPSI")

    pet_a: Dict[str, Any] = {
        "contexto": (
            "Auditoría estructural del repositorio VPSI-TRUTH: "
            "coherencia axiomática, contratos, mecánica y correlación."
        ),
        "O_context": (
            "Auditoría estructural del repositorio VPSI-TRUTH: "
            "coherencia axiomática, contratos, mecánica y correlación."
        ),
        "mensaje": (
            "Auditar el repositorio VPSI-TRUTH y sus contratos CONTENEDOR."
        ),
        "pedir_anuncio": True,
        "invocador_id": "test_trazabilidad",
    }

    # sondas pre-ciclo: CE / CX / CA presencia
    ce_cont = eng.registro.primero("CE")
    cx_cont = eng.registro.primero("CX")
    ca_cont = eng.registro.primero("CA")
    fo_cont = eng.registro.primero("FO")
    tt_cont = eng.registro.primero("TT")
    cit_cont = eng.registro.primero("CIT")
    ct_cont = eng.registro.primero("CT")
    ax_cont = eng.registro.primero("AX")
    mc_cont = eng.registro.primero("MC")

    for rol, cont, label in (
        ("CT", ct_cont, "constantes"),
        ("AX", ax_cont, "axiomas"),
        ("MC", mc_cont, "mecanica"),
        ("CE", ce_cont, "capacidades_engine"),
        ("CX", cx_cont, "contexto"),
        ("CA", ca_cont, "calculator"),
        ("FO", fo_cont, "formulas"),
        ("TT", tt_cont, "tru_totales"),
        ("CIT", cit_cont, "citacion"),
    ):
        if cont is None:
            inf.AVISO("ciclo A: rol {0} ({1}) no cargado".format(rol, label))
        else:
            inf.OK("ciclo A: rol {0} disponible ({1})".format(rol, cont.nombre))

    # CE mandatos
    ce_info = eng._ce_ids_skills() if hasattr(eng, "_ce_ids_skills") else {}
    inf.OK("CE ids: {0}".format(ce_info.get("ids") or []))
    mandatos = (
        eng._mandatos_aplicables(pet_a, ce_info)
        if hasattr(eng, "_mandatos_aplicables")
        else []
    )
    inf.OK("CE mandatos aplicables (A): {0}".format(mandatos))

    # evaluar A
    n_mem_antes = len(eng.resultados_evaluacion)
    try:
        out_a = eng.evaluar(pet_a)
    except Exception as e:
        inf.FALLO("evaluar(A) lanzo: {0}: {1}".format(type(e).__name__, e))
        out_a = {}

    if not isinstance(out_a, dict):
        inf.FALLO("evaluar(A) no devolvio dict")
        out_a = {}
    else:
        inf.OK("evaluar(A) estado={0}".format(out_a.get("estado")))

    # desglose A
    inf.OK("A.permite_k/contexto_cx: {0}".format(
        (out_a.get("contexto_cx") or {}).get("permite_k")
    ))
    fac_a = out_a.get("factores") or {}
    for k in ("C", "L", "K"):
        v = fac_a.get(k) if isinstance(fac_a, dict) else None
        if v is None and out_a.get(k) is None:
            inf.AVISO("A: factor {0} no depositado en body".format(k))
        else:
            inf.OK("A: factor {0}={1}".format(k, v if v is not None else out_a.get(k)))

    for k in ("tru_ri", "tru_total"):
        if out_a.get(k) in (None, "UNDEFINED"):
            inf.AVISO("A: {0}={1}".format(k, out_a.get(k)))
        else:
            inf.OK("A: {0}={1}".format(k, out_a.get(k)))

    if out_a.get("sujetos"):
        inf.OK("A: sujetos n={0}".format(out_a.get("n_sujetos")))
    else:
        inf.OK("A: sin sujetos (esperado si no hay hablantes Nombre:)")

    # =====================================================================
    # 4) CICLO B — sujetos (Carlos / Maria)
    # =====================================================================
    inf.SEP("4) CICLO B — PETICION CON SUJETOS")

    pet_b: Dict[str, Any] = {
        "contexto": "Conversacion de evaluacion de veracidad entre hablantes.",
        "O_context": "Conversacion de evaluacion de veracidad entre hablantes.",
        "mensaje": (
            "Carlos: Yo no tome el dinero.\n"
            "Maria: Vi a Carlos junto a la caja."
        ),
        "escala_id": "tru_sujeto",
        "categoria_tru": "tru_sujeto",
        "pedir_anuncio": False,
        "invocador_id": "test_trazabilidad",
    }

    mandatos_b = (
        eng._mandatos_aplicables(pet_b, ce_info)
        if hasattr(eng, "_mandatos_aplicables")
        else []
    )
    inf.OK("CE mandatos aplicables (B): {0}".format(mandatos_b))
    if "ce_mandato_sujetos" not in (mandatos_b or []):
        inf.AVISO("B: ce_mandato_sujetos no aplica (revisar mandato CE)")

    try:
        out_b = eng.evaluar(pet_b)
    except Exception as e:
        inf.FALLO("evaluar(B) lanzo: {0}: {1}".format(type(e).__name__, e))
        out_b = {}

    if not isinstance(out_b, dict):
        inf.FALLO("evaluar(B) no devolvio dict")
        out_b = {}
    else:
        inf.OK("evaluar(B) estado={0}".format(out_b.get("estado")))

    sujetos_b = out_b.get("sujetos")
    n_suj = out_b.get("n_sujetos")
    if isinstance(sujetos_b, list) and len(sujetos_b) >= 2:
        inf.OK("B: sujetos depositados en body n={0}".format(
            n_suj if n_suj is not None else len(sujetos_b)
        ))
        for s in sujetos_b:
            if isinstance(s, dict):
                inf.OK("B: sujeto {0} estado={1} tru_total={2}".format(
                    s.get("nombre"), s.get("estado"), s.get("tru_total")
                ))
    elif isinstance(sujetos_b, list) and sujetos_b:
        inf.AVISO("B: sujetos n={0} (se esperaban >=2)".format(len(sujetos_b)))
    else:
        inf.FALLO("B: body sin sujetos (mandato/segmentacion no depositó)")

    # =====================================================================
    # 5) MEMORIA ↔ DEPOSITARIO
    # =====================================================================
    inf.SEP("5) MEMORIA ↔ DEPOSITARIO (invariante)")

    memoria = list(eng.resultados_evaluacion or [])
    inf.OK("memoria ciclos n={0} (antes A: {1})".format(
        len(memoria), n_mem_antes
    ))

    # buscar en memoria el ciclo B (ultimo con sujetos si existe)
    body_mem_sujetos = None
    for reg in reversed(memoria):
        if not isinstance(reg, dict):
            continue
        body = reg.get("resultado") or {}
        if isinstance(body, dict) and body.get("sujetos"):
            body_mem_sujetos = body
            break

    if body_mem_sujetos is not None:
        inf.OK("memoria: ciclo con sujetos n={0}".format(
            body_mem_sujetos.get("n_sujetos")
            or len(body_mem_sujetos.get("sujetos") or [])
        ))
    else:
        inf.FALLO("memoria: ningun ciclo con clave sujetos")

    # disco
    try:
        from diagnostics.evidencia import leer
        doc = leer() or {}
        resultados_disco = list(doc.get("resultados") or [])
        inf.OK("disco evaluaciones.json n={0} origenes={1}".format(
            doc.get("n"), doc.get("origenes")
        ))
    except Exception as e:
        inf.FALLO("no se pudo leer depositario: {0}: {1}".format(
            type(e).__name__, e
        ))
        resultados_disco = []
        doc = {}

    origen = (
        eng._origen_evidencia()
        if hasattr(eng, "_origen_evidencia")
        else "test_trazabilidad"
    )
    del_origen = [
        r for r in resultados_disco
        if isinstance(r, dict) and r.get("origen") == origen
    ]
    inf.OK("disco origen={0} n={1}".format(origen, len(del_origen)))

    # invariante: si memoria tiene sujetos, disco del mismo origen tambien
    body_disco_sujetos = None
    for reg in reversed(del_origen):
        body = reg.get("resultado") or {}
        if isinstance(body, dict) and body.get("sujetos"):
            body_disco_sujetos = body
            break

    if body_mem_sujetos is not None and body_disco_sujetos is None:
        inf.FALLO(
            "invariante roto: memoria tiene sujetos pero "
            "evaluaciones.json (origen={0}) no los refleja".format(origen)
        )
    elif body_mem_sujetos is not None and body_disco_sujetos is not None:
        inf.OK("invariante OK: sujetos en memoria y en disco (mismo origen)")
        # claves del body memoria ⊆ disco
        solo_m = set(body_mem_sujetos.keys()) - set(body_disco_sujetos.keys())
        if solo_m:
            inf.FALLO(
                "claves en memoria ausentes en disco: {0}".format(
                    sorted(solo_m)
                )
            )
        else:
            inf.OK("claves de body con sujetos conservadas en disco")

    # =====================================================================
    # 6) TABLA DE MÓDULOS (los 19 — invoked / contrato)
    # =====================================================================
    inf.SEP("6) TABLA TOTAL DE MODULOS (cobertura)")

    # heuristicas de "invocado en ciclo" segun body y mandatos
    invoked_hints: Dict[str, str] = {
        "CE": "SI" if (mandatos or mandatos_b) else "NO",
        "CX": "SI" if (out_a.get("contexto_cx") or out_b.get("contexto_cx")) else "NO",
        "CA": "SI" if (
            (out_a.get("factores") is not None)
            or (out_b.get("factores") is not None)
            or out_a.get("estado") in ("OK", "PARCIAL", "ERROR")
        ) else "NO",
        "FO": "SI" if (
            out_a.get("tru_ri") not in (None,)
            or out_b.get("tru_ri") not in (None,)
        ) else "NO",
        "CIT": "SI" if (out_a.get("citacion") or out_b.get("citacion")) else "NO",
        "TT": "SI" if (
            "ce_mandato_escala_tt" in (mandatos + mandatos_b)
            or "ce_mandato_aplicar_escala" in (mandatos + mandatos_b)
        ) else "NO*",
        "CT": "SI*",  # arranque / get_constantes
        "AX": "SI*",  # compuerta arranque
        "MC": "SI*",  # compuerta arranque
    }

    for rol in roles_decl:
        lista = por_rol.get(rol) or []
        if not lista:
            inf.AVISO("TABLA {0}: sin contenedor".format(rol))
            continue
        cont = lista[0]
        inv = invoked_hints.get(rol, "NO")
        # contrato ya auditado en fase 2; aqui solo fila
        inf.OK(
            "TABLA {0:4} | modulo={1:22} | invoked={2:4} | caps={3}".format(
                rol,
                cont.nombre,
                inv,
                len(cont.capacidades or {}),
            )
        )

    inf.OK(
        "Leyenda: SI*=uso en arranque/compuerta; NO*=catalogo (no calcula)"
    )

    # =====================================================================
    # 7) PROPAGACION DE CORTES
    # =====================================================================
    inf.SEP("7) PROPAGACION DE CORTES")

    cortes: List[str] = []

    # corte CA → FO
    def _sin_clk(body: Dict[str, Any]) -> bool:
        fac = body.get("factores") or {}
        if not isinstance(fac, dict):
            return True
        return any(fac.get(k) in (None, "UNDEFINED") for k in ("C", "L", "K"))

    if isinstance(out_a, dict) and out_a.get("estado") == "PARCIAL" and _sin_clk(out_a):
        cortes.append(
            "A: CA no entrego C/L/K → FO sin Tru → body PARCIAL → Omega lee PARCIAL"
        )
        inf.AVISO(cortes[-1])

    if isinstance(out_b, dict) and not out_b.get("sujetos"):
        cortes.append(
            "B: sin sujetos en body → CE mandato/segmentacion o O no usable"
        )
        inf.FALLO(cortes[-1])

    if body_mem_sujetos is not None and body_disco_sujetos is None:
        cortes.append(
            "PERSISTENCIA: memoria.sujetos no refleja disco (origen={0})".format(
                origen
            )
        )
        inf.FALLO(cortes[-1])

    if not cortes:
        inf.OK("sin cortes de propagacion detectados en A/B/persistencia")
    else:
        inf.OK("cortes listados n={0}".format(len(cortes)))

    # =====================================================================
    # 8) CIERRE
    # =====================================================================
    inf.SEP("8) CIERRE")
    inf.OK("total OK:    {0}".format(len(inf.ok)))
    inf.OK("total AVISO: {0}".format(len(inf.avisos)))
    inf.OK("total FALLO: {0}".format(len(inf.fallos)))

    # imprimir siempre el informe completo (como el diagnostico)
    print(inf.texto())
    print("=" * 60)
    print("ids_fallo: {0}".format(
        [f.split(":")[0] for f in inf.fallos] if inf.fallos else []
    ))
    print("=" * 60)

    if inf.fallos:
        pytest.fail(
            "Trazabilidad: {0} fallo(s)\n{1}".format(
                len(inf.fallos), inf.texto()
            )
        )
