# -*- coding: utf-8 -*-
"""
modules/tru_totales/__init__.py
===============================

Módulo VPSI-TRUTH — Tru totales

CONTRATO (leer primero)
-----------------------
Aquí están las *capacidades de categorías* de alcance de Tru_Ri y Tru_total.

  Utilícenlas cuando quieran.

  - Este módulo NO calcula.
  - Este módulo NO orquesta.
  - Este módulo NO tiene voz ni voto sobre el pedido.
  - Solo expone el catálogo ordenado de escalas evaluables.

Quién hace qué
--------------
  Omega Report
      Pide mostrar un total (p.ej. «Tru total del sujeto», «Tru de la frase»).
      No calcula: declara qué quiere ver.

  Engine
      Lee este catálogo, junta O (CX) + segmentos + pedido,
      y orquesta el ciclo hacia conteos y Calculator.

  CX
      Fija el contexto O.

  conteos
      Cuenta sobre el segmento pedido bajo ese O.

  Calculator (CA)
      Aplica las fórmulas que ya tiene (C, L, K, Tru_Ri, Tru_total con α, β).
      Calcula lo que Engine le diga: una letra, una frase, S_i, el diálogo, …

  tru_totales (este módulo)
      Catálogo pasivo: «existen estas categorías; esta es su unidad;
      esto es lo que requieren como material».
      Cero voluntad. Cero aritmética. Cero imports de cálculo.

Flujo típico (automático para el usuario del repo)
-------------------------------------------------
  1. Omega / petición: «Tru total del sujeto» / «Tru de la conversación» / …
  2. Engine consulta este INIT → resuelve la categoría del catálogo.
  3. CX aporta O; se segmenta el material (S_1…S_N si aplica).
  4. conteos + CA calculan bajo ese O y ese segmento.
  5. Omega muestra el Tru_Ri / Tru_total pedido.

El usuario del framework no arma el ciclo a mano: el contrato de este
INIT es lo suficientemente explícito para que Engine sepa *qué categorías
existen* y Calculator sepa *qué le están pidiendo calcular*.

Extensión
---------
  Agregar o editar un archivo en categorias/*.py.
  Este INIT los lee solo. No hace falta modificar el INIT para una
  categoría nueva (mismo patrón que axiomas/ y contexto/).

Prohibido en este módulo y en categorias/
-----------------------------------------
  - import de calculator / fórmulas / conteos con fin de calcular
  - valores numéricos de Tru, C, L, K
  - algoritmos de agregación
  - nombres propios de sujetos (usar S_i; Engine asigna María/Carlo/…)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DIR = Path(__file__).parent
_CAT_DIR = _DIR / "categorias"

__version__ = "1.1"

# Contrato de forma de cada categoría (centinela).
# Todos los archivos de categorias/ deben poder normalizarse a esto.
_CAMPOS_OBLIGATORIOS = (
    "id",           # tru_atomo | tru_frase | tru_sujeto | …
    "nombre",       # etiqueta legible
    "unidad",       # qué material cubre
    "enunciado",    # definición operativa del alcance
)

_CAMPOS_OPCIONALES_CONOCIDOS = (
    "nivel_fractal",       # 1..n orden de escala (no constante geométrica)
    "requiere",            # material / O / segmentos (lista de strings)
    "factores_evaluables", # p.ej. ["Tru_Ri", "Tru_total"]
    "agrega_desde",        # ids de escala inferior (declarativo, no algoritmo)
    "senales",             # prosa que resolver_pedido reconoce
    "anclas",              # ids AX/CX de referencia
    "version",
    "notas",
)


# ---------------------------------------------------------------------------
# Carga: lee todas las categorías debajo
# ---------------------------------------------------------------------------
def _cargar_desde_archivo(archivo: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    errores: List[str] = []
    if archivo.name.startswith("_") or archivo.name == "__init__.py":
        return [], errores

    nombre_mod = f"tru_totales_cat_{archivo.stem}"
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return [], [f"{archivo.name}: no se pudo crear spec"]

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001
        return [], [f"{archivo.name}: import {type(e).__name__}: {e}"]

    halladas: List[Dict[str, Any]] = []
    una = getattr(mod, "CATEGORIA", None)
    if isinstance(una, dict):
        halladas.append(una)
    varias = getattr(mod, "CATEGORIAS", None)
    if isinstance(varias, list):
        for item in varias:
            if isinstance(item, dict):
                halladas.append(item)
    if not halladas:
        for attr in ("DECLARACION", "declaracion", "TOTAL"):
            val = getattr(mod, attr, None)
            if isinstance(val, dict):
                halladas.append(val)
                break
    if not halladas:
        errores.append(f"{archivo.name}: sin CATEGORIA/CATEGORIAS exportada")
    return halladas, errores


def _validar_categoria(cat: Dict[str, Any], origen: str) -> List[str]:
    errs: List[str] = []
    for k in _CAMPOS_OBLIGATORIOS:
        if k not in cat or not str(cat.get(k, "")).strip():
            errs.append(f"{origen}: falta campo obligatorio '{k}'")

    # Oficio prohibido: traer números de Tru/C/L/K
    for prohibido in ("Tru_Ri", "Tru_total", "tru_ri", "tru_total", "C", "L", "K"):
        if prohibido in cat and cat[prohibido] is not None:
            if prohibido in ("C", "L", "K") and isinstance(cat.get(prohibido), bool):
                continue
            errs.append(
                f"{origen}: no debe traer valor '{prohibido}' "
                f"(oficio Calculator; tru_totales solo cataloga)"
            )
    return errs


def _normalizar(cat: Dict[str, Any], origen: str) -> Dict[str, Any]:
    factores = cat.get("factores_evaluables") or ["Tru_Ri", "Tru_total"]
    if not isinstance(factores, list):
        factores = ["Tru_Ri", "Tru_total"]

    nivel = cat.get("nivel_fractal")
    try:
        nivel_n = int(nivel) if nivel is not None else None
    except (TypeError, ValueError):
        nivel_n = None

    return {
        "id": str(cat["id"]).strip().lower(),
        "nombre": str(cat["nombre"]).strip(),
        "unidad": str(cat["unidad"]).strip(),
        "enunciado": str(cat["enunciado"]).strip(),
        "nivel_fractal": nivel_n,
        "requiere": [str(x) for x in (cat.get("requiere") or [])],
        "factores_evaluables": [str(x) for x in factores],
        "agrega_desde": [str(x) for x in (cat.get("agrega_desde") or [])],
        "senales": [str(x).lower() for x in (cat.get("senales") or [])],
        "anclas": [str(x) for x in (cat.get("anclas") or [])],
        "origen": origen,
        "version": str(cat.get("version") or "1.0"),
        "notas": str(cat.get("notas") or ""),
    }


def recolectar() -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Lee categorias/*.py (y *.py no privados en la raíz del módulo).
    Retorna (categorías normalizadas, errores de forma/carga).
    """
    cats: List[Dict[str, Any]] = []
    errores: List[Dict[str, str]] = []
    archivos: List[Path] = []

    if _CAT_DIR.is_dir():
        archivos.extend(sorted(_CAT_DIR.glob("*.py")))
    archivos.extend(sorted(_DIR.glob("*.py")))

    vistos: set = set()
    for archivo in archivos:
        if archivo.name == "__init__.py" or archivo.name.startswith("_"):
            continue
        key = str(archivo.resolve())
        if key in vistos:
            continue
        vistos.add(key)

        halladas, errs = _cargar_desde_archivo(archivo)
        for e in errs:
            errores.append({"archivo": archivo.name, "error": e})
        for raw in halladas:
            ve = _validar_categoria(raw, archivo.name)
            if ve:
                for e in ve:
                    errores.append({"archivo": archivo.name, "error": e})
                continue
            try:
                cats.append(_normalizar(raw, archivo.stem))
            except Exception as e:  # noqa: BLE001
                errores.append({
                    "archivo": archivo.name,
                    "error": f"normalizar: {type(e).__name__}: {e}",
                })

    por_id: Dict[str, List[str]] = {}
    for c in cats:
        por_id.setdefault(c["id"], []).append(c["origen"])
    for cid, origenes in por_id.items():
        if len(origenes) > 1:
            errores.append({
                "archivo": ",".join(origenes),
                "error": f"id duplicado '{cid}' en {origenes}",
            })

    # orden estable por nivel_fractal luego id
    cats.sort(key=lambda c: (c["nivel_fractal"] is None, c["nivel_fractal"] or 0, c["id"]))
    return cats, errores


