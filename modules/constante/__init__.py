"""
VPSI-TRUTH --- modules/constante/__init__.py

Contenedor de constantes. Rol CT.

Este módulo expone las constantes geométricas fundamentales del marco VPSI:
- ALPHA = 26/27 (techo estructural).
- BETA = 1/27 (piso estructural).

Estas constantes son derivadas del cubo 3x3x3 en ℝ³ y son invariantes en todo el sistema.
"""

from fractions import Fraction

# ===============================================================
# CONSTANTES GEOMÉTRICAS (Derivadas del cubo 3x3x3 en ℝ³)
# ===============================================================
ALPHA = Fraction(26, 27)  # Techo estructural: fracción observable del cubo.
BETA = Fraction(1, 27)    # Piso estructural: fracción interior irreducible del cubo.

# ===============================================================
# CONTENEDOR: Metadatos del módulo
# ===============================================================
CONTENEDOR = {
    "nombre": "constante",
    "rol": "CT",  # Rol: Constantes
    "version": "1.0",
    "requiere": [],  # No tiene dependencias
    "descripcion": (
        "Expone las constantes geométricas ALPHA y BETA, derivadas del cubo 3x3x3 en ℝ³. "
        "Estas constantes son invariantes y se usan en todos los cálculos de verdad."
    ),
}

# ===============================================================
# EXPORTACIÓN: Lo que el módulo expone al exterior
# ===============================================================
__all__ = [
    "ALPHA",
    "BETA",
    "CONTENEDOR",
]
