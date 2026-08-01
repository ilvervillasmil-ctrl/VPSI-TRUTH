from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List
from core.diagnostico import DiagnosticoGlobal  # Integración con Diagnostics

from .acceso import Canal, hay_acceso, hay_dns, HAY_REQUESTS

# ===============================================================
# CONTENEDOR (Contrato del módulo)
# ===============================================================
CONTENEDOR = {
    "nombre": "realidad",
    "rol": "RE",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Contenedor de realidad. Rol RE. "
        "Filtro de funciones únicas. Descubre funciones en la carpeta y "
        "comprueba que no se contradigan entre sí."
    ),
    "capacidades": {
        "verificar": barrer,
        "inventario": inventario,
    },
}

_DIR = Path(__file__).parent

CLAVES_FUNCION = ("nombre", "hace")

# ===============================================================
# DESCUBRIMIENTO (Engine: Lógica interna)
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
# ENGINE (Orquestador)
# ===============================================================

def barrer() -> Dict[str, Any]:
    """
    Filtro de paso al Engine. Orquesta la lógica del módulo:
    1. Descubre funciones en la carpeta.
    2. Comprueba que no se contradigan entre sí.
    """
    hallado = _descubrir()
    choques: List[str] = []
    errores: List[str] = []

    # Validar que cada declaración tenga las claves requeridas
    for archivo, meta in sorted(hallado.items()):
        for clave in CLAVES_FUNCION:
            if not meta.get(clave):
                errores.append(f"{archivo}: FUNCION sin '{clave}'")

    # Validar unicidad: dos archivos no pueden reclamar la misma función
    por_nombre: Dict[str, List[str]] = {}
    for archivo, meta in sorted(hallado.items()):
        n = meta.get("nombre")
        if n:
            por_nombre.setdefault(n, []).append(archivo)

    for nombre, archivos in sorted(por_nombre.items()):
        if len(archivos) > 1:
            choques.append(
                f"funcion '{nombre}' reclamada por {archivos}: "
                "no se sabe cuál responde"
            )

    # Validar piso: una carpeta vacía es coherente con todo
    if not hallado:
        errores.append("ninguna funcion declarada: coherente por vacuidad")

    # Enviar reporte a DiagnosticoGlobal si hay choques o errores (Reporte Omega)
    if choques or errores:
        DiagnosticoGlobal.recibir_reporte(
            modulo="realidad",
            errores=[{"tipo": "choque", "detalle": choque} for choque in choques] +
                    [{"tipo": "error", "detalle": error} for error in errores]
        )

    return {
        "contenedor": CONTENEDOR["nombre"],
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "funciones": sorted(por_nombre),
    }

# ===============================================================
# CENTINELA (Eyenet)
# ===============================================================

def verificar_salida(salida: Dict[str, Any]) -> bool:
    """
    Valida la salida del Engine (barrer).
    - Si la salida es coherente, devuelve True.
    - Si no lo es, ya se envió un reporte a DiagnosticoGlobal en barrer().
    """
    return salida.get("coherente", False)

# ===============================================================
# INTROSPECCIÓN
# ===============================================================

def inventario() -> Dict[str, Any]:
    """Devuelve un resumen de las funciones descubiertas."""
    hallado = _descubrir()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "funciones": {m["nombre"]: m for m in hallado.values() if m.get("nombre")},
    }

# ===============================================================
# EXPORTACIÓN
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "Canal", "hay_acceso", "hay_dns", "HAY_REQUESTS",
    "barrer",
    "inventario",
    "verificar_salida",  # Nueva función para el Centinela
]
