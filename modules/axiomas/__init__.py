"""
VPSI-TRUTH — modules/axiomas/__init__.py

Contenedor de axiomas. Rol AX.

Qué es:
  Vigila declaraciones (axioma | lema | teorema | corolario | definicion).
  No pertenece a ninguna teoría. No calcula Tru_total.

Qué vigila:
  - contradiccion_directa
  - contradiccion_de_cota
  Si hay choque o error de carga → coherente=False.

Capacidades de contrato:
  verificar, inventario, axiomas, generatividad (TR1/U1).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# DiagnosticoGlobal es opcional: no debe tumbar el arranque de AX
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


# ===============================================================
# Carga desde archivos planos / VPSI.py
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
# Recolección unificada (usada por barrer / inventario / generatividad)
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
    """
    Capacidad principal: coherencia axiomática del cuerpo.
    """
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
    }


def verificar_salida(salida: Dict) -> bool:
    return bool(salida.get("coherente", False))


def declaraciones(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    """
    Capacidad 'axiomas': lista normalizada si el cuerpo es coherente.
    Si no es coherente → lista vacía (fail-closed de exposición).
    """
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
        "version": "9.4",
        "tipos": list(TIPOS),
        "declaraciones": len(decls),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS},
        "cuerpos": sorted({d["cuerpo"] for d in decls}),
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
    }


def generatividad() -> Dict:
    """
    TR1 sobre el cuerpo de declaraciones AX.
    Dominio D_i = set(gobierna).
    Compatible si D_i ∩ D_j ≠ ∅.
    Novedoso si D_i ∪ D_j ⊃ D_i y ⊃ D_j.
    U1 proxy: novedad > 0 ⇒ NO_STAGNANT.
    """
    decls, errores = recolectar()
    theta = [
        d for d in decls
        if d.get("tipo") in ("teorema", "axioma") and d.get("gobierna")
    ]
    n = len(theta)
    pares_tot = n * (n - 1) // 2 if n >= 2 else 0
    compatibles = 0
    novedosos = 0
    dominios = sorted({g for d in theta for g in (d.get("gobierna") or [])})

    for i in range(n):
        Di = set(theta[i].get("gobierna") or [])
        for j in range(i + 1, n):
            Dj = set(theta[j].get("gobierna") or [])
            if not (Di & Dj):
                continue
            compatibles += 1
            union = Di | Dj
            if union > Di and union > Dj:
                novedosos += 1

    return {
        "contenedor": "axiomas",
        "theta_n": n,
        "pares_totales": pares_tot,
        "pares_compatibles": compatibles,
        "pares_novedosos": novedosos,
        "im_vs_theta": "GENERATIVO" if novedosos > n else "ESTANCADO",
        "u1_proxy": "NO_STAGNANT" if novedosos > 0 else "REVISAR",
        "dominios": dominios,
        "errores_recoleccion": len(errores),
        "por_tipo_theta": {
            t: sum(1 for d in theta if d["tipo"] == t)
            for t in ("axioma", "teorema")
        },
        "nota": (
            "Medición estructural TR1 sobre declaraciones AX. "
            "Sin interpretación. Tru_total lo calculan CA/FO."
        ),
    }


# ===============================================================
# Contrato (AL FINAL: todas las funciones ya existen)
# ===============================================================
CONTENEDOR = {
    "nombre": "axiomas",
    "rol": "AX",
    "version": "9.4",
    "requiere": [],
    "descripcion": (
        "Contenedor de axiomas. Rol AX. "
        "Define y vigila axiomas, lemas, teoremas y corolarios. "
        "No calcula Tru_total. Mide generatividad TR1 sobre su propio cuerpo."
    ),
    "capacidades": {
        "verificar": barrer,
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
    "declaraciones",
    "axiomas",
    "contradiccion_directa",
    "contradiccion_de_cota",
    "barrer",
    "verificar_salida",
    "inventario",
    "generatividad",
]
