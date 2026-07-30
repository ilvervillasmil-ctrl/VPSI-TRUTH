"""
======================================================================
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


CONTENEDOR = {
    "nombre":   "constante",
    "rol":      "CT",
    "version":  "1.0",
    "requiere": [],
}


# ======================================================================
# THE 3D PLANE
# ======================================================================
# Three orthogonal cartesian axes. A unit cube. Not a modelling choice:
# it is the space something has to be cut in for the cut to have an
# inside.

DIMENSION = 3                    # R3
AXES      = ("x", "y", "z")      # orthogonal


# ======================================================================
# THE PARTITION
# ======================================================================
# Minimum regular partition of R3 that owns a distinguishable interior.
# Three divisions per axis, giving 3^3 subcubes of equal volume.
# The single interior cell is the irreducible residue: it arises from
# the impossibility of the observer observing itself without altering
# the system.
# Used in: ALPHA, BETA, C_MAX, the whole topology below

DIVISIONS_PER_AXIS = 3           # 3   the only cut that gives one middle

CUBE_TOTAL    = DIVISIONS_PER_AXIS ** DIMENSION   # 27  3^3, all positions
CUBE_CENTER   = 1                                 # 1   the observer
CUBE_EXTERIOR = CUBE_TOTAL - CUBE_CENTER          # 26  the observable

N_CUBE = CUBE_TOTAL              # 27  minimum 3D structure with interior


# ======================================================================
# THE SEED
# ======================================================================
# The two fractions the partition produces. Everything in the system is
# derived from these two, or it is rejected.
# Held as exact rationals: in floating point 26/27 + 1/27 does not equal
# one, and the closure could not be checked by equality.
# Used in: modules/formulas, core/engine, core/validator

ALPHA = Fraction(CUBE_EXTERIOR, CUBE_TOTAL)   # 0.962962962962963  observable
BETA  = Fraction(CUBE_CENTER,   CUBE_TOTAL)   # 0.037037037037037  observer

C_MAX = ALPHA                    # 0.962962962962963  ceiling on Tru


# ======================================================================
# ANATOMY OF THE SURFACE
# ======================================================================
# The 26 observable subcubes sort into three layers by how much of them
# touches the outside. A face is more exposed than an edge, an edge more
# than a vertex.
#     faces      one whole face against the exterior
#     edges      one edge against the exterior
#     vertices   one corner against the exterior
# The three layers close the surface: 6 + 12 + 8 = 26.
# With the center: 1 + 6 + 12 + 8 = 27.

LAYER_FACES    =  6              # 6   share a full face with the exterior
LAYER_EDGES    = 12              # 12  share an edge with the exterior
LAYER_VERTICES =  8              # 8   share a vertex with the exterior

SURFACE = LAYER_FACES + LAYER_EDGES + LAYER_VERTICES   # 26  = CUBE_EXTERIOR


# ======================================================================
# TRANSITIONS
# ======================================================================
# Adjacency of the partition. Each cell has a fixed number of moves
# available to it, set by where it sits.
# The total factors as the internal scale times the observable surface:
# 6, the faces of the central subcube, by 26. No free parameter --- 156
# is determined by the shape.

TRANS_CENTER      = 6            # 6   faces of the central subcube
TRANS_PER_FACE    = 9            # 9   x 6  faces    =  54
TRANS_PER_EDGE    = 6            # 6   x 12 edges    =  72
TRANS_PER_VERTEX  = 3            # 3   x 8  vertices =  24

TRANSITIONS = (
    TRANS_CENTER
    + LAYER_FACES    * TRANS_PER_FACE
    + LAYER_EDGES    * TRANS_PER_EDGE
    + LAYER_VERTICES * TRANS_PER_VERTEX
)                                # 156 = 6 x 26

PERCEPTUAL_MODE = 5              # 5   faces of the center seen from outside


# ======================================================================
# TOPOLOGY  (from the partition, expressed in the seed)
# ======================================================================
# The angle of the partition. Its exact form is algebraic, and it is
# written in the seed itself:
#
#     sin^2(theta) = BETA
#     cos^2(theta) = ALPHA
#     tan^2(theta) = BETA / ALPHA
#
# Which makes the pythagorean identity
#
#     sin^2(theta) + cos^2(theta) = 1
#
# the same statement as the closure of the partition
#
#     ALPHA + BETA = 1
#
# The angle itself is transcendental and has no rational form. What is
# exact is its squared sine, and that is BETA. The angle is offered as
# a reading, not as a definition.

SIN2_THETA = BETA                # 0.037037037037037  = BETA
COS2_THETA = ALPHA               # 0.962962962962963  = ALPHA
TAN2_THETA = BETA / ALPHA        # 0.038461538461538  = 1/26

R_FIN = Fraction(1) + BETA       # 1.037037037037037  the cube plus its center


def theta():
    """Angle in radians. Read from SIN2_THETA, not stored."""
    return math.asin(math.sqrt(float(SIN2_THETA)))


def theta_degrees():
    """Angle in degrees. 11.09..."""
    return math.degrees(theta())


# ======================================================================
# CLOSURE
# ======================================================================
# Structural verification. Touch one number above and the file refuses
# to import.

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
# The rejection. Any constant that wants into the system declares the
# expression it comes from. It is recomputed with ALPHA and BETA as the
# only names in scope, and compared. What does not match does not pass.
# A constant needing pi, e or any outside value cannot be written here,
# so it cannot be derived, so it is refused.
# Used in: modules/formulas

_SCOPE = {
    "ALPHA":    ALPHA,
    "BETA":     BETA,
    "Fraction": Fraction,
}


def derives(value, expression):
    """
    Recompute and compare. Returns the value, or raises.

        derives(Fraction(28, 27), "1 + BETA")     -> 28/27
        derives(Fraction(1, 2),   "1 + BETA")     -> ValueError
        derives(0.785,            "math.pi / 4")  -> ValueError
    """
    try:
        got = eval(expression, {"__builtins__": {}}, dict(_SCOPE))
    except Exception as e:
        raise ValueError(
            f"does not connect to the seed: {expression!r} is not "
            f"evaluable in ALPHA and BETA "
            f"({type(e).__name__}: {e})"
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
            f"does not connect to the seed: {expression} = {got}, "
            f"declared {want}"
        )

    return want


# ======================================================================
# READING
# ======================================================================

def seed():
    return {"ALPHA": ALPHA, "BETA": BETA}


def partition():
    return {
        "dimension":          DIMENSION,
        "axes":               list(AXES),
        "divisions_per_axis": DIVISIONS_PER_AXIS,
        "total":              CUBE_TOTAL,
        "exterior":           CUBE_EXTERIOR,
        "center":             CUBE_CENTER,
    }


def anatomy():
    return {
        "center":   CUBE_CENTER,
        "faces":    LAYER_FACES,
        "edges":    LAYER_EDGES,
        "vertices": LAYER_VERTICES,
        "surface":  SURFACE,
        "total":    CUBE_TOTAL,
        "transitions": {
            "center":        TRANS_CENTER,
            "faces":         LAYER_FACES    * TRANS_PER_FACE,
            "edges":         LAYER_EDGES    * TRANS_PER_EDGE,
            "vertices":      LAYER_VERTICES * TRANS_PER_VERTEX,
            "total":         TRANSITIONS,
            "factorisation": f"{TRANS_CENTER} x {CUBE_EXTERIOR}",
        },
        "perceptual_mode": PERCEPTUAL_MODE,
    }


def topology():
    return {
        "sin2_theta":    str(SIN2_THETA),
        "cos2_theta":    str(COS2_THETA),
        "tan2_theta":    str(TAN2_THETA),
        "r_fin":         str(R_FIN),
        "theta_rad":     theta(),
        "theta_degrees": theta_degrees(),
    }


def inventario():
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version":    CONTENEDOR["version"],
        "partition":  partition(),
        "anatomy":    anatomy(),
        "seed":       {"ALPHA": str(ALPHA), "BETA": str(BETA)},
        "c_max":      str(C_MAX),
        "topology":   topology(),
        "closure": {
            "alpha_plus_beta":  str(ALPHA + BETA),
            "exact":            ALPHA + BETA == Fraction(1),
            "layers_close":     SURFACE == CUBE_EXTERIOR,
            "transitions":      TRANSITIONS == TRANS_CENTER * CUBE_EXTERIOR,
            "pythagorean":      SIN2_THETA + COS2_THETA == Fraction(1),
        },
    }


__all__ = [
    "CONTENEDOR",
    "ALPHA", "BETA", "C_MAX",
    "DIMENSION", "AXES", "DIVISIONS_PER_AXIS",
    "CUBE_TOTAL", "CUBE_EXTERIOR", "CUBE_CENTER", "N_CUBE",
    "LAYER_FACES", "LAYER_EDGES", "LAYER_VERTICES", "SURFACE",
    "TRANSITIONS", "PERCEPTUAL_MODE",
    "SIN2_THETA", "COS2_THETA", "TAN2_THETA", "R_FIN",
    "theta", "theta_degrees",
    "derives", "seed", "partition", "anatomy", "topology", "inventario",
]
