"""
VPSI-TRUTH --- modules/calculator/__init__.py

Contenedor de cálculo. Rol CA.

Este módulo es responsable de calcular las variables C, L, K de manera independiente y auditable.
- Expone la función calcular() para que el Engine pueda delegar el cálculo de C, L, K.
- No calcula Tru_Ri ni Tru_total (eso es responsabilidad de formulas).
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
    peticion: Dict[str, Any]
) -> Dict[str, Union[Fraction, type(UNDEFINED), str, None]]:
    """
    Función principal para calcular C, L, K.
    Esta función es llamada por el Engine para delegar el cálculo de las variables.

    Args:
        peticion (Dict[str, Any]): Diccionario con los datos necesarios para el cálculo.
            - "mensaje": Descripción D (para método teórico).
            - "contexto": Contexto observable O_context (obligatorio para K).
            - "compromisos": Lista de compromisos estructurales (para método operacional).
            - "contradicciones": Número de contradicciones (para método operacional).
            - "posturas": Lista de posturas asumidas (para método operacional).
            - "reversiones": Número de reversiones de postura (para método operacional).
            - "afirmaciones": Lista de afirmaciones verificables (para método operacional).
            - "afirmaciones_falsas": Número de afirmaciones falsas (para método operacional).
            - "metodo": "teorico" o "operacional" (default: "operacional").

    Returns:
        Dict[str, Union[Fraction, type(UNDEFINED), str, None]]:
            - "C": Valor de C (Fraction o UNDEFINED).
            - "L": Valor de L (Fraction o UNDEFINED).
            - "K": Valor de K (Fraction o UNDEFINED).
            - "tru_ri": Valor de Tru_Ri (Fraction o UNDEFINED).
            - "tru_total": Valor de Tru_total (Fraction o UNDEFINED).
            - "estado": Estado del cálculo ("sin_evidencia", "evaluada", etc.).
            - "limitante": Factor limitante ("C", "L", "K" o None).
            - "detenido_en": Factor donde se detuvo el cálculo ("C", "L", "K" o None).
    """
    # Extraer datos de la petición
    mensaje = peticion.get("mensaje")
    contexto = peticion.get("contexto")
    compromisos = peticion.get("compromisos")
    contradicciones = peticion.get("contradicciones")
    posturas = peticion.get("posturas")
    reversiones = peticion.get("reversiones")
    afirmaciones = peticion.get("afirmaciones")
    afirmaciones_falsas = peticion.get("afirmaciones_falsas")
    metodo = peticion.get("metodo", "operacional")

    # Inicializar variables
    C = L = K = UNDEFINED
    tru_ri = tru_total = UNDEFINED
    estado = "sin_evidencia"
    limitante = None
    detenido_en = None

    # Calcular C
    if metodo == "teorico":
        if mensaje is not None:
            C = _calcular_c_teorico(mensaje)
        else:
            C = UNDEFINED
            detenido_en = "C"
    else:  # operacional
        if compromisos is not None and contradicciones is not None:
            C = _calcular_c_operacional(compromisos, contradicciones)
        else:
            C = UNDEFINED
            detenido_en = "C"

    # Calcular L
    if metodo == "teorico":
        if mensaje is not None:
            L = _calcular_l_teorico(mensaje)
        else:
            L = UNDEFINED
            detenido_en = "L"
    else:  # operacional
        if posturas is not None and reversiones is not None:
            L = _calcular_l_operacional(posturas, reversiones)
        else:
            L = UNDEFINED
            detenido_en = "L"

    # Calcular K
    if contexto is None:
        K = UNDEFINED
        detenido_en = "K"
    else:
        if metodo == "teorico":
            if mensaje is not None:
                K = _calcular_k_teorico(mensaje, contexto)
            else:
                K = UNDEFINED
                detenido_en = "K"
        else:  # operacional
            if afirmaciones is not None and afirmaciones_falsas is not None:
                K = _calcular_k_operacional(afirmaciones, afirmaciones_falsas, contexto)
            else:
                K = UNDEFINED
                detenido_en = "K"

    # Determinar el factor limitante
    if not es_undefined(C) and not es_undefined(L) and not es_undefined(K):
        limitante = min(C, L, K, key=lambda x: x if not es_undefined(x) else Fraction(1, 1))
        if es_undefined(limitante):
            limitante = None
        else:
            limitante = "C" if limitante == C else "L" if limitante == L else "K"
    else:
        limitante = None

    # Calcular Tru_Ri y Tru_total si C, L, K están definidos
    if not es_undefined(C) and not es_undefined(L) and not es_undefined(K):
        tru_ri = C * L * K
        from modules.constante import ALPHA, BETA
        tru_total = (tru_ri * ALPHA) + BETA
        estado = "evaluada"
    else:
        tru_ri = UNDEFINED
        tru_total = UNDEFINED
        estado = "sin_evidencia"

    return {
        "C": C,
        "L": L,
        "K": K,
        "tru_ri": tru_ri,
        "tru_total": tru_total,
        "estado": estado,
        "limitante": limitante,
        "detenido_en": detenido_en,
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
