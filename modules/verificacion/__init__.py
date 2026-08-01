from .auditor import AuditorAxiomatico
from core.diagnostico import DiagnosticoGlobal  # Integración con Diagnostics

# ===============================================================
# CONTENEDOR (Contrato del módulo)
# ===============================================================
CONTENEDOR = {
    "nombre": "verificacion",
    "rol": "VX",  # Rol de verificación y auto-auditoría transversal
    "version": "1.0.0",
    "requiere": ["codigo_fuente", "declaraciones_axiomaticas"],
    "descripcion": (
        "Contenedor de verificación. Rol VX. "
        "Auto-ejecutor de contraste axiomático sobre código y contenedores."
    ),
    "capacidades": {
        "verificar": "auditar_sistema",  # Capacidad para auditar el sistema
        "axiomas": "axiomas",           # Devuelve axiomas del módulo
    }
}

# ===============================================================
# ENGINE (Orquestador)
# ===============================================================
def auditar_sistema(base: dict) -> dict:
    """
    Función expuesta para auditar código fuente contra axiomas.
    Orquesta la lógica del módulo:
    1. Ejecuta el barrido transversal usando AuditorAxiomatico.
    2. Retorna el resultado de la auditoría.
    """
    auditor = AuditorAxiomatico()
    resultado = auditor.ejecutar_barrido_transversal(
        base.get("codigo_fuente", {}),
        base.get("declaraciones_axiomaticas", {})
    )

    # Enviar reporte a DiagnosticoGlobal si hay errores (Reporte Omega)
    if not resultado.get("coherente", True):
        DiagnosticoGlobal.recibir_reporte(
            modulo="verificacion",
            errores=[{"tipo": "error_auditoria", "detalle": error} for error in resultado.get("errores", [])]
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
    return salida.get("coherente", False)

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
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "CONTENEDOR",
    "auditar_sistema",
    "axiomas",
    "verificar_salida",  # Nueva función para el Centinela
]
