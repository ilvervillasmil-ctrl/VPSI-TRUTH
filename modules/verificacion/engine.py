"""
VPSI-TRUTH --- modules/verificacion/engine.py

Motor de verificación y auditoría axiomática.

Version: 1.1.0

Oficio único:
    Auditar código fuente y contenedores frente al corpus axiomático,
    integrando el diagnóstico global y la exposición formal de contrato.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .auditor import AuditorAxiomatico
from core.diagnostico import DiagnosticoGlobal  # Integración con Diagnostics


# ===============================================================
# ENGINE (Orquestador)
# ===============================================================
def auditar_sistema(base: dict = None) -> dict:
    """
    Función expuesta para auditar código fuente contra axiomas.
    Orquesta la lógica del módulo:
    1. Ejecuta el barrido transversal usando AuditorAxiomatico.
    2. Retorna el resultado de la auditoría.

    No calcula Tru_total.
    El Engine solo ejecuta lo que el CONTENEDOR de este módulo declara.
    """
    base = base or {}
    auditor = AuditorAxiomatico()
    resultado = auditor.ejecutar_barrido_transversal(
        base.get("codigo_fuente", {}),
        base.get("declaraciones_axiomaticas", {}),
    )

    # Enviar reporte a DiagnosticoGlobal si hay errores (Reporte Omega)
    if not resultado.get("coherente", True):
        DiagnosticoGlobal.recibir_reporte(
            modulo="verificacion",
            errores=[
                {"tipo": "error_auditoria", "detalle": error}
                for error in resultado.get("errores", [])
            ],
        )

    return resultado


# ===============================================================
# CENTINELA (Eyenet)
# ===============================================================
def verificar_salida(salida: dict) -> bool:
    """
    Valida la salida del Engine (auditar_sistema).
    - Si la salida es coherente, devuelve True.
    - Si no lo es, ya se envió un reporte a DiagnosticoGlobal en auditar_sistema().
    """
    return bool(salida.get("coherente", False))


# ===============================================================
# FUNCIÓN axiomas()
# ===============================================================
def axiomas() -> list:
    """Devuelve los axiomas del módulo."""
    return [
        {
            "id": "VX-1",
            "tipo": "axioma",
            "sujeto": "codigo_fuente",
            "relacion": "debe_cumplir",
            "objeto": "corpus_axiomatico",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["verificacion"],
            "enunciado": (
                "Ningún segmento de código o lógica implementada puede violar "
                "las restricciones formales declaradas en los axiomas del sistema."
            ),
        }
    ]


# ===============================================================
# CONTENEDOR (Contrato del módulo — al final, funciones ya definidas)
# ===============================================================
CONTENEDOR = {
    "nombre": "verificacion",
    "rol": "VX",
    "version": "1.1.0",
    "requiere": [],
    "descripcion": (
        "Contenedor de verificación. Rol VX. "
        "Auto-ejecutor de contraste axiomático sobre código y contenedores. "
        "No calcula Tru_total. "
        "El Engine no tiene poder propio: ejecuta solo lo que este contrato declara."
    ),
    "capacidades": {
        "verificar": auditar_sistema,
        "axiomas": axiomas,
    },
}


# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "auditar_sistema",
    "axiomas",
    "verificar_salida",
]
