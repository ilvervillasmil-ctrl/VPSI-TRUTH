"""
VPSI-TRUTH --- modules/citacion/__init__.py

Rol CIT — citación / anuncio de la cadena norma–evidencia–O.

OFICIO
  Citar y anunciar. Autoridad total sobre la *forma* y el *universo
  citable del ciclo*: puede anunciar todo lo que Engine y los módulos
  ya aportaron (ids, factores reportados, O, límites, FO aplicada, …).

  Engine orquesta el ciclo y entrega el paquete.
  CIT no orquesta módulos ajenos: lee el paquete y documenta.

NO OFICIO
  - Calcular C, L, K, Tru_Ri, Tru_total.
  - Fijar O.
  - Aprobar/rechazar material de realidad.
  - Veredicto personal ("miente" / "dice la verdad").
  - Interpretar estados mentales.
  - Sustituir AX, MC, CA, FO, CX, TX, RE, CH, SF o Engine.

AGENCIA
  Total para citar: si está en el paquete del ciclo (o en fuentes
  resolubles sin recálculo), puede anunciarse.
  Cero agencia sobre el valor numérico del cálculo.

Versión 1.1 — anunciar(paquete) de ciclo + anunciar(cita) de forma.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ===============================================================
# CONTENEDOR (contrato con Engine)
# ===============================================================

CONTENEDOR = {
    "nombre": "citacion",
    "rol": "CIT",
    "version": "1.1.0",
    "descripcion": (
        "Citar y anunciar la cadena norma–evidencia–O del ciclo. "
        "Autoridad total de anuncio sobre lo aportado en el paquete. "
        "No calcula Tru. No fija O. No juzga personas. "
        "Engine entrega el paquete; CIT documenta el porqué."
    ),
    "requiere": [],
    "capacidades": {
        "anunciar": "anunciar",
        "anunciar_todo": "anunciar_todo",
        "citar": "citar",
        "registrar": "registrar",
        "resolver_enunciado": "resolver_enunciado",
        "inventario": "inventario",
        "barrer": "barrer",
        "verificar": "verificar",
        "limpiar_ciclo": "limpiar_ciclo",
        "evaluar": "anunciar",
        "registrar": "registrar",
    },
}

FUNCION = {
    "nombre": "citacion",
    "hace": (
        "Registrar y exponer citas del ciclo: AX, MC, CX, TX, CA, FO, RE, "
        "CT, CH, SF, límites estructurales y evidencia. "
        "anunciar(paquete) arma la cadena desde el resultado del Engine."
    ),
    "no_hace": [
        "calcular_C",
        "calcular_L",
        "calcular_K",
        "calcular_Tru",
        "fijar_O",
        "evaluar_verdad_personal",
        "interpretar_estados_mentales",
        "orquestar_modulos",
        "aprobar_material_realidad",
    ],
    "agencia": (
        "Total para citar lo presente en el paquete del ciclo. "
        "Nula sobre valores numéricos de C/L/K/Tru."
    ),
    "autoridad": (
        "Única autoridad: forma y exposición de la cadena. "
        "Si no hay base, anuncia límite de precisión; no rellena factores."
    ),
}

TIPOS_CITA = (
    "ax", "mc", "cx", "tx", "ca", "fo", "re", "ct", "ch", "sf",
    "limite", "evidencia", "citacion",
)

CAMPOS_OBLIGATORIOS = (
    "id", "tipo", "fuente_modulo", "enunciado", "descripcion", "evidencia_ref",
)
CAMPOS_OPCIONALES = ("o_ref", "contexto_ciclo", "meta")


# ===============================================================
# REGISTRO DE CICLO (proceso; no verdad persistente)
# ===============================================================

_REGISTRO: List[Dict[str, Any]] = []


def _validar_cita(cita: Dict[str, Any]) -> List[str]:
    errores: List[str] = []
    if not isinstance(cita, dict):
        return ["cita debe ser dict"]
    tipo = cita.get("tipo")
    if tipo not in TIPOS_CITA:
        errores.append("tipo de cita no admitido: {0}".format(tipo))
    for campo in CAMPOS_OBLIGATORIOS:
        if campo == "id" and tipo == "limite":
            continue
        if not cita.get(campo) and cita.get(campo) != 0:
            errores.append("falta campo obligatorio: {0}".format(campo))
    return errores


def _normalizar_cita(cita: Dict[str, Any]) -> Dict[str, Any]:
    out = {
        "id": cita.get("id"),
        "tipo": cita.get("tipo"),
        "fuente_modulo": cita.get("fuente_modulo"),
        "enunciado": cita.get("enunciado") or "",
        "descripcion": cita.get("descripcion") or "",
        "evidencia_ref": cita.get("evidencia_ref") or "",
    }
    for c in CAMPOS_OPCIONALES:
        if c in cita and cita[c] is not None:
            out[c] = cita[c]
    return out


def limpiar_ciclo() -> Dict[str, Any]:
    n = len(_REGISTRO)
    _REGISTRO.clear()
    return {"ok": True, "limpiadas": n}


def registrar(cita: Dict[str, Any]) -> Dict[str, Any]:
    errores = _validar_cita(cita)
    if errores:
        return {"ok": False, "errores": errores}
    normalizada = _normalizar_cita(cita)
    _REGISTRO.append(normalizada)
    return {"ok": True, "n": len(_REGISTRO), "cita": normalizada}


def citar(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    pet = peticion or {}
    out = list(_REGISTRO)
    if pet.get("modulo"):
        out = [c for c in out if c.get("fuente_modulo") == pet["modulo"]]
    if pet.get("tipo"):
        out = [c for c in out if c.get("tipo") == pet["tipo"]]
    if pet.get("o_ref"):
        out = [c for c in out if c.get("o_ref") == pet["o_ref"]]
    if pet.get("id"):
        out = [c for c in out if c.get("id") == pet["id"]]
    return {"citas": out, "n": len(out), "nota": "solo exposición; sin recálculo"}


# ===============================================================
# ANUNCIO DE UNA CITA (forma)
# ===============================================================

def _anuncio_de_cita(cita: Dict[str, Any]) -> Dict[str, Any]:
    errores = _validar_cita(cita)
    if errores:
        return {"ok": False, "errores": errores, "anuncio": None}
    c = _normalizar_cita(cita)
    return {
        "ok": True,
        "anuncio": {
            "titulo": "[{0}] {1}".format(c.get("fuente_modulo"), c.get("id")),
            "tipo": c.get("tipo"),
            "enunciado": c.get("enunciado"),
            "descripcion": c.get("descripcion"),
            "evidencia_ref": c.get("evidencia_ref"),
            "o_ref": c.get("o_ref"),
            "contexto_ciclo": c.get("contexto_ciclo"),
        },
    }


def anunciar_todo(filtro: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    pack = citar(filtro)
    anuncios: List[Dict[str, Any]] = []
    for c in pack["citas"]:
        r = _anuncio_de_cita(c)
        if r.get("ok") and r.get("anuncio"):
            anuncios.append(r["anuncio"])
    return {
        "anuncios": anuncios,
        "n": len(anuncios),
        "filtro": filtro or {},
        "nota": "capacidad total de anuncio; presentación puede filtrar",
    }


def resolver_enunciado(id_norma: str) -> Dict[str, Any]:
    if not id_norma:
        return {
            "id": id_norma,
            "enunciado": None,
            "descripcion": None,
            "resuelto": False,
            "nota": "id vacío",
        }
    for c in _REGISTRO:
        if c.get("id") == id_norma and c.get("enunciado"):
            return {
                "id": id_norma,
                "enunciado": c.get("enunciado"),
                "descripcion": c.get("descripcion"),
                "fuente_modulo": c.get("fuente_modulo"),
                "resuelto": True,
                "nota": "resuelto desde registro de ciclo",
            }
    # Puente AX sin inventar
    try:
        from modules.citacion.fuentes import ax as fuente_ax

        r = fuente_ax.anunciar_id(
            str(id_norma),
            evidencia_ref="resolver_enunciado",
            registrar=False,
        )
        if r.get("resuelto") and r.get("cita"):
            c = r["cita"]
            return {
                "id": id_norma,
                "enunciado": c.get("enunciado"),
                "descripcion": c.get("descripcion"),
                "fuente_modulo": c.get("fuente_modulo"),
                "resuelto": True,
                "nota": "resuelto desde declaraciones AX",
            }
    except Exception:
        pass
    return {
        "id": id_norma,
        "enunciado": None,
        "descripcion": None,
        "resuelto": False,
        "nota": "sin enunciado en registro ni en AX cargado",
    }


# ===============================================================
# DETECCIÓN: paquete de ciclo (Engine) vs cita suelta
# ===============================================================

def _es_paquete_ciclo(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if "resultado" in obj and isinstance(obj.get("resultado"), dict):
        return True
    if "contexto_cx" in obj and "tipos_peticion" in obj:
        return True
    if obj.get("engine_version") and ("resultado" in obj or "peticion" in obj):
        return True
    return False


def _es_cita_suelta(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if _es_paquete_ciclo(obj):
        return False
    # forma mínima de cita
    return "tipo" in obj or "enunciado" in obj or "id" in obj


# ===============================================================
# ANUNCIAR CICLO — autoridad total de cita sobre el paquete
# ===============================================================

def _evidencia_ref(paquete: Dict[str, Any]) -> str:
    inv = paquete.get("invocador_id") or "ciclo"
    ver = paquete.get("engine_version") or ""
    res = paquete.get("resultado") or {}
    seq = res.get("secuencia")  # puede no estar aún
    return "ciclo:{0}:v{1}".format(inv, ver) + (
        ":seq={0}".format(seq) if seq is not None else ""
    )


def _o_ref(paquete: Dict[str, Any]) -> Optional[str]:
    res = paquete.get("resultado") or {}
    cx = paquete.get("contexto_cx") or {}
    reg = cx.get("registro") if isinstance(cx.get("registro"), dict) else {}
    for src in (res, cx, reg, paquete.get("peticion") or {}):
        if not isinstance(src, dict):
            continue
        for k in ("O_id", "o_id", "O_context", "contexto", "enunciado_O"):
            v = src.get(k)
            if v is not None and str(v).strip() and str(v).strip().lower() not in (
                "undefined",
                "indefinido",
                "none",
                "null",
            ):
                return str(v).strip()[:200]
    return None


def _anunciar_paquete(paquete: Dict[str, Any]) -> Dict[str, Any]:
    """
    Oficio principal para Engine.
    Lee solo el paquete. No calcula Tru. No inventa factores.
    Autoridad total para citar lo presente.
    """
    limpiar_ciclo()

    res = paquete.get("resultado") if isinstance(paquete.get("resultado"), dict) else {}
    cx = paquete.get("contexto_cx") if isinstance(paquete.get("contexto_cx"), dict) else {}
    tipos = list(paquete.get("tipos_peticion") or cx.get("tipos_peticion") or [])
    if not tipos:
        tipos = ["dame_cadena_completa"]

    evid = _evidencia_ref(paquete)
    o_ref = _o_ref(paquete)
    ctx_ciclo = str(res.get("estado") or cx.get("modo_entrada") or "ciclo")

    errores: List[str] = []
    n_fuentes = 0

    def _ok_fuente(r: Any) -> None:
        nonlocal n_fuentes
        if isinstance(r, dict) and r.get("ok") is False:
            errores.extend([str(e) for e in (r.get("errores") or [])])
        else:
            n_fuentes += 1

    # ----- CX -----
    try:
        from modules.citacion.fuentes import cx as fuente_cx

        if cx:
            _ok_fuente(
                fuente_cx.desde_resolver(
                    cx,
                    evidencia_ref=evid,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
        estado_cx = None
        reg = cx.get("registro") if isinstance(cx.get("registro"), dict) else {}
        estado_cx = reg.get("estado") or cx.get("estado")
        if estado_cx in ("indefinido",) or res.get("estado") == "UNDEFINED":
            _ok_fuente(
                fuente_cx.anunciar_indefinido(
                    motivo=str(
                        res.get("razon")
                        or "O/contexto no usable en el ciclo (Def-5.3.1)"
                    ),
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
    except Exception as e:
        errores.append("fuente cx: {0}: {1}".format(type(e).__name__, e))

    # ----- CA (factores ya en resultado; no recalcular) -----
    try:
        from modules.citacion.fuentes import ca as fuente_ca

        factores = res.get("factores") if isinstance(res.get("factores"), dict) else {}
        C = factores.get("C")
        L = factores.get("L")
        K = factores.get("K")
        if C is not None or L is not None or K is not None:
            _ok_fuente(
                fuente_ca.anunciar_factores(
                    C=C,
                    L=L,
                    K=K,
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
        elif res.get("estado") in ("PARCIAL", "UNDEFINED"):
            _ok_fuente(
                fuente_ca.anunciar_sin_factores(
                    motivo=str(res.get("razon") or "factores incompletos en ciclo"),
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
    except Exception as e:
        errores.append("fuente ca: {0}: {1}".format(type(e).__name__, e))

    # ----- FO (valores ya calculados en resultado) -----
    try:
        from modules.citacion.fuentes import fo as fuente_fo

        tru_ri = res.get("tru_ri") or res.get("Tru_Ri")
        tru_total = res.get("tru_total") or res.get("Tru_total")
        if (
            tru_ri is not None
            and tru_total is not None
            and str(tru_ri) not in ("UNDEFINED", "None")
            and str(tru_total) not in ("UNDEFINED", "None")
        ):
            factores = res.get("factores") if isinstance(res.get("factores"), dict) else {}
            _ok_fuente(
                fuente_fo.anunciar_formula_aplicada(
                    tru_ri=tru_ri,
                    tru_total=tru_total,
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    C=factores.get("C"),
                    L=factores.get("L"),
                    K=factores.get("K"),
                    registrar=True,
                )
            )
        elif "dame_normas" in tipos or "dame_cadena_completa" in tipos:
            _ok_fuente(
                fuente_fo.anunciar_expresion(
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
    except Exception as e:
        errores.append("fuente fo: {0}: {1}".format(type(e).__name__, e))

    # ----- CT ancla (lectura; no recalcula aritmética de valuación) -----
    try:
        from modules.citacion.fuentes import ct as fuente_ct

        if res.get("alpha") is not None or res.get("beta") is not None:
            _ok_fuente(
                fuente_ct.anunciar_valores(
                    alpha=res.get("alpha"),
                    beta=res.get("beta"),
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
        elif "dame_normas" in tipos or "dame_cadena_completa" in tipos:
            _ok_fuente(
                fuente_ct.anunciar_ancla(
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
    except Exception as e:
        errores.append("fuente ct: {0}: {1}".format(type(e).__name__, e))

    # ----- AX ids (valuacion.ids / ids_cx_relevantes) -----
    try:
        from modules.citacion.fuentes import ax as fuente_ax

        ids: List[str] = []
        val = res.get("valuacion") if isinstance(res.get("valuacion"), dict) else {}
        for src in (
            val.get("ids"),
            cx.get("ids_cx_relevantes"),
            res.get("ids"),
        ):
            if isinstance(src, list):
                for i in src:
                    s = str(i).strip()
                    if s and s not in ids:
                        ids.append(s)
        if ids:
            pack_ax = fuente_ax.anunciar_lista(
                ids,
                evidencia_ref=evid,
                o_ref=o_ref,
                contexto_ciclo=ctx_ciclo,
                registrar=True,
            )
            n_fuentes += int(pack_ax.get("n") or 0)
    except Exception as e:
        errores.append("fuente ax: {0}: {1}".format(type(e).__name__, e))

    # ----- MC permite_k / informe si vino en paquete -----
    try:
        from modules.citacion.fuentes import mc as fuente_mc

        if "permite_k" in cx:
            _ok_fuente(
                fuente_mc.anunciar_permite_k(
                    permite_k=bool(cx.get("permite_k")),
                    enunciado="permite_k={0} según CX del ciclo.".format(
                        cx.get("permite_k")
                    ),
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
        informe_mc = paquete.get("informe_mecanica") or res.get("informe_mecanica")
        if isinstance(informe_mc, dict):
            _ok_fuente(
                fuente_mc.desde_informe_barrer(
                    informe_mc,
                    evidencia_ref=evid,
                    o_ref=o_ref,
                    contexto_ciclo=ctx_ciclo,
                    registrar=True,
                )
            )
    except Exception as e:
        errores.append("fuente mc: {0}: {1}".format(type(e).__name__, e))

    # ----- Límites estructurales (sin inventar números) -----
    try:
        from modules.citacion.fuentes import limite as fuente_lim

        factores = res.get("factores") if isinstance(res.get("factores"), dict) else {}
        tiene_factores = all(
            factores.get(k) is not None
            and str(factores.get(k)) not in ("UNDEFINED", "None", "")
            for k in ("C", "L", "K")
        )
        permite_k = cx.get("permite_k")
        reg = cx.get("registro") if isinstance(cx.get("registro"), dict) else {}
        o_estado = reg.get("estado")
        if res.get("estado") == "UNDEFINED":
            o_estado = o_estado or "indefinido"

        pack_lim = fuente_lim.anunciar_desde_ciclo(
            evidencia_ref=evid,
            o_ref=o_ref,
            contexto_ciclo=ctx_ciclo,
            permite_k=permite_k if isinstance(permite_k, bool) else None,
            tiene_factores=tiene_factores,
            o_estado=o_estado,
            registrar=True,
        )
        if pack_lim.get("citas"):
            n_fuentes += len(pack_lim.get("citas") or [])
    except Exception as e:
        errores.append("fuente limite: {0}: {1}".format(type(e).__name__, e))

    # ----- Fractal: cita del propio oficio CIT -----
    try:
        from modules.citacion.esquema import plantilla

        cita_self = plantilla(
            id="CIT-CICLO",
            tipo="citacion",
            fuente_modulo="citacion",
            enunciado=(
                "CIT anunció la cadena del ciclo; estado_resultado={0}; "
                "tipos_peticion={1}.".format(res.get("estado"), tipos)
            ),
            descripcion=(
                "Auto-cita del oficio de citación; no calcula Tru; "
                "documenta que el cierre de anuncio se ejecutó."
            ),
            evidencia_ref=evid,
            o_ref=o_ref,
            contexto_ciclo=ctx_ciclo,
            meta={"tipos_peticion": tipos, "estado": res.get("estado")},
        )
        registrar(cita_self)
        n_fuentes += 1
    except Exception as e:
        errores.append("cita fractal: {0}: {1}".format(type(e).__name__, e))

    anuncios_pack = anunciar_todo()
    return {
        "estado": "OK" if n_fuentes > 0 else "VACIO",
        "ok": n_fuentes > 0,
        "n_citas": len(_REGISTRO),
        "n_anuncios": anuncios_pack.get("n", 0),
        "anuncios": anuncios_pack.get("anuncios") or [],
        "tipos_peticion": tipos,
        "evidencia_ref": evid,
        "o_ref": o_ref,
        "errores": errores,
        "engine_version": paquete.get("engine_version"),
        "nota": (
            "CIT: autoridad total de anuncio sobre el paquete; "
            "cero agencia sobre valores de Tru; sin recálculo."
        ),
    }


# ===============================================================
# OFICIO ÚNICO: anunciar (cita | paquete)
# ===============================================================

def anunciar(arg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Entrada única para Engine y para uso manual.

    - Si arg es paquete de ciclo (Engine._cierre_cit) → cadena completa.
    - Si arg es una cita suelta → un bloque de anuncio.
    - Si arg es None → anunciar_todo() del registro actual.

    No calcula Tru. No inventa factores.
    """
    if arg is None:
        return anunciar_todo()

    if _es_paquete_ciclo(arg):
        return _anunciar_paquete(arg)

    if _es_cita_suelta(arg):
        # registrar + anunciar forma
        reg = registrar(arg)
        if not reg.get("ok"):
            return {
                "ok": False,
                "errores": reg.get("errores") or ["cita inválida"],
                "anuncio": None,
            }
        return _anuncio_de_cita(reg.get("cita") or arg)

    return {
        "ok": False,
        "estado": "ERROR_FORMA",
        "errores": [
            "anunciar: se esperaba paquete de ciclo (resultado/contexto_cx) "
            "o una cita con tipo/enunciado"
        ],
        "anuncio": None,
    }


