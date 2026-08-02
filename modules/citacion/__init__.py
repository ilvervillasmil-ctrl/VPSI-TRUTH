"""
VPSI-TRUTH --- modules/citacion/__init__.py

Módulo de citación / enunciados de norma–evidencia–O.

OFICIO ÚNICO
  Citar y anunciar. Registrar y exponer la cadena
  (id + enunciado + descripción + evidencia_ref + O)
  que Engine y los módulos ya produjeron en un ciclo.

NO OFICIO (prohibido en este módulo)
  - Calcular C, L, K, Tru_Ri, Tru_total.
  - Fijar O.
  - Aprobar o rechazar material de realidad.
  - Declarar que alguien "miente" o "dice la verdad" como veredicto personal.
  - Interpretar estados mentales.
  - Sustituir a AX, MC, CA, FO, CX, TX, RE, CH, SF o Engine.
  - Orquestar módulos.

La palabra coordinada la orquesta Engine.
Este módulo solo documenta el porqué, citando lo que cada instrumento aportó.
No inventa evidencia. No recalcula.

Capacidad de anuncio: TOTAL (puede citar todo lo aportado en el ciclo).
Presentación (Omega u otro visor): puede filtrar; este módulo no limita el universo citable.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# ===============================================================
# CONTENEDOR (contrato con Engine)
# ===============================================================

CONTENEDOR = {
    "nombre": "citacion",
    "rol": "CIT",
    "version": "1.0.0",
    "descripcion": (
        "Citar y anunciar la cadena norma–evidencia–O de un ciclo de evaluación. "
        "No calcula. No juzga personas. No inventa factores. "
        "Expone id, enunciado, descripción y referencias que otros módulos "
        "ya emitieron bajo orquestación de Engine. "
        "Capacidad de anuncio total; la presentación puede filtrar."
    ),
    "requiere": [],
    "capacidades": {
        "citar": "citar",
        "registrar": "registrar",
        "anunciar": "anunciar",
        "anunciar_todo": "anunciar_todo",
        "resolver_enunciado": "resolver_enunciado",
        "inventario": "inventario",
        "barrer": "barrer",
        "verificar": "verificar",
        "limpiar_ciclo": "limpiar_ciclo",
    },
}

# ===============================================================
# FUNCIÓN / ALCANCE
# ===============================================================

FUNCION = {
    "nombre": "citacion",
    "hace": (
        "Registrar y exponer citas del ciclo: ids de axiomas/teoremas/lemas/corolarios, "
        "pasos de mecánica, reglas de taxonomía, fijaciones de contexto, "
        "oficios reportados de calculator/fórmulas (sin rehacer la cuenta), "
        "material de realidad etiquetado, límites de precisión y refs de evidencia. "
        "Cada cita lleva enunciado y descripción. "
        "Responde a peticiones del tipo: "
        "'necesito lo que hizo correlación bajo tal contexto' "
        "devolviendo citas y anuncios, no un recálculo."
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
    "provee": [
        "cita_estructurada",
        "anuncio_estructurado",
        "registro_de_ciclo",
        "enunciado_de_id",
        "descripcion_de_aporte",
        "limite_de_precision_citado",
    ],
    "anuncio": {
        "capacidad": "total",
        "campos_obligatorios": [
            "id",
            "tipo",
            "fuente_modulo",
            "enunciado",
            "descripcion",
            "evidencia_ref",
        ],
        "campos_opcionales": [
            "o_ref",
            "contexto_ciclo",
            "meta",
        ],
        "presentacion": (
            "Omega u otro visor puede filtrar por tipo, modulo o id; "
            "citacion no limita el universo citable del ciclo."
        ),
    },
    "respecto_otros_contratos": (
        "El contenido del enunciado se toma de lo que cada módulo declara "
        "en su contrato o salida; citacion define la maqueta de anuncio, "
        "no el funcionamiento interno de esos módulos."
    ),
    "fractal": (
        "Las mismas reglas se aplican a este módulo: "
        "si anuncia, debe poder citar de dónde salió su propia salida "
        "(contrato + archivos internos), sin calcular Tru."
    ),
    "autoridad": (
        "Única autoridad: citar y anunciar según lo que cada módulo/instrumento "
        "aportó en el ciclo orquestado por Engine. "
        "Cero autoridad sobre el valor numérico del cálculo. "
        "Si no hay base suficiente, anuncia límite de precisión; no rellena."
    ),
    "auditoria": (
        "Los tests y Omega pueden usar las citas para auditar el instrumento: "
        "si el cálculo no cuadra con norma+evidencia, el desajuste es evidencia "
        "contra el sistema, no un veredicto sobre personas."
    ),
}

# ===============================================================
# TIPOS DE CITA
# ===============================================================

TIPOS_CITA = (
    "ax",         # axioma / teorema / lema / corolario
    "mc",         # correlación mecánica
    "cx",         # contexto / O
    "tx",         # taxonomía
    "ca",         # calculator (oficio reportado; sin rehacer cuenta)
    "fo",         # fórmula aplicada (expresión; sin recomputar)
    "re",         # realidad / material etiquetado
    "ct",         # constantes / ancla
    "ch",         # cache / evidencia persistida
    "sf",         # self (si aportó al ciclo)
    "limite",     # no hay base suficiente para precisar
    "evidencia",  # ref a artefacto o turno
    "citacion",   # fractal: cita sobre el propio módulo de citación
)

# ===============================================================
# ESQUEMA DE UNA CITA
# ===============================================================

CAMPOS_OBLIGATORIOS = tuple(FUNCION["anuncio"]["campos_obligatorios"])
CAMPOS_OPCIONALES = tuple(FUNCION["anuncio"]["campos_opcionales"])


def _validar_cita(cita: Dict[str, Any]) -> List[str]:
    errores: List[str] = []
    if not isinstance(cita, dict):
        return ["cita debe ser dict"]
    tipo = cita.get("tipo")
    if tipo not in TIPOS_CITA:
        errores.append("tipo de cita no admitido: {0}".format(tipo))
    for campo in CAMPOS_OBLIGATORIOS:
        if campo == "id" and tipo == "limite":
            # límite puede no tener id de norma
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


# ===============================================================
# REGISTRO DE CICLO (memoria de proceso; no persistencia de verdad)
# ===============================================================

_REGISTRO: List[Dict[str, Any]] = []


def limpiar_ciclo() -> Dict[str, Any]:
    """Limpia el registro del ciclo actual. No toca artefactos en disco."""
    n = len(_REGISTRO)
    _REGISTRO.clear()
    return {"ok": True, "limpiadas": n}


def registrar(cita: Dict[str, Any]) -> Dict[str, Any]:
    """
    Acumula una cita del ciclo.
    Obligatorios: id (salvo tipo=limite), tipo, fuente_modulo,
    enunciado, descripcion, evidencia_ref.
    No valida verdad; solo forma.
    """
    errores = _validar_cita(cita)
    if errores:
        return {"ok": False, "errores": errores}
    normalizada = _normalizar_cita(cita)
    _REGISTRO.append(normalizada)
    return {"ok": True, "n": len(_REGISTRO), "cita": normalizada}


# ===============================================================
# OFICIO: CITAR / ANUNCIAR
# ===============================================================

def citar(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Devuelve citas del ciclo, opcionalmente filtradas.
    Filtros admitidos: modulo, tipo, o_ref, id.
    No calcula. No orquesta.
    """
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
    return {
        "citas": out,
        "n": len(out),
        "nota": "solo exposición; sin recálculo",
    }


