"""
VPSI-TRUTH --- modules/constante/__init__.py

THE SEED: Punto de anclaje del sistema.
Single source of truth. Every module reads from here. Nothing here reads from anywhere else.

El Engine depende absolutamente de este módulo. Sin ALPHA y BETA, el sistema no funciona.
Contenido: Plano 3D, partición, ALPHA, BETA, topología.

Si este módulo no tiene su topología correcta, el Engine no accede a él.
"""

from __future__ import annotations
import math
from fractions import Fraction
from typing import Any, Dict, List

# ===============================================================
# SEGMENTO 1 --- IDENTIDAD
# ===============================================================
CONTENEDOR = {
    "nombre": "constante",
    "rol": "CT",
    "version": "1.0",
    "requiere": [],
    "descripcion": "Punto de anclaje: expone ALPHA=26/27 y BETA=1/27 (derivados del cubo 3×3×3).",
    "obligatorio": True,  # Este módulo es obligatorio para el Engine
}

# ===============================================================
# SEGMENTO 2 --- ERRORES
# ===============================================================
class InvarianteRotoError(Exception):
    """Error si ALPHA + BETA != 1 o alguna aserción de cierre falla."""
    pass

# ===============================================================
# SEGMENTO 3 --- CONSTANTES Y CONTRATOS
# ===============================================================
# Plano 3D: Tres ejes cartesianos ortogonales. Un cubo unitario.
DIMENSION = 3
AXES = ("x", "y", "z")

# Partición: División mínima regular de R3 que tiene un interior distinguible.
DIVISIONES_PER_AXIS = 3
CUBE_TOTAL = DIVISIONS_PER_AXIS ** DIMENSION  # 27
CUBE_CENTER = 1  # 1 (el observador)
CUBE_EXTERIOR = CUBE_TOTAL - CUBE_CENTER  # 26 (lo observable)
N_CUBE = CUBE_TOTAL

# La semilla: Las dos fracciones que produce la partición.
ALPHA = Fraction(CUBE_EXTERIOR, CUBE_TOTAL)  # 26/27 (lo observable)
BETA = Fraction(CUBE_CENTER, CUBE_TOTAL)    # 1/27 (el observador)
C_MAX = ALPHA  # Techo estructural

# Anatomía de la superficie: Capas del cubo.
LAYER_FACES = 6      # 6 caras
LAYER_EDGES = 12     # 12 aristas
LAYER_VERTICES = 8   # 8 vértices
SURFACE = LAYER_FACES + LAYER_EDGES + LAYER_VERTICES  # 26 = CUBE_EXTERIOR

# Transiciones: Adyacencia de la partición.
TRANS_CENTER = 6
TRANS_PER_FACE = 9
TRANS_PER_EDGE = 6
TRANS_PER_VERTEX = 3
TRANSITIONS = (
    TRANS_CENTER
    + LAYER_FACES * TRANS_PER_FACE
    + LAYER_EDGES * TRANS_PER_EDGE
    + LAYER_VERTICES * TRANS_PER_VERTEX
)  # 156 = 6 * 26
PERCEPTUAL_MODE = 5  # Modo perceptual

# Topología: Derivada de la partición.
SIN2_THETA = BETA
COS2_THETA = ALPHA
TAN2_THETA = BETA / ALPHA
R_FIN = Fraction(1) + BETA  # 28/27

# ===============================================================
# SEGMENTO 4 --- ESTADO (Colecciones auto-llenables)
# ===============================================================
_DECLARACIONES: List[Dict[str, Any]] = []

# ===============================================================
# SEGMENTO 5 --- GANCHOS DE ANEXO (Decoradores)
# ===============================================================
def declarar(d: Dict[str, Any]) -> Dict[str, Any]:
    """Registra una declaración axiomática del contenedor."""
    _DECLARACIONES.append(d)
    return d

# ===============================================================
# SEGMENTO 6 --- LECTURA (Funciones privadas)
# ===============================================================
def _validar_invariante() -> None:
    """Valida que todas las aserciones de cierre se cumplan."""
    assert DIMENSION == 3, "DIMENSION debe ser 3."
    assert DIVISIONS_PER_AXIS ** DIMENSION == CUBE_TOTAL, "CUBE_TOTAL debe ser 27."
    assert CUBE_EXTERIOR + CUBE_CENTER == CUBE_TOTAL, "CUBE_EXTERIOR + CUBE_CENTER debe ser 27."
    assert SURFACE == CUBE_EXTERIOR, "SURFACE debe ser igual a CUBE_EXTERIOR."
    assert CUBE_CENTER + SURFACE == CUBE_TOTAL, "CUBE_CENTER + SURFACE debe ser 27."
    assert TRANSITIONS == TRANS_CENTER * CUBE_EXTERIOR, "TRANSITIONS debe ser 6 * 26."
    assert ALPHA + BETA == Fraction(1), "ALPHA + BETA debe ser 1."
    assert SIN2_THETA + COS2_THETA == Fraction(1), "SIN2_THETA + COS2_THETA debe ser 1."
    assert TAN2_THETA == SIN2_THETA / COS2_THETA, "TAN2_THETA debe ser SIN2_THETA / COS2_THETA."
    assert C_MAX == ALPHA, "C_MAX debe ser igual a ALPHA."
    assert R_FIN == Fraction(1) + BETA, "R_FIN debe ser 1 + BETA."

