"""
VPSI-TRUTH  ---  modules/realidad

Contenedor de realidad. Rol RE.

======================================================================
Este archivo es el filtro. No habla de los archivos que hay en la
carpeta: habla de la FUNCION que cada uno cumple.

Cada archivo de la carpeta declara una funcion unica. Hoy hay una:

    acceso.py    conexion a Internet

Manana habra otras. El filtro no cambia por eso: descubre lo que hay,
comprueba que no se contradigan entre si, y solo entonces deja pasar
al Engine.

Contradiccion aqui significa una cosa: dos archivos reclamando la
misma funcion. Si dos declaran hacer lo mismo, no se sabe cual
responde, y lo que cruzaria al Engine seria ambiguo.
======================================================================
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List

from .acceso import Canal, hay_acceso, hay_dns, HAY_REQUESTS

CONTENEDOR = {
    "nombre": "realidad",
    "rol": "RE",
    "version": "1.0",
    "requiere": [],
}

_DIR = Path(__file__).parent

CLAVES_FUNCION = ("nombre", "hace")

# ===============================================================
# DESCUBRIMIENTO
# ===============================================================

def _descubrir() -> Dict[str, Dict[str, Any]]:
    """
    Recorre la carpeta y recoge lo que cada archivo declara en FUNCION.
    Un archivo sin FUNCION no participa: no declara, no pasa.
    """
    registro: Dict[str, Dict[str, Any]] = {}

    for f in sorted(_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        clave = f"realidad_{f.stem}"
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)

        meta = getattr(mod, "FUNCION", None)
        if not isinstance(meta, dict):
            continue

        registro.setdefault(f.name, {
            "archivo": f.name,
            "nombre": meta.get("nombre"),
            "hace": meta.get("hace"),
            "provee": list(meta.get("provee", [])),
        })

    return registro

# ===============================================================
# FILTRO
# ===============================================================

def barrer() -> Dict[str, Any]:
    """
    Filtro de paso al Engine. No lanza: informa.

    coherente == False  =>  realidad no cruza.
    """
    hallado = _descubrir()
    choques: List[str] = []
    errores: List[str] = []

    # forma: cada declaracion completa
    for archivo, meta in sorted(hallado.items()):
        for clave in CLAVES_FUNCION:
            if not meta.get(clave):
                errores.append(f"{archivo}: FUNCION sin '{clave}'")

    # unicidad: dos archivos no pueden reclamar la misma funcion
    por_nombre: Dict[str, List[str]] = {}
    for archivo, meta in sorted(hallado.items()):
        n = meta.get("nombre")
        if n:
            por_nombre.setdefault(n, []).append(archivo)

    for nombre, archivos in sorted(por_nombre.items()):
        if len(archivos) > 1:
            choques.append(
                f"funcion '{nombre}' reclamada por {archivos}: "
                "no se sabe cual responde"
            )

    # piso: una carpeta vacia es coherente con todo
    if not hallado:
        errores.append("ninguna funcion declarada: coherente por vacuidad")

    return {
        "contenedor": CONTENEDOR["nombre"],
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "funciones": sorted(por_nombre),
    }

# ===============================================================
# INTROSPECCION
# ===============================================================

def inventario() -> Dict[str, Any]:
    hallado = _descubrir()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "funciones": {m["nombre"]: m for m in hallado.values() if m.get("nombre")},
    }

# ===============================================================
# EXPORTACION
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "Canal", "hay_acceso", "hay_dns", "HAY_REQUESTS",
    "barrer",
    "inventario",
]
