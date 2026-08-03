"""
VPSI-TRUTH — modules/axiomas/__init__.py

Contenedor de axiomas. Rol AX. v9.5

Qué es:
  Vigila declaraciones (axioma | lema | teorema | corolario | definicion).
  No pertenece a ninguna teoría. No calcula Tru_total.
  No clasifica entrada (eso es CX). No orquesta (eso es Engine).

Qué vigila:
  - contradiccion_directa
  - contradiccion_de_cota
  Si hay choque o error de carga → coherente=False.

Qué expone:
  - verificar / barrer: coherencia del cuerpo
  - axiomas / declaraciones: lista si coherente (fail-closed)
  - generatividad: TR1/U1 sobre Θ (capa operativa + canónica paper)
  - inventario: mapa del módulo

Def-5.3.1 / dominio O:
  Vive en las declaraciones de los cuerpos (p.ej. contexto_AX, VPSI).
  Este INIT no re-enuncia el teorema: lo carga, lo vigila y lo expone.
  CX aplica la clasificación de entrada; AX es el juez del grafo.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from core.diagnostico import DiagnosticoGlobal  # type: ignore
except Exception:  # noqa: BLE001
    DiagnosticoGlobal = None  # type: ignore

# ===============================================================
# Constantes
# ===============================================================
OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")
TIPOS = ("axioma", "lema", "teorema", "corolario", "definicion")

AXIOMA = "axioma"
LEMA = "lema"
TEOREMA = "teorema"
COROLARIO = "corolario"
DEFINICION = "definicion"

TRADUCCION_CLAVES = {
    "type": "tipo",
    "subject": "sujeto",
    "relation": "relacion",
    "object": "objeto",
    "polarity": "polaridad",
    "statement": "enunciado",
    "depends_on": "depende_de",
    "governs": "gobierna",
    "cota": "cota",
}

_DIR = Path(__file__).parent

# Dominios donde suele vivir la exigencia de O / K (exposición, no cálculo)
DOMINIOS_K_O = frozenset({
    "contexto", "ontologia", "epistemologia", "verificacion",
    "dominio", "k", "o_context", "correlacion",
})


# ===============================================================
# Carga
# ===============================================================
def _cargar_declaraciones_desde_archivo(archivo: Path) -> List[Dict]:
    if archivo.name.startswith("_"):
        return []

    nombre_mod = f"axiomas_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return []

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)

    declaraciones = getattr(mod, "DECLARACIONES", None)
    if declaraciones is None and callable(getattr(mod, "declaraciones", None)):
        try:
            declaraciones = mod.declaraciones()
        except Exception:  # noqa: BLE001
            declaraciones = []

    # Alias frecuentes en archivos de cuerpo
    if declaraciones is None:
        for attr in ("CUERPO", "declaraciones_lista"):
            val = getattr(mod, attr, None)
            if isinstance(val, list):
                declaraciones = val
                break

    return declaraciones if isinstance(declaraciones, list) else []


def _ruta_vpsi() -> Optional[Path]:
    candidatos = [
        _DIR.parent.parent / "VPSI.py",
        _DIR.parent / "VPSI.py",
        _DIR / "VPSI.py",
    ]
    for p in candidatos:
        if p.exists():
            return p
    return None


# ===============================================================
# Normalización
# ===============================================================
def normalizar(decl_original: Dict, cuerpo: str) -> Dict:
    if not isinstance(decl_original, dict):
        raise ValueError(f"{cuerpo}: declaración no es dict")

    decl: Dict[str, Any] = {}
    for clave_orig, valor in decl_original.items():
        decl[TRADUCCION_CLAVES.get(clave_orig, clave_orig)] = valor

    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(
                f"{cuerpo}:{decl.get('id', '?')} sin clave obligatoria '{k}'"
            )

    tipo = str(decl["tipo"]).lower()
    tipo = {
        "axiom": "axioma",
        "theorem": "teorema",
        "corollary": "corolario",
        "lemma": "lema",
        "definition": "definicion",
    }.get(tipo, tipo)

    if tipo not in TIPOS:
        raise ValueError(
            f"{cuerpo}:{decl['id']} tipo '{tipo}' no válido. Admitidos: {TIPOS}"
        )
    if not isinstance(decl["polaridad"], bool):
        raise ValueError(f"{cuerpo}:{decl['id']} polaridad debe ser bool")

    return {
        "id": str(decl["id"]),
        "cuerpo": cuerpo,
        "tipo": tipo,
        "sujeto": str(decl["sujeto"]),
        "relacion": str(decl["relacion"]),
        "objeto": str(decl["objeto"]),
        "polaridad": bool(decl["polaridad"]),
        "cota": None if decl.get("cota") is None else str(decl["cota"]),
        "depende_de": [str(x) for x in decl.get("depende_de", [])],
        "gobierna": [str(x) for x in decl.get("gobierna", [])],
        "enunciado": str(decl.get("enunciado", "")),
    }


def clave(d: Dict) -> Tuple[str, str, str]:
    return (
        d["sujeto"].lower().strip(),
        d["relacion"].lower().strip(),
        d["objeto"].lower().strip(),
    )


def ref(d: Dict) -> str:
    return f"{d['cuerpo']}:{d['id']}"


# ===============================================================
# Recolección
# ===============================================================
def recolectar(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Carga y normaliza todas las declaraciones del módulo.
    Retorna (decls, errores). No lanza: acumula errores de carga.
    """
    decls: List[Dict] = []
    errores: List[Dict] = []

    for archivo in sorted(_DIR.glob("*.py")):
        if archivo.name == "__init__.py":
            continue
        try:
            for d in _cargar_declaraciones_desde_archivo(archivo):
                decls.append(normalizar(d, archivo.stem))
        except Exception as e:  # noqa: BLE001
            errores.append({
                "archivo": archivo.name,
                "error": f"{type(e).__name__}: {e}",
            })

    vpsi = _ruta_vpsi()
    if vpsi is not None:
        try:
            for d in _cargar_declaraciones_desde_archivo(vpsi):
                decls.append(normalizar(d, "VPSI"))
        except Exception as e:  # noqa: BLE001
            errores.append({
                "archivo": str(vpsi.name),
                "error": f"{type(e).__name__}: {e}",
            })

    if declaraciones_externas:
        for nombre, lista in declaraciones_externas.items():
            if not isinstance(lista, list):
                errores.append({
                    "modulo": nombre,
                    "error": "declaraciones externas no es lista",
                })
                continue
            for d in lista:
                try:
                    decls.append(normalizar(d, nombre))
                except ValueError as e:
                    errores.append({"modulo": nombre, "error": str(e)})

    return decls, errores