def barrer() -> Dict[str, Any]:
    """Coherencia del catálogo. No calcula Tru."""
    cats, errores = recolectar()
    return {
        "coherente": not errores,
        "categorias": len(cats),
        "ids": [c["id"] for c in cats],
        "errores": errores,
        "version": __version__,
        "contrato": (
            "Catálogo pasivo de alcances Tru_Ri/Tru_total. "
            "Engine/Omega usan; Calculator calcula; este módulo no calcula."
        ),
    }


def categorias() -> List[Dict[str, Any]]:
    """Lista del catálogo si coherente; si no → []."""
    r = barrer()
    if not r["coherente"]:
        return []
    cats, _ = recolectar()
    return cats


def por_id(cat_id: str) -> Optional[Dict[str, Any]]:
    key = str(cat_id or "").strip().lower()
    for c in categorias():
        if c["id"] == key:
            return dict(c)
    return None


def ids() -> List[str]:
    return [c["id"] for c in categorias()]


def es_valida(cat_id: str) -> bool:
    return str(cat_id or "").strip().lower() in set(ids())


def capacidades() -> Dict[str, Any]:
    """
    Vista explícita para Engine/Omega:

      «Aquí están las capacidades de categorías; utilícenlas cuando quieran.»
    """
    cats, errores = recolectar()
    return {
        "modulo": "tru_totales",
        "version": __version__,
        "mensaje": (
            "Capacidades de categorías de Tru_Ri y Tru_total. "
            "Úsenlas cuando quieran. Este módulo no calcula."
        ),
        "como_usar": (
            "Omega declara el total a mostrar; Engine resuelve la categoría "
            "con resolver_pedido / por_id; CX aporta O; conteos + Calculator "
            "aplican la fórmula sobre el segmento."
        ),
        "categorias": [
            {
                "id": c["id"],
                "nombre": c["nombre"],
                "unidad": c["unidad"],
                "nivel_fractal": c["nivel_fractal"],
                "factores_evaluables": c["factores_evaluables"],
                "requiere": c["requiere"],
            }
            for c in cats
        ],
        "total": len(cats),
        "coherente": not errores,
        "errores": errores,
    }


