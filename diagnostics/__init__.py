"""
VPSI-TRUTH --- diagnostics/__init__.py

Módulo para el Omega Report.
- El Engine solo delega la generación del reporte a este módulo.
- La lógica del Omega Report ya está implementada en otros archivos de esta carpeta.
"""

# ===============================================================
# CONTENEDOR: Metadatos para el Engine
# ===============================================================
CONTENEDOR = {
    "nombre": "diagnostic",
    "rol": "DG",  # Rol único para el módulo de diagnóstico
    "version": "1.0",
    "requiere": [],  # No requiere claves específicas en la petición
    "descripcion": "Genera el Omega Report (⟨Ω⟩).",
    "capacidades": {
        "evaluar": "generar_reporte",  # Función que delega a la lógica existente
    }
}

# ===============================================================
# FUNCIÓN QUE DELEGA A LA LÓGICA EXISTENTE
# ===============================================================
def generar_reporte(peticion):
    """
    Función que delega la generación del Omega Report a la lógica ya implementada
    en los archivos de la carpeta diagnostic/.
    """
    # Importar la lógica existente del Omega Report desde otros archivos de diagnostic/
    from .omega_logic import generar_omega_report_completo

    # Delegar la generación del reporte a la función existente
    return generar_omega_report_completo(peticion)
