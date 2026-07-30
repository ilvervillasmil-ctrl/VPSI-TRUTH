"""
VPSI-TRUTH / modules/formulas/truth.py

Formula de la Verdad.

    Tru_Ri(D)    = C(D) * L(D) * K(D)
    Tru_total(D) = ( C(D) * L(D) * K(D) * ALPHA ) + BETA
"""

from modules.constante import ALPHA, BETA


FORMULA = {
    "nombre": "verdad",
    "expresion": "Tru_total = ( C * L * K * ALPHA ) + BETA",
    "fuente": "Teorema de la Verdad, VPSI v9.4",
}


def tru_ri(C, L, K):
    """Tru_Ri = C * L * K"""
    return C * L * K


def tru_total(C, L, K):
    """Tru_total = ( C * L * K * ALPHA ) + BETA"""
    return (C * L * K * ALPHA) + BETA
