"""
VPSI-TRUTH --- modules/diagnostico

Rol DG: fachada / enlace a core.diagnostico.

No calcula Tru. No orquesta. No duplica el censo.
Expone al Engine las funciones ya establecidas en core.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.diagnostico import (
    DiagnosticoGlobal,
    DiagnosticoError,
    PESOS,
    barrer_diagnostico,
)

# ===============================================================
# CONTENEDOR (contrato Engine)
# ===============================================================
CONTENEDOR = {
    "nombre": "diagnostico",
    "rol": "DG",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Enlace al diagnóstico global de core. Solo lectura / recepción de "
        "reportes de módulos. Cero actuación sobre Engine o negocio."
    ),
    "capacidades": {
        "censo": "censo",
        "verificar": "verificar",
        "barrer": "verificar",
        "presentar": "presentar",
        "reportar": "reportar",
        "inventario": "inventario",
    },
}


# ===============================================================
# Puente (delega en core)
# ===============================================================
def censo(engine: Any = None, **kwargs: Any) -> Dict[str, Any]:
    """Requiere engine; mismo contrato que DiagnosticoGlobal.censo."""
    if engine is None:
        return {
            "tipo": "diagnostico_global",
            "estado": "UNDEFINED",
            "razon": "censo DG requiere instancia Engine",
        }
    return DiagnosticoGlobal.censo(engine, **kwargs)


def verificar(engine: Any = None, **kwargs: Any) -> Dict[str, Any]:
    """Capacidad de compuerta: informe de solo lectura."""
    out = censo(engine, **kwargs)
    if isinstance(out, dict) and "pct_global" in out:
        out = dict(out)
        out["coherente"] = True  # DG no invalida arranque; solo observa
    return out


def presentar(informe: Optional[Dict[str, Any]] = None, **kwargs: Any) -> str:
    if informe is None:
        return "[DG] sin informe"
    return DiagnosticoGlobal.presentar(informe)


def reportar(modulo: str = "", errores: Optional[List] = None, **kwargs: Any) -> bool:
    """Enlace a DiagnosticoGlobal.recibir_reporte (core)."""
    fn = getattr(DiagnosticoGlobal, "recibir_reporte", None)
    if not callable(fn):
        return False
    return bool(fn(modulo=modulo, errores=errores, **kwargs))


def inventario() -> Dict[str, Any]:
    return {
        "contenedor": CONTENEDOR["nombre"],
        "rol": CONTENEDOR["rol"],
        "version": CONTENEDOR["version"],
        "core": "core.diagnostico.DiagnosticoGlobal",
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "pesos": dict(PESOS),
        "nota": "Enlace puro; lógica canónica en core/diagnostico.py",
    }


# Reexport explícito (quien importe el módulo DG ve el core)
__all__ = [
    "CONTENEDOR",
    "DiagnosticoGlobal",
    "DiagnosticoError",
    "PESOS",
    "barrer_diagnostico",
    "censo",
    "verificar",
    "presentar",
    "reportar",
    "inventario",
]