# ===============================================================
# INVENTARIO / CENTINELA
# ===============================================================

def inventario() -> Dict[str, Any]:
    return {
        "contenedor": CONTENEDOR["nombre"],
        "rol": CONTENEDOR["rol"],
        "version": CONTENEDOR["version"],
        "tipos_cita": list(TIPOS_CITA),
        "campos_obligatorios": list(CAMPOS_OBLIGATORIOS),
        "campos_opcionales": list(CAMPOS_OPCIONALES),
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "registro_n": len(_REGISTRO),
        "no_hace": list(FUNCION["no_hace"]),
        "agencia": FUNCION["agencia"],
        "autoridad": FUNCION["autoridad"],
        "anuncio_capacidad": "total",
        "oficio_ciclo": (
            "anunciar(paquete) con resultado+contexto_cx → cadena completa"
        ),
    }


def barrer() -> Dict[str, Any]:
    errores: List[str] = []
    choques: List[str] = []

    for t in TIPOS_CITA:
        if not isinstance(t, str) or not t:
            errores.append("tipo de cita inválido en TIPOS_CITA")

    for prohibido in ("tru_total", "tru_ri", "calcular", "evaluar_verdad"):
        for cap in CONTENEDOR["capacidades"]:
            if prohibido in str(cap).lower():
                choques.append(
                    "capacidad incompatible con oficio de citacion: {0}".format(cap)
                )

    coherente = not errores and not choques
    return {
        "coherente": coherente,
        "choques": choques,
        "errores": errores,
        "funciones": list(CONTENEDOR["capacidades"].keys()),
        "registro_n": len(_REGISTRO),
        "version": CONTENEDOR["version"],
        "nota": "centinela CIT; sin juicio de verdad; anunciar acepta paquete de ciclo",
    }


def verificar() -> Dict[str, Any]:
    return barrer()


# ===============================================================
# EXPORTS
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "FUNCION",
    "TIPOS_CITA",
    "CAMPOS_OBLIGATORIOS",
    "CAMPOS_OPCIONALES",
    "registrar",
    "citar",
    "anunciar",
    "anunciar_todo",
    "resolver_enunciado",
    "limpiar_ciclo",
    "inventario",
    "barrer",
    "verificar",
]
