"""
VPSI-TRUTH --- modules/constante/__init__.py

THE SEED: Punto de anclaje del sistema.
Single source of truth. Every module reads from here. Nothing here reads from anywhere else.

El Engine depende absolutamente de este módulo. Sin ALPHA y BETA, el sistema no funciona.
"""

from fractions import Fraction
import math

# ===============================================================
# CONTENEDOR
# ===============================================================
CONTENEDOR = {
    "nombre": "constante",
    "rol": "CT",
    "version": "1.0",
    "requiere": [],
}

# ===============================================================
# THE 3D PLANE
# ===============================================================
DIMENSION = 3
AXES = ("x", "y", "z")

# ===============================================================
# THE PARTITION
# ===============================================================
DIVISIONES_PER_AXIS = 3
CUBE_TOTAL = DIVISIONES_PER_AXIS ** DIMENSION
CUBE_CENTER = 1
CUBE_EXTERIOR = CUBE_TOTAL - CUBE_CENTER
N_CUBE = CUBE_TOTAL

# ===============================================================
# THE SEED
# ===============================================================
ALPHA = Fraction(CUBE_EXTERIOR, CUBE_TOTAL)  # 26/27
BETA = Fraction(CUBE_CENTER, CUBE_TOTAL)     # 1/27
C_MAX = ALPHA

# ===============================================================
# ANATOMY OF THE SURFACE
# ===============================================================
LAYER_FACES = 6
LAYER_EDGES = 12
LAYER_VERTICES = 8
SURFACE = LAYER_FACES + LAYER_EDGES + LAYER_VERTICES

# ===============================================================
# TRANSITIONS
# ===============================================================
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

# ===============================================================
# TOPOLOGY
# ===============================================================
SIN2_THETA = BETA
COS2_THETA = ALPHA
TAN2_THETA = BETA / ALPHA
R_FIN = Fraction(1) + BETA

def theta():
    return math.asin(math.sqrt(float(SIN2_THETA)))

def theta_degrees():
    return math.degrees(theta())

# ===============================================================
# CLOSURE
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
# CONNECTION
# ===============================================================
_SCOPE = {
    "ALPHA": ALPHA,
    "BETA": BETA,
    "Fraction": Fraction,
}

def derives(value, expression):
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