def por_dominio(
    dominio: str,
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    """
    Filtro de lectura: declaraciones cuyo gobierna toca un dominio.
    No interpreta; no calcula Tru. Útil para CX/CIT al citar.
    """
    dom = str(dominio).lower().strip()
    decls, _ = recolectar(declaraciones_externas)
    out = []
    for d in decls:
        gobs = [str(g).lower().strip() for g in (d.get("gobierna") or [])]
        if dom in gobs or any(dom in g for g in gobs):
            out.append(d)
    return out


def ids_dominio_k_o(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[str]:
    """
    Ids que gobiernan dominios relacionados con K/O/contexto.
    Exposición del grafo ya cargado (p.ej. Def-5.3.1 si está en el cuerpo).
    """
    decls, _ = recolectar(declaraciones_externas)
    ids: List[str] = []
    for d in decls:
        gobs = {str(g).lower().strip() for g in (d.get("gobierna") or [])}
        if gobs & DOMINIOS_K_O:
            ids.append(d["id"])
        # también por enunciado/objeto si el id es canónico de dominio
        blob = (
            f"{d.get('sujeto','')} {d.get('objeto','')} {d.get('enunciado','')}"
        ).lower()
        if any(x in blob for x in ("def-5.3.1", "o_context", "dominio o", "permite_k")):
            if d["id"] not in ids:
                ids.append(d["id"])
    return sorted(set(ids))


# ===============================================================
# Contradicciones
# ===============================================================
def contradiccion_directa(decls: List[Dict]) -> List[Dict]:
    grupos: Dict[Tuple[str, str, str], List[Dict]] = {}
    for d in decls:
        grupos.setdefault(clave(d), []).append(d)

    choques: List[Dict] = []
    for k, grupo in grupos.items():
        afirman = [d for d in grupo if d["polaridad"]]
        niegan = [d for d in grupo if not d["polaridad"]]
        for a in afirman:
            for n in niegan:
                choques.append({
                    "tipo": "contradiccion_directa",
                    "tripleta": " - ".join(k),
                    "declaracion_1": {
                        "id": a["id"],
                        "ubicacion": ref(a),
                        "enunciado": a["enunciado"],
                    },
                    "declaracion_2": {
                        "id": n["id"],
                        "ubicacion": ref(n),
                        "enunciado": n["enunciado"],
                    },
                    "mensaje": (
                        f"Contradicción en '{' - '.join(k)}': "
                        f"{ref(a)} AFIRMA vs {ref(n)} NIEGA"
                    ),
                })
    return choques


def contradiccion_de_cota(decls: List[Dict]) -> List[Dict]:
    grupos: Dict[Tuple[str, str], List[Dict]] = {}
    for d in decls:
        if d["cota"] is None:
            continue
        grupos.setdefault(
            (d["sujeto"].lower().strip(), d["relacion"].lower().strip()),
            [],
        ).append(d)

    choques: List[Dict] = []
    for (suj, rel), grupo in grupos.items():
        porcota: Dict[str, List[str]] = {}
        for d in grupo:
            porcota.setdefault(d["cota"], []).append(ref(d))
        if len(porcota) > 1:
            choques.append({
                "tipo": "contradiccion_de_cota",
                "sujeto": suj,
                "relacion": rel,
                "cotas": porcota,
                "mensaje": (
                    f"Contradicción de cota en '{suj} {rel}'. "
                    f"Cotas: {list(porcota.keys())}"
                ),
            })
    return choques


# ===============================================================
# Capacidades de contrato
# ===============================================================
def barrer(declaraciones_externas: Optional[Dict[str, List[Dict]]] = None) -> Dict:
    """Capacidad principal: coherencia axiomática del cuerpo."""
    decls, errores = recolectar(declaraciones_externas)
    choques = contradiccion_directa(decls) + contradiccion_de_cota(decls)

    if (choques or errores) and DiagnosticoGlobal is not None:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="axiomas",
                errores=(
                    [{"tipo": "choque", "detalle": c} for c in choques]
                    + [{"tipo": "error_carga", "detalle": e} for e in errores]
                ),
            )
        except Exception:  # noqa: BLE001
            pass

    cuerpos = sorted({d["cuerpo"] for d in decls})
    por_tipo = {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS}

    return {
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "declaraciones": len(decls),
        "cuerpos": cuerpos,
        "por_tipo": por_tipo,
        "ids_dominio_k_o": ids_dominio_k_o(declaraciones_externas)
        if not (choques or errores)
        else [],
    }


def verificar_salida(salida: Dict) -> bool:
    return bool(salida.get("coherente", False))


def declaraciones(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    """Lista normalizada si el cuerpo es coherente; si no → []."""
    resultado = barrer(declaraciones_externas)
    if not resultado["coherente"]:
        return []
    decls, _ = recolectar(declaraciones_externas)
    return decls


def axiomas(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    """Alias de contrato: misma semántica que declaraciones()."""
    return declaraciones(declaraciones_externas)


def inventario(peticion=None) -> Dict:
    decls, errores = recolectar()
    return {
        "contenedor": "axiomas",
        "version": "9.5",
        "tipos": list(TIPOS),
        "declaraciones": len(decls),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS},
        "cuerpos": sorted({d["cuerpo"] for d in decls}),
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
        "ids_dominio_k_o": ids_dominio_k_o(),
        "nota": (
            "Def-5.3.1 y dominio O viven en los cuerpos cargados; "
            "este módulo los vigila y expone, no los clasifica en entrada."
        ),
    }


# --- ids canónicos del paper (TR1, |Θ|=24) ---
THETA_CANONICO = frozenset({
    "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10",
    "T11", "T12", "T13", "T14", "T15", "T16", "T17",
    "U0", "U1", "M1", "M.1", "B-Canonical", "TT.6.1", "TR1",
})

DOMINIO_CANONICO = {
    "ontologia": "ONT",
    "ont": "ONT",
    "informacion": "INF",
    "info": "INF",
    "logica": "LOG",
    "log": "LOG",
    "epistemologia": "EPI",
    "epi": "EPI",
    "semantica": "SEM",
    "sem": "SEM",
    "temporal": "TMP",
    "tmp": "TMP",
    "meta": "MET",
    "met": "MET",
    "constantes": "MET",
    "self": "EPI",
    "inferencia_causal": "INF",
    "verificacion": "EPI",
    "ver": "VER",
    "contexto": "SEM",
}


def _dominios_canonicos(gobierna) -> set:
    out = set()
    for g in gobierna or []:
        key = str(g).lower().strip()
        out.add(DOMINIO_CANONICO.get(key, key.upper()[:3]))
    return out


def _medir_pares(theta: list) -> dict:
    n = len(theta)
    pares_tot = n * (n - 1) // 2 if n >= 2 else 0
    compatibles = 0
    novedosos = 0
    for i in range(n):
        Di = theta[i]["dominios"]
        for j in range(i + 1, n):
            Dj = theta[j]["dominios"]
            if not (Di & Dj):
                continue
            compatibles += 1
            union = Di | Dj
            if union > Di and union > Dj:
                novedosos += 1
    return {
        "theta_n": n,
        "pares_totales": pares_tot,
        "pares_compatibles": compatibles,
        "pares_novedosos": novedosos,
        "im_vs_theta": (
            "GENERATIVO" if n > 0 and novedosos > n
            else ("ESTANCADO" if n > 0 else "SIN_DATOS")
        ),
    }


def generatividad() -> dict:
    """
    TR1 en dos capas (saber, no creer):

    1) operativa  — todo axioma/teorema con gobierna (grafo del repo)
    2) canonica   — solo los 24 ids del paper + dominios normalizados

    No inventa candidatos. No calcula Tru. Una sola definición (sin duplicar).
    """
    decls, errores = recolectar()

    oper = []
    for d in decls:
        if d.get("tipo") not in ("teorema", "axioma"):
            continue
        gob = d.get("gobierna") or []
        if not gob:
            continue
        oper.append({
            "id": d["id"],
            "tipo": d["tipo"],
            "dominios": set(gob),
        })
    m_op = _medir_pares(oper)
    dominios_op = sorted({g for n in oper for g in n["dominios"]})

    por_id = {}
    for d in decls:
        i = str(d.get("id", ""))
        if i in THETA_CANONICO:
            cand = {
                "id": i,
                "tipo": d.get("tipo"),
                "dominios": _dominios_canonicos(d.get("gobierna")),
            }
            prev = por_id.get(i)
            if prev is None or len(cand["dominios"]) >= len(prev["dominios"]):
                por_id[i] = cand

    can = [por_id[i] for i in sorted(por_id.keys()) if por_id[i]["dominios"]]
    m_can = _medir_pares(can)
    dominios_can = sorted({g for n in can for g in n["dominios"]})
    faltan = sorted(THETA_CANONICO - set(por_id.keys()))
    sin_dominio = sorted(i for i, n in por_id.items() if not n["dominios"])

    u1_proxy = (
        "NO_STAGNANT"
        if m_can.get("pares_novedosos", 0) > 0 or m_op.get("pares_novedosos", 0) > 0
        else "REVISAR"
    )

    return {
        "contenedor": "axiomas",
        "theta_n": m_op["theta_n"],
        "pares_totales": m_op["pares_totales"],
        "pares_compatibles": m_op["pares_compatibles"],
        "pares_novedosos": m_op["pares_novedosos"],
        "im_vs_theta": m_op["im_vs_theta"],
        "dominios": dominios_op,
        "u1_proxy": u1_proxy,
        "errores_recoleccion": len(errores),
        "por_tipo_theta": {
            "axioma": sum(1 for n in oper if n["tipo"] == "axioma"),
            "teorema": sum(1 for n in oper if n["tipo"] == "teorema"),
        },
        "canonica": {
            **m_can,
            "ids_presentes": sorted(por_id.keys()),
            "ids_faltantes": faltan,
            "ids_sin_dominio": sin_dominio,
            "dominios": dominios_can,
            "objetivo_paper": {
                "theta_n": 24,
                "im_esperada": 153,
                "nota": "|Im(⊕)|=153 > 24=|Θ| en enumeración del texto",
            },
        },
        "ids_dominio_k_o": ids_dominio_k_o(),
        "nota": (
            "Capa operativa = grafo del repo. "
            "Capa canonica = solo ids TR1 del paper. "
            "Dominio O/K: ver ids_dominio_k_o y cuerpos (no se clasifica entrada aquí)."
        ),
    }


# ===============================================================
# Contrato
# ===============================================================
CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX",
    "version": "9.5",
    "requiere": [],
    "descripcion": (
        "Contenedor de axiomas. Rol AX. "
        "Define y vigila axiomas, lemas, teoremas y corolarios. "
        "No calcula Tru_total. No clasifica O de entrada (CX). "
        "Mide generatividad TR1 sobre su propio cuerpo. "
        "Expone ids de dominio K/O ya cargados en el grafo."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "axiomas": axiomas,
        "generatividad": generatividad,
    },
}


__all__ = [
    "CONTENEDOR",
    "AXIOMA",
    "LEMA",
    "TEOREMA",
    "COROLARIO",
    "DEFINICION",
    "TIPOS",
    "normalizar",
    "clave",
    "ref",
    "recolectar",
    "por_dominio",
    "ids_dominio_k_o",
    "declaraciones",
    "axiomas",
    "contradiccion_directa",
    "contradiccion_de_cota",
    "barrer",
    "verificar_salida",
    "inventario",
    "generatividad",
]
