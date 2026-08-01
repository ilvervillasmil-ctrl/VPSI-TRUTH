from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List
from core.diagnostico import DiagnosticoGlobal  # Integración con Diagnostics

from .acceso import Canal, hay_acceso, hay_dns, HAY_REQUESTS

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
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            registro[f.name] = {
                "archivo": f.name,
                "error": f"{type(e).__name__}: {e}",
            }
            continue

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
# ENGINE (Orquestador del módulo / filtro)
# ===============================================================

def barrer() -> Dict[str, Any]:
    """
    Filtro de paso al Engine. Orquesta la lógica del módulo:
    1. Descubre funciones en la carpeta.
    2. Comprueba que no se contradigan entre sí.
    3. Carpeta vacía = vacío legítimo (aún no hay anclas montadas).

    No calcula Tru_total. Eso corresponde a CA / FO.
    El Engine solo ejecuta lo que el CONTENEDOR de este módulo declara.
    """
    hallado = _descubrir()
    choques: List[str] = []
    errores: List[str] = []
    notas: List[str] = []

    # Validar que cada declaración tenga las claves requeridas
    for archivo, meta in sorted(hallado.items()):
        if "error" in meta:
            errores.append(f"{archivo}: {meta['error']}")
            continue
        for clave in CLAVES_FUNCION:
            if not meta.get(clave):
                errores.append(f"{archivo}: FUNCION sin '{clave}'")

    # Validar unicidad: dos archivos no pueden reclamar la misma función
    por_nombre: Dict[str, List[str]] = {}
    for archivo, meta in sorted(hallado.items()):
        if "error" in meta:
            continue
        n = meta.get("nombre")
        if n:
            por_nombre.setdefault(n, []).append(archivo)

    for nombre, archivos in sorted(por_nombre.items()):
        if len(archivos) > 1:
            choques.append(
                f"funcion '{nombre}' reclamada por {archivos}: "
                "no se sabe cuál responde"
            )

    # Carpeta vacía: vacío legítimo, no error por vacuidad
    if not hallado:
        notas.append("ninguna funcion declarada todavía (vacío legítimo)")

    # Enviar reporte a DiagnosticoGlobal si hay choques o errores (Reporte Omega)
    if choques or errores:
        DiagnosticoGlobal.recibir_reporte(
            modulo="realidad",
            errores=(
                [{"tipo": "choque", "detalle": choque} for choque in choques]
                + [{"tipo": "error", "detalle": error} for error in errores]
            ),
        )

    return {
        "contenedor": "realidad",
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "funciones": sorted(por_nombre),
        "notas": notas,
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
    return bool(salida.get("coherente", False))


# ===============================================================
# INTROSPECCIÓN
# ===============================================================

def inventario() -> Dict[str, Any]:
    """Devuelve un resumen de las funciones descubiertas."""
    hallado = _descubrir()
    return {
        "contenedor": "realidad",
        "version": "1.0",
        "funciones": {
            m["nombre"]: m
            for m in hallado.values()
            if m.get("nombre") and "error" not in m
        },
    }


# ===============================================================
# CONTENEDOR (Contrato del módulo — al final, funciones ya definidas)
# ===============================================================
# Contrato literal para el Engine:
# conoce este mapa y solo actúa según lo que aquí se declara.
CONTENEDOR = {
    "nombre": "realidad",
    "rol": "RE",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Contenedor de realidad. Rol RE. "
        "Ancla de lo establecido y filtro de funciones únicas. "
        "Descubre funciones en la carpeta y comprueba que no se contradigan entre sí. "
        "Si hay contradicción interna, no pasa hacia arriba. "
        "No calcula Tru_total (eso es CA/FO). "
        "El Engine no tiene poder propio: ejecuta solo lo que este contrato declara."
    ),
    "capacidades": {
        "verificar": barrer,
        "inventario": inventario,
    },
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
