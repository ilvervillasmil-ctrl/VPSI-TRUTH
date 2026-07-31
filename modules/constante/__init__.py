"""
VPSI-TRUTH --- modules/constante/__init__.py

THE SEED: Punto de anclaje del sistema.
Single source of truth. Every module reads from here.
"""

from __future__ import annotations
import math
from fractions import Fraction

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================
CONTENEDOR = {
    "nombre": "constante",
    "rol": "CT",
    "version": "1.0",
    "requiere": [],
    "obligatorio": True,
}

# ===============================================================
# SEGMENTO 3 --- CONSTANTES Y CONTRATOS
# ===============================================================
DIMENSION = 3
AXES = ("x", "y", "z")

DIVISIONES_PER_AXIS = 3
CUBE_TOTAL = DIVISIONES_PER_AXIS ** DIMENSION
CUBE_CENTER = 1
CUBE_EXTERIOR = CUBE_TOTAL - CUBE_CENTER

LAYER_FACES = 6
LAYER_EDGES = 12
LAYER_VERTICES = 8
SURFACE = LAYER_FACES + LAYER_EDGES + LAYER_VERTICES

TRANS_CENTER = 6
TRANS_PER_FACE = 9
TRANS_PER_EDGE = 6
TRANS_PER_VERTEX = 3
TRANSITIONS = (
    TRANS_CENTER
    + LAYER_FACES * TRANS_PER_FACE
    + LAYER_EDGES * TRANS_PER_EDGE
    + LAYER_VERTICES * TRANS_PER_VERTEX
)
PERCEPTUAL_MODE = 5

ALPHA = Fraction(CUBE_EXTERIOR, CUBE_TOTAL)
BETA = Fraction(CUBE_CENTER, CUBE_TOTAL)
C_MAX = ALPHA

SIN2_THETA = BETA
COS2_THETA = ALPHA
TAN2_THETA = BETA / ALPHA
R_FIN = Fraction(1) + BETA

# ===============================================================
# SEGMENTO 4 --- VALIDACIÓN DE INVARIANTES
# ===============================================================
assert DIMENSION == 3
assert DIVISIONES_PER_AXIS ** DIMENSION == CUBE_TOTAL
assert CUBE_EXTERIOR + CUBE_CENTER == CUBE_TOTAL
assert SURFACE == CUBE_EXTERIOR
assert CUBE_CENTER + SURFACE == CUBE_TOTAL
assert TRANSITIONS == TRANS_CENTER * CUBE_EXTERIOR
assert ALPHA + BETA == Fraction(1)
assert SIN2_THETA + COS2_THETA == Fraction(1)
assert TAN2_THETA == SIN2_THETA / COS2_THETA
assert C_MAX == ALPHA
assert R_FIN == Fraction(1) + BETA

# ===============================================================
# SEGMENTO 7 --- API DEL CONTENEDOR
# ===============================================================
def seed():
    return {"ALPHA": ALPHA, "BETA": BETA}

def partition():
    return {
        "dimension": DIMENSION,
        "axes": list(AXES),
        "divisions_per_axis": DIVISIONES_PER_AXIS,
        "total": CUBE_TOTAL,
        "exterior": CUBE_EXTERIOR,
        "center": CUBE_CENTER,
    }

def anatomy():
    return {
        "center": CUBE_CENTER,
        "faces": LAYER_FACES,
        "edges": LAYER_EDGES,
        "vertices": LAYER_VERTICES,
        "surface": SURFACE,
        "total": CUBE_TOTAL,
        "transitions": {
            "center": TRANS_CENTER,
            "faces": LAYER_FACES * TRANS_PER_FACE,
            "edges": LAYER_EDGES * TRANS_PER_EDGE,
            "vertices": LAYER_VERTICES * TRANS_PER_VERTEX,
            "total": TRANSITIONS,
            "factorisation": f"{TRANS_CENTER} x {CUBE_EXTERIOR}",
        },
        "perceptual_mode": PERCEPTUAL_MODE,
    }

def topology():
    return {
        "sin2_theta": str(SIN2_THETA),
        "cos2_theta": str(COS2_THETA),
        "tan2_theta": str(TAN2_THETA),
        "r_fin": str(R_FIN),
        "theta_rad": math.asin(math.sqrt(float(SIN2_THETA))),
        "theta_degrees": math.degrees(math.asin(math.sqrt(float(SIN2_THETA)))),
    }

def theta():
    return math.asin(math.sqrt(float(SIN2_THETA)))

def theta_degrees():
    return math.degrees(theta())

def derives(value, expression):
    _SCOPE = {"ALPHA": ALPHA, "BETA": BETA, "Fraction": Fraction}
    try:
        got = eval(expression, {"__builtins__": {}}, _SCOPE)
    except Exception as e:
        raise ValueError(
            f"does not connect to the seed: {expression!r} is not "
            f"evaluable in ALPHA and BETA ({type(e).__name__}: {e})"
        )

    if not isinstance(got, Fraction):
        try:
            got = Fraction(got)
        except (TypeError, ValueError):
            raise ValueError(
                f"does not connect to the seed: {expression!r} yields "
                f"{type(got).__name__}, not a rational"
            )

    want = value if isinstance(value, Fraction) else Fraction(value)

    if got != want:
        raise ValueError(
            f"does not connect to the seed: {expression} = {got}, declared {want}"
        )

    return want
