"""
Fórmula de la Verdad (VPSI v9.4).

    Tru_Ri(D)    = min(C(D) * L(D) * K(D), ALPHA)  # Teorema 16: Tru_Ri ≤ α
    Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA
"""

from fractions import Fraction
from modules.constante import ALPHA, BETA

FORMULA = {
    "nombre": "verdad",
    "expresion": "Tru_total = ( min(C * L * K, ALPHA) * ALPHA ) + BETA",
    "fuente": "Teorema de la Verdad, VPSI v9.4 (Teorema 16: Techo Estructural α)",
}

def tru_ri(C, L, K):
    """Tru_Ri = min(C * L * K, ALPHA) (Teorema 16: Tru_Ri ≤ α)."""
    return min(C * L * K, ALPHA)

def tru_total(C, L, K):
    """Tru_total = (Tru_Ri * ALPHA) + BETA."""
    return (tru_ri(C, L, K) * ALPHA) + BETA