def anunciar(cita: Dict[str, Any]) -> Dict[str, Any]:
    """
    Una cita → bloque de anuncio (maqueta de citacion).
    enunciado + descripcion + refs. Sin cálculo.
    """
    errores = _validar_cita(cita)
    if errores:
        return {"ok": False, "errores": errores, "anuncio": None}
    c = _normalizar_cita(cita)
    bloque = {
        "titulo": "[{0}] {1}".format(c.get("fuente_modulo"), c.get("id")),
        "tipo": c.get("tipo"),
        "enunciado": c.get("enunciado"),
        "descripcion": c.get("descripcion"),
        "evidencia_ref": c.get("evidencia_ref"),
        "o_ref": c.get("o_ref"),
        "contexto_ciclo": c.get("contexto_ciclo"),
    }
    return {"ok": True, "anuncio": bloque}


def anunciar_todo(filtro: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Anuncia todas las citas del ciclo (o filtradas).
    Pensado para auditoría completa; Omega puede usar un subconjunto.
    """
    pack = citar(filtro)
    anuncios: List[Dict[str, Any]] = []
    for c in pack["citas"]:
        r = anunciar(c)
        if r.get("ok") and r.get("anuncio"):
            anuncios.append(r["anuncio"])
    return {
        "anuncios": anuncios,
        "n": len(anuncios),
        "filtro": filtro or {},
        "nota": (
            "capacidad total de anuncio; "
            "presentación puede filtrar sin limitar el universo citable"
        ),
    }


def resolver_enunciado(id_norma: str) -> Dict[str, Any]:
    """
    Resuelve enunciado textual de un id si hay puente a AX u otra fuente.
    El init no calcula; la resolución detallada vive en archivos de la carpeta
    (fuentes/ax.py, etc.). Aquí: oficio del contrato + búsqueda en registro.
    """
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
    return {
        "id": id_norma,
        "enunciado": None,
        "descripcion": None,
        "resuelto": False,
        "nota": (
            "sin enunciado en registro de ciclo; "
            "puente a AX/fuentes pendiente en archivos de citacion"
        ),
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
        "anuncio_capacidad": FUNCION["anuncio"]["capacidad"],
        "autoridad": FUNCION["autoridad"],
    }


def barrer() -> Dict[str, Any]:
    """
    Coherencia interna del módulo de citación.
    No barre AX. No calcula Tru.
    """
    errores: List[str] = []
    choques: List[str] = []

    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in (
            "id",
            "tipo",
            "fuente_modulo",
            "enunciado",
            "descripcion",
            "evidencia_ref",
        ):
            choques.append("campo obligatorio inesperado en contrato: {0}".format(campo))

    for t in TIPOS_CITA:
        if not isinstance(t, str) or not t:
            errores.append("tipo de cita inválido en TIPOS_CITA")

    # fractal: el módulo no debe declarar capacidades de cálculo
    for prohibido in ("tru_total", "tru_ri", "calcular", "evaluar_verdad"):
        for cap in CONTENEDOR["capacidades"]:
            if prohibido in cap.lower():
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
        "nota": "centinela de citacion; sin juicio de verdad",
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
