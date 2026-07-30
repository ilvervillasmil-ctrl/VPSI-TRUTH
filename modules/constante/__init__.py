"""
VPSI-TRUTH  ---  modules/constante
THE SEED
======================================================================

Single source of truth. Every module reads from here. Nothing here
reads from anywhere else.

The Engine does all the work, but the Engine depends absolutely on
this file. A formula that does not connect to ALPHA and BETA does not
pass, and without that the rest does not hold.

Contents:  the 3D plane, the partition, ALPHA and BETA, the topology.
            Nothing else.

----------------------------------------------------------------------
WHAT THIS MEANS  ---  for anyone reading, code or not
----------------------------------------------------------------------

Imagine a solid cube. To measure anything inside it you first have to
divide it. Cut each of the three edges into three, and the cube breaks
into 27 equal little cubes.

Now count how many of those 27 touch the outside:

     26 of them touch at least one outer face. You can see them.
      1 of them touches nothing. It sits in the middle, wrapped by the
        other 26. You cannot see it from outside, and from inside it
        cannot see out.

That is the whole idea. The 26 are what can be observed. The 1 is the
observer. Two fractions, and only two:

     ALPHA = 26/27      what can be observed
     BETA  =  1/27      the observer

     ALPHA + BETA = 1   nothing is left over

Why cut into three and not two or four:

     two cuts  ->  2^3 =  8 cubes, and all eight touch the outside.
                   There is no middle. Nothing to be an observer.

     three     ->  3^3 = 27 cubes, and exactly one touches nothing.
                   The middle appears, and it appears once.

     four      ->  4^3 = 64 cubes. A middle exists, but there are eight
                   of them. The center stops being a single place.

Three is the only cut that produces a middle and produces it alone.
That is why the partition is minimal: below it there is no inside,
above it the inside is not one.

BETA being greater than zero is the statement that the observer
exists. BETA being exactly 1/27 is how much room it takes.

ALPHA + BETA = 1 is the statement that there is no third part. What
can be observed and the one observing use up the whole cube.

======================================================================
"""

import math
from fractions import Fraction

# ======================================================================
# CONTENEDOR
# ======================================================================

CONTENEDOR = {
    "nombre":   "constante",
    "rol":      "CT",
    "version":  "1.0",
    "requiere": [],
}

# ======================================================================
# THE 3D PLANE
# ======================================================================

DIMENSION = 3
AXES = ("x", "y", "z")

# ======================================================================
# THE PARTITION
# ======================================================================

DIVISIONS_PER_AXIS = 3
CUBE_TOTAL = DIVISIONS_PER_AXIS ** DIMENSION
CUBE_CENTER = 1
CUBE_EXTERIOR = CUBE_TOTAL - CUBE_CENTER
N_CUBE = CUBE_TOTAL

# ======================================================================
# THE SEED
# ======================================================================

ALPHA = Fraction(CUBE_EXTERIOR, CUBE_TOTAL)  # 26/27
BETA = Fraction(CUBE_CENTER, CUBE_TOTAL)     # 1/27
C_MAX = ALPHA

# ======================================================================
# ANATOMY OF THE SURFACE
# ======================================================================

LAYER_FACES = 6
LAYER_EDGES = 12
LAYER_VERTICES = 8
SURFACE = LAYER_FACES + LAYER_EDGES + LAYER_VERTICES

# ======================================================================
# TRANSITIONS
# ======================================================================

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

# ======================================================================
# TOPOLOGY
# ======================================================================

SIN2_THETA = BETA
COS2_THETA = ALPHA
TAN2_THETA = BETA / ALPHA
R_FIN = Fraction(1) + BETA

def theta():
    return math.asin(math.sqrt(float(SIN2_THETA)))

def theta_degrees():
    return math.degrees(theta())

# ======================================================================
# CLOSURE
# ======================================================================

assert DIMENSION == 3
assert DIVISIONS_PER_AXIS ** DIMENSION == CUBE_TOTAL
assert CUBE_EXTERIOR + CUBE_CENTER == CUBE_TOTAL
assert SURFACE == CUBE_EXTERIOR
assert CUBE_CENTER + SURFACE == CUBE_TOTAL
assert TRANSITIONS == TRANS_CENTER * CUBE_EXTERIOR
assert ALPHA + BETA == Fraction(1)
assert SIN2_THETA + COS2_THETA == Fraction(1)
assert TAN2_THETA == SIN2_THETA / COS2_THETA
assert C_MAX == ALPHA
assert R_FIN == Fraction(1) + BETA

# ======================================================================
# CONNECTION
# ======================================================================

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

# ======================================================================
# READING
# ======================================================================

def seed():
    return {"ALPHA": ALPHA, "BETA": BETA}

def partition():
    return {
        "dimension": DIMENSION,
        "axes": list(AXES),
        "divisions_per_axis": DIVISIONS_PER_AXIS,
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
        "theta_rad": theta(),
        "theta_degrees": theta_degrees(),
    }

def inventario():
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "partition": partition(),
        "anatomy": anatomy(),
        "seed": {"ALPHA": str(ALPHA), "BETA": str(BETA)},
        "c_max": str(C_MAX),
        "topology": topology(),
        "closure": {
            "alpha_plus_beta": str(ALPHA + BETA),
            "exact": ALPHA + BETA == Fraction(1),
            "layers_close": SURFACE == CUBE_EXTERIOR,
            "transitions": TRANSITIONS == TRANS_CENTER * CUBE_EXTERIOR,
            "pythagorean": SIN2_THETA + COS2_THETA == Fraction(1),
        },
    }

# ======================================================================
# EXPORTACIÓN (REQUERIDO PARA QUE EL ENGINE Y OTROS MÓDULOS IMPORTEN)
# ======================================================================

__all__ = [
    # Contenedor
    "CONTENEDOR",

    # Constantes fundamentales
    "ALPHA", "BETA", "C_MAX",

    # Geometría del cubo
    "DIMENSION", "AXES", "DIVISIONS_PER_AXIS",
    "CUBE_TOTAL", "CUBE_EXTERIOR", "CUBE_CENTER", "N_CUBE",

    # Capas del cubo
    "LAYER_FACES", "LAYER_EDGES", "LAYER_VERTICES", "SURFACE",

    # Transiciones
    "TRANSITIONS", "TRANS_CENTER", "TRANS_PER_FACE", "TRANS_PER_EDGE", "TRANS_PER_VERTEX", "PERCEPTUAL_MODE",

    # Topología
    "SIN2_THETA", "COS2_THETA", "TAN2_THETA", "R_FIN",

    # Funciones
    "theta", "theta_degrees", "derives", "seed", "partition", "anatomy", "topology", "inventario",
]
