"""
VPSI-TRUTH  ---  modules/correlacion_mecanica

Contenedor de mecanica. Rol MC.

======================================================================
Este archivo es el filtro. Lee los archivos de la carpeta en su orden
nativo, calcula la mecanica que resulta de lo que ellos mismos dicen,
y comprueba una sola cosa: que no se contradigan entre si.

No exige. No dispone. No ordena. No completa lo que falte. No elige
entre dos versiones. Si dos archivos colisionan sobre un mismo nodo,
no pasa nadie, y el filtro reporta exactamente los identificadores en
desacuerdo: el arreglo es de ellos.

Las reglas del propio filtro estan declaradas abajo y entran al
barrido general. El filtro que hace cumplir los axiomas tampoco se
escapa de los axiomas.
======================================================================
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

CONTENEDOR = {
    "nombre": "correlacion_mecanica",
    "rol": "MC",
    "version": "1.0",
    "requiere": [],
}

_DIR = Path(__file__).parent

APROBADO = "APROBADO"
RECHAZADO = "RECHAZADO"

# ===============================================================
# SEGMENTO 1 --- DECLARACIONES DEL FILTRO
# ===============================================================

DECLARACIONES = [
    {
        "id": "CORR_SEQ_01",
        "tipo": "axioma",
        "sujeto": "mecanica_declarada",
        "relacion": "se_lee_en",
        "objeto": "orden_nativo",
        "polaridad": True,
        "cota": None,
        "depende_de": [],
        "gobierna": ["correlacion_mecanica"],
        "enunciado": (
            "Principio de Secuencia Transversal: los objetos de la carpeta "
            "se leen en su orden nativo para verificar que la transicion "
            "entre estados cumpla la continuidad causal."
        ),
    },
    {
        "id": "CORR_SEQ_02",
        "tipo": "axioma",
        "sujeto": "colision_sobre_un_nodo",
        "relacion": "permite_el_paso",
        "objeto": "mecanica",
        "polaridad": False,
        "cota": None,
        "depende_de": ["CORR_SEQ_01"],
        "gobierna": ["correlacion_mecanica"],
        "enunciado": (
            "Criterio de No Contradiccion Cruzada: si dos declaraciones de "
            "archivos distintos colisionan sobre el mismo nodo, el paso se "
            "bloquea y se reportan los identificadores en desacuerdo."
        ),
    },
]


def axiomas() -> List[Dict[str, Any]]:
    """Declaraciones del contenedor para el barrido general."""
    return DECLARACIONES

# ===============================================================
# SEGMENTO 2 --- LECTURA EN ORDEN NATIVO
# ===============================================================

def _leer() -> Dict[str, Any]:
    """
    Recoge lo que cada archivo declara en MECANICA, sin exigirle forma:
    se lee lo que hay.
    """
    hallado: Dict[str, Any] = {}
    for f in sorted(_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        clave = f"mecanica_{f.stem}"
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)

        meta = getattr(mod, "MECANICA", None)
        if isinstance(meta, dict):
            hallado[f.name] = meta
    return hallado


def _nodos(meta: Dict[str, Any]) -> List[str]:
    """El orden nativo de un archivo: la secuencia tal como viene."""
    orden = meta.get("orden")
    if isinstance(orden, (list, tuple)):
        return [str(x) for x in orden]
    return []


def _precedencias(nodos: List[str]) -> List[Tuple[str, str]]:
    """Del orden nativo salen todos los pares 'antes de'."""
    return [(a, b) for i, a in enumerate(nodos) for b in nodos[i + 1:]]

# ===============================================================
# SEGMENTO 3 --- FILTRO
# ===============================================================

def barrer() -> Dict[str, Any]:
    """
    Calcula la mecanica y comprueba que los archivos no colisionen.
    No lanza: informa.

    estado == RECHAZADO  =>  la mecanica no cruza hacia el Engine.
    """
    hallado = _leer()
    choques: List[str] = []
    errores: List[str] = []

    if not hallado:
        errores.append("ninguna mecanica declarada")
        return _informe([], choques, errores, {})

    # quien dice que un nodo va antes de otro
    precede: Dict[Tuple[str, str], List[str]] = {}
    for archivo, meta in sorted(hallado.items()):
        nodos = _nodos(meta)
        if len(nodos) < 2:
            errores.append(f"{archivo}: sin orden nativo legible")
            continue
        for a, b in _precedencias(nodos):
            precede.setdefault((a, b), []).append(archivo)

    # CORR_SEQ_02: colision sobre el mismo nodo
    for (a, b), quienes in sorted(precede.items()):
        contrarios = precede.get((b, a))
        if contrarios and (a, b) < (b, a):
            choques.append(
                f"nodo '{a}'/'{b}': {quienes} lo ponen en un orden y "
                f"{contrarios} en el contrario"
            )

    # CORR_SEQ_01: continuidad causal, sin secuencia que se muerda la cola
    universo = {x for par in precede for x in par}
    pendientes = set(universo)
    mecanica: List[str] = []
    while pendientes:
        libres = sorted(
            n for n in pendientes
            if not any((o, n) in precede for o in pendientes if o != n)
        )
        if not libres:
            choques.append(
                f"nodos {sorted(pendientes)}: la secuencia se muerde la cola, "
                "no hay orden posible"
            )
            break
        mecanica.extend(libres)
        pendientes -= set(libres)

    return _informe(mecanica, choques, errores, hallado)


def _informe(mecanica, choques, errores, hallado) -> Dict[str, Any]:
    limpio = not (choques or errores)
    return {
        "contenedor": CONTENEDOR["nombre"],
        "estado": APROBADO if limpio else RECHAZADO,
        "coherente": limpio,
        "choques": choques,
        "errores": errores,
        "mecanica": mecanica if limpio else [],
        "archivos": sorted(hallado),
    }

# ===============================================================
# SEGMENTO 4 --- INTROSPECCION
# ===============================================================

def inventario() -> Dict[str, Any]:
    hallado = _leer()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "declaraciones": len(DECLARACIONES),
        "archivos": sorted(hallado),
        "declaran": {a: m.get("nombre") for a, m in sorted(hallado.items())},
    }

# ===============================================================
# SEGMENTO 5 --- EXPORTACION
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "DECLARACIONES", "axiomas",
    "barrer", "inventario",
    "APROBADO", "RECHAZADO",
]