# ===============================================================
# SEGMENTO 7 --- API DEL CONTENEDOR (Contrato con el Engine)
# ===============================================================
def barrer() -> Dict[str, Any]:
    """Filtro de paso al Engine. Valida las aserciones de cierre."""
    try:
        _validar_invariante()
        return {
            "contenedor": CONTENEDOR["nombre"],
            "estado": "APROBADO",
            "coherente": True,
            "faltas": [],
        }
    except AssertionError as e:
        return {
            "contenedor": CONTENEDOR["nombre"],
            "estado": "RECHAZADO",
            "coherente": False,
            "faltas": [str(e)],
        }

def inventario() -> Dict[str, Any]:
    """Describe el contenedor sin tocar disco/red."""
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

def axiomas() -> List[Dict[str, Any]]:
    """Declaraciones axiomáticas del contenedor para el barrido general."""
    return _DECLARACIONES

# ===============================================================
# SEGMENTO 8 --- REGLAS (Validaciones internas)
# ===============================================================
@regla
def _validar_particion() -> List[str]:
    """Valida que la partición del cubo sea correcta."""
    faltas = []
    if DIVISIONS_PER_AXIS ** DIMENSION != 27:
        faltas.append("DIVISIONS_PER_AXIS ** DIMENSION debe ser 27.")
    if CUBE_EXTERIOR + CUBE_CENTER != 27:
        faltas.append("CUBE_EXTERIOR + CUBE_CENTER debe ser 27.")
    return faltas

@regla
def _validar_constantes() -> List[str]:
    """Valida que ALPHA y BETA sean correctos."""
    faltas = []
    if ALPHA + BETA != Fraction(1):
        faltas.append("ALPHA + BETA debe ser 1.")
    if ALPHA != Fraction(26, 27):
        faltas.append("ALPHA debe ser 26/27.")
    if BETA != Fraction(1, 27):
        faltas.append("BETA debe ser 1/27.")
    return faltas

# ===============================================================
# SEGMENTO 9 --- DECLARACIONES (Axiomas/Teoremas del módulo)
# ===============================================================
declarar({
    "id": "CT-1",
    "tipo": "axioma",
    "sujeto": "ALPHA",
    "relacion": "+",
    "objeto": "BETA",
    "polaridad": True,
    "enunciado": "ALPHA + BETA = 1 (Ley de Conservación: lo observable y el observador agotan el cubo).",
    "cota": None,
    "depende_de": [],
    "gobierna": ["FO-1", "FO-2"],
})

declarar({
    "id": "CT-2",
    "tipo": "definicion",
    "sujeto": "ALPHA",
    "relacion": "=",
    "objeto": "26/27",
    "polaridad": True,
    "enunciado": "ALPHA = 26/27 (fracción accesible del cubo 3×3×3).",
    "cota": "26/27",
    "depende_de": [],
    "gobierna": ["FO-1"],
})

declarar({
    "id": "CT-3",
    "tipo": "definicion",
    "sujeto": "BETA",
    "relacion": "=",
    "objeto": "1/27",
    "polaridad": True,
    "enunciado": "BETA = 1/27 (fracción interior irreducible del cubo 3×3×3).",
    "cota": "1/27",
    "depende_de": [],
    "gobierna": ["FO-2"],
})

declarar({
    "id": "CT-4",
    "tipo": "axioma",
    "sujeto": "CUBE_TOTAL",
    "relacion": "=",
    "objeto": "27",
    "polaridad": True,
    "enunciado": "CUBE_TOTAL = 27 (partición mínima con interior distinguible).",
    "cota": "27",
    "depende_de": [],
    "gobierna": [],
})

# ===============================================================
# ZONA DE ANEXO
# ===============================================================
# Funciones de lectura (no requieren decoradores, son parte de la API pública)

def theta() -> float:
    """Ángulo en radianes. Derivado de SIN2_THETA = BETA."""
    return math.asin(math.sqrt(float(SIN2_THETA)))

def theta_degrees() -> float:
    """Ángulo en grados. 11.09..."""
    return math.degrees(theta())

def derives(value: Any, expression: str) -> Fraction:
    """
    Recomputa y compara. Devuelve el valor si la expresión es válida en el contexto de ALPHA y BETA.
    Ejemplo:
        derives(Fraction(28, 27), "1 + BETA") -> 28/27
        derives(Fraction(1, 2), "1 + BETA") -> ValueError
    """
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

def seed() -> Dict[str, Fraction]:
    """Devuelve ALPHA y BETA."""
    return {"ALPHA": ALPHA, "BETA": BETA}

def partition() -> Dict[str, Any]:
    """Devuelve la partición del cubo."""
    return {
        "dimension": DIMENSION,
        "axes": list(AXES),
        "divisions_per_axis": DIVISIONS_PER_AXIS,
        "total": CUBE_TOTAL,
        "exterior": CUBE_EXTERIOR,
        "center": CUBE_CENTER,
    }

def anatomy() -> Dict[str, Any]:
    """Devuelve la anatomía del cubo."""
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

def topology() -> Dict[str, Any]:
    """Devuelve la topología derivada de la partición."""
    return {
        "sin2_theta": str(SIN2_THETA),
        "cos2_theta": str(COS2_THETA),
        "tan2_theta": str(TAN2_THETA),
        "r_fin": str(R_FIN),
        "theta_rad": theta(),
        "theta_degrees": theta_degrees(),
    }

# ===============================================================
# EXPORTACIÓN (Funciones y constantes públicas)
# ===============================================================
# No se usa __all__ para permitir anexo al final sin editar esta lista.
# Python exporta todo lo que no empieza con "_".