def inventario(peticion: Any = None) -> Dict[str, Any]:
    caps = capacidades()
    return {
        "contenedor": "tru_totales",
        "version": __version__,
        "rol": "TT",
        "funcion": (
            "Catálogo pasivo de categorías de alcance de Tru_Ri / Tru_total. "
            "Auto-carga categorias/*.py. No calcula. No orquesta. "
            "Engine y Omega utilizan las capacidades cuando las necesitan."
        ),
        "capacidades": caps,
        "extension": (
            "Editar o agregar un archivo en categorias/ sin tocar este INIT."
        ),
        "formula_referencia": (
            "Tru_Ri = C·L·K ; Tru_total = Tru_Ri·α + β — las aplica Calculator, "
            "no este módulo."
        ),
    }


def resolver_pedido(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Normaliza un pedido de Omega/Engine a una categoría del catálogo.
    No calcula. No orquesta.
    """
    peticion = dict(peticion or {})
    cats, errores = recolectar()
    if errores and not cats:
        return {
            "ok": False,
            "error": "modulo_incoherente",
            "errores": errores,
            "mensajes": ["Catálogo incoherente; no hay categorías cargadas."],
        }

    # SECCIÓN CORREGIDA: Sincronización de vocabulario con CE y Engine
    raw_id = (
        peticion.get("escala_id") or 
        peticion.get("categoria_tru") or 
        peticion.get("categoria") or 
        peticion.get("tipo_total") or 
        peticion.get("id")
    )
    
    if raw_id and es_valida(str(raw_id)):
        meta = por_id(str(raw_id)) or {}
        return {
            "ok": True,
            "categoria": meta["id"],
            "nombre": meta.get("nombre"),
            "unidad": meta.get("unidad"),
            "nivel_fractal": meta.get("nivel_fractal"),
            "factores_evaluables": list(meta.get("factores_evaluables") or []),
            "requiere": list(meta.get("requiere") or []),
            "agrega_desde": list(meta.get("agrega_desde") or []),
            "anclas": list(meta.get("anclas") or []),
            "sujeto_indice": peticion.get("sujeto_indice"),  # S_i si Engine lo trae
            "mensajes": [
                f"Categoría '{meta['id']}' disponible. "
                "Engine orquesta; Calculator calcula; tru_totales no calcula."
            ],
        }

    tipos = peticion.get("tipos_total") or peticion.get("categorias")
    if isinstance(tipos, (list, tuple)):
        res = [str(t).strip().lower() for t in tipos if es_valida(str(t))]
        if res:
            return {
                "ok": True,
                "categoria": res[0],
                "categorias": res,
                "multiple": True,
                "mensajes": [
                    "Varias categorías pedidas. Cada una se calcula en su "
                    "segmento/O; sin fusión silenciosa."
                ],
            }

    texto = " ".join(
        str(peticion.get(k) or "")
        for k in ("pedido", "texto", "objetivo", "tarea", "mensaje")
    ).lower()
    for c in cats:
        for s in c.get("senales") or []:
            if s and s in texto:
                return {
                    "ok": True,
                    "categoria": c["id"],
                    "nombre": c.get("nombre"),
                    "unidad": c.get("unidad"),
                    "nivel_fractal": c.get("nivel_fractal"),
                    "factores_evaluables": list(c.get("factores_evaluables") or []),
                    "requiere": list(c.get("requiere") or []),
                    "agrega_desde": list(c.get("agrega_desde") or []),
                    "anclas": list(c.get("anclas") or []),
                    "mensajes": [f"Pedido en prosa → categoría '{c['id']}'."],
                }

    return {
        "ok": False,
        "categoria": None,
        "error": "categoria_no_reconocida",
        "categorias_validas": [c["id"] for c in cats],
        "mensajes": [
            "Categoría no reconocida. "
            f"Catálogo: {', '.join(c['id'] for c in cats) or '(vacío)'}."
        ],
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    if not isinstance(salida, dict) or salida.get("error"):
        return False
    if "coherente" in salida:
        return bool(salida.get("coherente"))
    cat = salida.get("categoria")
    return bool(cat) and es_valida(str(cat))


CONTENEDOR = {
    "nombre": "tru_totales",
    "rol": "TT",
    "version": __version__,
    "requiere": [],  # no impone; el catálogo está disponible para quien lo use
    "descripcion": (
        "Catálogo pasivo de categorías de alcance de Tru_Ri / Tru_total. "
        "Aquí están las capacidades; Engine y Omega las utilizan cuando quieren. "
        "Calculator calcula. Este módulo no calcula ni orquesta. "
        "Auto-carga categorias/*.py."
    ),
    "capacidades": {
        "verificar": barrer,
        "barrer": barrer,
        "inventario": inventario,
        "capacidades": capacidades,
        "categorias": categorias,
        "resolver_pedido": resolver_pedido,
    },
}

__all__ = [
    "CONTENEDOR",
    "recolectar",
    "barrer",
    "categorias",
    "por_id",
    "ids",
    "es_valida",
    "capacidades",
    "inventario",
    "resolver_pedido",
    "verificar_salida",
]
