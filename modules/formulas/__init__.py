"""
VPSI-TRUTH / modules/formulas

Contenedor de fórmulas. Rol FO.
Expone tru_ri y tru_total al Engine. Cada fórmula vive en su propio
archivo y se descubre por el directorio.
"""

import importlib.util
import sys
from pathlib import Path
from fractions import Fraction

# Importar las fórmulas canónicas (REQUERIDO por el rol FO)
from .truth import tru_ri, tru_total

CONTENEDOR = {
    "nombre": "formulas",
    "rol": "FO",
    "version": "1.0",
    "requiere": [],
}

_DIR = Path(__file__).parent

# ===============================================================
# DESCUBRIMIENTO DE FÓRMULAS
# ===============================================================

def _descubrir():
    """
    Descubre todas las fórmulas en el directorio que declaran FORMULA.
    Cada archivo .py (excepto __init__.py) debe definir un diccionario FORMULA.
    """
    registro = {}
    for f in sorted(_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue  # Ignorar __init__.py
        clave = f"formulas_{f.stem}"
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        spec.loader.exec_module(mod)
        meta = getattr(mod, "FORMULA", None)
        if isinstance(meta, dict) and "nombre" in meta:
            registro[meta["nombre"]] = {
                "archivo": f.name,
                "expresion": meta.get("expresion", "No definida"),
                "fuente": meta.get("fuente", "Desconocida"),
            }
    return registro

# ===============================================================
# INVENTARIO
# ===============================================================

def inventario():
    """
    Devuelve el inventario de fórmulas cargadas.
    """
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "formulas": _descubrir(),
    }

# ===============================================================
# AXIOMAS PARA EL BARRIDO AXIOMÁTICO
# ===============================================================

def axiomas():
    """
    Axiomas declarados por este contenedor para el barrido axiomático.
    """
    return [
        {
            "id": "FO-1",
            "tipo": "axioma",
            "sujeto": "Tru_total",
            "relacion": "acotado_superiormente_por",
            "objeto": "ALPHA",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["formulas"],
            "enunciado": "Tru_total(D) ≤ ALPHA (Teorema 16: Structural Ceiling α).",
        },
        {
            "id": "FO-2",
            "tipo": "axioma",
            "sujeto": "Tru_total",
            "relacion": "acotado_inferiormente_por",
            "objeto": "BETA",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["formulas"],
            "enunciado": "Tru_total(D) ≥ BETA (Teorema 17: Impossibility of Total Collapse).",
        },
        {
            "id": "FO-3",
            "tipo": "axioma",
            "sujeto": "Tru_Ri",
            "relacion": "admite_compensacion_entre_factores",
            "objeto": "C_L_K",
            "polaridad": False,
            "cota": None,
            "depende_de": [],
            "gobierna": ["formulas"],
            "enunciado": "Tru_Ri no admite compensación entre C, L, K (TA5: Multiplicatividad).",
        },
    ]

# ===============================================================
# EXPORTACIÓN (REQUERIDO POR EL ROL FO)
# ===============================================================

__all__ = [
    "CONTENEDOR",
    "tru_ri",
    "tru_total",
    "inventario",
    "axiomas",
]
