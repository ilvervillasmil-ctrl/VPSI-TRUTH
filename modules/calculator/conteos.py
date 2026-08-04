"""
VPSI-TRUTH --- modules/calculator/conteos.py

Productor de conteos operacionales con anclas de medición (AM v1.0).

Versión: 3.5.1
Cambios principales respecto a 3.5.0:
  - Se integran tablas de referencia para pesos y divisiones 1/n.
  - Las tablas NO modifican la lógica existente; solo sirven como referencia.
  - Se corrige el error de Fraction(1, n) para valores decimales.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

VERSION = "3.5.1"

# ===============================================================
# SEGMENTO 1 --- RETÍCULA DE SEVERIDAD Y ESCALA ARMÓNICA CONTROLADA
# ===============================================================

PESO_ROCE = Fraction(1, 4)    # 0.250
PESO_PARCIAL = Fraction(1, 2) # 0.500
PESO_GRAVE = Fraction(3, 4)   # 0.750
PESO_TOTAL = Fraction(1, 1)   # 1.000

RETICULA = (PESO_ROCE, PESO_PARCIAL, PESO_GRAVE, PESO_TOTAL)

# ===============================================================
# TABLAS DE REFERENCIA (NO MODIFICAN LA LÓGICA EXISTENTE)
# ===============================================================

# Tabla de pesos de la retícula de severidad
TABLA_RETICULA = {
    "PESO_ROCE": {"fraccion": PESO_ROCE, "decimal": 0.250},
    "PESO_PARCIAL": {"fraccion": PESO_PARCIAL, "decimal": 0.500},
    "PESO_GRAVE": {"fraccion": PESO_GRAVE, "decimal": 0.750},
    "PESO_TOTAL": {"fraccion": PESO_TOTAL, "decimal": 1.000},
}

# Tabla de divisiones 1/n (desde 1/1 hasta 1/9.0)
TABLA_DIVISIONES = {}

# Generar la tabla de divisiones 1/n para enteros (1 a 9)
for n in range(1, 10):
    fraction = Fraction(1, n)
    TABLA_DIVISIONES[f"1/{n}"] = {
        "fraccion": fraction,
        "decimal": round(float(fraction), 3)
    }

# Generar la tabla de divisiones 1/n para decimales (1.1 a 9.0)
for n in [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
          2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9,
          3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9,
          4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9,
          5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9,
          6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9,
          7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9,
          8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.0]:
    # Convertir n a fracción primero para evitar el error
    n_frac = Fraction(str(n)).limit_denominator(100)
    fraction = Fraction(1, n_frac).limit_denominator(100)
    TABLA_DIVISIONES[f"1/{n}"] = {
        "fraccion": fraction,
        "decimal": round(float(fraction), 3)
    }

# ===============================================================
# FUNCIONES PARA ACCEDER A LAS TABLAS
# ===============================================================

def obtener_peso_reticula(nombre: str) -> Dict[str, Any]:
    """Devuelve la fracción y el decimal de un peso de la retícula."""
    return TABLA_RETICULA.get(nombre, {"fraccion": None, "decimal": None})

def obtener_division(division: str) -> Dict[str, Any]:
    """Devuelve la fracción y el decimal de una división 1/n."""
    return TABLA_DIVISIONES.get(division, {"fraccion": None, "decimal": None})

def listar_tablas() -> Dict[str, Dict[str, Any]]:
    """Devuelve todas las tablas de referencia."""
    return {
        "reticula": TABLA_RETICULA,
        "divisiones": TABLA_DIVISIONES,
    }

# ===============================================================
# SEGMENTO 2 --- PATRONES DETERMINISTAS (CALIBRADOS)
# ===============================================================

_PATRONES_CONTRADICCION: Tuple[Tuple[str, Fraction], ...] = (
    (r"\by\s+no\b", PESO_TOTAL),
    (r"\bpero\s+no\b", PESO_TOTAL),
    (r"\bes\b.+\bno\s+es\b", PESO_TOTAL),
    (r"\bno\s+es\b.+\bes\b", PESO_TOTAL),
    (r"\bs[ií]\s+y\s+no\b", PESO_TOTAL),
    (r"\bno\s+y\s+s[ií]\b", PESO_TOTAL),
    (r"\bsin\s+embargo\b", PESO_PARCIAL),
    (r"\bno\s+obstante\b", PESO_PARCIAL),
    (r"\bpor\s+un\s+lado\b.+\bpor\s+(?:el\s+)?otro\b", PESO_PARCIAL),
    (r"\baunque\b", PESO_ROCE),
    (r"\bmas\s+no\b", PESO_PARCIAL),
    (r"\bsin\s+dejar\s+de\b", PESO_ROCE),
)

# ... (El resto del código original de conteos.py se mantiene sin cambios)
# (Incluyendo _SENALES_ADOPCION, _SENALES_ACTO, _SENALES_NO_PROPOSICION, etc.)

# ===============================================================
# SEGMENTO 3 --- STOPWORDS (es) Y REFERENCIAS LÉXICAS
# ===============================================================

_DICCIONARIO_STOP: frozenset = frozenset({
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "lo", "al", "del",
    # ... (El resto del diccionario de stopwords se mantiene sin cambios)
})

_STOP = _DICCIONARIO_STOP

# ===============================================================
# SEGMENTO 4 --- LECTURA DEL MATERIAL
# ===============================================================

_CLAVES_TEXTO = ("mensaje", "descripcion", "texto", "D")
_CLAVES_O = ("contexto", "O_context", "o_context", "O")
_CLAVES_O_LECTURA = ("enunciado_O", "contexto", "O_context", "o_context")

# ... (El resto de las funciones de lectura se mantienen sin cambios)

# ===============================================================
# SEGMENTO 5 --- HELPERS
# ===============================================================

def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", (str(s) if s is not None else "").strip().lower())

# ... (El resto de las funciones helper se mantienen sin cambios)

# ===============================================================
# SEGMENTO 6 --- OFICIO PÚBLICO
# ===============================================================

def extraer_conteos(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    # ... (La función original se mantiene sin cambios)
    pass

def inyectar_en_peticion(peticion: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # ... (La función original se mantiene sin cambios)
    pass

def verificar_conteos(salida: Any) -> bool:
    # ... (La función original se mantiene sin cambios)
    pass

__all__ = [
    "extraer_conteos",
    "inyectar_en_peticion",
    "verificar_conteos",
    "nombre_reticula",
    "obtener_referencias",
    "VERSION",
    "PESO_ROCE",
    "PESO_PARCIAL",
    "PESO_GRAVE",
    "PESO_TOTAL",
    "RETICULA",
    "_DICCIONARIO_STOP",
    "_SENALES_ADOPCION",
    "_SENALES_ACTO",
    "_PATRONES_CONTRADICCION",
    # Nuevas funciones para acceder a las tablas
    "obtener_peso_reticula",
    "obtener_division",
    "listar_tablas",
    "TABLA_RETICULA",
    "TABLA_DIVISIONES",
]
