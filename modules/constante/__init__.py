"""
VPSI-TRUTH --- modules/calculator/__init__.py

Contenedor de cálculo. Rol CA.

Este módulo es responsable de calcular las variables C, L, K de manera independiente y auditable.
- No calcula Tru_Ri ni Tru_total (eso es responsabilidad de formulas).
- Expone la función calcular() para que el Engine pueda delegar el cálculo de C, L, K.
- Usa Fraction para precisión matemática.
- Devuelve UNDEFINED si falta información (ej: O_context para K).

Dependencias:
- CT (constantes ALPHA, BETA).
- MC (correlacion_mecanica para validar orden causal).
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, List, Optional, Union, Any

# ===============================================================
# CONTENEDOR: Metadatos del módulo
# ===============================================================
CONTENEDOR = {
    "nombre": "calculator",
    "rol": "CA",  # Rol: Cálculo de variables de verdad (C, L, K)
    "version": "1.0",
    "requiere": ["CT", "MC"],  # Depende de constantes y correlación mecánica
    "descripcion": (
        "Calcula las variables fundamentales de verdad (C, L, K) usando métodos "
        "teóricos (IlverVillasmil.pdf) u operacionales (PROTOCOLO.pdf). "
        "Expone la función calcular() para el Engine."
    ),
}

# ===============================================================
# ESTADO UNDEFINIDO (UNDEFINED)
# ===============================================================
class _Undefined:
    """Estado para valores sin evidencia. Propaga limpiamente sin intervencionismo."""
    __slots__ = ()

    def __repr__(self):
        return "UNDEFINED"

    def __bool__(self):
        raise TypeError("UNDEFINED no admite conversión a booleano")

    def __eq__(self, otro):
        return isinstance(otro, _Undefined)

    def __hash__(self):
        return hash("VPSI_UNDEFINED")

UNDEFINED = _Undefined()

def es_undefined(v) -> bool:
    """Verifica si un valor es UNDEFINED."""
    return v is UNDEFINED or isinstance(v, _Undefined)

# ===============================================================
# EXCEPCIONES: Errores específicos del módulo
# ===============================================================
class DominioError(Exception):
    """Un valor está fuera del dominio permitido [0, 1]."""
    pass

class ContextoError(Exception):
    """Falta O_context para calcular K."""
    pass

class MetodoError(Exception):
    """Método no soportado (debe ser 'teorico' o 'operacional')."""
    pass

# ===============================================================
# FUNCIÓN PRINCIPAL: calcular()
# ===============================================================
def calcular(
    descripcion: Optional[str] = None,
    compromisos: Optional[List[str]] = None,
    contradicciones: Optional[int] = None,
    posturas: Optional[List[str]] = None,
    reversiones: Optional[int] = None,
    afirmaciones: Optional[List[str]] = None,
    afirmaciones_falsas: Optional[int] = None,
    o_context: Optional[str] = None,
    metodo: str = "operacional"
) -> Dict[str, Union[Fraction, type(UNDEFINED)]]:
    """
    Función principal para calcular C, L, K.
    Esta función es llamada por el Engine para delegar el cálculo de las variables.

    Args:
        descripcion (str): Descripción D (para método teórico).
        compromisos (List[str]): Lista de compromisos estructurales (para método operacional).
        contradicciones (int): Número de contradicciones (para método operacional).
        posturas (List[str]): Lista de posturas asumidas (para método operacional).
        reversiones (int): Número de reversiones de postura (para método operacional).
        afirmaciones (List[str]): Lista de afirmaciones verificables (para método operacional).
        afirmaciones_falsas (int): Número de afirmaciones falsas (para método operacional).
        o_context (str): Contexto observable (obligatorio para K).
        metodo (str): "teorico" o "operacional" (default: "operacional").

    Returns:
        Dict[str, Union[Fraction, type(UNDEFINED)]]:
            - "C": Valor de C (Fraction o UNDEFINED).
            - "L": Valor de L (Fraction o UNDEFINED).
            - "K": Valor de K (Fraction o UNDEFINED).
            - "metodo": Método usado ("teorico" o "operacional").
            - "o_context": Contexto observable usado (o None).
    """
    # Calcular C
    if metodo == "teorico":
        C = _calcular_c_teorico(descripcion) if descripcion is not None else UNDEFINED
    else:
        C = _calcular_c_operacional(compromisos, contradicciones)

    # Calcular L
    if metodo == "teorico":
        L = _calcular_l_teorico(descripcion) if descripcion is not None else UNDEFINED
    else:
        L = _calcular_l_operacional(posturas, reversiones)

    # Calcular K
    if o_context is None:
        K = UNDEFINED
    else:
        if metodo == "teorico":
            K = _calcular_k_teorico(descripcion, o_context) if descripcion is not None else UNDEFINED
        else:
            K = _calcular_k_operacional(afirmaciones, afirmaciones_falsas, o_context)

    return {
        "C": C,
        "L": L,
        "K": K,
        "metodo": metodo,
        "o_context": o_context,
    }

# ===============================================================
# FUNCIONES INTERNAS: Delegación a sub-módulos
# ===============================================================
def _calcular_c_teorico(descripcion: str) -> Union[Fraction, type(UNDEFINED)]:
    """Delegación a coherencia.py para método teórico."""
    from .coherencia import _calcular_c_teorico as _c_teorico
    return _c_teorico(descripcion)

def _calcular_c_operacional(compromisos: Optional[List[str]], contradicciones: Optional[int]) -> Union[Fraction, type(UNDEFINED)]:
    """Delegación a coherencia.py para método operacional."""
    from .coherencia import _calcular_c_operacional as _c_operacional
    return _c_operacional(compromisos, contradicciones)

def _calcular_l_teorico(descripcion: str) -> Union[Fraction, type(UNDEFINED)]:
    """Delegación a logica.py para método teórico."""
    from .logica import _calcular_l_teorico as _l_teorico
    return _l_teorico(descripcion)

def _calcular_l_operacional(posturas: Optional[List[str]], reversiones: Optional[int]) -> Union[Fraction, type(UNDEFINED)]:
    """Delegación a logica.py para método operacional."""
    from .logica import _calcular_l_operacional as _l_operacional
    return _l_operacional(posturas, reversiones)

def _calcular_k_teorico(descripcion: str, o_context: str) -> Union[Fraction, type(UNDEFINED)]:
    """Delegación a correlacion_k.py para método teórico."""
    from .correlacion_k import _calcular_k_teorico as _k_teorico
    return _k_teorico(descripcion, o_context)

def _calcular_k_operacional(afirmaciones: Optional[List[str]], afirmaciones_falsas: Optional[int], o_context: str) -> Union[Fraction, type(UNDEFINED)]:
    """Delegación a correlacion_k.py para método operacional."""
    from .correlacion_k import _calcular_k_operacional as _k_operacional
    return _k_operacional(afirmaciones, afirmaciones_falsas, o_context)

# ===============================================================
# EXPORTACIÓN: Lo que el módulo expone al exterior
# ===============================================================
__all__ = [
    # Metadatos
    "CONTENEDOR",
    # Estado y utilidades
    "UNDEFINED",
    "es_undefined",
    # Excepciones
    "DominioError",
    "ContextoError",
    "MetodoError",
    # Función principal para el Engine
    "calcular",
]
