# VPSI-TRUTH / modules/verificacion/__init__.py

from .auditor import AuditorAxiomatico

CONTENEDOR = {
    "nombre": "verificacion",
    "rol": "VX",  # Rol de verificación y auto-auditoría transversal
    "version": "1.0.0",
    "requiere": ["codigo_fuente", "declaraciones_axiomaticas"],
    "descripcion": "Auto-ejecutor de contraste axiomático sobre código y contenedores.",
}

def auditar_sistema(base: dict) -> dict:
    """Función expuesta para auditar código fuente contra axiomas."""
    auditor = AuditorAxiomatico()
    return auditor.ejecutar_barrido_transversal(
        base.get("codigo_fuente", {}),
        base.get("declaraciones_axiomaticas", {})
    )

def axiomas() -> list:
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
