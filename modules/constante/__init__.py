"""
VPSI-TRUTH --- modules/constante/__init__.py

Contenedor de constantes. Rol CT.

Este módulo expone las constantes geométricas fundamentales del marco VPSI:
- ALPHA = 26/27 (techo estructural).
- BETA  = 1/27  (piso estructural).

Estas constantes son derivadas del cubo 3x3x3 en ℝ³ y son invariantes en todo el sistema.
"""

from fractions import Fraction

# ===============================================================
# CONSTANTES GEOMÉTRICAS (Derivadas del cubo 3x3x3 en ℝ³)
# ===============================================================
ALPHA = Fraction(26, 27)  # Techo estructural: fracción observable del cubo.
BETA  = Fraction(1, 27)   # Piso estructural: fracción interior irreducible del cubo.

# ===============================================================
# CAPACIDADES (funciones que el contrato declara)
# ===============================================================
def get_alpha(peticion=None):
    """Capacidad 'alpha': devuelve la constante ALPHA."""
    return ALPHA

def get_beta(peticion=None):
    """Capacidad 'beta': devuelve la constante BETA."""
    return BETA

def inventario(peticion=None):
    """Capacidad opcional de inventario."""
    return {
        "ALPHA": str(ALPHA),
        "BETA": str(BETA),
        "tipo": "Fraction",
        "origen": "cubo 3x3x3 en ℝ³",
    }

# ===============================================================
# CONTENEDOR: Contrato del módulo
# ===============================================================
CONTENEDOR = {
    "nombre": "constante",
    "rol": "CT",
    "version": "1.0",
    "requiere": [],
    "descripcion": (
        "Expone las constantes geométricas ALPHA y BETA, derivadas del cubo 3x3x3 en ℝ³. "
        "Estas constantes son invariantes y se usan en todos los cálculos de verdad."
    ),
    "capacidades": {
        "alpha": "get_alpha",      # obligatorio para CT
        "beta": "get_beta",        # obligatorio para CT
        "inventario": "inventario", # opcional
    },
}

# ===============================================================
# EXPORTACIÓN
# ===============================================================
__all__ = [
    "ALPHA",
    "BETA",
    "get_alpha",
    "get_beta",
    "inventario",
    "CONTENEDOR",
]
